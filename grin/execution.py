#!/usr/bin/env python3

from grin.token import GrinToken, GrinTokenKind

class ProgramState:
    """
    Keeps track of the program's state
    - token_lines is the program itself in grin tokens
    - ip is where the execution currently is
    - vars stores variables
    - goto_labels is a dictionary that should enable the goto functionality to work.
    - return_stack is list designed like a stack to keep track of return values
    - output stores list of values being printed
    - input_func enables the ability to test INNUM and INSTR
    """
    def __init__(self, token_lines: list[list[GrinToken]], input_func=input):
        self.token_lines = token_lines
        self.ip = 0
        self.vars = {}
        self.goto_labels = {}
        self.return_stack = []
        self.output = []
        self.input_func = input_func

def _get_starter_index(tokens: list[GrinToken]):
    """A function that gets the token considering the possiblity of labels"""
    if (len(tokens) >= 2
        and tokens[0].kind() == GrinTokenKind.IDENTIFIER
        and tokens[1].kind() == GrinTokenKind.COLON):
        return 2
    else:
        return 0

def execute(token_lines: list[list[GrinToken]], input_func=input):
    state = ProgramState(token_lines, input_func)

    while 0 <= state.ip < len(state.token_lines):
        tokens = state.token_lines[state.ip]
        start = _get_starter_index(tokens)
        keyword = tokens[start].kind()
        print(keyword)
        break
