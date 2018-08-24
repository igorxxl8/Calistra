"""This module contains class Task for represent single task entity,
class TaskStatus"""


class TaskStatus:
    OPENED = 'opened'
    SOLVED = 'solved'
    ACTIVATED = 'activated'
    FAILED = 'failed'


class RelatedTaskType:
    """
    This class defines constants which using in related tasks
    """
    BLOCKER = 'blocker'
    CONTROLLER = 'controller'


class Task:
    """
    This class defines single task entity attributes
    """
    def __init__(self, name, key, queue=None, description=None, parent=None,
                 related=None, author=None, responsible: list=None, priority=0,
                 progress=0, start=None, deadline=None, tags=None,
                 reminder=None, creating_time=None):

        self.name = name
        self.queue = queue
        self.description = description
        self.parent = parent
        self.sub_tasks = []
        self.related = related
        self.author = author
        self.priority = priority
        self.progress = progress
        self.start = start
        self.deadline = deadline
        self.tags = tags
        self.reminder = reminder
        self.status = TaskStatus.OPENED
        self.key = key
        self.creating_time = creating_time
        self.editing_time = creating_time

        if responsible is None:
            self.responsible = []
        else:
            self.responsible = responsible
