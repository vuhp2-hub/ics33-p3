#!/usr/bin/env python3

from .token import GrinToken
from .program_state import ProgramState
from .token import GrinTokenKind

def _value_from_token(state: ProgramState, value_token: GrinToken):
    kind = value_token.kind()
    assert kind in (
        GrinTokenKind.LITERAL_INTEGER,
        GrinTokenKind.LITERAL_FLOAT,
        GrinTokenKind.LITERAL_STRING,
        GrinTokenKind.IDENTIFIER
    )
    if kind == GrinTokenKind.IDENTIFIER:
        return state.vars.get(value_token.text(), 0)
    else:
        return value_token.value()

class Statement:
    """Base class for all statements."""
    def execute(self, state: ProgramState) -> None:
        raise NotImplementedError

class LetStatement(Statement):
    def __init__(self, var_token: GrinToken, value_token: GrinToken):
        self._var_token = var_token
        self._value_token = value_token

    def execute(self, state: ProgramState) -> None:
        state.vars[self._var_token.text()] = _value_from_token(state, self._value_token)
        state.ip += 1

class PrintStatement(Statement):
    def __init__(self, value_token: GrinToken):
        self._value_token = value_token

    def execute(self, state: ProgramState) -> None:
        value = _value_from_token(state, self._value_token)
        state.output.append(str(value))
        state.ip += 1

class EndStatement(Statement):
    def execute(self, state: ProgramState) -> None:
        # Jump ip out of range so the main loop ends cleanly
        state.ip = len(state.token_lines)

class VariableUpdateStatement(Statement):
    """Shared structure: KEYWORD <identifier> <value>"""
    def __init__(self, var_token: GrinToken, value_token: GrinToken):
        self._var_token = var_token
        self._value_token = value_token

    def var_name(self) -> str:
        return self._var_token.text()

    def operand_value(self, state):
        return _value_from_token(state, self._value_token)
