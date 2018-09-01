"""This module contains functions for logging program executing"""

import functools
import logging
import logging.config

console_logger = None
library_logger = None
config_file = None
is_enabled = True


def set_logger_config_file(configuration):
    global config_file
    config_file = configuration


def set_logger_enabled(value):
    global is_enabled
    is_enabled = value


def get_logger(is_library_logger=False):
    """
    This function for creating program logger
    :return logger
    """
    global console_logger, library_logger, config_file
    if is_library_logger and library_logger:
        return library_logger
    if is_library_logger is False and console_logger:
        return console_logger

    logging.config.fileConfig(config_file)

    if is_library_logger:
        logger = logging.getLogger('library_logger')
        library_logger = logger
    else:
        logger = logging.getLogger('console_logger')
        console_logger = logger
    if is_enabled is False:
        logging.disable(logging.CRITICAL)
    return logger


def log_lib(func):
    @functools.wraps(func)
    def logger_func(*args, **kwargs):
        if is_enabled is False:
            return func(*args, **kwargs)

        global library_logger
        if library_logger is None:
            library_logger = get_logger(True)

        try:
            library_logger.debug('Call function: {}, module - {}'.format(
                func.__name__, func.__module__)
            )
            library_logger.debug('Args: {}'.format(str(args)))
            library_logger.debug('Kwargs: {}'.format(str(kwargs)))
            result = func(*args, **kwargs)
            library_logger.debug('Result: {}'.format(result))
            return result
        except Exception as e:
            library_logger.error(
                'Function "{}" raise exception {}! Details '.format(
                    func.__name__, e.__class__.__name__)

            )

            raise e

    return logger_func


def log_cli(func):
    """
    A decorator for wraping console functions and logging it content or write
     exception message in case error
    """

    @functools.wraps(func)
    def logger_func(*args, **kwargs):
        if is_enabled is False:
            return func(*args, **kwargs)
        global console_logger
        if console_logger is None:
            console_logger = get_logger()

        try:
            console_logger.debug('Call function: {}, module - {}'.format(
                func.__name__, func.__module__)
            )
            console_logger.debug('Args: {}'.format(str(args)))
            console_logger.debug('Kwargs: {}'.format(str(kwargs)))
            result = func(*args, **kwargs)
            console_logger.debug('Result: {}'.format(result))
            return result
        except Exception as e:
            console_logger.error(
                'Function "{}" raise exception {}! Details '.format(
                    func.__name__, e.__class__.__name__)

            )

            raise e

    return logger_func
