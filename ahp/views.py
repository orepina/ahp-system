# coding: utf-8
import json
import sys
import hashlib
import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail, BadHeaderError
from django.core import serializers
from django.db.models import F
from django.db.models import Max
from django.template import RequestContext, loader

from ahp.models import Project, Group, User, Node, UserNodes, GroupNodes, Edge, Weight, Level, LevelNodes, Question, UserInfo

from django import forms

#TODO везде учесть проблему повторения, отсутсвия, обработка ошибок и все такое
#TODO класс для форм, может класс связь с моделями

def index(request):
    #bu = json.loads(request.body)
    #print >> sys.stderr, bu['adjacency_list']
    #проверка на непустой запрос, создание группы в лругом месте, здесь вытаскиваем готовую
    #fk_group = Group.objects.create(info=bu['info'])
    #придумать вот это дело - str(user.id) ( откуда id брать)
    #hash_str = hashlib.sha1(str(datetime.datetime.now())).hexdigest()
    #hash = hash_str[-10:]
    #user = User.objects.create(email=bu['email'], info=bu['info'], group=fk_group, id_hash=hash)
    #print >> sys.stderr, user.email
    #try:
    #    send_mail('Olya', 'Privet', 'qjkzzz@gmail.com', ['enot444@yandex.ru'], fail_silently=False)
    #except BadHeaderError:
    #        return HttpResponse('Invalid header found.')
    edges = serializers.serialize('json', Edge.objects.all())
    #return JsonResponse(edges)
    print >> sys.stderr, edges
    return HttpResponse(json.dumps(edges), content_type="application/json")

class QuestionForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

# +пользователь может добавлять новые критерии?
#сколько раз разрешать пользователю отправлять данные?
def form_for_participant(request, hash_user_id):
    #hash_user_id = '809ffca6e3'
    #TODO get or 404
    user = User.objects.get(id_hash=hash_user_id)
    user_group = user.group
    #print >> sys.stderr, 'user  ' , user, 'user_group  ' , user_group
    if request.method == 'GET':
        #form = NameForm(request.POST)
        question_list = Question.objects.filter(group=user_group)
        levels = Level.objects.order_by('order')
        level_nodes = []
        for level in levels:
            nodes = LevelNodes.objects.filter(level=level)
            if level.info == 'alternatives':
                a = {}
                a['name'] = level
                a['nodes'] = []
                for node in nodes:
                    if group_has_node(user_group, node):
                        a['nodes'].append(node)
            else:
                l = {}
                l['name'] = level
                l['nodes'] = []
                for node in nodes:
                    if group_has_node(user_group, node):
                        l['nodes'].append(node)
                level_nodes.append(l)
        level_nodes.append(a)
        context = {
            'question_list': question_list,
            'level_nodes': level_nodes,
            #'form': form
        }
        return render(request, 'ahp/test.html', context)

    if request.method == 'POST':
        print >> sys.stderr, request.POST
        # что делать если мы разрешии отправлять несколько раз, а пользователь снял галочку? (удалять все)
        UserNodes.objects.filter(user=user).delete()
        for field in request.POST:
            if field!='node':
                question = Question.objects.get(pk=field)
                answer = request.POST[field]
                #print >> sys.stderr,'answer  ' , answer, 'question  ' , question
                user_info = UserInfo.objects.update_or_create(user=user, question=question,defaults=dict(answer=answer))
                #print >> sys.stderr,'user_info  ' , user_info
            else:
                for node_id in request.POST.getlist('node'):
                    node = Node.objects.get(pk=node_id)
                    user_nodes = UserNodes.objects.create(user=user, node=node)
                    print >> sys.stderr, 'node  ' , node
                    print >> sys.stderr, 'UserNodes  ' , user_nodes
                    group_nodes = GroupNodes.objects.get(group=user_group, node=node)
                    group_nodes.type = 'user_choice'
                    #можно накрутить количство, поэтому может в UserNodes добавить group и агрегировать по ней
                    group_nodes.count = group_nodes.count+1
                    group_nodes.save()
                    print >> sys.stderr, 'group_nodes  ', group_nodes
        return HttpResponse('спасибки')
    #вообще тут гет запрос (в урле передается хэш, по нему выбираем пользователя->группу-> нужные вопросы)
    # а ответ пользователя - гет с параметрами в теле + заголовок


def group_has_node(group, node):
    #GroupNodes.objects.get(group=group, node=node)
    group_nodes = GroupNodes.objects.filter(group=group)
    for group_node in group_nodes:
        if node.node.pk == group_node.node.pk:
            return True
    return False


#get node, level, edge
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
    info = data['info']
    level_id = data['level_id']
    order = data['order']
    if data['act_type'] == 'add':
        Level.objects.create(order=order, info=info)
    #пока что редактировани только инфы(нет перемещений)
    if data['act_type'] == 'edit':
        level = Level.objects.get(pk=level_id)
        level.info = info
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
    info = data['info']

    level = Level.objects.get(pk=level_id)
    parent_nodes, children_nodes = level_edges_nodes(level)

    if data['act_type'] == 'add':
        node = Node.objects.create(info=info)
        LevelNodes.objects.create(level=level, node=node)
        for parent_node in parent_nodes:
            Edge.objects.create(node=node, parent=parent_node.node, level=level)
        for child_node in children_nodes:
            Edge.objects.create(node=child_node.node, parent=node, level=level)
    #пока что редактировани только инфы(без перемещений в другие уровни)
    if data['act_type'] == 'edit':
        node = Node.objects.get(pk=node_id)
        node.info = info
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

    """
    levels = Level.objects.filter(order__gt=order_of_modified)
    for level in levels:
        new_order = level['order']-1
        level['order'] = new_order
        level.save()
    """


#get groups
def groups_list(request):
    groups = serializers.serialize('json', Group.objects.all())
    return HttpResponse(json.dumps({
        'groups': groups
    }), content_type="application/json")


#put group(add, change, delete)
def group(request):
    data = json.loads(request.body)
    group_id = data['group_id']
    info = data['info']
    if data['act_type'] == 'add':
        Group.objects.create(info=info)
    if data['act_type'] == 'edit':
        g = Group.objects.get(pk=group_id)
        g.info = info
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


#TODO что делать если снимаем галочку? каждый раз перезаписывать все целиком?(сейчас так и делаем)
#еще count 1 добавлять и тип менять
#put groups nodes(add, delete)
def group_nodes(request):
    GroupNodes.objects.all().delete()
    data = json.loads(request.body)
    for group in data:
        g = Group.objects.get(pk=group)
        for node in data[group]:
            n = Node.objects.get(pk=node)
            GroupNodes.objects.create(group=g, node=n, type='for_form', count=0)
            #GroupNodes.objects.update_or_create(group=g, node=n, type='for_form', count=0)
    return HttpResponse('')


#put question(add,delete,edit)
def question(request):
    data = json.loads(request.body)
    question_id = data['question_id']
    group_id = data['group_id']
    info = data['info']
    if data['act_type'] == 'add':
        g = Group.objects.get(pk=group_id)
        Question.objects.create(group=g, name=info, description=info)
    if data['act_type'] == 'edit':
        q = Question.objects.get(pk=question_id)
        q.name = info
        q.description = info
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
    if data['act_type'] == 'add':
        group = Group.objects.get(pk=group_id)
        User.objects.create(name=name, description='', email=email, id_hash='', group=group)
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
    user = User.objects.get(pk=user_id)
    user.id_hash = hash_id(user_id)
    user.save()
    header = 'Исследование'
    url = 'http://127.0.0.1:8000/ahp/' + user.id_hash
    text = data['text'] + '    ' + url
    email = user.email
    send_email(header, text, email)
    return HttpResponse('') #4. возвращаем ответ что все прерасно отправлено!!!


    #2.1 формируем текст для отправки в котором должна присутсвовать ссылка
    #3. отправляем на мыло
    #4. возвращаем ответ что все прерасно отправлено
    #5. нужна ли у user галочка ему письмо отправлено или хватит наличия id_hash?


def hash_id(id):
    hash_str = hashlib.sha1(str(id)).hexdigest()
    hash = hash_str[-10:]
    return hash


def send_email(header, text, email):
    try:
        # заголовок,  текст,  адрес рассылки,  адрес получателя,  и непоятный параметр
        send_mail(header, text, 'qjkzzz@gmail.com', [email], fail_silently=False)
    except BadHeaderError:
            return HttpResponse('Invalid header found.')


#может быть вообще не нужен save
def group_nodes_for_comparison(request):
    GroupNodes.objects.filter(type='for comparison').update(type='for form')
    data = json.loads(request.body)
    for group in data:
        g = Group.objects.get(pk=group)
        for node in data[group]:
            n = Node.objects.get(pk=node)
            group_node = GroupNodes.objects.get(group=g, node=n)
            group_node.type = 'for comparison'
            group_node.save()
    return HttpResponse('')


def send_comparison_form(request):
    group_nodes_for_comparison(request)
    group = Group.objects.get(info='group 1')
    pairwise_list = []
    pairwise_list = data_for_comparison(group)
    #send emails - отдельному пользователю или группе?
    return HttpResponse('')


def form_for_comparison(request, hash_user_id):
    #hash_user_id = '809ffca6e3'
    #TODO get or 404
    user = User.objects.get(id_hash=hash_user_id)
    user_group = user.group
    #print >> sys.stderr, 'user  ' , user, 'user_group  ' , user_group
    if request.method == 'GET':
        pairwise_list = data_for_comparison(group)
        context = {
            'pairwise_list': pairwise_list,
            #'form': form
        }
        return render(request, 'ahp/test.html', context)


    #print >> sys.stderr, pairwise_list
    # куда теперь сохраняем и что вообще делаем Weight??
    #а вот тут нужен метод для формирования формы
    # нужно формировать пары для сравнений, для этого нужно юзер->группа->из группы вершины с типом 'for comparison'
    # дальше нужна структура дерева - это Level, LevelNodes и Edge (и Node за компанию)
    # для вывода достаточно. обработка индекса согласованности на питоне. результаты в Weight

    return HttpResponse('')


def data_for_comparison(group):
    group_nodes_ids = GroupNodes.objects.values_list('node', flat=True).filter(type='for comparison', group=group)
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
            children_nodes = Edge.objects.filter(parent=node.node)
            if len(children_nodes)>0:
                pairwise_generation(children_nodes, node, pairwise_list)
    return pairwise_list



def pairwise_generation(nodes, parent, pairwise_list):
    include_nodes = []
    for node_left in nodes:
        #print sys.stderr,'node_left  ', node_left
        include_nodes.append(node_left)
        #print sys.stderr,'include_nodes  ', include_nodes
        #print sys.stderr,'set(nodes).difference(include_nodes)  ', set(nodes).difference(include_nodes)
        for node_right in set(nodes).difference(include_nodes):
            pairwise_obj = {}
            pairwise_obj['parent'] = parent.node
            pairwise_obj['left_node'] = node_left.node
            pairwise_obj['right_node']= node_right.node
            pairwise_list.append(pairwise_obj)



