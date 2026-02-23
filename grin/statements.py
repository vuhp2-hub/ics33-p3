#!/usr/bin/env python3

from .token import GrinToken
from .program_state import ProgramState
from .utility import GrinRuntimeError, compare_values, value_from_token, resolve_jump_target

class Statement:
    """Base class for all statements."""
    def execute(self, state: ProgramState) -> None:
        raise NotImplementedError

class LetStatement(Statement):
    def __init__(self, var_token: GrinToken, value_token: GrinToken):
        self._var_token = var_token
        self._value_token = value_token

    def execute(self, state: ProgramState) -> None:
        state.vars[self._var_token.text()] = value_from_token(state, self._value_token)
        state.ip += 1

class PrintStatement(Statement):
    def __init__(self, value_token: GrinToken):
        self._value_token = value_token

    def execute(self, state: ProgramState) -> None:
        value = value_from_token(state, self._value_token)
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
        return value_from_token(state, self._value_token)

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

class JumpStatement(Statement):
    """Parent class for GoTo and GoSub"""
    def __init__(self, target_token: GrinToken, condition=None):
        self._target_token = target_token
        # Optional conditional
        self._condition = condition

    def should_jump(self, state: ProgramState) -> bool:
        """Resolve optional conditional clause if it exists"""
        if self._condition is None:
            return True

        left_token, comp_op_token, right_token = self._condition
        left_val = value_from_token(state, left_token)
        right_val = value_from_token(state, right_token)
        return compare_values(left_val, comp_op_token.kind(), right_val)

    def destination(self, state) -> int:
        return resolve_jump_target(state, self._target_token)

class GoToStatement(JumpStatement):
    """Implementation of GoTo"""
    def execute(self, state: ProgramState) -> None:
        if self.should_jump(state):
            state.ip = self.destination(state)
        else:
            state.ip += 1

class GoSubStatement(JumpStatement):
    """GoSub Execution Implementation"""
    def execute(self, state: ProgramState) -> None:
        if self.should_jump(state):
            destination = self.destination(state)
            state.return_stack.append(state.ip + 1)
            state.ip = destination
        else:
            state.ip += 1

class ReturnStatement(Statement):
    def execute(self, state) -> None:
        if not state.return_stack:
            raise GrinRuntimeError("Runtime error: RETURN without GOSUB")
        state.ip = state.return_stack.pop()
