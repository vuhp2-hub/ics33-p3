#!/usr/bin/env python3

import unittest
import grin.execution as execution
from grin.parsing import parse
from grin.utility import GrinRuntimeError
from typing import Iterator


class TestExecutionStarterIndex(unittest.TestCase):
    def test_get_starter_index_no_label(self):
        test_input = ['LET A 4']
        token = list(parse(test_input))[0]
        self.assertEqual(execution._get_starter_index(token), 0)

    def test_get_starter_index_with_label(self):
        test_input = ['LABEL: LET A 4']
        token = list(parse(test_input))[0]
        self.assertEqual(execution._get_starter_index(token), 2)


def _empty_str():
    return ''


def _iter(iterator: Iterator):
    def closure():
        return next(iterator)

    return closure


def _run_grin(program_text: str, inputs: list[str] | None = None) -> list[str]:
    raw_lines = program_text.splitlines()
    token_lines = list(parse(raw_lines))

    output: list[str] = []
    if inputs:
        iterator = iter(inputs)
        execution.execute(
            token_lines, input_func=_iter(iterator), output_func=output.append
        )
    else:
        execution.execute(token_lines, input_func=_empty_str, output_func=output.append)
    return output


class TestLetPrint(unittest.TestCase):
    def test_basic_let_print(self):
        out = _run_grin('LET A 5\nPRINT A\n.\n')
        self.assertEqual(out, ['5'])

    def test_unset_variable_defaults_to_zero(self):
        out = _run_grin('PRINT X\n.\n')
        self.assertEqual(out, ['0'])

    def test_let_from_other_variable(self):
        out = _run_grin('LET A 7\nLET B A\nPRINT B\n.\n')
        self.assertEqual(out, ['7'])

    def test_string_literal(self):
        out = _run_grin('LET MSG "Hello Boo!"\nPRINT MSG\n.\n')
        self.assertEqual(out, ['Hello Boo!'])

    def test_float_literal(self):
        out = _run_grin('LET F 13.015625\nPRINT F\n.\n')
        self.assertEqual(out, ['13.015625'])

    def test_labeled_line(self):
        out = _run_grin('START: LET A 3\nPRINT A\n.\n')
        self.assertEqual(out, ['3'])


class TestArithmeticAdd(unittest.TestCase):
    def test_add_int_int(self):
        out = _run_grin('LET A 4\nADD A 3\nPRINT A\n.\n')
        self.assertEqual(out, ['7'])

    def test_add_int_float(self):
        out = _run_grin('LET A 4\nADD A 2.5\nPRINT A\n.\n')
        self.assertEqual(out, ['6.5'])

    def test_add_float_int(self):
        out = _run_grin('LET A 4.5\nADD A 2\nPRINT A\n.\n')
        self.assertEqual(out, ['6.5'])

    def test_add_string_string(self):
        out = _run_grin('LET S "Boo"\nADD S "lean"\nPRINT S\n.\n')
        self.assertEqual(out, ['Boolean'])

    def test_add_invalid_types_raises(self):
        # int + string not allowed
        program = 'LET A 1\nADD A "x"\nPRINT A\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)


class TestArithmeticSub(unittest.TestCase):
    def test_sub_int_int(self):
        out = _run_grin('LET A 10\nSUB A 3\nPRINT A\n.\n')
        self.assertEqual(out, ['7'])

    def test_sub_float_float(self):
        out = _run_grin('LET A 10.5\nSUB A 3.0\nPRINT A\n.\n')
        self.assertEqual(out, ['7.5'])

    def test_sub_invalid_types_raises(self):
        program = 'LET S "hi"\nSUB S 1\nPRINT S\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)


class TestArithmeticMult(unittest.TestCase):
    def test_mult_int_int(self):
        out = _run_grin('LET A 6\nMULT A 7\nPRINT A\n.\n')
        self.assertEqual(out, ['42'])

    def test_mult_float_int(self):
        out = _run_grin('LET A 3.5\nMULT A 2\nPRINT A\n.\n')
        self.assertEqual(out, ['7.0'])

    def test_mult_string_int(self):
        out = _run_grin('LET S "Boo"\nMULT S 3\nPRINT S\n.\n')
        self.assertEqual(out, ['BooBooBoo'])

    def test_mult_int_string(self):
        out = _run_grin('LET A 3\nLET S "Boo"\nMULT A S\nPRINT A\n.\n')
        # MULT A S updates A, so result should be "BooBooBoo"
        self.assertEqual(out, ['BooBooBoo'])

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
        out = _run_grin('LET A 7\nDIV A 2\nPRINT A\n.\n')
        self.assertEqual(out, ['3'])

    def test_div_int_int_truncates_toward_zero_negative(self):
        # IMPORTANT: trunc toward 0, so -7 / 2 -> -3
        out = _run_grin('LET A -7\nDIV A 2\nPRINT A\n.\n')
        self.assertEqual(out, ['-3'])

    def test_div_float_float(self):
        out = _run_grin('LET A 7.5\nDIV A 3.0\nPRINT A\n.\n')
        self.assertEqual(out, ['2.5'])

    def test_div_int_float(self):
        out = _run_grin('LET A 7\nDIV A 2.0\nPRINT A\n.\n')
        self.assertEqual(out, ['3.5'])

    def test_div_by_zero_int_raises(self):
        program = 'LET A 7\nDIV A 0\nPRINT A\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

    def test_div_by_zero_float_raises(self):
        program = 'LET A 7.0\nDIV A 0.0\nPRINT A\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)

    def test_div_invalid_types_raises(self):
        program = 'LET S "Boo"\nDIV S 2\nPRINT S\n.\n'
        with self.assertRaises(GrinRuntimeError):
            _run_grin(program)


class TestBuildGotoLabels(unittest.TestCase):
    def test_single_label_index(self):
        token_lines = list(parse(['START: LET A 1', 'PRINT A', '.']))
        labels = execution._build_goto_labels(token_lines)
        self.assertEqual(labels['START'], 0)

    def test_multiple_labels(self):
        token_lines = list(
            parse(['LET A 1', 'L1: PRINT A', 'LET A 2', 'L2: PRINT A', '.'])
        )
        labels = execution._build_goto_labels(token_lines)
        self.assertEqual(labels['L1'], 1)
        self.assertEqual(labels['L2'], 3)


class TestGoto(unittest.TestCase):
    # Basic relative jumps
    def test_goto_forward_skips_line(self):
        out = _run_grin('LET A 1\nGOTO 2\nLET A 99\nPRINT A\n.\n')
        self.assertEqual(out, ['1'])

    def test_goto_backward_loop(self):
        out = _run_grin('LET A 3\nPRINT A\nSUB A 1\nGOTO -2 IF A > 0\n.\n')
        self.assertEqual(out, ['3', '2', '1'])

    def test_goto_label_jumps_to_labeled_line(self):
        out = _run_grin('LET A 1\nGOTO "DEST"\nPRINT "NO"\nDEST: PRINT A\n.\n')
        self.assertEqual(out, ['1'])

    # Variable-based targets
    def test_goto_target_from_variable_int(self):
        out = _run_grin('LET OFFSET 2\nLET A 1\nGOTO OFFSET\nPRINT "NO"\nPRINT A\n.\n')
        self.assertEqual(out, ['1'])

    def test_goto_target_from_variable_label(self):
        out = _run_grin('LET L "DEST"\nGOTO L\nPRINT "NO"\nDEST: PRINT "YES"\n.\n')
        self.assertEqual(out, ['YES'])

    # Conditional jumps
    def test_goto_if_true_jumps(self):
        out = _run_grin('LET A 3\nGOTO 2 IF A < 4\nPRINT "NO"\nPRINT "YES"\n.\n')
        self.assertEqual(out, ['YES'])

    def test_goto_if_false_does_not_jump(self):
        out = _run_grin('LET A 5\nGOTO 2 IF A < 4\nPRINT "NO"\nPRINT "YES"\n.\n')
        self.assertEqual(out, ['NO', 'YES'])

    # Runtime errors
    def test_goto_zero_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('GOTO 0\n.\n')

    def test_goto_unknown_label_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('GOTO "MISSING"\n.\n')

    def test_goto_target_variable_wrong_type_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('LET T 1.5\nGOTO T\n.\n')

    def test_goto_out_of_bounds_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('GOTO 999\n.\n')


class TestGoSubReturn(unittest.TestCase):
    def test_gosub_relative_and_return(self):
        # GOSUB 4 from line 2 jumps to line 6, sets A and B, RETURN goes back to line 3
        out = _run_grin(
            'LET A 1\nGOSUB 4\nPRINT A\nPRINT B\nEND\nLET A 2\nLET B 3\nRETURN\n.\n'
        )
        self.assertEqual(out, ['2', '3'])

    def test_gosub_label_and_return(self):
        out = _run_grin(
            'LET A 10\nGOSUB "CHUNK"\nPRINT A\nEND\nCHUNK: LET A 99\nRETURN\n.\n'
        )
        self.assertEqual(out, ['99'])

    def test_nested_gosub_returns_in_lifo_order(self):
        # Outer gosub jumps to OUTER, which gosubs to INNER, which returns to OUTER,
        # then OUTER returns back to main.
        out = _run_grin(
            'PRINT "MAIN"\n'
            'GOSUB "OUTER"\n'
            'PRINT "DONE"\n'
            'END\n'
            'OUTER: PRINT "OUTER"\n'
            'GOSUB "INNER"\n'
            'PRINT "OUTER_AFTER"\n'
            'RETURN\n'
            'INNER: PRINT "INNER"\n'
            'RETURN\n'
            '.\n'
        )
        self.assertEqual(out, ['MAIN', 'OUTER', 'INNER', 'OUTER_AFTER', 'DONE'])

    def test_return_without_gosub_is_error(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('RETURN\n.\n')

    def test_gosub_if_false_does_not_jump_or_push(self):
        # If the condition is false, the GOSUB should have no effect.
        out = _run_grin(
            'LET A 5\nGOSUB 2 IF A < 4\nPRINT "MAIN"\nEND\nPRINT "SUB"\nRETURN\n.\n'
        )
        self.assertEqual(out, ['MAIN'])

    def test_gosub_if_true_jumps_and_return_works(self):
        # If the condition is true, it should jump into subroutine and RETURN to main.
        out = _run_grin(
            'LET A 3\nGOSUB 3 IF A < 4\nPRINT "MAIN"\nEND\nPRINT "SUB"\nRETURN\n.\n'
        )
        self.assertEqual(out, ['SUB', 'MAIN'])


class TestInstrStatement(unittest.TestCase):
    def test_instr_reads_string_and_prints_it(self):
        out = _run_grin('INSTR X\nPRINT X\n.\n', inputs=['Hello Boo!'])
        self.assertEqual(out, ['Hello Boo!'])

    def test_instr_allows_empty_string(self):
        out = _run_grin('INSTR X\nPRINT X\n.\n', inputs=[''])
        self.assertEqual(out, [''])

    def test_instr_overwrites_existing_variable(self):
        out = _run_grin('LET X "old"\nINSTR X\nPRINT X\n.\n', inputs=['new'])
        self.assertEqual(out, ['new'])


class TestInnumStatement(unittest.TestCase):
    def test_innum_reads_integer(self):
        out = _run_grin('INNUM X\nPRINT X\n.\n', inputs=['11'])
        self.assertEqual(out, ['11'])

    def test_innum_reads_negative_integer(self):
        out = _run_grin('INNUM X\nPRINT X\n.\n', inputs=['-18'])
        self.assertEqual(out, ['-18'])

    def test_innum_strips_whitespace_integer(self):
        out = _run_grin('INNUM X\nPRINT X\n.\n', inputs=['   42   '])
        self.assertEqual(out, ['42'])

    def test_innum_reads_float_with_digits(self):
        out = _run_grin('INNUM X\nPRINT X\n.\n', inputs=['11.75'])
        self.assertEqual(out, ['11.75'])

    def test_innum_reads_float_with_trailing_dot(self):
        out = _run_grin('INNUM X\nPRINT X\n.\n', inputs=['3.'])
        self.assertEqual(out, ['3.0'])

    def test_innum_strips_whitespace_float(self):
        out = _run_grin('INNUM X\nPRINT X\n.\n', inputs=['   -3.0   '])
        self.assertEqual(out, ['-3.0'])

    def test_innum_invalid_input_raises(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('INNUM X\nPRINT X\n.\n', inputs=['abc'])

    def test_innum_empty_input_raises(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('INNUM X\nPRINT X\n.\n', inputs=['   '])

    def test_innum_multiple_dots_raises(self):
        with self.assertRaises(GrinRuntimeError):
            _run_grin('INNUM X\nPRINT X\n.\n', inputs=['3.4.5'])


if __name__ == '__main__':
    unittest.main()
