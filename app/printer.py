"""This module contains class Printer for formatted output program entities"""


import sys


def concat(*args):
    """
    This function join all args into single one
    :param args:
    :return: concat string
    """
    return ''.join(args)


def formatted_string(string):
    """
    This function form string for pretty output task attribute
    :param string:
    :return: formatted string
    """
    str_len = len(string) + Printer.TAB_LEN
    return concat(Printer.DELIMETER * 2, string,
                  ' ' * (Printer.LINE_LEN - str_len), '|')


class Printer:
    """
    This class represent constants and methods for formatted output program
    entities
    """
    LINE_LEN = 125
    TAB_LEN = 7
    DELIMETER = '|\t'
    LINE = '-'*LINE_LEN
    SEPARATOR = concat(DELIMETER, '+', '-' * LINE_LEN, '+')
    CL_RED = "\033[1;31m"
    CL_BLUE = "\033[1;34m"
    CL_CYAN = "\033[1;36m"
    CL_YELLOW = '\033[93m'
    CL_GREEN = '\033[32m'
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    REVERSE = "\033[;7m"

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def print_queues(queues, queue_type=None):
        """
        This method print all queues in pretty format
        :param queues:
        :param queue_type:
        :return: None
        """
        if queue_type is None:
            queue_type = 'Queues'
        if not queues:
            print('\t{}: queues not found'.format(queue_type))
            return
        print(concat(Printer.DELIMETER, '{}:'.format(queue_type)))
        for queue in queues:
            print(
                concat(
                    Printer.DELIMETER * 2,
                    'Name: "{}" key: {}'.format(queue.name, queue.key)
                )
            )
        print()

    @staticmethod
    def print_tasks(tasks, tasks_type: str, full=False, color=None):
        """
        This method print all tasks in pretty format
        :param tasks:
        :param tasks_type: opened, solved, activated or failed
        :param full: flag, define printing in long format
        :param color:  output color
        :return: None
        """
        if not tasks:
            print('\t{}: tasks not found.'.format(tasks_type))
            return
        if color is None:
            color = Printer.BOLD
        print(concat(Printer.DELIMETER, '{}:'.format(tasks_type)))
        size = len(tasks)
        if full:
            for task in tasks:
                Printer.print_task_fully(task)
            print(Printer.SEPARATOR)
        else:
            for i in range(size):
                Printer.print_task_briefly(tasks[i], color, i + 1, 2)
            print()
        sys.stdout.write(Printer.RESET)

    @staticmethod
    def print_task_briefly(task, color=None, number=None, indent_level=0):
        """
        This function print single task in short format
        :param task:
        :param color:
        :param number:
        :param indent_level:
        :return: None
        """
        if color is None:
            color = Printer.RESET
        if number is None:
            number = ''
        sys.stdout.write(color)
        print(concat(
            Printer.DELIMETER * indent_level,
            '{}) Name: "{}", key: {}, queue: {} updated: {}, status: {}, '
            'deadline: {}'.format(number, task.name, task.key, task.queue,
                                  task.editing_time, task.status, task.deadline))
        )

    @staticmethod
    def print_task_fully(task):
        """
        This function print single task in long format
        :param task:
        :return: None
        """
        print(Printer.SEPARATOR)
        print(formatted_string('Name: {}'.format(task.name)))
        print(formatted_string('Key: {}'.format(task.key)))
        print(formatted_string('Author: {}'.format(task.author)))
        print(formatted_string('Description: {}'.format(task.description)))
        print(formatted_string('Status: {}'.format(task.status)))
        print(formatted_string('Queue key: {}'.format(task.queue)))

        spaces = '-' * (100 - task.progress)
        progress_bar = concat('[', '|' * task.progress, spaces, ']')
        print(formatted_string(
            'Progress: {}%, {}'.format(task.progress, progress_bar)))

        print(formatted_string('Deadline: {}'.format(task.deadline)))
        print(formatted_string('Updated: {}'.format(task.editing_time)))
        print(formatted_string('Tags: {}'.format(task.tags)))
        print(formatted_string('Responsible: {}'.format(task.responsible)))

        print(formatted_string('Parent: {}'.format(task.parent)))
        print(formatted_string('Related: {}'.format(task.related)))
        print(formatted_string('Priority:{}'.format(task.priority)))

    @staticmethod
    def print_reminders(reminders):
        """
        This function print all reminders in pretty format
        :param reminders:
        :return: None
        """
        # TODO: форматированный вывод
        sys.stdout.write(Printer.CL_YELLOW)
        for reminder in reminders:
            print(reminder)

        sys.stdout.write(Printer.RESET)


    @staticmethod
    def print_notifications(notifications):
        """
        This function print all notifications in pretty format
        :param notifications:
        :return: None
        """
        # TODO: форматированный вывод
        sys.stdout.write(Printer.UNDERLINE)
        index = 1
        for notification in notifications:
            print('{}) {}'.format(index, notification))
            index += 1
        sys.stdout.write(Printer.RESET)
