# coding: utf-8
import json
import sys
import hashlib
import datetime
import numpy

from collections import defaultdict

from django import forms
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.core.mail import send_mail, BadHeaderError
from django.core import serializers
from django.db.models import F
from django.db.models import Max
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as authUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from ahp.models import Project, Group, User, Node, UserNodes, GroupNodes, Edge, Weight, Level, LevelNodes, Question, UserInfo


#TODO везде учесть проблему повторения, отсутсвия, обработка ошибок и все такое
#TODO класс для форм, может класс связь с моделями

#/login/?next=/ahp/#

@login_required(login_url='/ahp/login/')
def main(request):
    print >> sys.stderr, 'request.user', request.user
    return render(request, 'ahp/index.html')


def login(request):
    return HttpResponse('незалогинен')


def popup(request):
    return render(request, 'ahp/popup.html')


# +пользователь может добавлять новые критерии?
#сколько раз разрешать пользователю отправлять данные?
def form_for_participant(request, hash_user_id):
    #hash_user_id = '809ffca6e3'
    #TODO get or 404
    user = User.objects.get(id_hash=hash_user_id)
    user_group = user.group
    if request.method == 'GET':
        if user.hierarchy_form == 'check':
            HttpResponse('ты уже заполнял')
        else:
            question_list = Question.objects.filter(group=user_group)
            levels = Level.objects.order_by('order')
            level_nodes = []
            for level in levels:
                nodes = LevelNodes.objects.filter(level=level)
                if level.name == 'alternatives':
                    a = {}
                    a['name'] = level
                    a['nodes'] = []
                    for node in nodes:
                        if group_has_node(user_group, node):
                            a['nodes'].append(node)
                    level_nodes.append(a)
                else:
                    l = {}
                    l['name'] = level
                    l['nodes'] = []
                    for node in nodes:
                        if group_has_node(user_group, node):
                            l['nodes'].append(node)
                    level_nodes.append(l)
            context = {
                'question_list': question_list,
                'level_nodes': level_nodes,
            }
            return render(request, 'ahp/hierarchy_form.html', context)

    if request.method == 'POST':
        #TODO тк мы вносим в БД информацию что форма пройдена(user.hierarchy_form = 'check'), то можно заблокировать открытие формы и не перезаписывать данные
        # что делать если мы разрешии отправлять несколько раз, а пользователь снял галочку? (удалять все)
        UserNodes.objects.filter(user=user).delete()
        for field in request.POST:
            if field!='node':
                question = Question.objects.get(pk=field)
                answer = request.POST[field]
                user_info = UserInfo.objects.update_or_create(user=user, question=question,defaults=dict(answer=answer))
            else:
                for node_id in request.POST.getlist('node'):
                    node = Node.objects.get(pk=node_id)
                    user_nodes = UserNodes.objects.create(user=user, node=node)
                    group_nodes = GroupNodes.objects.get(group=user_group, node=node)
                    group_nodes.type = 'user_choice'
                    #можно накрутить количство, поэтому может в UserNodes добавить group и агрегировать по ней
                    group_nodes.count = group_nodes.count+1
                    group_nodes.save()
        user.hierarchy_form = 'check'
        user.save()
        return HttpResponse('спасибки')


def group_has_node(group, node):
    group_nodes = GroupNodes.objects.filter(group=group)
    for group_node in group_nodes:
        if node.node.pk == group_node.node.pk:
            return True
    return False

@login_required(login_url='/auth/')
def common_hierarchy(request):
    nodes = serializers.serialize('json', Node.objects.all())
    edges = serializers.serialize('json', Edge.objects.all())
    levels = serializers.serialize('json', Level.objects.all())
    level_nodes = serializers.serialize('json', LevelNodes.objects.all())
    return HttpResponse(json.dumps({
        'nodes': nodes,
        'edges': edges,
        'levels': levels,
        'level_nodes': level_nodes
    }), content_type="application/json")


#put level(add, change, delete)
def level(request):
    data = json.loads(request.body)
    name = data['name']
    description = data['description']
    level_id = data['level_id']
    order = data['order']
    if data['act_type'] == 'add':
        Level.objects.create(order=order, name=name, description=description )
    #пока что редактировани только инфы(нет перемещений)
    if data['act_type'] == 'edit':
        level = Level.objects.get(pk=level_id)
        level.name = name
        level.description = description
        level.save()
    if data['act_type'] == 'delet':
        #удаляем все edge c таким потомком и переформируем
        level = Level.objects.get(pk=level_id)
        edge_consist(level)
        node_consist(level)
        level.delete()
        order_consist(order)
    return HttpResponse('')


def edge_consist(level):
    parent_nodes, children_nodes = level_edges_nodes(level)
    for parent_node in parent_nodes:
        for child_node in children_nodes:
            Edge.objects.create(node=child_node.node, parent=parent_node.node, level=level)
    Edge.objects.filter(level=level).delete()


def node_consist(level):
    level_nodes = LevelNodes.objects.filter(level=level)
    for level_node in level_nodes:
        Node.objects.get(pk=level_node.node.pk).delete()

#put node(add, change, delete)
#пока что без нормального ветвления
def node(request):
    data = json.loads(request.body)
    node_id = data['node_id']
    level_id = data['level_id']
    name = data['name']
    description = data['description']
    level = Level.objects.get(pk=level_id)
    parent_nodes, children_nodes = level_edges_nodes(level)

    if data['act_type'] == 'add':
        node = Node.objects.create(name=name, description=description)
        LevelNodes.objects.create(level=level, node=node)
        for parent_node in parent_nodes:
            Edge.objects.create(node=node, parent=parent_node.node, level=level)
        for child_node in children_nodes:
            Edge.objects.create(node=child_node.node, parent=node, level=level)
    #пока что редактировани только инфы(без перемещений в другие уровни)
    if data['act_type'] == 'edit':
        node = Node.objects.get(pk=node_id)
        node.name = name
        node.description = description
        node.save()
    if data['act_type'] == 'delet':
        node = Node.objects.get(pk=node_id)
        #может и не понадобиттся? вдруг удаяляется автоматически вместе с вершиной
        Edge.objects.filter(node=node).delete()
        Edge.objects.filter(parent=node).delete()
        node.delete()
    return HttpResponse('')


def level_edges_nodes(level):
    max_order = Level.objects.all().aggregate(Max('order'))['order__max']
    if level.order == 2 and level.order == max_order:
        l_parent = Level.objects.get(order=0)
        l_child = Level.objects.get(order=1)
    elif level.order == 2 :
        l_parent = Level.objects.get(order=0)
        l_child = Level.objects.get(order=level.order+1)
    elif  level.order == 1:
        l_parent = Level.objects.get(order=max_order)
        l_child = None
    elif  level.order == max_order:
        l_parent = Level.objects.get(order=level.order-1)
        l_child = Level.objects.get(order=1)
    elif  level.order == 0:
        l_parent = None
        l_child = None
    else:
        l_parent = Level.objects.get(order=level.order-1)
        l_child = Level.objects.get(order=level.order+1)
    parent_nodes = LevelNodes.objects.filter(level=l_parent)
    children_nodes = LevelNodes.objects.filter(level=l_child)
    print >> sys.stderr, parent_nodes
    print >> sys.stderr, children_nodes
    return parent_nodes, children_nodes


def order_consist(order_of_modified):
    l = Level.objects.filter(order__gt=order_of_modified).update(order=F('order')-1)


#get groups
def groups_list(request):
    groups = serializers.serialize('json', Group.objects.all())
    groups_count = {}
    for group in Group.objects.all():
         groups_count[group.pk] = { 'for_hierarchy': GroupNodes.objects.filter(group=group).count(),
                                    'for_comparison': GroupNodes.objects.filter(group=group, type='for comparison form').count()}
    return HttpResponse(json.dumps({
        'groups': groups,
        'groups_count': groups_count
    }), content_type="application/json")


#put group(add, change, delete)
def group(request):
    data = json.loads(request.body)
    group_id = data['group_id']
    name = data['name']
    description = data['description']
    if data['act_type'] == 'add':
        Group.objects.create(name=name, description=description)
    if data['act_type'] == 'edit':
        g = Group.objects.get(pk=group_id)
        g.name = name
        g.descrpition = descrpition
        g.save()
    if data['act_type'] == 'delet':
        g = Group.objects.get(pk=group_id)
        g.delete()
        #удаление из GroupNodes?
    return HttpResponse('')


#get groups nodes
def group_nodes_list(request):
    #filter на type
    groups_nodes = serializers.serialize('json', GroupNodes.objects.all())
    return HttpResponse(json.dumps({
        'group_nodes': groups_nodes
    }), content_type="application/json")


#TODO делать ли отдельно для каждой группы?
def group_nodes(request):
    GroupNodes.objects.all().delete()
    data = json.loads(request.body)
    for group in data:
        g = Group.objects.get(pk=group)
        for node in data[group]:
            n = Node.objects.get(pk=node)
            GroupNodes.objects.create(group=g, node=n, type='for hierarchy form', count=0)
    return HttpResponse('')


def chosen_group_nodes(request):
    data = json.loads(request.body)
    nodes = data['nodes']
    group = data['group']
    GroupNodes.objects.filter(group=group).delete()
    for node in nodes:
        n = Node.objects.get(pk=node)
        g = Group.objects.get(pk=group)
        GroupNodes.objects.create(group=g, node=n, type='for hierarchy form', count=0)
    return HttpResponse('')


#put question(add,delete,edit)
def question(request):
    data = json.loads(request.body)
    question_id = data['question_id']
    group_id = data['group_id']
    name = data['name']
    descrpition = data['descrpition']
    if data['act_type'] == 'add':
        g = Group.objects.get(pk=group_id)
        Question.objects.create(group=g, name=name, description=description)
    if data['act_type'] == 'edit':
        q = Question.objects.get(pk=question_id)
        q.name = name
        q.description = description
        q.save()
    if data['act_type'] == 'delet':
        q = Question.objects.get(pk=question_id)
        q.delete()
    return HttpResponse('')


#get all question
def group_question_list(request):
    group_questions = serializers.serialize('json', Question.objects.all())
    return HttpResponse(json.dumps({
        'group_questions': group_questions
    }), content_type="application/json")


#put user(add,delete,edit)
def user(request):
    data = json.loads(request.body)
    user_id = data['user_id']
    name = data['name']
    description = data['description']
    email = data['email']
    group_id = data['group_id']
    confidence = 1
    if data['act_type'] == 'add':
        group = Group.objects.get(pk=group_id)
        User.objects.create(name=name, description='', email=email, id_hash='', group=group, confidence=1)
    if data['act_type'] == 'edit':
        g = Group.objects.get(pk=group_id)
        u = User.objects.get(pk=user_id)
        u.name = name
        u.description = description
        u.email = email
        u.group = g
        u.save()
    if data['act_type'] == 'delet':
        u = User.objects.get(pk=user_id)
        u.delete()
    return HttpResponse('')


#get all users
def users_list(request):
    users = serializers.serialize('json', User.objects.all())
    return HttpResponse(json.dumps({
        'users': users
    }), content_type="application/json")


#put all questions
def questions(request):
    Question.objects.all().delete()
    data = json.loads(request.body)
    for question in data:
        print >> sys.stderr, question
        n = question['name']
        d = question['description']
        g_id = question['group']
        g = Group.objects.get(pk=g_id)
        Question.objects.create(group=g, name=n, description=d)
    return HttpResponse('')


#send email !
def email(request):
    data = json.loads(request.body)
    user_id = data['user_id']
    text = data['text']
    act_type = data['act_type']
    user = User.objects.get(pk=user_id)
    user.id_hash = hash_id(user_id)
    if act_type == 'send_email_hierarchy':
        header = 'Исследование1'
        url = request.build_absolute_uri(reverse("ahp.views.form_for_participant", kwargs={'hash_user_id': user.id_hash}))
        text = data['text'] + '    ' + url
        email = user.email
        send_email(header, text, email)
        user.hierarchy_form = 'email'
    if act_type == 'send_email_comparison':
        header = 'Исследование2'
        url = request.build_absolute_uri(reverse("ahp.views.form_for_comparison", kwargs={'hash_user_id': user.id_hash}))
        text = data['text'] + '    ' + url
        email = user.email
        send_email(header, text, email)
        # if пиьсмо прекрасно отправлено
        user.comparison_form = 'email'
    user.save()
    return HttpResponse('')


def hash_id(id):
    hash_str = hashlib.sha1(str(id)).hexdigest()
    hash = hash_str[-10:]
    return hash


def send_email(header, text, email):
    try:
        # заголовок,  текст,  адрес рассылки,  адрес получателя,  и непоятный параметр
        print >> sys.stderr, 'TRY SEND EMAIL TO  '+'email: '+email+'  WITH TEXT  '+text
        send_mail(header, text, 'qjkzzz@gmail.com', [email], fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found.')


#может быть вообще не нужен save
#сохранение выбранных вершин для всех групп
def chosen_group_nodes_for_comparison(request):
    data = json.loads(request.body)
    group = data['group']
    nodes = data['nodes']
    GroupNodes.objects.filter(group=group, type='for comparison form').update(type='for hierarchy form')
    for node in nodes:
        g = Group.objects.get(pk=group)
        n = Node.objects.get(pk=node)
        group_node = GroupNodes.objects.get(group=g, node=n)
        group_node.type = 'for comparison form'
        group_node.save()
    return HttpResponse('')


def form_for_comparison(request, hash_user_id):
    #hash_user_id = '809ffca6e3'
    #TODO get or 404
    #  TODO - делать ли кнопку назад? (если да, то в GET считываем из БД, тогда в БД добавить поле с view и наверное даже новую таблицу(потому что пары формируются при обращении, в БД только вектор)
    line = [{'val':9, 'view':9},
            {'val':8, 'view':8},
            {'val':7, 'view':7},
            {'val':6, 'view':6},
            {'val':5, 'view':5},
            {'val':4, 'view':4},
            {'val':3, 'view':3},
            {'val':2, 'view':2},
            {'val':1, 'view':1},
            {'val':1.0/2, 'view':2},
            {'val':1.0/3, 'view':3},
            {'val':1.0/4, 'view':4},
            {'val':1.0/5, 'view':5},
            {'val':1.0/6, 'view':6},
            {'val':1.0/7, 'view':7},
            {'val':1.0/8, 'view':8},
            {'val':1.0/9, 'view':9},
            ]
    user = User.objects.get(id_hash=hash_user_id)
    user_group = user.group
    pairwise_list = data_for_comparison(user_group)

    paginator = Paginator(pairwise_list, 1) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        bunches = paginator.page(page)
    except PageNotAnInteger:
        bunches = paginator.page(1)
    except EmptyPage:
        bunches = paginator.page(paginator.num_pages)
    if request.method == 'GET':
        messages = ''
        action = ''
        return render_to_response('ahp/pairwise_comparison_form.html', {'bunches': bunches, 'line': line, 'messages': messages, action: 'action' })

    if request.method == 'POST':
        # TODO сохранять предыдущие отмеченные результаты(тогда новая таблица нужна)
        # TODO сделать нормальные урлы
        #http://127.0.0.1:8000/ahp/comparison/4781b33fa1/
        number = len(pairwise_list[int(bunches.number)-1]['children'])
        pairwise_list[int(bunches.number)-1]['children'] = insert_priority(request.POST, pairwise_list[int(bunches.number)-1]['children'], line)
        # проверка на заполненность всех вершин (кнопка не должна загораться до того как отмечены все и не прошли проверку)
        if len(request.POST) == number+1 :
            node_list, Matrix = create_Matrix(pairwise_list[int(bunches.number)-1]['children'])
            OS, vector_priority, isRecalculation = calculate_weigth(Matrix)
            if 'auto_revision' in request.POST:
                return save_and_next(node_list, vector_priority, user, pairwise_list[int(bunches.number)-1]['parent'], bunches)
            if 'next' in request.POST:
                if isRecalculation:
                    for_message = ''
                    for index, node in enumerate(node_list):
                        for_message = for_message + 'node: ' +str(node)+'vector_priority: '+str(vector_priority[index])
                    messages = 'вы сравнили плохо, пересравните или автоматически ваши оценки пересчитаются вот так: '+for_message
                    action = 'recalculation'
                    return render_to_response('ahp/pairwise_comparison_form.html', {'bunches': bunches, 'line': line, 'messages': messages,  'action': action })
                else:
                    return save_and_next(node_list, vector_priority, user, pairwise_list[int(bunches.number)-1]['parent'], bunches)
        else:
            messages = 'сравните пжлста все критерии'
            action = 'not all'
            return render_to_response('ahp/pairwise_comparison_form.html', {'bunches': bunches, 'line': line, 'messages': messages, action: 'action' })# + message


def save_and_next(node_list, vector_priority, user, parent, bunches):
    for index, node in enumerate(node_list):
        edge = Edge.objects.get(parent=parent, node=node)
        weight = Weight.objects.update_or_create(edge=edge, user=user, defaults=dict(weight=vector_priority[index]))
    if bunches.has_next():
        user.comparison_form = str(bunches.number)
        user.save()
        url = "/ahp/comparison/"+str(user.id_hash)+"?page="+str(bunches.next_page_number())
        return redirect(url)
    else:
        user.comparison_form = 'check'
        user.save()
        return HttpResponse('спасибки')


def insert_priority(data, pairwise_nodes, line):
    for index_node in data:
        # избавиться от этого {u'next':
        if index_node != 'next' and index_node != 'auto_revision':
            #избавиться от первого индекса потому что его можно брять у тек страницы + попробовать присваивать значения кортежами?(но нои не поппорядку)
            pairwise_nodes[int(index_node)]['priority'] = line[int(data[index_node])]['val']
            pairwise_nodes[int(index_node)]['value'] = int(data[index_node])
            #pairwise_list[int(nodes[0])]['children'][int(nodes[1])]['priority'] = line[int(request.POST[index_node])]['val']
    return pairwise_nodes;


def create_Matrix(bunch_nodes):
    node_list = []
    for couple_nodes in bunch_nodes:
        if node_list.count(couple_nodes['left_node']) == 0:
            node_list.append(couple_nodes['left_node'])
        if node_list.count(couple_nodes['right_node']) == 0:
            node_list.append(couple_nodes['right_node'])
    size = len(node_list)
    Matrix =  numpy.ones((size, size))
    for couple_nodes in bunch_nodes:
        l_i = node_list.index(couple_nodes['left_node'])
        r_i = node_list.index(couple_nodes['right_node'])
        Matrix[l_i][r_i] = float(couple_nodes['priority'])
        Matrix[r_i][l_i] = 1.0/float(couple_nodes['priority'])
    return node_list, Matrix


def calculate_weigth(Matrix):
    SS = [0.0, 0.0, 0.0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, 1.51, 1.48, 1.56, 1.57, 1.59]
    eigenvalues, eigenvectors = numpy.linalg.eig(Matrix)
    lyambd_max = eigenvalues.max()
    index_max = eigenvalues.argmax()
    eigenvector =  eigenvectors[:,index_max].real
    norma = eigenvector.sum()
    vector_priority =  eigenvector/eigenvector.sum()
    size = len(vector_priority)
    IS = (lyambd_max - size)/(size-1)
    if size > 2 :
        OS = IS/SS[size]
    else:
        OS = 0
    if OS > 0.3:
        isRecalculation = True
        revision_of_judgments(Matrix, vector_priority)
    else:
        try:
            isRecalculation
        except NameError:
            isRecalculation = False
    return OS, vector_priority, isRecalculation


def revision_of_judgments(Matrix, vector_priority):
    #разобраться и сделать со строками
    size = len(vector_priority)
    Matrix_W =  numpy.ones((size, size))
    for i in range(0, size):
        for j in range(0, size):
            Matrix_W[i][j] = float(vector_priority[i]/vector_priority[j])
            Matrix_W[j][i] = float(vector_priority[j]/vector_priority[i])
    Matrix_delta = numpy.zeros((size, size))
    Matrix_delta = numpy.absolute(Matrix - Matrix_W)
    i,j = numpy.unravel_index(Matrix_delta.argmax(), Matrix_delta.shape)
    Matrix[i][j] = float(vector_priority[i]/vector_priority[j])
    calculate_weigth(Matrix)


def data_for_comparison(group):
    group_nodes_ids = GroupNodes.objects.values_list('node', flat=True).filter(type='for comparison form', group=group)
    ids = set(group_nodes_ids) | set('1')
    edges = Edge.objects.all()
    levels_queryset = Level.objects.order_by('order')
    levels = list(levels_queryset)
    alt_level = levels.pop(1)
    levels.append(alt_level)
    pairwise_list = []
    for level in levels:
        nodes = LevelNodes.objects.filter(node__in=set(ids), level=level)
        for node in nodes:
            children_nodes = Edge.objects.filter(parent=node.node, node__in=set(ids))
            if len(children_nodes)>1:
                pairwise_bunch = {}
                pairwise_bunch['parent'] = node.node
                pairwise_bunch['children'] = pairwise_generation(children_nodes)
                pairwise_list.append(pairwise_bunch)
    return pairwise_list



def pairwise_generation(nodes):
    nodes_list = []
    include_nodes = []
    for node_left in nodes:
        include_nodes.append(node_left)
        for node_right in set(nodes).difference(include_nodes):
            pairwise_obj = {}
            pairwise_obj['left_node'] = node_left.node
            pairwise_obj['right_node']= node_right.node
            pairwise_obj['priority'] = ''
            pairwise_obj['value'] = ''
            nodes_list.append(pairwise_obj)
    return nodes_list


def global_priority_calculation(request):
    #1. обработка request
    """
    group_id = 66
    group = Group.objects.get(pk=group_id)
    group_nodes = GroupNodes.objects.filter(group=group)
    """
    #или передавать сразу
    # groups, users
    #если мы передаем пользователей, значит надо брать готовый список, но пока мы этого не делаем, потом просто будем брать список из запроса
    #хотя если пользователи. то они из одной группы обычно, так что смысла мало(напишу потом если понадобится)
    for group in groups:
        group_nodes = GroupNodes.objects.filter(group=group)
        group_users = User.objects.filter(group=group)
        nodes_list.extend(group_nodes)#склейка массивов
        users_list.extend(group_users)#склейка массивов
    nodes = list(set(nodes_list))
    users = list(set(users_list))#хотя зачем если они и так не повторяются?

#может передавать группы, чтобы в будущем учитывать вес каждой??
    global_priority = loop_tree(nodes, users, groups)

    print >> sys.stderr,'global_priority  ',  global_priority
    return HttpResponse('')

#везде передавать users или group
#по group формируем вершины, по users - веса
#доделать это и начать засовывать ангулар
#
def loop_tree(nodes, users, groups):
    level = Level.objects.get(name='alternatives')
    alternatives = Edge.objects.filter(level=level, node__in=set(nodes.values_list('node', flat=True)))
    Matrix = create_weigth_Matrix(alternatives, users)
    while len(set(edges.values_list('parent', flat=True)))>1:
        groups_edges = edges.filter(node__in=set(nodes.values_list('node', flat=True)))
        parent_edges = Edge.objects.filter(node__in=set(groups_edges.values_list('parent', flat=True)))# +groupnodes
        parent_Matrix = create_weigth_Matrix(parent_edges, users)
        new_Matrix = numpy.dot(Matrix, parent_Matrix)
        Matrix = new_Matrix
        edges = parent_edges
    return Matrix


def create_weigth_Matrix(edges, users):
    nodes = list(set(edges.values_list('node', flat=True)))
    parents = list(set(edges.values_list('parent', flat=True)))
    print >> sys.stderr,'nodes',  nodes
    print >> sys.stderr,'parents', parents
    print >> sys.stderr,'     '

    Matrix =  numpy.zeros((len(nodes), len(parents)), "f")
    for index_node, node in enumerate(nodes):
        for index_parent, parent in enumerate(parents):
            edge = edges.get(node=node,parent=parent)
            for user in users:
            #for users in user =>
                Matrix[index_node][index_parent] = Weight.objects.get(edge=edge, user=user).weight#^в степени доверия к пользователю(в зависимости от группы или противоречивости)
            #Matrix[index_node][index_parent] берем корень из этого всего равный колву пользователей (len(users))
    return Matrix


