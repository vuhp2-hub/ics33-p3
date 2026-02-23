#!/usr/bin/env python3

import unittest

from grin.utility import compare_values, GrinRuntimeError, value_from_token
from grin.token import GrinToken, GrinTokenKind
from grin.program_state import ProgramState
from grin.test_utilities import make_state

class TestCompareValues(unittest.TestCase):
    # Integer comparisons
    def test_int_less_than(self):
        self.assertTrue(compare_values(3, GrinTokenKind.LESS_THAN, 5))
    def test_int_equal(self):
        self.assertTrue(compare_values(4, GrinTokenKind.EQUAL, 4))
    def test_int_not_equal(self):
        self.assertTrue(compare_values(4, GrinTokenKind.NOT_EQUAL, 5))
    def test_int_greater_equal(self):
        self.assertTrue(compare_values(5, GrinTokenKind.GREATER_THAN_OR_EQUAL, 5))

    # Float comparisons
    def test_float_less_than(self):
        self.assertTrue(compare_values(2.5, GrinTokenKind.LESS_THAN, 3.0))
    def test_float_greater_than(self):
        self.assertTrue(compare_values(5.1, GrinTokenKind.GREATER_THAN, 2.0))

    # Mixed int/float
    def test_int_float_equal(self):
        self.assertTrue(compare_values(3, GrinTokenKind.EQUAL, 3.0))
    def test_float_int_less(self):
        self.assertTrue(compare_values(2.5, GrinTokenKind.LESS_THAN, 3))

    # String comparisons
    def test_string_equal(self):
        self.assertTrue(compare_values("Boo", GrinTokenKind.EQUAL, "Boo"))
    def test_string_not_equal(self):
        self.assertTrue(compare_values("Boo", GrinTokenKind.NOT_EQUAL, "Lean"))
    def test_string_lexicographic_less(self):
        self.assertTrue(compare_values("Apple", GrinTokenKind.LESS_THAN, "Banana"))
    def test_string_greater_equal(self):
        self.assertTrue(compare_values("Zoo", GrinTokenKind.GREATER_THAN_OR_EQUAL, "Zoo"))

    # Invalid comparisons
    def test_int_string_invalid(self):
        with self.assertRaises(GrinRuntimeError):
            compare_values(3, GrinTokenKind.EQUAL, "Boo")
    def test_string_float_invalid(self):
        with self.assertRaises(GrinRuntimeError):
            compare_values("Boo", GrinTokenKind.LESS_THAN, 3.0)
    def test_invalid_operator(self):
        # If your helper assumes only relational ops, this might be AssertionError instead.
        with self.assertRaises(GrinRuntimeError):
            compare_values(3, None, 4)

def _compare_tokens(state: ProgramState, left_tok: GrinToken, op_tok: GrinToken, right_tok: GrinToken) -> bool:
    """Adapter: tokens -> values -> compare_values"""
    left_val = value_from_token(state, left_tok)
    right_val = value_from_token(state, right_tok)
    return compare_values(left_val, op_tok.kind(), right_val)

class TestIfCondition(unittest.TestCase):
    def test_if_numeric_true(self):
        # A=3, check A < 4 => True
        state = make_state(["GOTO 2 IF A < 4"], ip=0)
        state.vars["A"] = 3
        tokens = state.token_lines[0]
        left_tok = tokens[3]
        op_tok = tokens[4]
        right_tok = tokens[5]
        self.assertTrue(_compare_tokens(state, left_tok, op_tok, right_tok))

    def test_if_numeric_false(self):
        # A=5, check A < 4 => False
        state = make_state(["GOTO 2 IF A < 4"], ip=0)
        state.vars["A"] = 5
        tokens = state.token_lines[0]
        left_tok = tokens[3]
        op_tok = tokens[4]
        right_tok = tokens[5]
        self.assertFalse(_compare_tokens(state, left_tok, op_tok, right_tok))

    def test_if_int_float_mixed(self):
        # 3 = 3.0 => True
        state = make_state(["GOTO 1 IF 3 = 3.0"], ip=0)
        tokens = state.token_lines[0]
        left_tok = tokens[3]
        op_tok = tokens[4]
        right_tok = tokens[5]

        self.assertTrue(_compare_tokens(state, left_tok, op_tok, right_tok))

    def test_if_string_lexicographic(self):
        # "Apple" < "Banana" => True
        state = make_state(['GOTO 1 IF "Apple" < "Banana"'], ip=0)
        tokens = state.token_lines[0]
        left_tok = tokens[3]
        op_tok = tokens[4]
        right_tok = tokens[5]

        self.assertTrue(_compare_tokens(state, left_tok, op_tok, right_tok))

    def test_if_invalid_type_combo_raises(self):
        # 1 = "x" => runtime error (int vs string)
        state = make_state(['GOTO 1 IF 1 = "x"'], ip=0)
        tokens = state.token_lines[0]
        left_tok = tokens[3]
        op_tok = tokens[4]
        right_tok = tokens[5]

        with self.assertRaises(GrinRuntimeError):
            _compare_tokens(state, left_tok, op_tok, right_tok)

    def test_if_identifier_defaults_to_zero(self):
        # A not set => defaults to 0, so 0 < 4 => True
        state = make_state(["GOTO 2 IF A < 4"], ip=0)
        tokens = state.token_lines[0]
        left_tok = tokens[3]
        op_tok = tokens[4]
        right_tok = tokens[5]

        self.assertTrue(_compare_tokens(state, left_tok, op_tok, right_tok))

if __name__ == "__main__":
    unittest.main()
