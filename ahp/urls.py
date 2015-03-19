from django.conf.urls import patterns, url

from ahp import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<user_id>\d+)/$', views.user_hierarchy, name='user_hierarchy'),
    url(r'^(?P<common_tree>\d+)/$', views.user_hierarchy, name='user_hierarchy'),
    url(r'^(?P<users>\d+)/$', views.user_hierarchy, name='user_hierarchy'),
    url(r'^(?P<groups>\d+)/$', views.user_hierarchy, name='user_hierarchy'),
    url(r'^(?P<group_tree>\d+)/$', views.user_hierarchy, name='user_hierarchy'),
)