from django.db import models
import hashlib


class Project(models.Model):
    info = models.CharField(max_length=30, default='')
    type = models.CharField(max_length=30, default='')
    def __unicode__(self):
        return self.info


class Group(models.Model):
    name = models.CharField(max_length=30, default='')
    description = models.CharField(max_length=30, default='')
    project = models.ForeignKey(Project)
    def __unicode__(self):
        return self.name


class User(models.Model):
    email = models.CharField(max_length=30, default='')
    name = models.CharField(max_length=30, default='')
    description = models.CharField(max_length=30, default='')
    id_hash = models.CharField(max_length=15, default='')
    group = models.ForeignKey(Group)
    hierarchy_form = models.CharField(max_length=15, default='')
    comparison_form = models.CharField(max_length=15, default='')
    confidence1 = models.IntegerField()
    confidence2 = models.IntegerField()
    project = models.ForeignKey(Project)
    def __unicode__(self):
        return self.name


class Node(models.Model):
    name = models.CharField(max_length=30, default='')
    description = models.CharField(max_length=30, default='')
    project = models.ForeignKey(Project)
    def __unicode__(self):
        return self.name


class Level(models.Model):
    order = models.IntegerField()
    name = models.CharField(max_length=30, default='')
    description = models.CharField(max_length=30, default='')
    type = models.CharField(max_length=30, default='')
    project = models.ForeignKey(Project)
    def __unicode__(self):
        return self.name


class UserNodes(models.Model):
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)


class GroupNodes(models.Model):
    node = models.ForeignKey(Node)
    group = models.ForeignKey(Group)
    type = models.CharField(max_length=30, default='')
    count = models.IntegerField()
    project = models.ForeignKey(Project)


class Question(models.Model):
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=30, default='')
    description = models.CharField(max_length=30, default='')
    project = models.ForeignKey(Project)
    def __unicode__(self):
        return self.name


class UserInfo(models.Model):
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=30, default='')


class LevelNodes(models.Model):
    level = models.ForeignKey(Level)
    node = models.ForeignKey(Node)
    project = models.ForeignKey(Project)
    def __unicode__(self):
        return self.node.name


class Edge(models.Model):
    node = models.ForeignKey(Node, blank=True, null=True, related_name='children')
    parent = models.ForeignKey(Node, blank=True, null=True, related_name='parent')
    level = models.ForeignKey(Level)
    project = models.ForeignKey(Project)
    def __unicode__(self):
        return self.node.name


class Weight(models.Model):
    edge = models.ForeignKey(Edge)
    user = models.ForeignKey(User)
    weight = models.FloatField(default=1)









