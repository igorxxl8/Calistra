"""module which contains functions for execute program instructions"""
from parser import Parser
import sys


def run():
    """
    Runs the program
    :return: int -- exit code: 0 - program ends without error, 1 - program get error during executing
    """
    parser = Parser(sys.argv)
    commands = parser.get_commands()

    # check for the presence of the target object
    if not commands.target:
        parser.show_usage(stream=sys.stderr)
        return 1

    # check for the presence of the action with target object
    if not commands.action:
        parser.show_usage(stream=sys.stderr, level=2)
        return 1


if __name__ == '__main__':
    pass
