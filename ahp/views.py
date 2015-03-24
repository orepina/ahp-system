# coding: utf-8
import json
import sys
import hashlib
import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail, BadHeaderError
from django.http import JsonResponse
from django.core import serializers
from django.db.models import F

from ahp.models import Project, Group, User, Node, UserNodes, GroupNodes, Edge, Weight, Level, LevelNodes


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


def level(request):
    data = json.loads(request.body)
    info = data['info']
    level_id = data['level_id']
    project = Project.objects.get(pk=1)
    order = data['order']
    if data['act_type'] == 'add':
        Level.objects.create(order=order, info=info, project=project)
    #пока что редактировани только инфы(нет перемещений)
    if data['act_type'] == 'edit':
        l = Level.objects.get(pk=level_id)
        l.info = info
        l.save()
    if data['act_type'] == 'delet':
        l = Level.objects.get(pk=level_id)
        l.delete()
        order_consist(order)
    return HttpResponse('')


#пока что без построения иерархии, а вообще нужно делать Edge, получать родителя или находить по уровням
def node(request):
    data = json.loads(request.body)
    node_id = data['node_id']
    level_id = data['level_id']
    info = data['info']
    project = Project.objects.get(pk=1)
    if data['act_type'] == 'add':
        n = Node.objects.create(info=info, project=project)
        l = Level.objects.get(pk=level_id)
        LevelNodes.objects.create(level=l, node=n)
    #пока что редактировани только инфы(без перемещений в другие уровни)
    if data['act_type'] == 'edit':
        n = Node.objects.get(pk=node_id)
        n.info = info
        n.save()
    if data['act_type'] == 'delet':
        n = Node.objects.get(pk=node_id)
        n.delete()
    return HttpResponse('')


def order_consist(order_of_modified):
    Level.objects.filter(order__gt=order_of_modified).update(order=F('order')-1)
    """
    levels = Level.objects.filter(order__gt=order_of_modified)
    for level in levels:
        new_order = level['order']-1
        level['order'] = new_order
        level.save()
    """






def user_hierarchy(request, user_id):
    #user = get_object_or_404(User, pk=user_id)
    #а вот тут мы получаешь хэш, вычисляем айди(или берем из БД) и генерим форму по имеющимся для данного id данным в БД
    #context = {'user': user}#ваще передаем tree
    #return render(request, 'ahp/user_hierarchy.html', context)
    return HttpResponse(user_id+' ')


def user_hierarchy_vote(request, user_id):
    return HttpResponse('')