from django.conf.urls import patterns, url

from django.contrib.auth.views import login

from ahp import views

from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^common_hierarchy/$', views.common_hierarchy, name='common_hierarchy'),
    url(r'^level/$', views.level, name='level'),
    url(r'^node/$', views.node, name='node'),
    url(r'^groups_list/$', views.groups_list, name='groups_list'),
    url(r'^group/$', views.group, name='group'),
    url(r'^group_nodes_list/$', views.group_nodes_list, name='group_nodes_list'),
    url(r'^group_nodes/$', views.group_nodes, name='group_nodes'),
    url(r'^chosen_group_nodes/$', views.chosen_group_nodes, name='chosen_group_nodes'),
    url(r'^question/$', views.question, name='question'),
    url(r'^group_question_list/$', views.group_question_list, name='group_question_list'),
    url(r'^users_list/$', views.users_list, name='users_list'),
    url(r'^user/$', views.user, name='user'),
    url(r'^questions/$', views.questions, name='questions'),
    url(r'^email/$', views.email, name='email'),
    url(r'^chosen_group_nodes_for_comparison/$', views.chosen_group_nodes_for_comparison, name='chosen_group_nodes_for_comparison'),

    url(r'^$', views.main, name='main'),
    url(r'^popup/$', views.popup, name='popup'),

    url(r'^login/$', login),
    url(r'^global_priority/$', views.global_priority_calculation, name='global_priority_calculation'),

    url(r'^hierarchy/(?P<hash_user_id>\w+)/$', views.form_for_participant, name='form_for_participant'),
    url(r'^comparison/(?P<hash_user_id>\w+)/$', views.form_for_comparison, name='form_for_comparison'),
)

