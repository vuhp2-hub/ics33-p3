#!/usr/bin/env python3

import unittest
import grin.execution as execution
from grin.parsing import parse

class TestExecution(unittest.TestCase):
    def test_get_starter_index_no_label(self):
        test_input = ['LET A 4']
        token = list(parse(test_input))[0]
        self.assertEqual(execution._get_starter_index(token), 0)
    def test_get_starter_index_with_label(self):
        test_input = ['LABEL: LET A 4']
        token = list(parse(test_input))[0]
        self.assertEqual(execution._get_starter_index(token), 2)
