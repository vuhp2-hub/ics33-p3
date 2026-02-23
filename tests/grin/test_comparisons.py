#!/usr/bin/env python3

import unittest

from grin.utility import compare_values, GrinRuntimeError
from grin.token import GrinTokenKind

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

if __name__ == "__main__":
    unittest.main()
