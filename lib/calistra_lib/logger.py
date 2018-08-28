"""This module contains functions for logging program executing"""

import functools
import logging
from calistra_lib.constants import LoggingConstants

console_logger = None
library_logger = None


def get_logger(is_library_logger=False):
    """
    This function for creating program logger
    :return logger
    """
    global console_logger, library_logger
    if is_library_logger and library_logger:
        return library_logger
    if is_library_logger is False and console_logger:
        return console_logger

    if is_library_logger:
        logger = logging.getLogger(LoggingConstants.LIBRARY_LOGGER)
    else:
        logger = logging.getLogger(LoggingConstants.CONSOLE_LOGGER)

    file = logging.FileHandler(LoggingConstants.LOG_FILE)
    formatter = logging.Formatter(LoggingConstants.LOG_FORMAT)
    file.setFormatter(formatter)
    logger.addHandler(file)
    logger.setLevel(logging.DEBUG)

    if is_library_logger:
        library_logger = logger
    else:
        console_logger = logger

    return logger


def log_lib(func):
    @functools.wraps(func)
    def logger_func(*args, **kwargs):
        global library_logger
        if library_logger is None:
            library_logger = get_logger(LoggingConstants.LIBRARY_LOGGER)

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
        global console_logger
        if console_logger is None:
            console_logger = get_logger(LoggingConstants.CONSOLE_LOGGER)

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
