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
from django.db.models import F, Max, Sum, Q
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as authUser
from django.contrib.auth import authenticate, login, logout, views
from django.contrib.auth.decorators import login_required, user_passes_test

from ahp.models import Project, Group, User, Node, UserNodes, GroupNodes, Edge, Weight, Level, LevelNodes, Question, UserInfo


#TODO везде учесть проблему повторения, отсутсвия, обработка ошибок и все такое
#TODO класс для форм, может класс связь с моделями


def main(request):
    if Project.objects.filter(type='current').count()==1:
        return render(request, 'ahp/index.html')
    else:
        url = "/ahp/projects/"
        return redirect(url)


def projects(request):
    if request.method == 'GET':
        projects_list = Project.objects.all()
        Project.objects.all().update(type='')
        return render(request, 'ahp/projects.html', {'projects': projects_list})
    if request.method == 'POST':
        if len(request.POST)>0:
            for field in request.POST:
                project_id = request.POST[field]
            if project_id == 'new':
                project = Project.objects.create(info='...', type='current')
                level_goal = Level.objects.create(project=project, name='goal', description='', order=0)
                node_goal = Node.objects.create(project=project, name='', description='')
                ln_goal = LevelNodes.objects.create(project=project, level=level_goal, node=node_goal)
                Level.objects.create(project=project, name='alternatives', description='', order=1)
            else:
                p = Project.objects.get(pk=project_id)
                p.type = 'current'
                p.save()
            url = "/ahp"
            return redirect(url)
        else:
            return render(request, 'ahp/projects.html', {'projects': projects_list})


def hierarchy_graph(request):
    return render(request, 'ahp/hierarchy_graph.html')


def hierarchy(request):
    return render(request, 'ahp/hierarchy.html')


def group_template(request):
    return render(request, 'ahp/group_template.html')


def votes(request):
    return render(request, 'ahp/votes.html')


def priority(request):
    return render(request, 'ahp/priority.html')


def login(request):
    template_response = views.login(request)
    return template_response


def popup(request):
    return render(request, 'ahp/popup.html')

def group_questions(request):
    return render(request, 'ahp/group_questions.html')


def form_for_participant(request, hash_user_id):
    user = User.objects.get(id_hash=hash_user_id)
    project = user.project
    user_group = user.group
    level = Level.objects.get(name='goal', project=project)
    goal = LevelNodes.objects.get(level=level, project=project).node
    if request.method == 'GET':
        if user.hierarchy_form == 'check':
            return render(request, 'ahp/form_thanks.html')
        if user.hierarchy_form == 'timeout':
            return HttpResponse('')
        else:
            question_list = Question.objects.filter(group=user_group, project=project)
            levels = Level.objects.filter(project=project).order_by('order')
            level_nodes = []
            a = {}
            for level in levels:
                nodes = LevelNodes.objects.filter(level=level, project=project)
                if level.name == 'alternatives':
                    a['name'] = 'Возможные исходы'
                    a['nodes'] = []
                    for node in nodes:
                        if group_has_node(user_group, node):
                            a['nodes'].append(node)
                else:
                    if level.name != 'goal':
                        l = {}
                        l['name'] = level.name
                        l['nodes'] = []
                        for node in nodes:
                            if group_has_node(user_group, node):
                                l['nodes'].append(node)
                        level_nodes.append(l)
            level_nodes.append(a)
            context = {
                'question_list': question_list,
                'level_nodes': level_nodes,
                'user': user,
                'goal': Node.objects.get(pk=goal.pk)
            }
            return render(request, 'ahp/hierarchy_form.html', context)

    if request.method == 'POST':
        #if len(request.POST.getlist('node'))<3:
        for field in request.POST:
            if field!='node':
                question = Question.objects.get(pk=field, project=project)
                answer = request.POST[field]
                user_info = UserInfo.objects.update_or_create(user=user, question=question, defaults=dict(answer=answer))
            else:
                for node_id in request.POST.getlist('node'):
                    node = Node.objects.get(pk=node_id, project=project)
                    user_nodes = UserNodes.objects.create(user=user, node=node, project=project)
                    group_nodes = GroupNodes.objects.get(group=user_group, node=node)
                    #group_nodes.type = 'user_choice'
                    group_nodes.count = group_nodes.count+1
                    group_nodes.save()
        user.hierarchy_form = 'check'
        user.save()
        return render(request, 'ahp/form_thanks.html')


def group_has_node(group, node):
    group_nodes = GroupNodes.objects.filter(group=group)
    for group_node in group_nodes:
        if node.node.pk == group_node.node.pk:
            return True
    return False


def common_hierarchy(request):
    project = Project.objects.get(type='current')
    nodes = serializers.serialize('json', Node.objects.filter(project=project))
    edges = serializers.serialize('json', Edge.objects.filter(project=project))
    levels = serializers.serialize('json', Level.objects.filter(project=project))
    level_nodes = serializers.serialize('json', LevelNodes.objects.filter(project=project))
    return HttpResponse(json.dumps({
        'nodes': nodes,
        'edges': edges,
        'levels': levels,
        'level_nodes': level_nodes
    }), content_type="application/json")


#put level(add, change, delete)
def level(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    name = data['name']
    description = data['description']
    level_id = data['level_id']
    order = data['order']
    if data['act_type'] == 'add':
        Level.objects.create(order=order, name=name, description=description, project=project, type='')
    if data['act_type'] == 'edit':
        level = Level.objects.get(pk=level_id, project=project)
        level.name = name
        level.description = description
        level.save()
    if data['act_type'] == 'delet':
        level = Level.objects.get(pk=level_id, project=project)
        edge_consist(level)
        node_consist(level)
        level.delete()
        order_consist(order)
    return HttpResponse('')


def edge_consist(level):
    project = Project.objects.get(type='current')
    parent_nodes, children_nodes, l_child = level_edges_nodes(level)
    for parent_node in parent_nodes:
        for child_node in children_nodes:
            Edge.objects.create(node=child_node.node, parent=parent_node.node, level=l_child, project=project)
    Edge.objects.filter(level=level, project=project).delete()


def node_consist(level):
    project = Project.objects.get(type='current')
    level_nodes = LevelNodes.objects.filter(level=level)
    for level_node in level_nodes:
        Node.objects.get(pk=level_node.node.pk, project=project).delete()

#put node(add, change, delete)
#пока что без нормального ветвления
def node(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    node_id = data['node_id']
    level_id = data['level_id']
    name = data['name']
    description = data['description']
    level = Level.objects.get(pk=level_id)
    parent_nodes, children_nodes, l_child = level_edges_nodes(level)

    if data['act_type'] == 'add':
        node = Node.objects.create(name=name, description=description, project=project)
        LevelNodes.objects.create(level=level, node=node, project=project)
        for parent_node in parent_nodes:
            Edge.objects.create(node=node, parent=parent_node.node, level=level, project=project)
        for child_node in children_nodes:
            Edge.objects.create(node=child_node.node, parent=node, level=l_child, project=project)
        if LevelNodes.objects.filter(level=level, project=project).count()==1:
            for parent_node in parent_nodes:
                for child_node in children_nodes:
                    Edge.objects.filter(node=child_node.node, parent=parent_node.node, project=project).delete()
    #пока что редактировани только инфы(без перемещений в другие уровни)
    if data['act_type'] == 'edit':
        node = Node.objects.get(pk=node_id, project=project)
        node.name = name
        node.description = description
        node.save()
        if LevelNodes.objects.get(node=node, project=project).level == Level.objects.get(name='goal', project=project):
            project.info = name
            project.save()
    if data['act_type'] == 'delet':
        node = Node.objects.get(pk=node_id, project=project)
        #может и не понадобиттся? вдруг удаяляется автоматически вместе с вершиной
        Edge.objects.filter(node=node, project=project).delete()
        Edge.objects.filter(parent=node, project=project).delete()
        node.delete()
        if LevelNodes.objects.filter(level=level, project=project).count()==0:
            for parent_node in parent_nodes:
                for child_node in children_nodes:
                    Edge.objects.create(node=child_node.node, parent=parent_node.node, level=l_child, project=project)
    return HttpResponse('')


def level_edges_nodes(level):
    project = Project.objects.get(type='current')
    max_order = Level.objects.filter(project=project).aggregate(Max('order'))['order__max']
    if level.order == 2 and level.order == max_order:
        l_parent = Level.objects.get(order=0, project=project)
        l_child = Level.objects.get(order=1, project=project)
    elif level.order == 2 :
        l_parent = Level.objects.get(order=0, project=project)
        l_child = Level.objects.get(order=level.order+1, project=project)
    elif  level.order == 1:
        l_parent = Level.objects.get(order=max_order, project=project)
        l_child = None
    elif  level.order == max_order:
        l_parent = Level.objects.get(order=level.order-1, project=project)
        l_child = Level.objects.get(order=1, project=project)
    elif  level.order == 0:
        l_parent = None
        l_child = None
    else:
        l_parent = Level.objects.get(order=level.order-1, project=project)
        l_child = Level.objects.get(order=level.order+1, project=project)
    parent_nodes = LevelNodes.objects.filter(level=l_parent, project=project)
    children_nodes = LevelNodes.objects.filter(level=l_child, project=project)
    return parent_nodes, children_nodes, l_child


def order_consist(order_of_modified):
    project = Project.objects.get(type='current')
    l = Level.objects.filter(order__gt=order_of_modified, project=project).update(order=F('order')-1)


#get groups
def groups_list(request):
    project = Project.objects.get(type='current')
    groups = serializers.serialize('json', Group.objects.filter(project=project))
    groups_count = {}
    for group in Group.objects.filter(project=project):
        #project=project?
         groups_count[group.pk] = { 'for_hierarchy': GroupNodes.objects.filter(group=group, project=project).count(),
                                    'for_comparison': GroupNodes.objects.filter(group=group, project=project, type='for comparison form').count()}
    return HttpResponse(json.dumps({
        'groups': groups,
        'groups_count': groups_count
    }), content_type="application/json")


#put group(add, change, delete)
def group(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    group_id = data['group_id']
    name = data['name']
    description = data['description']
    if data['act_type'] == 'add':
        g = Group.objects.create(name=name, description=description, project=project)
        name_q = 'Если Вы считаете, что есть критерии, которые не учтены в иерархии выше, то напишите их и укажите уровень, к которому вы бы их отнесли'
        q = Question.objects.create(group=g, name=name_q, description='special', project=project)
    if data['act_type'] == 'edit':
        g = Group.objects.get(pk=group_id, project=project)
        g.name = name
        g.descrpition = descrpition
        g.save()
    if data['act_type'] == 'delet':
        g = Group.objects.get(pk=group_id, project=project)
        g.delete()
        #удаление из GroupNodes?
    return HttpResponse('')


#get groups nodes
def group_nodes_list(request):
    project = Project.objects.get(type='current')
    groups_nodes = serializers.serialize('json', GroupNodes.objects.filter(project=project))
    return HttpResponse(json.dumps({
        'group_nodes': groups_nodes
    }), content_type="application/json")


def users_answer_hierarchy(request):
    project = Project.objects.get(type='current')
    user_nodes = serializers.serialize('json', UserNodes.objects.filter(project=project))
    return HttpResponse(json.dumps({
        'user_nodes': user_nodes
    }), content_type="application/json")


def users_answer_comparison(request):
    user_comparison = {}
    project = Project.objects.get(type='current')
    users = User.objects.filter(comparison_form='check', project=project)
    for user in users:
        user_comparison[user.pk] = create_user_answer_comparison(user);
    return HttpResponse(json.dumps({
        'user_comparison': user_comparison
    }), content_type="application/json")


def create_user_answer_comparison(user):
    answer = []
    project = Project.objects.get(type='current')
    user_nodes = GroupNodes.objects.values_list('node', flat=True).filter(type='for comparison form', group=user.group, project=project)
    level = Level.objects.get(name='goal', project=project)
    goal = LevelNodes.objects.get(level=level, project=project).node
    edges = Edge.objects.filter(parent=goal, node__in=set(user_nodes), project=project)
    while len(edges.values_list('node', flat=True))>0:
        parent_edges = set(edges.values_list('parent', flat=True))
        for parent in parent_edges:
            answer_obj = {}
            answer_obj['parent'] = parent
            answer_obj['nodes'] = []
            bunch_edges = edges.filter(parent=parent)
            for edge in bunch_edges:
                answer_node = {}
                answer_node['node'] = edge.node.pk
                answer_node['weight'] = Weight.objects.get(user=user, edge=edge).weight
                answer_obj['nodes'].append(answer_node)
            answer.append(answer_obj)
        edges = Edge.objects.filter(node__in=set(user_nodes), parent__in=set(edges.values_list('node', flat=True)), project=project)
    return answer


#TODO делать ли отдельно для каждой группы?
def group_nodes(request):
    project = Project.objects.get(type='current')
    GroupNodes.objects.filter(project=project).delete()
    data = json.loads(request.body)
    for group in data:
        g = Group.objects.get(pk=group, project=project)
        for node in data[group]:
            n = Node.objects.get(pk=node, project=project)
            GroupNodes.objects.create(group=g, node=n, type='for hierarchy form', count=0, project=project)
    return HttpResponse('')


def chosen_group_nodes(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    nodes = data['nodes']
    group = data['group']
    GroupNodes.objects.filter(group=group, project=project).delete()
    for node in nodes:
        n = Node.objects.get(pk=node, project=project)
        g = Group.objects.get(pk=group, project=project)
        GroupNodes.objects.create(group=g, node=n, type='for hierarchy form', count=0, project=project)
    return HttpResponse('')


#put question(add,delete,edit)
def question(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    question_id = data['question_id']
    group_id = data['group_id']
    name = data['name']
    descrpition = data['descrpition']
    if data['act_type'] == 'add':
        g = Group.objects.get(pk=group_id, project=project)
        Question.objects.create(group=g, name=name, description=description, project=project)
    if data['act_type'] == 'edit':
        q = Question.objects.get(pk=question_id, project=project)
        q.name = name
        q.description = description
        q.save()
    if data['act_type'] == 'delet':
        q = Question.objects.get(pk=question_id, project=project)
        q.delete()
    return HttpResponse('')


#get all question
def group_question_list(request):
    project = Project.objects.get(type='current')
    group_questions = serializers.serialize('json', Question.objects.filter(project=project))
    return HttpResponse(json.dumps({
        'group_questions': group_questions
    }), content_type="application/json")


#put user(add,delete,edit)
def user(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    user_id = data['user_id']
    name = data['name']
    description = data['description']
    email = data['email']
    group_id = data['group_id']
    confidence1 = 0
    confidence2 = 0
    if data['act_type'] == 'add':
        group = Group.objects.get(pk=group_id, project=project)
        User.objects.create(name=name, description='', email=email, id_hash='', group=group, confidence1=confidence1, confidence2=confidence2, project=project)
    if data['act_type'] == 'edit':
        g = Group.objects.get(pk=group_id, project=project)
        u = User.objects.get(pk=user_id, project=project)
        u.name = name
        u.description = description
        u.email = email
        u.group = g
        u.save()
    if data['act_type'] == 'delet':
        u = User.objects.get(pk=user_id, project=project)
        u.delete()
    return HttpResponse('')


#get all users
def users_list(request):
    project = Project.objects.get(type='current')
    users = serializers.serialize('json', User.objects.filter(project=project))
    return HttpResponse(json.dumps({
        'users': users
    }), content_type="application/json")


#put all questions
def questions(request):
    project = Project.objects.get(type='current')
    Question.objects.filter(project=project).delete()
    data = json.loads(request.body)
    for question in data:
        n = question['name']
        d = question['description']
        g_id = question['group']
        g = Group.objects.get(pk=g_id, project=project)
        Question.objects.create(group=g, name=n, description=d, project=project)
    return HttpResponse('')


#send email !
def email(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    user_id = data['user_id']
    text = data['text']
    act_type = data['act_type']
    user = User.objects.get(pk=user_id, project=project)
    str_id = str(user_id) + str(project.pk)
    user.id_hash = hash_id(str_id)
    if act_type == 'send_email_hierarchy':
        header = 'Исследование: первый этап'
        url = request.build_absolute_uri(reverse("ahp.views.form_for_participant", kwargs={'hash_user_id': user.id_hash}))
        word = u'ссылке'
        to_href = '<a href="'+url+'">'+word+'</a>'
        text = data['text']
        text = text.replace(word, to_href)
        email = user.email
        send_email(header, text, email)
        user.hierarchy_form = 'email'
    if act_type == 'send_email_comparison':
        header = 'Исследование: второй этап'
        url = request.build_absolute_uri(reverse("ahp.views.form_for_comparison", kwargs={'hash_user_id': user.id_hash}))
        word = u'ссылке'
        to_href = '<a href="'+url+'">'+word+'</a>'
        text = data['text']
        text = text.replace(word, to_href)
        email = user.email
        send_email(header, text, email)
        user.comparison_form = 'email'
    user.save()
    return HttpResponse('')


def hash_id(id):
    hash_str = hashlib.sha1(id).hexdigest()
    hash = hash_str[-10:]
    return hash


def send_email(header, text, email):
    try:
        print >> sys.stderr, 'TRY SEND EMAIL TO  '+'email: '+email+'  WITH TEXT  '+text
        send_mail(header, '', 'qjkzzz@gmail.com', [email], fail_silently=False, html_message=text)
    except BadHeaderError:
        return HttpResponse('Invalid header found.')


#может быть вообще не нужен save
#сохранение выбранных вершин для всех групп
def chosen_group_nodes_for_comparison(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    group = data['group']
    nodes = data['nodes']
    GroupNodes.objects.filter(group=group, type='for comparison form', project=project).update(type='for hierarchy form')
    for node in nodes:
        g = Group.objects.get(pk=group, project=project)
        n = Node.objects.get(pk=node, project=project)
        group_node, created = GroupNodes.objects.get_or_create(group=g, node=n, project=project, defaults={'type': '', 'count':0})
        #group_node = GroupNodes.objects.create(group=g, node=n, project=project, type='')
        group_node.type = 'for comparison form'
        group_node.save()
    return HttpResponse('')


def form_for_comparison(request, hash_user_id):
    #TODO - делать ли кнопку назад? (если да, то в GET считываем из БД, тогда в БД добавить поле с view и наверное даже новую таблицу(потому что пары формируются при обращении, в БД только вектор)
    line = [{'val':9, 'view':9, 'color': '#275E8C'},
            {'val':8, 'view':8, 'color': '#275E8C'},
            {'val':7, 'view':7, 'color': '#275E8C'},
            {'val':6, 'view':6, 'color': '#275E8C'},
            {'val':5, 'view':5, 'color': '#275E8C'},
            {'val':4, 'view':4, 'color': '#275E8C'},
            {'val':3, 'view':3, 'color': '#275E8C'},
            {'val':2, 'view':2, 'color': '#275E8C'},
            {'val':1, 'view':1, 'color': '#275E8C'},
            {'val':1.0/2, 'view':2, 'color': '#275E8C'},
            {'val':1.0/3, 'view':3, 'color': '#275E8C'},
            {'val':1.0/4, 'view':4, 'color': '#275E8C'},
            {'val':1.0/5, 'view':5, 'color': '#275E8C'},
            {'val':1.0/6, 'view':6, 'color': '#275E8C'},
            {'val':1.0/7, 'view':7, 'color': '#275E8C'},
            {'val':1.0/8, 'view':8, 'color': '#275E8C'},
            {'val':1.0/9, 'view':9, 'color': '#275E8C'},
            ]
    user = User.objects.get(id_hash=hash_user_id)
    project = user.project
    user_group = user.group
    pairwise_list = data_for_comparison(user_group)
    pairwise_list.insert(0,'help')

    paginator = Paginator(pairwise_list, 1)
    page = request.GET.get('page')
    try:
        bunches = paginator.page(page)
    except PageNotAnInteger:
        bunches = paginator.page(1)
    except EmptyPage:
        bunches = paginator.page(paginator.num_pages)
    if request.method == 'GET':
        if user.comparison_form == 'check':
            return render(request, 'ahp/form_thanks.html')
        if user.comparison_form == 'timeout':
            return HttpResponse('')
        else:
            level = Level.objects.get(name='goal', project=project)
            node_goal = LevelNodes.objects.get(level=level, project=project).node
            goal = Node.objects.get(pk=node_goal.pk, project=project)
            messages = ''
            action = ''
            return render_to_response('ahp/pairwise_comparison_form.html', {'bunches': bunches, 'line': line, 'messages': messages, 'action': action, 'user': user, 'goal': goal })

    if request.method == 'POST':
        if bunches.number==1:
            url = "/ahp/comparison/"+str(user.id_hash)+"?page="+str(bunches.next_page_number())
            return redirect(url)
        else:
            right_number = int(int(bunches.number)- 1)
            number = len(pairwise_list[right_number]['children'])
            pairwise_list[right_number]['children'] = insert_priority(request.POST, pairwise_list[right_number]['children'], line)
            # проверка на заполненность всех вершин (кнопка не должна загораться до того как отмечены все и не прошли проверку)
            if len(request.POST) == number+1 :
                node_list, Matrix = create_Matrix(pairwise_list[right_number]['children'])
                OS, vector_priority, isRecalculation = calculate_weigth(Matrix)
                if 'auto_revision' in request.POST:
                    user.confidence1 = user.confidence1 + 1
                    user.save()
                    return save_and_next(node_list, vector_priority, user, pairwise_list[right_number]['parent'], bunches, request)
                if 'next' in request.POST:
                    if isRecalculation:
                        for_message = ''
                        for index, node in enumerate(node_list):
                            for_message = for_message +str(node)+':  '+str(format(vector_priority[index],'.2f'))+' \n'
                        messages = 'Ваши оценки слишком противоречивые. \n Пересмотрите, пожалуйста, свои суждения или воспользуйтесь возможностью автоматического устранения противоречий, в результате которого получаются следующие веса:  \n'+for_message
                        action = 'recalculation'
                        return render_to_response('ahp/pairwise_comparison_form.html', {'bunches': bunches, 'line': line, 'messages': messages,  'action': action })
                    else:
                        return save_and_next(node_list, vector_priority, user, pairwise_list[right_number]['parent'], bunches, request)
            else:
                messages = 'Сравните, пожалуйста, все предложенные варианты '
                action = 'not all'
                return render_to_response('ahp/pairwise_comparison_form.html', {'bunches': bunches, 'line': line, 'messages': messages, action: 'action' })# + message


def save_and_next(node_list, vector_priority, user, parent, bunches, request):
    project = Project.objects.get(type='current')
    for index, node in enumerate(node_list):
        edge = Edge.objects.get(parent=parent, node=node, project=project)
        weight = Weight.objects.update_or_create(edge=edge, user=user, defaults=dict(weight=vector_priority[index]))
    if bunches.has_next():
        user.comparison_form = str(bunches.number)
        user.save()
        url = "/ahp/comparison/"+str(user.id_hash)+"?page="+str(bunches.next_page_number())
        return redirect(url)
    else:
        user_confidence(user)
        user.comparison_form = 'check'
        user.save()
        return render(request, 'ahp/form_thanks.html')


def insert_priority(data, pairwise_nodes, line):
    for index_node in data:
        if index_node != 'next' and index_node != 'auto_revision':
            pairwise_nodes[int(index_node)]['priority'] = line[int(data[index_node])]['val']
            pairwise_nodes[int(index_node)]['value'] = int(data[index_node])
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
    #вычисление суммы другое(сумма квадратов под корнем)
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
    project = Project.objects.get(type='current')
    group_nodes_ids = list(GroupNodes.objects.values_list('node', flat=True).filter(type='for comparison form', group=group, project=project))
    level_goal = Level.objects.get(name='goal', project=project)
    goal = LevelNodes.objects.get(level=level_goal, project=project).node
    group_nodes_ids.append(goal.pk)
    ids = set(group_nodes_ids)
    edges = Edge.objects.filter(project=project)
    levels_queryset = Level.objects.filter(project=project).order_by('order')
    levels = list(levels_queryset)
    alt_level = levels.pop(1)
    if alt_level.type != 'absolute_value':
        levels.append(alt_level)
    else:
        levels.pop()
    pairwise_list = []
    for level in levels:
        nodes = LevelNodes.objects.filter(node__in=set(ids), level=level, project=project)
        for node in nodes:
            children_nodes = Edge.objects.filter(parent=node.node, node__in=set(ids), project=project)
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


def user_confidence(user):
    project = Project.objects.get(type='current')
    other_users = User.objects.filter(group=user.group, comparison_form='check', project=project)
    other_sum = other_users.aggregate(Sum('confidence2'))
    sum = other_sum['confidence2__sum']
    if len(other_users)>0:
        average = sum/len(other_users)
    else:
        average = user.confidence1
    if user.confidence1<=average:
        user.confidence2 = 1
    else:
        user.confidence2 = 1/(user.confidence1-average+1)
    #придумать второе доверие


def standard_deviation(group):
    project = Project.objects.get(type='current')
    group_nodes = GroupNodes.objects.filter(group=group, project=project)
    #except new user? -no
    group_users = User.objects.filter(group=group, comparison_form='check', project=project)
    list_of_standard_deviation = create_list_of_standard_deviation(group_nodes, group_users)
    return ''


def global_priority_calculation(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    groups = data['groups']
    checked_users = data['users']
    #если мы передаем пользователей, значит надо брать готовый список, но пока мы этого не делаем, потом просто будем брать список из запроса
    #хотя если пользователи. то они из одной группы обычно, так что смысла мало(напишу потом если понадобится)
    nodes_list = []
    users = []
    for group in groups:
        #type = for_comparison???
        group_nodes = GroupNodes.objects.filter(group=group['id'], project=project, type = 'for comparison form')
        group_users = User.objects.filter(group=group['id'], comparison_form='check', pk__in=set(checked_users), project=project)
        group_sum = group_users.aggregate(Sum('confidence2'))
        for group_user in group_users:
            #print >> sys.stderr, 'group_sum  ', (float(group['priority'])/float(100)) * (float(group_user.confidence2)/float(group_sum['confidence2__sum']))
            #group_priority = float(group['priority'])/float((100*len(group_users)))
            #group_priority = (float(group['priority'])/float(100)) * (float(group_user.confidence2)/float(group_sum['confidence2__sum']))
            users.append({'id': group_user, 'group_priority': float(group['priority'])/float((100*len(group_users)))})
        nodes_list.extend(group_nodes.values_list('node', flat=True))
    nodes = list(set(nodes_list))

    if len(users)>0:
        result = loop_tree(nodes, users, groups)
        return HttpResponse(json.dumps({
            'result': result,
        }), content_type="application/json")
    else:
        return HttpResponse('ошибка')


def create_list_of_standard_deviation(group_nodes, group_users):
    project = Project.objects.get(type='current')
    list_of_standard_deviation = []
    level = Level.objects.get(name='alternatives', project=project)
    edges = Edge.objects.filter(level=level, node__in=set(group_nodes), project=project)
    Matrix = create_standard_deviation_Matrix(edges, group_users)
    list_of_standard_deviation.append(Matrix)
    while len(set(edges.values_list('parent', flat=True)))>1:
        groups_edges = edges.filter(node__in=set(group_nodes))
        parent_edges = Edge.objects.filter(node__in=set(groups_edges.values_list('parent', flat=True)), project=project)
        Matrix = create_standard_deviation_Matrix(parent_edges, group_users)
        list_of_standard_deviation.append(Matrix)
        edges = parent_edges
    return list_of_standard_deviation


def create_standard_deviation_Matrix():
    nodes = list(set(edges.values_list('node', flat=True)))
    parents = list(set(edges.values_list('parent', flat=True)))
    Matrix =  numpy.ones((len(nodes), len(parents)), "f")
    sum_Matrix =  numpy.ones((len(nodes), len(parents)), "f")
    for index_node, node in enumerate(nodes):
        for index_parent, parent in enumerate(parents):
            edge = edges.get(node=node,parent=parent)
            for user in users:
                try:
                    weight = pow(Weight.objects.get(edge=edge, user=user['id']).weight, (user['group_priority']/len(users)))
                except Weight.DoesNotExist:
                    weight = 0
                Matrix[index_node][index_parent] = Matrix[index_node][index_parent] + weight
            Matrix[index_node][index_parent] = Matrix[index_node][index_parent]/len(users)
            for user in users:
                try:
                    weight = pow(Weight.objects.get(edge=edge, user=user['id']).weight, (user['group_priority']/len(users)))
                except Weight.DoesNotExist:
                    weight = 0
                sum_Matrix[index_node][index_parent] = sum_Matrix[index_node][index_parent] + pow(weight - Matrix[index_node][index_parent], 2)
            sum_Matrix[index_node][index_parent] = pow(sum_Matrix[index_node][index_parent]/(len(user)-1), 0.5)
    return sum_Matrix


def loop_tree(nodes_list, users_list, groups_list):
    project = Project.objects.get(type='current')
    level = Level.objects.get(name='alternatives', project=project)
    alternatives = Edge.objects.filter(level=level, node__in=set(nodes_list), project=project)
    edges = alternatives
    Matrix = create_weigth_Matrix(edges, users_list)
    while len(set(edges.values_list('parent', flat=True)))>1:
        groups_edges = edges.filter(node__in=set(nodes_list))
        parent_edges = Edge.objects.filter(node__in=set(groups_edges.values_list('parent', flat=True)), project=project)
        parent_Matrix = create_weigth_Matrix(parent_edges, users_list)
        new_Matrix = numpy.dot(Matrix, parent_Matrix)
        Matrix = new_Matrix
        edges = parent_edges
    result = {}
    alternatives = list(set(alternatives.values_list('node', flat=True)))
    for index, alternative in enumerate(alternatives):
        result[alternative] = Matrix.item((index))
    return result


def create_weigth_Matrix(edges, users):
    nodes = list(set(edges.values_list('node', flat=True)))
    parents = list(set(edges.values_list('parent', flat=True)))
    Matrix =  numpy.ones((len(nodes), len(parents)), "f")
    for index_node, node in enumerate(nodes):
        for index_parent, parent in enumerate(parents):
            edge = edges.get(node=node, parent=parent)
            for user in users:
                try:
                    weight = pow(Weight.objects.get(edge=edge, user=user['id']).weight, user['group_priority'])
                except Weight.DoesNotExist:
                    weight = pow(0.001, user['group_priority'])
                #print >> sys.stderr,'[index_node][index_parent]    ', index_node, '  ',index_parent
                #print >> sys.stderr,' weight    ', weight
                Matrix[index_node][index_parent] = Matrix[index_node][index_parent]* weight
            #Matrix[index_node][index_parent] = pow(Matrix[index_node][index_parent], (1.0/len(users)))
    #тут тоже нормализую вектор неправильно
    vect_sum = list(Matrix.sum(axis=0)) #numpy.linalg.norm(Matrix, axis=0)
    for i, val in enumerate(vect_sum):
        Matrix[:, i] = Matrix[:, i] / val
    return Matrix


def user_confidence_list(request):
    project = Project.objects.get(type='current')
    users = serializers.serialize('json', User.objects.filter(project=project))
    return HttpResponse(json.dumps({
        'users': users
    }), content_type="application/json")


def groups_votes(request):
    project = Project.objects.get(type='current')
    groups = Group.objects.filter(project=project);
    group_votes = [];
    for group in groups:
        group_votes.append({
            'group': group.pk,
            'hierarchy_email': int(User.objects.filter(group=group, hierarchy_form='email', project=project).count()) + int(User.objects.filter(group=group, hierarchy_form='check', project=project).count()),
            'comparison_email': int(User.objects.filter(group=group, comparison_form='email', project=project).count()) + int(User.objects.filter(group=group, comparison_form='check', project=project).count())
        })
    return HttpResponse(json.dumps({
        'group_votes': group_votes
    }), content_type="application/json")


def alt_type(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    level_id = data['level_id']
    type = data['type']
    level = Level.objects.get(pk=level_id, project=project)
    level.type = type
    level.save()
    return  HttpResponse('')


def save_absolute_value(request):
    project = Project.objects.get(type='current')
    data = json.loads(request.body)
    alt_edges = data['alt_edges']
    for crit in alt_edges:
        sum = 0
        for alt in alt_edges[crit]:
            sum = sum + float(alt['value'])
        for alt in alt_edges[crit]:
            edge = Edge.objects.get(project=project, parent=Node.objects.get(project=project, pk=crit), node=Node.objects.get(project=project, pk=alt['alt']))
            if sum == 0:
                weight = 1.0/float(len(alt_edges[crit]))
            else:
                weight = float(alt['value'])/float(sum)
            for user in User.objects.filter(project=project):
                Weight.objects.update_or_create(user=user, edge=edge, defaults=dict(weight=weight))
    return  HttpResponse('')
