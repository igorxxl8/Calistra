import functools
import logging
from calistra_lib.constants import LoggingConstants
import traceback

logger = None


def get_logger():
    global logger
    if logger:
        return logger
    logger = logging.getLogger(__name__)
    file = logging.FileHandler(LoggingConstants.LOG_FILE)
    formatter = logging.Formatter(LoggingConstants.LOG_FORMAT)
    file.setFormatter(formatter)
    logger.addHandler(file)
    logger.setLevel(logging.DEBUG)
    return logger


def log(func):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @functools.wraps(func)
    def logger_func(*args, **kwargs):
        global logger
        if logger is None:
            get_logger()

        try:
            logger.info('Call function: {}'.format(func.__name__))
            logger.info('Args: {}'.format(str(args)))
            logger.info('Kwargs: {}'.format(str(kwargs)))
            result = func(*args, *kwargs)
            logger.info('Result: {}'.format(result))
            return result
        except Exception as e:
            logger.error(str(e))
            logger.exception(str(e))
            raise e

    return logger_func
