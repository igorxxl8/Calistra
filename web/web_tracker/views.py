from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import TaskForm, QueueForm, PlanForm
from datetime import datetime as dt
import os

from .orm_storage.orm_task_storage import ORMTaskStorage
from .orm_storage.orm_queue_storage import ORMQueueStorage
from .orm_storage.orm_plan_storage import ORMPlanStorage
from .orm_storage.orm_user_storage import ORMUserStorage
from calistra_lib.task.task_controller import TaskController
from calistra_lib.plan.plan_controller import PlanController
from calistra_lib.queue.queue_controller import QueueController
from calistra_lib.user.user_controller import UserController
from calistra_lib.interface import Interface
from calistra_lib.constants import Time
from django.contrib.auth.decorators import login_required

# Create your views here.
DEL = 100000000000000000000


def update_all(func):
    def wrapped_func(*args, **kwargs):
        task_storage = ORMTaskStorage()
        task_controller = TaskController(task_storage)
        user_storage = ORMUserStorage()
        user_controller = UserController(user_storage)
        plan_storage = ORMPlanStorage()
        plan_controller = PlanController(plan_storage)
        queue_storage = ORMQueueStorage()
        queue_controller = QueueController(queue_storage)
        interface = Interface('', queue_controller, user_controller,
                              task_controller, plan_controller)
        interface.update_all()
        return func(*args, **kwargs)

    return wrapped_func


# @update_all
def title(request):
    if request.user.is_authenticated():
        return dashboard(request)
    else:
        return index(request)


def index(request):
    return render(request, 'web_tracker/index.html')


@login_required
def dashboard(request):
    user_storage = ORMUserStorage()
    queue_storage = ORMQueueStorage()
    plan_storage = ORMPlanStorage()
    task_storage = ORMTaskStorage()
    user = user_storage.get_user_by_nick(nick=request.user.username)
    queues = queue_storage.queues.filter(owner=user.uid)
    plans = plan_storage.plans.filter(author=user.nick)
    tasks_author = task_storage.get_task_by_author(user)
    tasks_responsible = task_storage.get_task_by_responsible(user)
    context = {'queues': queues,
               'plans': plans,
               'author_tasks': tasks_author,
               'responsible_tasks': tasks_responsible,
               'author_count': len(tasks_author),
               'responsible_count': len(tasks_responsible)
               }
    return render(request, 'web_tracker/dashboard.html', context)


# @update_all
@login_required
def new_task(request):
    if request.method != 'POST':
        form = TaskForm()
    else:
        form = TaskForm(data=request.POST)
        if form.is_valid():
            task_storage = ORMTaskStorage()
            task_controller = TaskController(task_storage)
            user_storage = ORMUserStorage()
            user_controller = UserController(user_storage)
            queue_storage = ORMQueueStorage()
            queue_controller = QueueController(queue_storage)

            user = user_storage.get_user_by_nick(nick=request.user.username)
            flag = True
            queue = queue_storage.find_queue(key=form.cleaned_data['queue'],
                                             owner=user)

            if flag:
                creating_time = dt.strftime(dt.now(), Time.EXTENDED_TIME_FORMAT)
                task = task_controller.add_task(
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data['description'],
                    queue=queue,
                    parent=form.cleaned_data['parent'],
                    related=form.cleaned_data['related'],
                    responsible=form.cleaned_data['responsible'],
                    priority=form.cleaned_data['priority'],
                    progress=form.cleaned_data['progress'],
                    start=form.cleaned_data['start'],
                    deadline=form.cleaned_data['deadline'],
                    tags=form.cleaned_data['tags'],
                    reminder=form.cleaned_data['reminder'],
                    key=os.urandom(6).hex(),
                    author=user,
                    creating_time=creating_time
                )
                user_controller.link_author_with_task(user, task)

                queue_controller.link_queue_with_task(queue, task)

                return HttpResponseRedirect(reverse('web_tracker:dashboard'))
    context = {'form': form}
    return render(request, 'web_tracker/new_task.html', context)


# @update_all
@login_required
def show_task(request, task_key):
    task_storage = ORMTaskStorage()
    queue_storage = ORMQueueStorage()
    task = task_storage.get_task_by_key(key=task_key)
    sub_tasks = task_storage.get_sub_tasks(task)
    parent_task = task_storage.get_task_by_key(task.parent)
    queue = queue_storage.get_queue_by_key(task.queue)
    context = {'task': task,
               'sub_tasks': sub_tasks,
               'parent_task': parent_task,
               'queue': queue
               }
    return render(request, 'web_tracker/show_task.html', context)


@login_required
def edit_task(request, task_key):
    task_storage = ORMTaskStorage()
    task_controller = TaskController(task_storage)
    queue_storage = ORMQueueStorage()
    queue_controller = QueueController(queue_storage)
    task = task_storage.get_task_by_key(task_key)
    queue = queue_storage.get_queue_by_key(task.queue)
    user_storage = ORMUserStorage()
    editor = user_storage.get_user_by_nick(request.user.username)
    editing_time = dt.strftime(dt.now(), Time.EXTENDED_TIME_FORMAT)

    if request.method != 'POST':
        form = TaskForm()

    else:
        form = TaskForm(instance=task, data=request.POST)
        if form.is_valid():
            task_controller.edit_task(
                task=task,
                task_queue=queue,
                editor=editor,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                parent=form.cleaned_data['parent'],
                responsible=form.cleaned_data['responsible'],
                priority=form.cleaned_data['priority'],
                start=form.cleaned_data['start'],
                deadline=form.cleaned_data['deadline'],
                tags=form.cleaned_data['tags'],
                reminder=form.cleaned_data['reminder'],
                status=form.cleaned_data['status'],
                editing_time=editing_time
            )

            return HttpResponseRedirect(reverse('web_tracker:dashboard'))
    context = {'form': form}
    return render(request, 'web_tracker/new_task.html', context)


# @update_all
@login_required
def new_queue(request):
    if request.method != 'POST':
        form = QueueForm()
    else:
        form = QueueForm(data=request.POST)
        if form.is_valid():
            user_storage = ORMUserStorage()
            queue_storage = ORMQueueStorage()
            queue_controller = QueueController(queue_storage)
            user_controller = UserController(user_storage)

            user = user_storage.get_user_by_nick(request.user.username)
            queue = queue_controller.add_queue(name=form.cleaned_data['name'],
                                               key=os.urandom(6).hex(),
                                               owner=user)
            user_controller.link_user_with_queue(user, queue)
            return HttpResponseRedirect(reverse('web_tracker:dashboard'))
    context = {'form': form}
    return render(request, 'web_tracker/new_queue.html', context)


# @update_all
@login_required
def show_queue(request, queue_key):
    queue_storage = ORMQueueStorage()
    task_storage = ORMTaskStorage()
    queue = queue_storage.queues.get(key=queue_key)
    opened_tasks = task_storage.get_opened_tasks(queue)
    solved_tasks = task_storage.get_solved_tasks(queue)
    failed_tasks = task_storage.get_failed_tasks(queue)
    context = {'queue': queue,
               'opened_tasks': opened_tasks,
               'solved_tasks': solved_tasks,
               'failed_tasks': failed_tasks
               }
    return render(request, 'web_tracker/show_queue.html', context)


# TODO: реализовать редактирование очереди
@login_required
def edit_queue(request, queue_key):
    pass


# @update_all
@login_required
def create_plan(request):
    if request.method != 'POST':
        form = PlanForm()
    else:
        form = PlanForm(data=request.POST)
        if form.is_valid():
            user_storage = ORMUserStorage()
            plan_storage = ORMPlanStorage()
            plan_controller = PlanController(plan_storage)

            user = user_storage.get_user_by_nick(nick=request.user.username)
            plan_controller.create_plan(
                key=os.urandom(8).hex(), author=user,
                name=form.cleaned_data['name'],
                period=form.cleaned_data['period'],
                activation_time=form.cleaned_data['time'],
                reminder=form.cleaned_data['reminder']
            )

            return HttpResponseRedirect(reverse('web_tracker:dashboard'))
    context = {'form': form}
    return render(request, 'web_tracker/create_plan.html', context)


# @update_all
@login_required
def show_plan(request, plan_key):
    plan_storage = ORMPlanStorage()

    plan = plan_storage.get_plan_by_key(plan_key)
    context = {'plan': plan}
    return render(request, 'web_tracker/show_plan.html', context)


# TODO: реализовать редактирование плана
@login_required
def edit_plan(request, plan_key):
    pass


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('web_tracker:index'))


# @update_all
def register(request):
    if request.method != 'POST':
        form = UserCreationForm()

    else:
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            user_storage = ORMUserStorage()
            user_controller = UserController(user_storage)
            queue_storage = ORMQueueStorage()
            queue_controller = QueueController(queue_storage)

            new_user = form.save()
            authenticated_user = authenticate(
                username=new_user.username,
                password=request.POST['password1']
            )
            user_controller.add_user(
                nick=new_user.username,
                uid=new_user.id
            )
            user = user_storage.get_user_by_nick(nick=new_user.username)
            queue = queue_controller.add_queue(name='default',
                                               key=os.urandom(6).hex(),
                                               owner=user)
            user_controller.link_user_with_queue(user, queue)
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('web_tracker:index'))
    context = {'form': form}

    return render(request, 'users/register.html', context)
