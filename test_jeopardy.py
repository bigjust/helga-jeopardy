from helga_jeopardy import jeopardy, eval_potential_answer

import unittest


class TestAnswerMatching(unittest.TestCase):

    def setUp(self):
        self.answer = 'winston churchill'

    def assertAnswer(self, input_line):
        correct, _ = eval_potential_answer(input_line.split(), self.answer)
        return self.assertTrue(correct)

    def test_exact_match(self):
        self.assertAnswer('winston churchill')

    def test_inexact_match(self):
        self.assertAnswer('winston l. churchill')

    def test_rambling_match(self):
        self.assertAnswer('i don\'t know, winston churchill maybe?')

    def test_case_insensitivty(self):
        self.assertAnswer('Winston Churchill')

    def test_stemming(self):
        self.answer = 'penny'
        self.assertAnswer('pennies')

    def test_remove_punctuation(self):
        self.answer = 'Baby, I Love Your Way'
        self.assertAnswer('ooh baby i love your way')

        self.answer = 'John F. Kennedy'
        self.assertAnswer('john f kennedy')

    def test_partial_match(self):
        correct, partial = eval_potential_answer(
            'kennedy'.split(),
            'john f. kennedy'
        )

        self.assertTrue(partial)
        self.assertFalse(correct)
