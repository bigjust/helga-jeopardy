from helga_jeopardy import jeopardy, eval_potential_answer

import unittest


class TestAnswerMatching(unittest.TestCase):

    def setUp(self):
        self.answer = 'winston churchill'

    def assertAnswer(self, input_line):
        return self.assertTrue(
            eval_potential_answer(input_line.split(), self.answer)
        )

    def test_exact_match(self):
        self.assertAnswer('winston churchill')

    def test_inexact_match(self):
        self.assertAnswer('winston l. churchill')

    def test_rambling_match(self):
        self.assertAnswer('i don\'t know, winston churchill maybe?')

    def test_case_insensitivty(self):
        self.assertAnswer('Winston Churchill')
