#!/usr/bin/env python3

from .token import GrinToken
from .program_state import ProgramState
from .token import GrinTokenKind

class GrinRuntimeError(Exception):
    """Raised when a runtime error occurs while executing a Grin program."""
    pass

def value_from_token(state: ProgramState, value_token: GrinToken):
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

