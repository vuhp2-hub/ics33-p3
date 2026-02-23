#!/usr/bin/env python3

from .token import GrinToken
from .program_state import ProgramState
from .token import GrinTokenKind
from .utility import GrinRuntimeError

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

class ArithmeticStatement(VariableUpdateStatement):
    def execute(self, state):
        name = self.var_name()
        left = state.vars.get(name, 0)
        right = self.operand_value(state)

        result = self.apply(left, right)
        state.vars[name] = result
        state.ip += 1

    def apply(self, left, right):
        raise NotImplementedError

class AddStatement(ArithmeticStatement):
    def apply(self, left, right):
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        raise GrinRuntimeError("Invalid types for ADD")

class SubStatement(ArithmeticStatement):
    def apply(self, left, right):
        # numeric - numeric only
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left - right

        raise GrinRuntimeError("Runtime error: invalid types for SUB")

class MultStatement(ArithmeticStatement):
    def apply(self, left, right):
        # numeric * numeric
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left * right

        # string * int
        if isinstance(left, str) and isinstance(right, int):
            if right < 0:
                raise GrinRuntimeError("Runtime error: negative string multiplication")
            return left * right

        # int * string
        if isinstance(left, int) and isinstance(right, str):
            if left < 0:
                raise GrinRuntimeError("Runtime error: negative string multiplication")
            return right * left

        raise GrinRuntimeError("Runtime error: invalid types for MULT")


class DivStatement(ArithmeticStatement):
    def apply(self, left, right):
        # numeric / numeric only
        if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
            raise GrinRuntimeError("Runtime error: invalid types for DIV")

        if right == 0 or right == 0.0:
            raise GrinRuntimeError("Runtime error: division by zero")

        # int / int -> int (truncate toward 0)
        if isinstance(left, int) and isinstance(right, int):
            return int(left / right)

        # otherwise float division
        return left / right
