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


def user_hierarchy(request, user_id):
    #user = get_object_or_404(User, pk=user_id)
    #а вот тут мы получаешь хэш, вычисляем айди(или берем из БД) и генерим форму по имеющимся для данного id данным в БД
    #context = {'user': user}#ваще передаем tree
    #return render(request, 'ahp/user_hierarchy.html', context)
    return HttpResponse(user_id+' ')


def user_hierarchy_vote(request, user_id):
    return HttpResponse('')