from parser import Parser
import sys


def main():
    parser_ = Parser(sys.argv)
    print(parser_.parse())


if __name__ == '__main__':
    main()