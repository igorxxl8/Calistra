from django.conf.urls import url
from django.contrib.auth.views import login

from . import views

urlpatterns = [
    # main page
    url(r'^$', views.title, name='title'),
    url(r'^$', views.index, name='index'),
    # page of user dashboard
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    # page for create new task
    url(r'^new_task/', views.new_task, name='new_task'),

    url(r'^tasks/show_task/$', views.show_task, name='show_task'),
    # page for create new queue
    url(r'^new_queue/', views.new_queue, name='new_queue'),
    # page for create new plan
    url(r'^create_plan/', views.create_plan, name='create_plan'),

    # login page
    url(r'^users/login/$', login, {'template_name': 'users/login.html'}, name='login'),

    # logout page
    url(r'^users/logout/$', views.logout_view, name='logout'),

    # register page
    url(r'^users/register/$', views.register, name='register'),

    url(r'^notify/$', views.notify, name='notify'),

    # page with info about single queue
    url(r'^queues/(?P<queue_key>[\w.@+-]+)/$', views.show_queue, name='show_queue'),

    # page with info about single plan
    url(r'^plans/(?P<plan_key>[\w.@+-]+)/$', views.show_plan, name='show_plan'),

    url(r'^tasks/(?P<task_key>[\w.@+-]+)/$', views.show_task, name='show_task'),

    # page for editing task
    url(r'^tasks/edit_task/(?P<task_key>[\w.@+-]+)/$', views.edit_task, name='edit_task'),

    # page for editing queue
    url(r'^edit_queue/(?P<queue_key>[\w.@+-]+)/$', views.edit_queue, name='edit_queue'),

    url(r'^delete_queue/(?P<queue_key>[\w.@+-]+)/$', views.delete_queue, name='delete_queue'),

    # page for editing plan
    url(r'^edit_plan/(?P<plan_key>[\w.@+-]+)/$', views.edit_plan, name='edit_plan'),

    url(r'^delete_task/(?P<task_key>[\w.@+-]+)/$', views.delete_task, name='delete_task'),

url(r'^delete_plan/(?P<plan_key>[\w.@+-]+)/$', views.delete_plan, name='delete_plan')


]