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

def _value_from_token(state: ProgramState, value_token: GrinToken):
    kind = value_token.kind()
    assert kind == GrinTokenKind.LITERAL_INTEGER or kind == GrinTokenKind.LITERAL_FLOAT or kind == GrinTokenKind.LITERAL_STRING or GrinTokenKind.IDENTIFIER
    if kind == GrinTokenKind.IDENTIFIER:
        return state.vars.get(value_token.text(), 0)
    else:
        return value_token.value()

def execute(token_lines: list[list[GrinToken]], input_func=input):
    state = ProgramState(token_lines, input_func)

    # The program can explicitly end.
    # This while loop condition is a way
    # to safeguard proper GOTO # or "Label"
    while 0 <= state.ip < len(state.token_lines):
        tokens = state.token_lines[state.ip]
        start = _get_starter_index(tokens)
        keyword = tokens[start].kind()
        if keyword == GrinTokenKind.LET:
            var_token = tokens[start + 1]
            value_token = tokens[start + 2]
            state.vars[var_token.text()] = _value_from_token(state, value_token)
            state.ip += 1
        elif keyword == GrinTokenKind.PRINT:
            value_token = tokens[start + 1]
            value = _value_from_token(state, value_token)
            state.output.append(str(value))
            state.ip += 1
        elif keyword == GrinTokenKind.END:
            break
        else:
            assert False, 'Not implemented'
    return state.output
