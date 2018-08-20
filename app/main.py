#!/usr/bin/env python3
"""Main entry point of console app calistra"""

__author__ = "Igor Turcevich <vip.turcevich3@gmail.com>"

from app import console_interface
import sys

# TODO: 1) Логирование


def start():
    """Execute program
    :return: None
    """
    # TODO: enable logging
    code = console_interface.run()
    sys.exit(code)


if __name__ == '__main__':
    start()
