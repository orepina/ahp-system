from django.conf.urls import patterns, url

from ahp import views

urlpatterns = patterns('',
    url(r'^common_hierarchy/$', views.common_hierarchy, name='common_hierarchy'),
    url(r'^level/$', views.level, name='level'),
    url(r'^node/$', views.node, name='node'),

    url(r'^$', views.index, name='index'),
    url(r'^(?P<user_id>\d+)/$', views.user_hierarchy, name='user_hierarchy'),
)