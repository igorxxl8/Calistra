"""
This module contains class Queue for representing single plan entity
"""


class Queue:
    """This class desctibe plan attributes"""
    def __init__(self, name, key, owner, opened_tasks=None, solved_tasks=None):
        self.name = name
        self.key = key
        self.owner = owner
        self.failed_tasks = []
        if opened_tasks is None:
            self.opened_tasks = []
        if solved_tasks is None:
            self.solved_tasks = []
