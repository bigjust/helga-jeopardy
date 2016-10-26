import nltk
import random
import requests
import smokesignal
import string

from nltk.stem.snowball import EnglishStemmer

from twisted.internet import reactor

from helga import settings
from helga.db import db
from helga.log import get_channel_logger
from helga.plugins import command, preprocessor


ANSWER_DELAY = getattr(settings, 'JEOPARDY_ANSWER_DELAY', 30)

api_endpoint = 'http://www.trivialbuzz.com/api/v1/'

correct_responses = [
    'look at the big brains on {}',
    '{}, you are correct.',
    '{} takes it, and has control of the board.',
]

def reset_channel(channel):
    """
    For channel name, make sure no question is active.
    """

    db.jeopardy.update_many({
        'channel': channel,
        'active': True
        }, {'$set': {'active': False}})

def process_token(token):
    """
    stuff we do to every token, both answer and responses.

    1. lowercase
    2. remove punctuation
    3. stem

    """

    # lowercase
    token = token.lower()

    # punctuation
    token = token.translate(string.maketrans('',''), string.punctuation)

    # stem
    stemmer = EnglishStemmer()
    token = stemmer.stem(token)

    return token

def eval_potential_answer(input_line, answer):
    """
    Checks if `input_line` is an match for `answer`
    """

    stemmer = EnglishStemmer()

    input_tokens = [process_token(token) for token in input_line]
    answer_tokens = [process_token(token) for token in answer.split()]

    matched = set(input_tokens).intersection(set(answer_tokens))
    partial = len(matched)

    if len(matched) == len(answer_tokens):
        return True, partial

    return False, partial

def reveal_answer(client, channel, args):
    client.msg(channel, 'the correct answer is: {}'.format(args))
    reset_channel(channel)

@command('j', help='jeopardy!')
def jeopardy(client, channel, nick, message, cmd, args):
    """
    Asks a question if there is no active question in the channel.

    If there are args and there is an active question, then evaluate
    the string as a possible answer.

    If there is an arg and there is no active question, ignore, was
    probably a late response.

    On the first correct response, deactivate the question and report
    the correct response (w/ nick).
    """

    # if we have an active question, and args, evaluate the answer

    question = db.jeopardy.find_one({
        'channel': channel,
        'active': True,
    })

    if question and args:
        correct, partial = eval_potential_answer(args, question['answer'])

        if correct:
            reset_channel(channel)
            return random.choice(correct_responses).format(nick)

        if partial > 0:
            return "{}, can you be more specific?".format(nick)

        # wrong answer, ignore
        return

    if question and not args:
        return

    if not question and args:
        return

    try:
        tb_resp = requests.get('{}questions/random.json'.format(api_endpoint)).json()['question']
        question_text = tb_resp['body'][1:-1]
        answer = tb_resp['response']
        category = tb_resp['category']['name']
        value = tb_resp['value']

        db.jeopardy.insert({
            'id': tb_resp['id'],
            'answer': answer,
            'channel': channel,
            'active': True,
        })

        reactor.callLater(ANSWER_DELAY, reveal_answer, client, channel, answer)

    except requests.exceptions.RequestException:
        return 'problem, check logs'

    return '[{}] For ${}: {}'.format(category, value, question_text)


@smokesignal.on('join')
def back_from_commercial(client, channel):

    reset_channel(channel)
    client.msg(channel, 'aaaand we\'re back!')
