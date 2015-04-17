from django.conf.urls import patterns, url

from ahp import views

urlpatterns = patterns('',
    url(r'^common_hierarchy/$', views.common_hierarchy, name='common_hierarchy'),
    url(r'^level/$', views.level, name='level'),
    url(r'^node/$', views.node, name='node'),
    url(r'^groups_list/$', views.groups_list, name='groups_list'),
    url(r'^group/$', views.group, name='group'),
    url(r'^group_nodes_list/$', views.group_nodes_list, name='group_nodes_list'),
    url(r'^group_nodes/$', views.group_nodes, name='group_nodes'),
    url(r'^question/$', views.question, name='question'),
    url(r'^group_question_list/$', views.group_question_list, name='group_question_list'),
    url(r'^users_list/$', views.users_list, name='users_list'),
    url(r'^user/$', views.user, name='user'),
    url(r'^questions/$', views.questions, name='questions'),
    url(r'^email/$', views.email, name='email'),
    url(r'^group_nodes_for_comparison/$', views.group_nodes_for_comparison, name='group_nodes_for_comparison'),
    url(r'^send_comparison_form/$', views.send_comparison_form, name='send_comparison_form'),
    url(r'^$', views.index, name='index'),

    url(r'^hierarchy/(?P<hash_user_id>\w+)/$', views.form_for_participant, name='form_for_participant'),
    url(r'^comparison/(?P<hash_user_id>\w+)/$', views.form_for_comparison, name='form_for_comparison'),

)