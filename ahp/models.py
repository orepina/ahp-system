from django.db import models
import hashlib


class Project(models.Model):
    info = models.CharField(max_length=30, default='')
    def __str__(self):
        return self.info


class Group(models.Model):
    info = models.CharField(max_length=30, default='')
    project = models.ForeignKey(Project)
    def __str__(self):
        return self.info


class User(models.Model):
    email = models.CharField(max_length=30, default='')
    info = models.CharField(max_length=30, default='')
    id_hash = models.CharField(max_length=15, default='')
    group = models.ForeignKey(Group)
    project = models.ForeignKey(Project)
    def __str__(self):
        return self.info


class Node(models.Model):
    info = models.CharField(max_length=30, default='')
    project = models.ForeignKey(Project)
    def __str__(self):
        return self.info


class Level(models.Model):
    order = models.IntegerField()
    info = models.CharField(max_length=30, default='')
    project = models.ForeignKey(Project)
    def __str__(self):
        return self.info


class UserNodes(models.Model):
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)


class GroupNodes(models.Model):
    node = models.ForeignKey(Node)
    group = models.ForeignKey(Group)
    type = models.CharField(max_length=30, default='')
    count = models.IntegerField()


class Question(models.Model):
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=30, default='')
    description = models.CharField(max_length=30, default='')


class UserInfo(models.Model):
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=30, default='')


class LevelNodes(models.Model):
    level = models.ForeignKey(Level)
    node = models.ForeignKey(Node)


class Edge(models.Model):
    node = models.ForeignKey(Node, blank=True, null=True, related_name='children')
    parent = models.ForeignKey(Node, blank=True, null=True, related_name='parent')
    project = models.ForeignKey(Project)
    #def __str__(self):
    #    return str(self.node) + '   ' + str(self.parent)
    #parent = models.ForeignKey('self', blank=True, null=True, related_name='children')


class Weight(models.Model):
    node = models.ForeignKey(Edge)
    user = models.ForeignKey(User)
    weight = models.CharField(max_length=30, default='')
    project = models.ForeignKey(Project)







