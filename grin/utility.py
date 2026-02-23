#!/usr/bin/env python3

from .token import GrinToken
from .program_state import ProgramState
from .token import GrinTokenKind
from typing import Any


class GrinRuntimeError(Exception):
    """Raised when a runtime error occurs while executing a Grin program."""

    pass


def value_from_token(state: ProgramState, value_token: GrinToken):
    kind = value_token.kind()
    assert kind in (
        GrinTokenKind.LITERAL_INTEGER,
        GrinTokenKind.LITERAL_FLOAT,
        GrinTokenKind.LITERAL_STRING,
        GrinTokenKind.IDENTIFIER,
    )
    if kind == GrinTokenKind.IDENTIFIER:
        return state.vars.get(value_token.text(), 0)
    else:
        return value_token.value()


def _apply_comp_operator(a: Any, op_kind: GrinTokenKind, b: Any):
    if op_kind == GrinTokenKind.EQUAL:
        return a == b
    if op_kind == GrinTokenKind.NOT_EQUAL:
        return a != b
    if op_kind == GrinTokenKind.LESS_THAN:
        return a < b
    if op_kind == GrinTokenKind.LESS_THAN_OR_EQUAL:
        return a <= b
    if op_kind == GrinTokenKind.GREATER_THAN:
        return a > b
    if op_kind == GrinTokenKind.GREATER_THAN_OR_EQUAL:
        return a >= b
    raise GrinRuntimeError('Unknown comparison operator')


def compare_values(left: Any, op_kind: GrinTokenKind, right: Any):
    """Interpret grin comparison expressions"""
    # Numeric
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        a = float(left) if isinstance(left, int) and isinstance(right, float) else left
        b = (
            float(right)
            if isinstance(right, int) and isinstance(left, float)
            else right
        )
        # simpler: a = float(left); b = float(right) works too
        a = float(left)
        b = float(right)
        return _apply_comp_operator(a, op_kind, b)

    # string comparisons
    if isinstance(left, str) and isinstance(right, str):
        return _apply_comp_operator(left, op_kind, right)

    raise GrinRuntimeError('Runtime error: invalid types for comparison')


def resolve_jump_target(state: ProgramState, target_token: GrinToken):
    destination_relative = None
    target_token_kind = target_token.kind()

    if target_token_kind == GrinTokenKind.LITERAL_INTEGER:
        destination_relative = target_token.value()
    elif target_token_kind == GrinTokenKind.LITERAL_STRING:
        destination_relative = target_token.value()
    elif target_token_kind == GrinTokenKind.IDENTIFIER:
        destination_relative = state.vars.get(target_token.text(), 0)
    else:
        raise AssertionError('Parser should prevent this')

    if isinstance(destination_relative, int):
        if destination_relative == 0:
            raise GrinRuntimeError('Runtime error: GOTO 0 is not permitted')

        dest = state.ip + destination_relative
        # Validate destination (0-based)
        if dest < 0:
            raise GrinRuntimeError('Runtime error: jump to non-positive line')
        if dest > len(state.token_lines):
            raise GrinRuntimeError('Runtime error: jump beyond program end')
        if dest == state.ip:
            raise GrinRuntimeError('Runtime error: jump to same line not permitted')
        return dest

    if isinstance(destination_relative, str):
        if destination_relative not in state.goto_labels:
            raise GrinRuntimeError('Runtime error: unknown label')
        dest = state.goto_labels[destination_relative]
        if dest == state.ip:
            raise GrinRuntimeError('Runtime error: jump to same line not permitted')
        return dest

    raise GrinRuntimeError('Runtime error: invalid GOTO/GOSUB target type')
