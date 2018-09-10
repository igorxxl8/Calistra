import os
from datetime import datetime as dt

from calistra_web.settings import TIME_FORMAT
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from calistra_lib.constants import Time
from calistra_lib.exceptions.base_exception import AppError
from calistra_lib.interface import Interface
from calistra_lib.plan.plan_controller import PlanController
from calistra_lib.queue.queue_controller import QueueController
from calistra_lib.task.task_controller import TaskController
from calistra_lib.user.user_controller import UserController
from .forms import (
    TaskForm,
    EditingTaskForm,
    QueueForm,
    PlanForm,
    UserCreationFormBoot
)
from .orm_storage.orm_plan_storage import ORMPlanStorage
from .orm_storage.orm_queue_storage import ORMQueueStorage
from .orm_storage.orm_task_storage import ORMTaskStorage
from .orm_storage.orm_user_storage import ORMUserStorage

# Create your views here.
DEL = 100000000000000000000

Time.DATETIME_FORMAT = TIME_FORMAT


def update_all(func):
    def wrapped_func(*args, **kwargs):
        task_storage = ORMTaskStorage()
        user_storage = ORMUserStorage()
        plan_storage = ORMPlanStorage()
        queue_storage = ORMQueueStorage()

        task_controller = TaskController(task_storage)
        user_controller = UserController(user_storage)
        plan_controller = PlanController(plan_storage)
        queue_controller = QueueController(queue_storage)
        interface = Interface('', queue_controller, user_controller,
                              task_controller, plan_controller)
        interface.update_all()
        return func(*args, **kwargs)

    return wrapped_func


@update_all
def title(request):
    if request.user.is_authenticated():
        return dashboard(request)
    else:
        return index(request)


def index(request):
    return render(request, 'web_tracker/index.html')


@update_all
@login_required
def dashboard(request):
    user_storage = ORMUserStorage()
    queue_storage = ORMQueueStorage()
    plan_storage = ORMPlanStorage()
    task_storage = ORMTaskStorage()
    user = user_storage.get_user_by_nick(nick=request.user.username)
    queues = queue_storage.get_user_queues(user)
    plans = plan_storage.get_user_plans(user)
    tasks_author = task_storage.get_tasks_by_author(user)
    tasks_responsible = task_storage.get_tasks_by_responsible(user)

    author_count = len(tasks_author)
    responsible_count = len(tasks_responsible)
    notifications = user.new_messages.split(',')
    context = {'queues': queues,
               'plans': plans,
               'author_tasks': tasks_author,
               'responsible_tasks': tasks_responsible,
               'tasks_count': author_count + responsible_count,
               'author_count': author_count,
               'responsible_count': responsible_count,
               'notifications': notifications
               }

    return render(request, 'web_tracker/dashboard.html', context)


def notify(request):
    user_storage = ORMUserStorage()
    user = user_storage.get_user_by_nick(request.user.username)
    user_controller = UserController(user_storage)
    context = {
        'messages': user.new_messages.split(','),
        'notifications': user.notifications.split(',')
    }
    user_controller.clear_new_messages(user)
    return render(request, 'web_tracker/notify.html', context)


@update_all
@login_required
def new_task(request):
    user_storage = ORMUserStorage()
    user = user_storage.get_user_by_nick(nick=request.user.username)
    if request.method != 'POST':
        form = TaskForm(user)

    else:
        form = TaskForm(user, data=request.POST)
        if form.is_valid():
            creating_time = dt.strftime(dt.now(), Time.EXTENDED_TIME_FORMAT)
            task_storage = ORMTaskStorage()
            task_controller = TaskController(task_storage)
            user_controller = UserController(user_storage)
            queue_storage = ORMQueueStorage()
            queue_controller = QueueController(queue_storage)
            queue = queue_storage.find_queue(key=form.cleaned_data['queue'],
                                             owner=user)

            resp = form.cleaned_data['responsible']
            responsible_users = ','.join(resp)
            start = form.cleaned_data['start']
            deadline = form.cleaned_data['deadline']
            try:
                Time.get_date(start)
            except Exception:
                start = ''
            try:
                Time.get_date(deadline)
            except Exception:
                deadline = ''

            key = os.urandom(8).hex()
            try:
                task = task_controller.add_task(
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data['description'],
                    queue=queue,
                    parent=form.cleaned_data['parent'],
                    related=form.cleaned_data['related'],
                    responsible=responsible_users,
                    priority=form.cleaned_data['priority'],
                    progress=form.cleaned_data['progress'],
                    start=start,
                    deadline=deadline,
                    tags=form.cleaned_data['tags'],
                    reminder=form.cleaned_data['reminder'],
                    key=key,
                    author=user,
                    creating_time=creating_time
                )
            except AppError as e:
                form.add_error('name', e.message)
                context = {'form': form}
                return render(request, 'web_tracker/new_task.html', context)
            user_controller.link_author_with_task(user, task)
            for user_nick in resp:
                user = user_storage.get_user_by_nick(user_nick)
                user_controller.link_responsible_with_task(user, task)
            queue_controller.link_queue_with_task(queue, task)

            return HttpResponseRedirect(
                reverse('web_tracker:show_task', args=(key,)))
    context = {'form': form}
    return render(request, 'web_tracker/new_task.html', context)


@update_all
@login_required
def show_task(request, task_key):
    user_storage = ORMUserStorage()
    task_storage = ORMTaskStorage()
    user_controller = UserController(user_storage)
    user = user_storage.get_user_by_nick(request.user.username)
    task = task_storage.get_task_by_key(key=task_key)
    task.priority = TaskForm.priority_choices[task.priority]
    try:
        task.start = Time.get_date(task.start)
    except Exception:
        pass
    try:
        task.deadline = Time.get_date(task.deadline)
    except Exception:
        pass

    if not user_controller.can_show(user, task):
        context = {'message': 'Cannot edit see task: "{}", key {}!'.format(
            task.name, task_key)
        }
        return render(request, 'web_tracker/404.html', context)

    sub_tasks = task_storage.get_sub_tasks(task)
    parent_task = task_storage.get_task_by_key(task.parent)
    queue_storage = ORMQueueStorage()
    queue = queue_storage.get_queue_by_key(task.queue)

    can_edit = user_controller.can_edit(user, task)
    can_show_parent = user_controller.can_show_parent(user, parent_task)
    context = {'task': task,
               'sub_tasks': sub_tasks,
               'parent_task': parent_task,
               'queue': queue,
               'can_edit': can_edit,
               'can_show_parent': can_show_parent
               }
    return render(request, 'web_tracker/show_task.html', context)


@update_all
@login_required
def edit_task(request, task_key):
    task_storage = ORMTaskStorage()
    task_controller = TaskController(task_storage)
    queue_storage = ORMQueueStorage()
    task = task_storage.get_task_by_key(task_key)
    queue = queue_storage.get_queue_by_key(task.queue)
    queue_controller = QueueController(queue_storage)
    user_storage = ORMUserStorage()
    editor = user_storage.get_user_by_nick(request.user.username)
    editing_time = dt.strftime(dt.now(), Time.EXTENDED_TIME_FORMAT)

    if request.method != 'POST':
        form = EditingTaskForm(editor, task, instance=task)

    else:
        form = EditingTaskForm(editor, task, instance=task, data=request.POST)

        if form.is_valid():
            start = form.cleaned_data['start']
            deadline = form.cleaned_data['deadline']
            try:
                Time.get_date(start)
            except Exception:
                start = ''
            try:
                Time.get_date(deadline)
            except Exception:
                deadline = ''

            status = form.cleaned_data['status']
            cur_status = task.status
            task_controller.edit_task(
                task=task,
                task_queue=queue,
                editor=editor,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                parent=form.cleaned_data['parent'],
                responsible=form.cleaned_data['responsible'],
                priority=form.cleaned_data['priority'],
                start=start,
                deadline=deadline,
                tags=form.cleaned_data['tags'],
                reminder=form.cleaned_data['reminder'],
                editing_time=editing_time
            )
            task.status = status
            task.save()

            if cur_status != task.status:
                if task.status == 'solved':
                    queue_controller.move_in_solved(queue, task)


                elif task.status == 'opened':
                    queue_controller.move_in_opened(queue, task)


                elif task.status == 'failed':
                    queue_controller.move_in_failed(queue, task)

            return HttpResponseRedirect(
                reverse('web_tracker:show_task', args=(task_key,)))
    context = {'form': form, 'task': task}
    return render(request, 'web_tracker/edit_task.html', context)


@update_all
@login_required
def delete_task(request, task_key):
    task_storage = ORMTaskStorage()
    task = task_storage.get_task_by_key(task_key)
    user_storage = ORMUserStorage()
    user = user_storage.get_user_by_nick(request.user.username)
    if task and task.author != user.nick:
        context = {'message': 'Access denied. You cannot delete this task!'}
        return render(request, 'web_tracker/404.html', context)

    if task:
        sub_tasks = task_storage.get_sub_tasks(task)
        for task in sub_tasks:
            task_storage.remove_task(task)
        task_storage.remove_task(task)

    return HttpResponseRedirect(reverse('web_tracker:index'))


@update_all
@login_required
def new_queue(request):
    user_storage = ORMUserStorage()

    user = user_storage.get_user_by_nick(request.user.username)
    if request.method != 'POST':
        form = QueueForm(user)
    else:
        form = QueueForm(user, data=request.POST)
        if form.is_valid():
            user_storage = ORMUserStorage()
            queue_storage = ORMQueueStorage()
            queue_controller = QueueController(queue_storage)
            user_controller = UserController(user_storage)

            user = user_storage.get_user_by_nick(request.user.username)
            key = os.urandom(6).hex()
            queue = queue_controller.add_queue(
                name=form.cleaned_data['name'].upper(),
                key=key,
                owner=user)
            user_controller.link_user_with_queue(user, queue)
            return HttpResponseRedirect(
                reverse('web_tracker:show_queue', args=(key,)))
    context = {'form': form}
    return render(request, 'web_tracker/new_queue.html', context)


@update_all
@login_required
def show_queue(request, queue_key):
    queue_storage = ORMQueueStorage()
    task_storage = ORMTaskStorage()
    queue = queue_storage.get_queue_by_key(key=queue_key)
    if queue.owner != request.user.id:
        context = {'message': 'Access denied. You cannot see this queue!'}
        return render(request, 'web_tracker/404.html', context)
    opened_tasks = task_storage.get_opened_tasks(queue)
    solved_tasks = task_storage.get_solved_tasks(queue)
    failed_tasks = task_storage.get_failed_tasks(queue)
    context = {'queue': queue,
               'opened_tasks': opened_tasks,
               'solved_tasks': solved_tasks,
               'failed_tasks': failed_tasks,
               'opened_tasks_count': len(opened_tasks),
               'solved_tasks_count': len(solved_tasks),
               'failed_tasks_count': len(failed_tasks),
               }
    return render(request, 'web_tracker/show_queue.html', context)


@update_all
@login_required
def edit_queue(request, queue_key):
    user_storage = ORMUserStorage()
    queue_storage = ORMQueueStorage()
    queue = queue_storage.get_queue_by_key(queue_key)
    editor = user_storage.get_user_by_nick(request.user.username)

    if queue.name == 'DEFAULT':
        context = {'message': 'Cannot edit default queue!'}
        return render(request, 'web_tracker/404.html', context)

    if request.method != 'POST':
        form = QueueForm(editor, instance=queue)

    else:
        form = QueueForm(editor, instance=queue, data=request.POST)
        if form.is_valid():
            queue_controller = QueueController(queue_storage)
            queue_controller.edit_queue(queue_key, form.cleaned_data['name'],
                                        editor)
            queue_storage.save_queue(queue)
            return HttpResponseRedirect(reverse('web_tracker:show_queue',
                                                args=(queue_key,)))
    context = {'form': form, 'queue': queue}
    return render(request, 'web_tracker/edit_queue.html', context)


@update_all
@login_required
def delete_queue(request, queue_key):
    queue_storage = ORMQueueStorage()
    queue = queue_storage.get_queue_by_key(queue_key)
    user_storage = ORMUserStorage()
    user = user_storage.get_user_by_uid(request.user.id)

    if queue.owner != user.uid:
        context = {'message': 'Access denied. You cannot delete this queue!'}
        return render(request, 'web_tracker/404.html', context)

    if queue.name == 'DEFAULT':
        context = {'message': 'Cannot delete default queue!'}
        return render(request, 'web_tracker/404.html', context)

    if queue.opened_tasks or queue.solved_tasks or queue.failed_tasks:
        task_storage = ORMTaskStorage()
        task_storage.delete_queue_tasks(queue)
    user_controller = UserController(user_storage)
    user_controller.unlink_user_and_queue(user, queue)
    queue_storage.remove_queue(queue)

    return HttpResponseRedirect(reverse('web_tracker:index'))


@update_all
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
            key = os.urandom(7).hex()
            plan_controller.create_plan(
                key=key, author=user,
                name=form.cleaned_data['name'],
                period=form.cleaned_data['period'],
                activation_time=form.cleaned_data['time'],
                reminder=form.cleaned_data['reminder']
            )

            return HttpResponseRedirect(
                reverse('web_tracker:show_plan', args=(key,)))
    context = {'form': form}
    return render(request, 'web_tracker/create_plan.html', context)


@update_all
@login_required
def show_plan(request, plan_key):
    plan_storage = ORMPlanStorage()
    plan = plan_storage.get_plan_by_key(plan_key)
    try:
        plan.time = Time.get_date(plan.time)
    except Exception:
        pass
    if plan.author != request.user.username:
        raise Http404
    context = {'plan': plan}
    return render(request, 'web_tracker/show_plan.html', context)


@update_all
@login_required
def edit_plan(request, plan_key):
    user_storage = ORMUserStorage()
    plan_storage = ORMPlanStorage()
    plan = plan_storage.get_plan_by_key(plan_key)
    editor = user_storage.get_user_by_nick(request.user.username)
    if plan.author != editor.nick:
        raise Http404
    try:
        plan.time = Time.get_date(plan.time)
    except Exception:
        pass
    if request.method != 'POST':
        form = PlanForm(instance=plan)

    else:
        form = PlanForm(instance=plan, data=request.POST)
        if form.is_valid():
            plan_controller = PlanController(plan_storage)
            plan_controller.edit_plan(plan_key, form.cleaned_data['name'],
                                      period=form.cleaned_data['period'],
                                      time=form.cleaned_data['time'],
                                      reminder=form.cleaned_data['reminder'])
            plan_storage.save_plans()
            return HttpResponseRedirect(reverse('web_tracker:plan_queue',
                                                args=(plan_key,)))
    context = {'form': form, 'plan': plan}
    return render(request, 'web_tracker/edit_plan.html', context)


@update_all
@login_required
def delete_plan(request, plan_key):
    plan_storage = ORMPlanStorage()
    plan = plan_storage.get_plan_by_key(plan_key)
    if plan.author != request.user.username:
        context = {'message': 'Access denied. You cannot delete this plan!'}
        return render(request, 'web_tracker/404.html', context)

    plan_storage.remove_plan(plan)
    return HttpResponseRedirect(reverse('web_tracker:index'))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('web_tracker:index'))


@update_all
def register(request):
    if request.method != 'POST':
        form = UserCreationFormBoot()

    else:
        form = UserCreationFormBoot(data=request.POST)

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
            queue = queue_controller.add_queue(name='DEFAULT',
                                               key=os.urandom(6).hex(),
                                               owner=user)
            user_controller.link_user_with_queue(user, queue)
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('web_tracker:index'))
    context = {'form': form}

    return render(request, 'users/register.html', context)
