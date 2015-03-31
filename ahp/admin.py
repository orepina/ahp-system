from django.contrib import admin
from ahp.models import Project, Group, User, Node, UserNodes, GroupNodes, Edge, Weight, Level, LevelNodes, Question



admin.site.register(Project)
admin.site.register(Group)
admin.site.register(User)
admin.site.register(Node)
admin.site.register(UserNodes)
admin.site.register(GroupNodes)
admin.site.register(Edge)
admin.site.register(Weight)
admin.site.register(Level)
admin.site.register(LevelNodes)
admin.site.register(Question)

# Register your models here.
