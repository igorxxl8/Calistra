try:
    from lib.calistra_lib.task.task import Task
    from lib.calistra_lib.task.task_storage import TaskStorage
    from lib.calistra_lib.task.task_controller import TaskController
    from lib.calistra_lib.user.user_storage import UserStorage
except ImportError:
    from calistra_lib.task.task import Task
    from calistra_lib.task.task_storage import TaskStorage
    from calistra_lib.task.task_controller import TaskController
    from calistra_lib.user.user_storage import UserStorage


class Interface:
    def __init__(self, online_user, user_db, task_db):
        self.online_user = online_user
        self.users_storage = UserStorage(user_db)
        self.tasks_storage = TaskStorage(task_db)
        pass

    def add_user(self, nick):
        self.users_storage.add_user(nick)

    def add_task(self):
        pass

    def del_task(self):
        pass

    def edit_task(self):
        pass

    def add_plan(self):
        pass

    def del_plan(self):
        pass

    def edit_plan(self):
        pass