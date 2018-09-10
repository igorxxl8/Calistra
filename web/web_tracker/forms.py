from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Task, Queue, Plan, User


class EventSplitDateTime(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.TextInput(attrs={'class': 'vDateField', 'type': 'date'}),
            forms.TextInput(attrs={'class': 'vTimeField', 'type': 'time'})]
        forms.MultiWidget.__init__(self, widgets, attrs)


class TaskForm(forms.ModelForm):
    queue = forms.ChoiceField()
    parent = forms.ChoiceField()
    responsible = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    status = forms.ChoiceField()
    priority = forms.ChoiceField(
        choices=[
            (-10, 'MINOR'),
            (-5, 'LOW'),
            (0, 'MEDIUM'),
            (5, 'HIGH'),
            (10, 'MAXIMUM')
        ]
    )
    priority_choices = {-10: 'MINOR',
                        -5: 'LOW',
                        0: 'MEDIUM',
                        5: 'HIGH',
                        10: 'MAXIMUM'}
    progress = forms.ChoiceField(
        choices=[(i, '{}%'.format(i)) for i in range(0, 101)]
    )

    class Meta:
        model = Task
        fields = ['queue', 'name', 'description', 'parent', 'related',
                  'priority', 'progress', 'status', 'start', 'deadline', 'tags',
                  'reminder']
        labels = {'name': 'Name', 'description': 'Description',
                  'status': 'Status',
                  'parent': 'Parent', 'related': 'Related tasks',
                  'priority': 'Priority', 'progress': 'Progress',
                  'start': 'Start', 'deadline': 'Deadline', 'tags': 'Tags',
                  'reminder': 'Reminder', 'responsible': 'Responsible'}

        widgets = {'description': forms.Textarea(attrs={'rows': 10}),
                   'tags': forms.Textarea(attrs={'rows': 1, 'resize': 'none'}),
                   'reminder': forms.Textarea(
                       attrs={'rows': 1, 'resize': 'none'})
                   }

    def __init__(self, user, task=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['responsible'] = forms.MultipleChoiceField(
            choices=[(i.nick, i.nick) for i in User.objects.all()],
            widget=forms.SelectMultiple)

        self.fields['queue'].choices = [(i.key, i.name) for i in
                                        Queue.objects.filter(owner=user.uid)]
        self.fields['start'].widget = EventSplitDateTime()
        self.fields['deadline'].widget = EventSplitDateTime()
        self.fields['parent'].choices = [(i.key, i.name) for i in
                                         Task.objects.filter(author=user.nick)]
        self.fields['parent'].choices.insert(0, ("", '---NOT SELECTED---'))
        self.fields['related'].choices = [(i.key, i.name) for i in
                                          Task.objects.filter(author=user.nick)]
        self.fields['related'].choices.insert(0, ("", '---NOT SELECTED---'))

        for field in self.fields:
            if field != 'start' and field != 'deadline':
                self.fields[field].widget.attrs.update(
                    {'class': 'form-control  no-resize'})
            if field != 'name':
                self.fields[field].required = False
            if (task and task.author != user.nick and
                    task.key in user.tasks_responsible.split(',')):
                self.fields[field].widget = forms.HiddenInput()

        self.fields['status'].wighet = forms.HiddenInput()


class EditingTaskForm(TaskForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['queue'].widget = forms.HiddenInput()
        self.fields['start'].required = False
        self.fields['status'].choices = [('opened', 'opened'),
                                         ('solved', 'solved'),
                                         ('failed', 'failed')]
        self.fields['deadline'].widget = forms.HiddenInput()
        self.fields['start'].widget = forms.HiddenInput()



class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        fields = ['name']
        labels = {'name': 'Name'}

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PlanForm(forms.ModelForm):
    period = forms.ChoiceField(choices=[
        ('hourly', 'HOURLY'),
        ('daily', 'DAILY'),
        ('weekly', 'WEEKLY'),
        ('monthly', 'MONTHLY'),
        ('yearly', 'YEARLY')])

    class Meta:
        model = Plan
        fields = ['name', 'time', 'period', 'reminder']
        labels = {'name': 'Name', 'reminder': 'Reminder',
                  'time': 'Activation time',
                  'period': 'Period'}

        widgets = {'reminder': forms.Textarea(
            attrs={'rows': 1, 'resize': 'none'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reminder'].required = False
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {'class': 'form-control no-resize'})

        self.fields['time'].widget = EventSplitDateTime()
        self.fields['time'].required = False


class UserCreationFormBoot(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
