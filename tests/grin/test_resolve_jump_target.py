#!/usr/bin/env python3

import unittest

from grin.utility import resolve_jump_target, GrinRuntimeError
from grin.test_utilities import make_state


class TestResolveJumpTarget(unittest.TestCase):
    # Integer literal targets
    def test_int_literal_forward(self):
        state = make_state(['LET A 1', 'GOTO 2', 'PRINT A', 'PRINT A'], ip=1)
        target_token = state.token_lines[1][1]
        dest = resolve_jump_target(state, target_token)
        self.assertEqual(dest, 3)

    def test_int_literal_backward(self):
        state = make_state(['PRINT "A"', 'PRINT "B"', 'PRINT "C"', 'GOTO -2'], ip=3)
        target_token = state.token_lines[3][1]
        dest = resolve_jump_target(state, target_token)
        self.assertEqual(dest, 1)

    def test_int_zero_is_error(self):
        state = make_state(['GOTO 0'], ip=0)
        target_token = state.token_lines[0][1]
        with self.assertRaises(GrinRuntimeError):
            resolve_jump_target(state, target_token)

    def test_jump_before_start_is_error(self):
        state = make_state(['GOTO -1'], ip=0)
        target_token = state.token_lines[0][1]
        with self.assertRaises(GrinRuntimeError):
            resolve_jump_target(state, target_token)

    def test_jump_beyond_end_is_error(self):
        state = make_state(['GOTO 100'], ip=0)
        target_token = state.token_lines[0][1]
        with self.assertRaises(GrinRuntimeError):
            resolve_jump_target(state, target_token)

    # String literal targets
    def test_string_label_found(self):
        state = make_state(['GOTO "DEST"', 'PRINT "NO"', 'DEST: PRINT "YES"'], ip=0)

        target_token = state.token_lines[0][1]
        dest = resolve_jump_target(state, target_token)
        self.assertEqual(dest, 2)

    def test_string_unknown_label_error(self):
        state = make_state(['GOTO "MISSING"'], ip=0)
        target_token = state.token_lines[0][1]
        with self.assertRaises(GrinRuntimeError):
            resolve_jump_target(state, target_token)

    # Identifier targets
    def test_identifier_int_target(self):
        state = make_state(['GOTO T'], ip=0)
        state.vars['T'] = 1

        target_token = state.token_lines[0][1]
        dest = resolve_jump_target(state, target_token)
        self.assertEqual(dest, 1)

    def test_identifier_label_target(self):
        state = make_state(['GOTO L', 'DEST: PRINT "YES"'], ip=0)
        state.vars['L'] = 'DEST'
        target_token = state.token_lines[0][1]
        dest = resolve_jump_target(state, target_token)
        self.assertEqual(dest, 1)

    def test_identifier_wrong_type_error(self):
        state = make_state(['GOTO T'], ip=0)
        state.vars['T'] = 1.5
        target_token = state.token_lines[0][1]
        with self.assertRaises(GrinRuntimeError):
            resolve_jump_target(state, target_token)


if __name__ == '__main__':
    unittest.main()
