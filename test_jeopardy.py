from helga_jeopardy import jeopardy, eval_potential_answer, clean_question


class TestAnswerMatching(object):

    def setup(self):
        self.answer = 'winston churchill'

    def assertAnswer(self, input_line):
        correct, _, _ = eval_potential_answer(input_line.split(), self.answer)
        assert correct

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

    def test_stopword(self):
        self.answer = 'the pen'
        self.assertAnswer('pen')

    def test_remove_punctuation(self):
        self.answer = 'Baby, I Love Your Way'
        self.assertAnswer('ooh baby i love your way')

        self.answer = 'John F. Kennedy'
        self.assertAnswer('john f kennedy')

    def test_or_parens(self):
        self.answer = 'the disciples (or apostles)'
        self.assertAnswer('disciples')
        self.assertAnswer('apostles')

    def test_partial_match(self):
        correct, partial, _ = eval_potential_answer(
            ['kennedy'],
            'john f. kennedy'
        )

        assert partial
        assert not correct

        correct, partial, _ = eval_potential_answer(
            ['one', 'flew', 'over'],
            'One Flew Over the Cuckoo\'s Nest'
        )

        assert partial == 2
        assert not correct

        correct, partial, _ = eval_potential_answer(
            ['earl', 'gray', 'tea'],
            'earl grey tea',
        )

        assert correct

    def test_ratio_match(self):

        correct, partial, ratio = eval_potential_answer(
            ['man'],
            'a man',
        )

        assert correct
        assert ratio == 0.75

    def test_clean_url(self):
        question = "what is a http://test.com/?"
        result_question, contexts = clean_question(question)

        assert result_question == "what is a"
        assert len(contexts) == 1
        assert contexts[0] == "http://test.com/?"

    def test_clean_multiple_urls(self):
        question = "this is a thing http://abc.com/b.gif and this is also a thing https://internet.org/a.jpg"
        result_question, contexts = clean_question(question)

        assert result_question == "this is a thing  and this is also a thing"
        assert len(contexts) == 2
        assert contexts[0] == "http://abc.com/b.gif"
        assert contexts[1] == "https://internet.org/a.jpg"