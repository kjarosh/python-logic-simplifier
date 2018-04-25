'''
A program that uses the logic simplifier.
'''
import fileinput
from logic_simplifier.simplifier import simplify


def main():
    for line in fileinput.input():
        print(simplify(line))


if __name__ == '__main__':
    main()
