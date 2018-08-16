from argparse import ArgumentParser
import sys


class FormattedParser(ArgumentParser):
    active_sub_parser = None

    def error(self, message):
        sys.stderr.write('error: {}\n'.format(message))
        self.help()
        sys.exit(2)

    def help(self):
        if self.active_sub_parser is not None:
            self.active_sub_parser.print_help()
        else:
            self.print_help()
