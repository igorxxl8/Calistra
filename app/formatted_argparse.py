"""This module contains FormattedParser class which producing the
correct help message
"""

from argparse import ArgumentParser
import sys


class FormattedParser(ArgumentParser):
    """
    This class using as wrapper for standard argument parser. It output help
     message in case incorrect user console input"""
    active_sub_parser = None

    def error(self, message):
        """
        Print error message
        :param message: message to print
        :return: None
        """
        sys.stderr.write('error: {}\n'.format(message))
        self.help()
        sys.exit(2)

    def help(self):
        """
        Choose correct help message for appropriate parser level
        :return: None
        """
        if self.active_sub_parser is not None:
            self.active_sub_parser.print_help()
        else:
            self.print_help()
