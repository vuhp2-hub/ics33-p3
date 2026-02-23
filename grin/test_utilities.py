#!/usr/bin/env python3

from .program_state import ProgramState
from .parsing import parse
from .execution import _build_goto_labels

def make_state(lines: list[str], ip: int = 0) -> ProgramState:
    """
    Parses the given Grin lines (without requiring caller to include '.'),
    builds ProgramState, and initializes goto_labels.
    Used by tests
    """
    token_lines = list(parse(lines + ["." ]))
    state = ProgramState(token_lines)
    state.goto_labels = _build_goto_labels(token_lines)
    state.ip = ip
    return state
