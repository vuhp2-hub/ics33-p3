#!/usr/bin/env python3

from .utility import GrinRuntimeError
from .token import GrinToken, GrinTokenKind
from .statements import (
    AddStatement,
    SubStatement,
    LetStatement,
    PrintStatement,
    EndStatement,
    Statement,
    MultStatement,
    DivStatement,
    GoToStatement
)
from .program_state import ProgramState

def _get_starter_index(tokens: list[GrinToken]):
    """A function that gets the token considering the possiblity of labels"""
    if (len(tokens) >= 2
        and tokens[0].kind() == GrinTokenKind.IDENTIFIER
        and tokens[1].kind() == GrinTokenKind.COLON):
        return 2
    else:
        return 0

def _build_statements(token_lines: list[list[GrinToken]]) -> list[Statement]:
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
        elif keyword == GrinTokenKind.ADD:
            statements.append(AddStatement(tokens[start + 1], tokens[start+2]))
        elif keyword == GrinTokenKind.SUB:
            statements.append(SubStatement(tokens[start + 1], tokens[start+2]))
        elif keyword == GrinTokenKind.MULT:
            statements.append(MultStatement(tokens[start + 1], tokens[start+2]))
        elif keyword == GrinTokenKind.DIV:
            statements.append(DivStatement(tokens[start + 1], tokens[start+2]))
        elif keyword == GrinTokenKind.GOTO:
            if len(tokens) > start + 2:
                # start+2: IF
                # 3, 4, 5 are operands and comparison operator
                condition = (tokens[start+3], tokens[start+4], tokens[start+5])
            else:
                condition = None
            statements.append(GoToStatement(tokens[start + 1], condition))
        else:
            raise GrinRuntimeError('Not implemented')
    return statements

def _build_goto_labels(token_lines: list[list[GrinToken]]) -> dict[str, int]:
    """Builds labels reference for GOTO statements"""
    labels = {}
    for index, tokens in enumerate(token_lines):
        if (len(tokens) >= 2
            and tokens[0].kind() == GrinTokenKind.IDENTIFIER
            and tokens[1].kind() == GrinTokenKind.COLON
        ):
            labels[tokens[0].text()] = index
    return labels

def execute(token_lines: list[list[GrinToken]], input_func=input):
    """Executes gin tokens with optional input_func parameter for testing INNUM, INSTR"""
    state = ProgramState(token_lines, input_func)

    statements = _build_statements(token_lines)
    state.goto_labels = _build_goto_labels(token_lines)
    # This while loop condition is a way
    # to safeguard proper GOTO # or "Label"
    # Also to end by unbounding state.ip
    while 0 <= state.ip < len(state.token_lines):
        statements[state.ip].execute(state)

    return state.output
