from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import TaskForm, QueueForm, PlanForm
import os
import uuid

from .orm_storage.orm_task_storage import ORMTaskStorage
from .orm_storage.orm_queue_storage import ORMQueueStorage
from .orm_storage.orm_plan_storage import ORMPlanStorage
from .orm_storage.orm_user_storage import ORMUserStorage
from calistra_lib.task.task_controller import TaskController
from calistra_lib.plan.plan_controller import PlanController
from calistra_lib.queue.queue_controller import QueueController
from calistra_lib.user.user_controller import UserController
from calistra_lib.interface import Interface
from django.contrib.auth.decorators import login_required

# Create your views here.

task_storage = ORMTaskStorage()
task_controller = TaskController(task_storage)
user_storage = ORMUserStorage()
user_controller = UserController(user_storage)
plan_storage = ORMPlanStorage()
plan_controller = PlanController(plan_storage)
queue_storage = ORMQueueStorage()
queue_controller = QueueController(queue_storage)
interface = Interface('', queue_controller, user_controller,
                      task_controller,
                      plan_controller)

DEL = 100000000000000000000


def online_user_setter(func):
    def wrapper_func(request):
        interface.set_online_user(request.user.username)
        print(interface.online_user.nick)
        return func(request)

    return wrapper_func


def title(request):
    if request.user.is_authenticated():
        return dashboard(request)
    else:
        return index(request)


def index(request):
    return render(request, 'web_tracker/index.html')


@online_user_setter
@login_required
def dashboard(request):
    user = interface.get_online_user()
    queues = queue_storage.queues.filter(owner=user.uid)
    author_tasks, responsible_tasks = interface.get_user_tasks()
    context = {'queues': queues, 'author_tasks': author_tasks,
               'responsible_tasks': responsible_tasks}
    return render(request, 'web_tracker/dashboard.html', context)


@online_user_setter
@login_required
def new_task(request):
    if request.method != 'POST':
        form = TaskForm()
    else:
        form = TaskForm(data=request.POST)
        if form.is_valid():
            interface.create_task(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                queue_key=form.cleaned_data['queue'],
                parent=None,
                related=form.cleaned_data['related'],
                responsible=None,
                priority=form.cleaned_data['priority'],
                progress=form.cleaned_data['progress'],
                start=form.cleaned_data['start'],
                deadline=form.cleaned_data['deadline'],
                tags=form.cleaned_data['tags'],
                reminder=form.cleaned_data['reminder'],
                key=os.urandom(6).hex())
            return HttpResponseRedirect(reverse('web_tracker:dashboard'))
    context = {'form': form}
    return render(request, 'web_tracker/new_task.html', context)


@online_user_setter
@login_required
def show_task(request):
    if request.method == 'GET':
        form = TaskForm(data=request.GET)
        context = {'form': form}
        return render(request, 'web_tracker/show_task.html', context)


@online_user_setter
@login_required
def new_queue(request):
    if request.method != 'POST':
        form = QueueForm()
    else:
        form = QueueForm(data=request.POST)
        if form.is_valid():
            interface.add_queue(name=form.cleaned_data['name'],
                                key=os.urandom(6))
            return HttpResponseRedirect(reverse('web_tracker:dashboard'))
    context = {'form': form}
    return render(request, 'web_tracker/new_queue.html', context)


@online_user_setter
@login_required
def create_plan(request):
    if request.method != 'POST':
        form = PlanForm()
    else:
        form = PlanForm(data=request.POST)
        if form.is_valid():
            interface.add_plan(key=os.urandom(7),
                               name=form.cleaned_data['name'],
                               time=form.cleaned_data['time'],
                               reminder=form.cleaned_data['reminder'])
            return HttpResponseRedirect(reverse('web_tracker:dashboard'))
    context = {'form': form}
    return render(request, 'web_tracker/create_plan.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('web_tracker:index'))


def register(request):
    if request.method != 'POST':
        form = UserCreationForm()

    else:
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            authenticated_user = authenticate(
                username=new_user.username,
                password=request.POST['password1']
            )
            interface.add_user(
                new_user.username,
                uid=uuid.uuid4().int // DEL,
                queue_key=os.urandom(6).hex()
            )
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('web_tracker:index'))
    context = {'form': form}

    return render(request, 'users/register.html', context)
