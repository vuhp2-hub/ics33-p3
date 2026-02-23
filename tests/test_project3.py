#!/usr/bin/env python3

import unittest
import sys
from io import StringIO
from project3 import read_program_lines

class TestReadProgramLines(unittest.TestCase):
    def test_reads_until_dot(self):
        fake_input = StringIO(
            "LET A 5\n"
            "PRINT A\n"
            ".\n"
            "THIS SHOULD NOT BE READ\n"
        )
        original_stdin = sys.stdin
        sys.stdin = fake_input
        try:
            lines = read_program_lines()
        finally:
            sys.stdin = original_stdin

        self.assertEqual(
            lines,
            ["LET A 5", "PRINT A", "."]
        )
    def test_dot_without_newline(self):
        fake_input = StringIO(
            "LET A 1\n"
            "."
        )
        original_stdin = sys.stdin
        sys.stdin = fake_input
        try:
            lines = read_program_lines()
        finally:
            sys.stdin = original_stdin

        self.assertEqual(
            lines,
            ["LET A 1", "."]
        )
    def test_only_dot(self):
        fake_input = StringIO(".\n")
        original_stdin = sys.stdin
        sys.stdin = fake_input
        try:
            lines = read_program_lines()
        finally:
            sys.stdin = original_stdin

        self.assertEqual(lines, ["."])
