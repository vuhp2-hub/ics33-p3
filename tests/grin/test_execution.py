#!/usr/bin/env python3

import unittest
import grin.execution as execution
from grin.parsing import parse

class TestExecutionStarterIndex(unittest.TestCase):
    def test_get_starter_index_no_label(self):
        test_input = ['LET A 4']
        token = list(parse(test_input))[0]
        self.assertEqual(execution._get_starter_index(token), 0)
    def test_get_starter_index_with_label(self):
        test_input = ['LABEL: LET A 4']
        token = list(parse(test_input))[0]
        self.assertEqual(execution._get_starter_index(token), 2)

def _empty_str(): return ''

def _run_grin(program_text: str) -> list[str]:
    raw_lines = program_text.splitlines()
    token_lines = list(parse(raw_lines))
    return execution.execute(token_lines, input_func=_empty_str)

class TestLetPrint(unittest.TestCase):
    def test_basic_let_print(self):
        out = _run_grin("LET A 5\nPRINT A\n.\n")
        self.assertEqual(out, ["5"])

    def test_unset_variable_defaults_to_zero(self):
        out = _run_grin("PRINT X\n.\n")
        self.assertEqual(out, ["0"])

    def test_let_from_other_variable(self):
        out = _run_grin("LET A 7\nLET B A\nPRINT B\n.\n")
        self.assertEqual(out, ["7"])

    def test_string_literal(self):
        out = _run_grin('LET MSG "Hello Boo!"\nPRINT MSG\n.\n')
        self.assertEqual(out, ["Hello Boo!"])

    def test_float_literal(self):
        out = _run_grin("LET F 13.015625\nPRINT F\n.\n")
        self.assertEqual(out, ["13.015625"])

    def test_labeled_line(self):
        out = _run_grin("START: LET A 3\nPRINT A\n.\n")
        self.assertEqual(out, ["3"])

if __name__ == '__main__':
    unittest.main()
