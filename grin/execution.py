#!/usr/bin/env python3

from .utility import GrinRuntimeError
from .token import GrinToken, GrinTokenKind
from .statements import LetStatement, PrintStatement, EndStatement, Statement
from .program_state import ProgramState

def _get_starter_index(tokens: list[GrinToken]):
    """A function that gets the token considering the possiblity of labels"""
    if (len(tokens) >= 2
        and tokens[0].kind() == GrinTokenKind.IDENTIFIER
        and tokens[1].kind() == GrinTokenKind.COLON):
        return 2
    else:
        return 0

def build_statements(token_lines: list[list[GrinToken]]) -> list[Statement]:
    """Convert token lines into executable Statement objects (one per program line)."""
    statements: list[Statement] = []
    for tokens in token_lines:
        start = _get_starter_index(tokens)
        keyword = tokens[start].kind()
        if keyword == GrinTokenKind.LET:
            statements.append(LetStatement(tokens[start + 1], tokens[start + 2]))
        elif keyword == GrinTokenKind.PRINT:
            statements.append(PrintStatement(tokens[start + 1]))
        elif keyword == GrinTokenKind.END:
            statements.append(EndStatement())
        else:
            raise GrinRuntimeError('Not implemented')
    return statements

def execute(token_lines: list[list[GrinToken]], input_func=input):
    state = ProgramState(token_lines, input_func)

    # This while loop condition is a way
    # to safeguard proper GOTO # or "Label"
    # Also to end by unbounding state.ip
    statements = build_statements(token_lines)
    while 0 <= state.ip < len(state.token_lines):
        statements[state.ip].execute(state)

    return state.output
