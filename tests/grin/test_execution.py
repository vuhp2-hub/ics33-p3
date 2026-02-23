#!/usr/bin/env python3

import unittest
import grin.execution as execution
from grin.parsing import parse
from grin.utility import GrinRuntimeError

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

class TestArithmeticAdd(unittest.TestCase):
    def test_add_int_int(self):
        out = _run_grin("LET A 4\nADD A 3\nPRINT A\n.\n")
        self.assertEqual(out, ["7"])

    def test_add_int_float(self):
        out = _run_grin("LET A 4\nADD A 2.5\nPRINT A\n.\n")
        self.assertEqual(out, ["6.5"])

    def test_add_float_int(self):
        out = _run_grin("LET A 4.5\nADD A 2\nPRINT A\n.\n")
        self.assertEqual(out, ["6.5"])

    def test_add_string_string(self):
        out = _run_grin('LET S "Boo"\nADD S "lean"\nPRINT S\n.\n')
        self.assertEqual(out, ["Boolean"])

    def test_add_invalid_types_raises(self):
        # int + string not allowed
        program = 'LET A 1\nADD A "x"\nPRINT A\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

class TestArithmeticSub(unittest.TestCase):
    def test_sub_int_int(self):
        out = _run_grin("LET A 10\nSUB A 3\nPRINT A\n.\n")
        self.assertEqual(out, ["7"])

    def test_sub_float_float(self):
        out = _run_grin("LET A 10.5\nSUB A 3.0\nPRINT A\n.\n")
        self.assertEqual(out, ["7.5"])

    def test_sub_invalid_types_raises(self):
        program = 'LET S "hi"\nSUB S 1\nPRINT S\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

class TestArithmeticMult(unittest.TestCase):
    def test_mult_int_int(self):
        out = _run_grin("LET A 6\nMULT A 7\nPRINT A\n.\n")
        self.assertEqual(out, ["42"])

    def test_mult_float_int(self):
        out = _run_grin("LET A 3.5\nMULT A 2\nPRINT A\n.\n")
        self.assertEqual(out, ["7.0"])

    def test_mult_string_int(self):
        out = _run_grin('LET S "Boo"\nMULT S 3\nPRINT S\n.\n')
        self.assertEqual(out, ["BooBooBoo"])

    def test_mult_int_string(self):
        out = _run_grin('LET A 3\nLET S "Boo"\nMULT A S\nPRINT A\n.\n')
        # MULT A S updates A, so result should be "BooBooBoo"
        self.assertEqual(out, ["BooBooBoo"])

    def test_mult_negative_string_multiplier_raises_string_int(self):
        program = 'LET S "Boo"\nMULT S -1\nPRINT S\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

    def test_mult_negative_string_multiplier_raises_int_string(self):
        program = 'LET A -2\nLET S "Boo"\nMULT A S\nPRINT A\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

    def test_mult_invalid_types_raises(self):
        program = 'LET S "Boo"\nMULT S 2.0\nPRINT S\n.\n'  # string * float not allowed
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)


class TestArithmeticDiv(unittest.TestCase):
    def test_div_int_int_truncates_toward_zero_positive(self):
        out = _run_grin("LET A 7\nDIV A 2\nPRINT A\n.\n")
        self.assertEqual(out, ["3"])

    def test_div_int_int_truncates_toward_zero_negative(self):
        # IMPORTANT: trunc toward 0, so -7 / 2 -> -3
        out = _run_grin("LET A -7\nDIV A 2\nPRINT A\n.\n")
        self.assertEqual(out, ["-3"])

    def test_div_float_float(self):
        out = _run_grin("LET A 7.5\nDIV A 3.0\nPRINT A\n.\n")
        self.assertEqual(out, ["2.5"])

    def test_div_int_float(self):
        out = _run_grin("LET A 7\nDIV A 2.0\nPRINT A\n.\n")
        self.assertEqual(out, ["3.5"])

    def test_div_by_zero_int_raises(self):
        program = "LET A 7\nDIV A 0\nPRINT A\n.\n"
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

    def test_div_by_zero_float_raises(self):
        program = "LET A 7.0\nDIV A 0.0\nPRINT A\n.\n"
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

    def test_div_invalid_types_raises(self):
        program = 'LET S "Boo"\nDIV S 2\nPRINT S\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

class TestBuildGotoLabels(unittest.TestCase):
    def test_single_label_index(self):
        token_lines = list(parse([
            "START: LET A 1",
            "PRINT A",
            "."
        ]))
        labels = execution._build_goto_labels(token_lines)
        self.assertEqual(labels["START"], 0)

    def test_multiple_labels(self):
        token_lines = list(parse([
            "LET A 1",
            "L1: PRINT A",
            "LET A 2",
            "L2: PRINT A",
            "."
        ]))
        labels = execution._build_goto_labels(token_lines)
        self.assertEqual(labels["L1"], 1)
        self.assertEqual(labels["L2"], 3)

class TestGoto(unittest.TestCase):
    # Basic relative jumps
    def test_goto_forward_skips_line(self):
        out = _run_grin(
            "LET A 1\n"
            "GOTO 2\n"
            "LET A 99\n"
            "PRINT A\n"
            ".\n"
        )
        self.assertEqual(out, ["1"])

    def test_goto_backward_loop(self):
        out = _run_grin(
            "LET A 3\n"
            "PRINT A\n"
            "SUB A 1\n"
            "GOTO -2 IF A > 0\n"
            ".\n"
        )
        self.assertEqual(out, ["3", "2", "1"])
    def test_goto_label_jumps_to_labeled_line(self):
        out = _run_grin(
            "LET A 1\n"
            "GOTO \"DEST\"\n"
            "PRINT \"NO\"\n"
            "DEST: PRINT A\n"
            ".\n"
        )
        self.assertEqual(out, ["1"])

    # Variable-based targets
    def test_goto_target_from_variable_int(self):
        out = _run_grin(
            "LET OFFSET 2\n"
            "LET A 1\n"
            "GOTO OFFSET\n"
            "PRINT \"NO\"\n"
            "PRINT A\n"
            ".\n"
        )
        self.assertEqual(out, ["1"])

    def test_goto_target_from_variable_label(self):
        out = _run_grin(
            "LET L \"DEST\"\n"
            "GOTO L\n"
            "PRINT \"NO\"\n"
            "DEST: PRINT \"YES\"\n"
            ".\n"
        )
        self.assertEqual(out, ["YES"])

    # Conditional jumps
    def test_goto_if_true_jumps(self):
        out = _run_grin(
            "LET A 3\n"
            "GOTO 2 IF A < 4\n"
            "PRINT \"NO\"\n"
            "PRINT \"YES\"\n"
            ".\n"
        )
        self.assertEqual(out, ["YES"])

    def test_goto_if_false_does_not_jump(self):
        out = _run_grin(
            "LET A 5\n"
            "GOTO 2 IF A < 4\n"
            "PRINT \"NO\"\n"
            "PRINT \"YES\"\n"
            ".\n"
        )
        self.assertEqual(out, ["NO", "YES"])

    # Runtime errors
    def test_goto_zero_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin("GOTO 0\n.\n")

    def test_goto_unknown_label_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('GOTO "MISSING"\n.\n')

    def test_goto_target_variable_wrong_type_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin("LET T 1.5\nGOTO T\n.\n")

    def test_goto_out_of_bounds_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin("GOTO 999\n.\n")

if __name__ == '__main__':
    unittest.main()
