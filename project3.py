# project3.py
#
# ICS 33 Winter 2026
# Project 3: Why Not Smile?
#
# The main module that executes your Grin interpreter.
#
# WHAT YOU NEED TO DO: You'll need to implement the outermost shell of your
# program here, but consider how you can keep this part as simple as possible,
# offloading as much of the complexity as you can into additional modules in
# the 'grin' package, isolated in a way that allows you to unit test them.

import sys
from grin.parsing import parse, GrinParseError
from grin.execution import execute


def read_program_lines() -> list[str]:
    """Returning list of strings as the lines included in input"""
    lines = []
    for line in sys.stdin:
        stripped = line.rstrip('\n')
        lines.append(stripped)
        if stripped == '.':
            break
    return lines


def main() -> None:
    try:
        raw_lines = read_program_lines()
        token_lines = list(parse(raw_lines))
        execute(token_lines, input_func=input, output_func=print)
    except GrinParseError as e:
        print(str(e))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(str(e))
