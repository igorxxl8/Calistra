from argparse import ArgumentParser
import sys


class FormattedParser(ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: {}\n'.format(message))
        self.print_help()
        sys.exit(2)
