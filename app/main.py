#!/usr/bin/env python3
"""Main entry point of console app calistra"""

__author__ = "Igor Turcevich <vip.turcevich3@gmail.com>"

import parser
import sys


def main():
    """Execute program
    :return: None
    """

    # TODO: enable logging

    code = parser.run()
    sys.exit(code)


if __name__ == '__main__':
    main()
