import os
import configparser
import shutil

# define configs created by program as default
LOGGERS_DEFAULT_CONFIGS = """
[loggers]
keys=root, console_logger, library_logger

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,extendedFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_console_logger]
level=DEBUG
handlers=fileHandler
qualname=console_logger
propagate=0

[logger_library_logger]
level=DEBUG
handlers=fileHandler
qualname=library_logger
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=extendedFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=extendedFormatter
args=(os.path.join(os.environ['HOME'], 'calistra_data', 'logs.log'), )

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=

[formatter_extendedFormatter]
format=%(asctime)s = %(name)s - %(levelname)s - %(message)s
datefmt=%d.%m.%y-%H:%M:%S
"""


class Files:
    """This class store all program files paths"""
    FOLDER = os.path.join(os.environ['HOME'], 'calistra_data')
    TASKS_FILE = os.path.join(FOLDER, 'tasks.json')
    PLANS_FILE = os.path.join(FOLDER, 'plans.json')
    QUEUES_FILE = os.path.join(FOLDER, 'queues.json')
    USERS_FILE = os.path.join(FOLDER, 'users.json')
    AUTH_FILE = os.path.join(FOLDER, 'auth.json')
    ONLINE = os.path.join(FOLDER, 'online_user.json')
    SETTINGS = os.path.join(FOLDER, 'settings.conf')

    LOG_FILE = os.path.join(FOLDER, 'logs.log')
    LOG_CONFIG = os.path.join(FOLDER, 'logger.conf')
    DEFAULT_LOG_CONFIG_FILE = os.path.join(FOLDER, 'default_logger_config.conf')

    # this list of tuples contains data for init empty files
    FILES = [
        (TASKS_FILE, '[]'),
        (QUEUES_FILE, '[]'),
        (PLANS_FILE, '[]'),
        (USERS_FILE, '[]'),
        (AUTH_FILE, '[]'),
        (ONLINE, '""'),
        (DEFAULT_LOG_CONFIG_FILE, LOGGERS_DEFAULT_CONFIGS),
        (LOG_FILE, '')
    ]

    @classmethod
    def update(cls):
        """
        This method change all file constants path
        :return: None
        """
        cls.TASKS_FILE = os.path.join(cls.FOLDER, 'tasks.json')
        cls.PLANS_FILE = os.path.join(cls.FOLDER, 'plans.json')
        cls.QUEUES_FILE = os.path.join(cls.FOLDER, 'queues.json')
        cls.USERS_FILE = os.path.join(cls.FOLDER, 'users.json')
        cls.AUTH_FILE = os.path.join(cls.FOLDER, 'auth.json')
        cls.ONLINE = os.path.join(cls.FOLDER, 'online_user.json')
        # cls.SETTINGS = os.path.join(cls.FOLDER, 'settings.conf')

        cls.LOG_FILE = os.path.join(cls.FOLDER, 'logs.log')
        cls.LOG_CONFIG = os.path.join(cls.FOLDER, 'logger.conf')
        cls.DEFAULT_LOG_CONFIG_FILE = os.path.join(cls.FOLDER,
                                                   'default_logger_config.conf')

        cls.FILES = [
            (cls.TASKS_FILE, '[]'),
            (cls.QUEUES_FILE, '[]'),
            (cls.PLANS_FILE, '[]'),
            (cls.USERS_FILE, '[]'),
            (cls.AUTH_FILE, '[]'),
            (cls.ONLINE, '""'),
            (cls.DEFAULT_LOG_CONFIG_FILE, LOGGERS_DEFAULT_CONFIGS),
            (cls.LOG_FILE, '')
        ]

    @classmethod
    def set_default(cls):
        """
        This method set program default path for file in folder
        :return: None
        """
        cls.FOLDER = os.path.join(os.environ['HOME'], 'calistra_data')
        cls.TASKS_FILE = os.path.join(cls.FOLDER, 'tasks.json')
        cls.PLANS_FILE = os.path.join(cls.FOLDER, 'plans.json')
        cls.QUEUES_FILE = os.path.join(cls.FOLDER, 'queues.json')
        cls.USERS_FILE = os.path.join(cls.FOLDER, 'users.json')
        cls.AUTH_FILE = os.path.join(cls.FOLDER, 'auth.json')
        cls.ONLINE = os.path.join(cls.FOLDER, 'online_user.json')
        cls.SETTINGS = os.path.join(cls.FOLDER, 'settings.conf')

        cls.LOG_FILE = os.path.join(cls.FOLDER, 'logs.log')
        cls.LOG_CONFIG = os.path.join(cls.FOLDER, 'logger.conf')
        cls.DEFAULT_LOG_CONFIG_FILE = os.path.join(cls.FOLDER,
                                                   'default_logger_config.conf')


class Configuration:
    @staticmethod
    def edit_settings(storage_path):
        """
        This method is using for editing program settings
        :param storage_path: path were file storage will be situated
        :raise FileExistsError
        :return: None
        """
        if storage_path is None:
            return
        if os.path.exists(storage_path):
            raise FileExistsError('calistra: You cannot use an existing folder '
                                  'as a storage. Define other name for storage!'
                                  '\n')

        settings = configparser.ConfigParser()
        settings.add_section('Settings')
        settings.set('Settings', 'storage_path', Files.FOLDER)
        settings.set('Settings', 'new_storage_path', storage_path)

        Configuration.write_config(Files.SETTINGS, settings)

    @staticmethod
    def write_config(file, config):
        """
        This method write configs in file
        :param file: path to file
        :param config:
        :return: None
        """
        if config:
            with open(file, 'w') as file_obj:
                config.write(file_obj)

    @staticmethod
    def apply_settings():
        """
        This method apply all edited settings on program. Recommended to
         use in start of program
        :return: None
        """
        if os.path.exists(Files.SETTINGS):
            # get ConfigParser instance and read configs from file
            settings = configparser.ConfigParser()
            settings.read(Files.SETTINGS)

            # storage_path - place where located old storage
            storage_path = settings.get('Settings', 'storage_path')
            # new_storage_path - place where will be located storage
            new_storage_path = settings.get('Settings', 'new_storage_path')
            Files.FOLDER = storage_path
            Files.update()
            # use settings only when places changed
            if new_storage_path != storage_path:
                # copy data from old folder to new
                shutil.copytree(Files.FOLDER, new_storage_path)
                Files.FOLDER = new_storage_path
                Files.update()

                # rewrite path to logs files
                _edit_logs_path_(Files.LOG_FILE)

                # set storage_path and new_storage_path equal
                settings.set('Settings', 'storage_path', new_storage_path)
                Configuration.write_config(Files.SETTINGS, settings)

    @staticmethod
    def reset_settings():
        """
        This method is using for reset all settings
        :return:
        """
        if os.path.exists(Files.SETTINGS):
            settings = configparser.ConfigParser()
            settings.read(Files.SETTINGS)
            storage_path = settings.get('Settings', 'storage_path')
            # remove default folder
            shutil.rmtree(Files.FOLDER)
            # copy from custom folder in default folder
            shutil.copytree(storage_path, Files.FOLDER)
            # remove custom folder
            shutil.rmtree(storage_path)
            # rewrite logs files path
            _edit_logs_path_(Files.LOG_FILE)

    @staticmethod
    def get_logger_configs(path):
        """
        This method using for getting ConfigParser instance for defined file
        :param path: path to file with logger configs
        :return: configs
        """
        if os.path.exists(path):
            configs = configparser.ConfigParser()
            configs.read(path)
            return configs

    @staticmethod
    def edit_logger_configs(logger_configs_file, level, enabled, log_file):
        configs = Configuration.get_logger_configs(logger_configs_file)
        if configs is None:
            configs = configparser.ConfigParser()
            configs.read(Files.DEFAULT_LOG_CONFIG_FILE)
        Configuration.edit_logger_file_path(configs, log_file)
        Configuration.edit_logger_enabled(configs, enabled)
        Configuration.edit_logger_level(configs, level)
        Configuration.write_config(logger_configs_file, configs)

    @staticmethod
    def edit_logger_file_path(logger_configs, log_file_path):
        """
        This method set new path for logs storage
        :param logger_configs:
        :param log_file_path:
        :return: NOne
        """
        if logger_configs is None:
            return
        if log_file_path is not None:
            log_file_path = ''.join(['("', log_file_path, '", )'])
            logger_configs.set('handler_fileHandler', 'args', log_file_path)

    @staticmethod
    def edit_logger_level(logger_configs, level):
        """
        This method set logging level for logger
        :param logger_configs:
        :param level:
        :return: None
        """
        if logger_configs is None:
            return
        if level is not None:
            logger_configs.set('logger_console_logger', 'level', level)
            logger_configs.set('logger_library_logger', 'level', level)
            logger_configs.set('logger_root', 'level', level)
            logger_configs.set('handler_consoleHandler', 'level', level)
            logger_configs.set('handler_fileHandler', 'level', level)

    @staticmethod
    def edit_logger_enabled(logger_configs, enabled):
        """
        This method set logger disabled or enabled
        :param logger_configs:
        :param enabled:
        :return: None
        """
        if logger_configs is None:
            return
        if enabled is not None:
            if 'ENABLED' not in logger_configs.sections():
                logger_configs.add_section('ENABLED')
            logger_configs.set('ENABLED', 'value', enabled)

    @staticmethod
    def is_logger_enabled():
        """
        This method check logger configs and define that logger enabled or
         disabled
        :return: True if logger enabled, else - False
        """
        logger_configs = Configuration.get_logger_configs(Files.LOG_CONFIG)
        if logger_configs is None:
            return True
        is_enabled = logger_configs.get('ENABLED', 'value')
        if is_enabled == 'True':
            return True
        return False


def _edit_logs_path_(log_file_path):
    default_logger_configs = Configuration.get_logger_configs(
        Files.DEFAULT_LOG_CONFIG_FILE)
    custom_logger_configs = Configuration.get_logger_configs(
        Files.LOG_CONFIG
    )
    Configuration.edit_logger_file_path(
        custom_logger_configs, log_file_path
    )

    Configuration.edit_logger_file_path(
        default_logger_configs, log_file_path)

    Configuration.write_config(
        Files.DEFAULT_LOG_CONFIG_FILE, default_logger_configs)

    Configuration.write_config(
        Files.LOG_CONFIG, custom_logger_configs
    )
