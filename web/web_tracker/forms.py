from django import forms

from .models import Task, Queue, Plan


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'queue', 'description', 'parent', 'related',
                  'priority', 'progress', 'start', 'deadline', 'tags',
                  'reminder', 'responsible']
        labels = {'name': 'Name', 'description': 'Description',
                  'parent': 'Parent', 'related': 'Related',
                  'priority': 'Priority', 'progress': 'Progress',
                  'start': 'Start', 'deadline': 'Deadline', 'tags': 'Tags',
                  'reminder': 'Reminder', 'responsible': 'Responsible'}

        widgets = {'description': forms.Textarea(attrs={'rows': 1}),
                   'tags': forms.Textarea(attrs={'rows': 1}),
                   'reminder': forms.Textarea(attrs={'rows': 1}),
                   'responsible': forms.Textarea(attrs={'rows': 1})}


class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        fields = ['name']
        labels = {'name': 'Name'}


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'time', 'reminder']
        labels = {'name': 'Name', 'reminder': 'Reminder',
                  'time': 'Activation time'}