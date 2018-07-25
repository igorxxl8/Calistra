from parser import Parser, ParserConstants
import sys


def main():
    parser_ = Parser(sys.argv)
    args_dict = parser_.get_args_dict()

    # get target for processing
    target = args_dict.pop(ParserConstants.TARGET)
    if not target:
        parser_.show_usage(dest=sys.stderr)
        exit(1)

    # TODO: process target

    # get action for perform target operation
    action = args_dict.pop(ParserConstants.ACTION)
    if not action:
        parser_.show_usage(dest=sys.stderr, level=2)
        exit(1)

    # TODO: process action


if __name__ == '__main__':
    main()
