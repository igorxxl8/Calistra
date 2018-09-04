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
    url(r'^users/logout/$', views.logout_view, name='logout'),
    url(r'^users/register/$', views.register, name='register')
]