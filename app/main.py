#!/usr/bin/env python3
"""Main entry point of console app calistra"""

__author__ = "Igor Turcevich <vip.turcevich3@gmail.com>"

from app import console_interface
import sys
from calistra_lib.logger import get_logger


def start():
    """Execute program
    :return: None
    """
    code = console_interface.run()
    get_logger().info('Process finished with exit code {}.\n'.format(code))
    sys.exit(code)


if __name__ == '__main__':
    start()
