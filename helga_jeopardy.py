import datetime
import nltk
import random
import re
import requests
import smokesignal
import string

from helga import settings, log
from helga.db import db
from helga.plugins import command

from bson.son import SON
from difflib import SequenceMatcher
from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer
from requests.exceptions import RequestException
from twisted.internet import reactor

logger = log.getLogger(__name__)

DEBUG = getattr(settings, 'HELGA_DEBUG', False)
ANSWER_DELAY = getattr(settings, 'JEOPARDY_ANSWER_DELAY', 30)

api_endpoint = 'http://www.trivialbuzz.com/api/v1/'

correct_responses = [
    'look at the big brains on {}',
    '{}, you are correct.',
    '{} takes it, and has control of the board.',
]

def reset_channel(channel, mongo_db=db.jeopardy):
    """
    For channel name, make sure no question is active.
    """

    logger.debug('resetting channel')

    mongo_db.update_many({
        'channel': channel,
        'active': True
    }, {'$set': {
        'active': False
    }})

remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def process_token(token):
    """
    stuff we do to every token, both answer and responses.

    1. cast to unicode and lower case
    2. remove punctuation
    3. stem

    """

    # cast to unicode and lower case
    token = u'{}'.format(token).lower()

    # remove punctuation
    token = token.translate(remove_punctuation_map)

    # stem
    stemmer = EnglishStemmer()
    token = stemmer.stem(token)

    return token

def eval_potential_answer(input_line, answer):
    """
    Checks if `input_line` is an match for `answer`

    returns a 3 item tuple:
    `bool`: True if correct
    `partial`: number of tokens matched
    `ratio`: ratio of matching characters

    """

    pot_answers = re.findall(r'\([^()]*\)|[^()]+', answer)

    if len(pot_answers) == 2:
        for pot_answer in pot_answers:
            pot_answer = pot_answer.replace('(','').replace(')','')
            correct, _, _ = eval_potential_answer(input_line, pot_answer)

            if correct:
                return correct, None, None

    correct = False
    partial = 0
    ratio = 0.0

    input_string = u''.join(input_line)

    sequence_matcher = SequenceMatcher(None, input_string, answer)
    ratio = sequence_matcher.ratio()

    if ratio >= 0.75:
        correct = True

    stemmer = EnglishStemmer()

    input_tokens = [process_token(token) for token in input_line]
    processed_answer_tokens = [process_token(token) for token in answer.split()]
    answer_tokens = []

    for tok in processed_answer_tokens:
        if tok not in stopwords.words('english'):
            answer_tokens.append(tok)

    # remove stopwords from answer_tokens

    matched = set(input_tokens).intersection(set(answer_tokens))
    partial = len(matched)

    logger.debug('matched: {}'.format(matched))
    logger.debug('ratio: {}'.format(ratio))

    if len(matched) == len(answer_tokens):
        correct = True

    return correct, partial, ratio

def reveal_answer(client, channel, question_text, answer, mongo_db=db.jeopardy):
    """
    This is the timer, essentially. When this point is reached, no more
    answers will be accepted, and our gracious host will reveal the
    answer in all of it's glory.
    """

    logger.debug('time to reveal the answer, if no one has guess')

    question = mongo_db.find_one({
        'channel': channel,
        'active': True,
        'question': question_text,
    })

    if not question:
        logger.debug('no active question, someone must have answered it! Good Show!')
        return

    client.msg(channel, u'the correct answer is: {}'.format(answer))

    mongo_db.update({
        'channel': channel,
        'question': question_text,
    }, { '$set': { 'active': False, }})


def retrieve_question(client, channel):
    """
    Return the question and correct answer.

    Adds question to the database, which is how it is tracked until
    active=False.

    """

    logger.debug('initiating question retrieval')

    try:
        tb_resp = requests.get('{}questions/random.json'.format(api_endpoint))
    except RequestException:
        return "Could not retrieve a question from the TrivialBuzz API"

    json_resp = tb_resp.json()['question']
    question_text = json_resp['body'][1:-1]
    answer = json_resp['response']
    category = json_resp['category']['name']
    value = json_resp['value']

    if DEBUG:
        logger.debug('psst! the answer is: {}'.format(answer))

    db.jeopardy.insert({
        'question': question_text,
        'answer': answer,
        'channel': channel,
        'value': value,
        'active': True,
    })

    question = '[{}] For ${}: {}'.format(category, value, question_text)

    logger.debug('will reveal answer in {} seconds'.format(ANSWER_DELAY))

    reactor.callLater(ANSWER_DELAY, reveal_answer, client, channel, question_text, answer)

    return question

def scores(client, channel, nick, alltime=False):
    """
    Returns top 3 scores in past week, plus the score of requesting
    nick, if the requesting nick is not in the top 3.
    """

    max_number = 3

    if alltime:
        max_number = 5

    pipeline = [
        {'$match': {
            'channel': channel,
        }},
        { '$group': {'_id': '$answered_by', 'money': {'$sum': '$value' }}},
        { '$sort': SON([('money', -1), ('_id', -1)])}
    ]

    title = "Jeopardy Leaderboard"

    if not alltime:
        title += " (Past 7 Days)"
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        pipeline[0]['$match']['timestamp'] = {'$gte': start_date }
    else:
        title += " Hall of Game"

    leaderboard = [leader_obj for leader_obj in db.jeopardy.aggregate(pipeline)]
    rank = 1

    if len(leaderboard):
        client.msg(channel, title)

    for leader in leaderboard:

        if leader['_id'] is None:
            continue

        money = leader['money']
        money = ('${:%d,.0f}'%(len(str(money))+1)).format(abs(money)).lstrip()

        if rank < max_number + 1:
            client.msg(channel, "{}. {} -- {}".format(rank, leader['_id'], money))

        if leader['_id'] == nick:
            if rank >= max_number + 1:
                # i see you getting all judgey
                client.msg(channel, "{}. {} -- {}".format(rank, leader['_id'], money))

        rank += 1


@command('j', help='usage: ,j [<response>|score]')
def jeopardy(client, channel, nick, message, cmd, args,
             quest_func=retrieve_question, mongo_db=db.jeopardy):
    """
    Asks a question if there is no active question in the channel.

    If there are args and there is an active question, then evaluate
    the string as a possible answer.

    If there is an arg and there is no active question, ignore, was
    probably a late response.

    On the first correct response, deactivate the question and report
    the correct response (w/ nick).

    if the command 'score' is given, prints simple leaderboard

    """

    if args and args[0] == 'score':
        alltime = False
        if len(args) > 1 and args[1] == 'all':
            alltime = True

        return scores(client, channel, nick, alltime=alltime)

    # if we have an active question, and args, evaluate the answer

    logger.debug('command #triggered')

    question = mongo_db.find_one({
        'channel': channel,
        'active': True,
    })

    if question and args:

        logger.debug('found active question')

        correct, partial, ratio = eval_potential_answer(args, question['answer'])

        if correct:

            logger.debug('answer is correct!')

            mongo_db.update({
                'question': question['question'],
            }, {'$set': {
                'active': False,
                'answered_by': nick,
                'timestamp': datetime.datetime.utcnow(),
            }})

            return random.choice(correct_responses).format(nick)

        if partial > 0:
            return "{}, can you be more specific?".format(nick)

        # wrong answer, ignore
        return

    if question and not args:
        logger.debug('no answer provided :/')
        return

    if not question and args:
        logger.debug('no active question :/')
        return

    question_text = quest_func(client, channel)

    return question_text


@smokesignal.on('join')
def back_from_commercial(client, channel):

    reset_channel(channel)
    client.msg(channel, 'aaaand we\'re back!')
