# test_token.py
#
# ICS 33 Winter 2026
# Project 3: Why Not Smile?
#
# Unit tests for the provided grin.token module.
#
# WHAT YOU NEED TO DO: Nothing, unless you make changes to grin.token
# (which shouldn't be necessary).

from grin.token import GrinTokenKind, GrinToken
import unittest



class GrinTokenKindTest(unittest.TestCase):
    def test_indexes_are_unique(self):
        indexes = set(kind.index() for kind in GrinTokenKind.__members__.values())
        self.assertEqual(len(indexes), len(GrinTokenKind.__members__))



if __name__ == '__main__':
    unittest.main()
