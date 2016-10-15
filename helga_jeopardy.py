import requests
import smokesignal

from twisted.internet import reactor

from helga import settings
from helga.plugins import command

ANSWER_DELAY = getattr(settings, 'JEOPARDY_ANSWER_DELAY', 60)

api_endpoint = 'http://www.trivialbuzz.com/api/v1/'

def reveal_answer(client, channel, args):
    client.msg(channel, 'the correct answer is: {}'.format(args))

@command('j', help='jeopardy!')
def jeopardy(client, channel, nick, message, cmd, args):

    try:
        tb_resp = requests.get('{}questions/random.json'.format(api_endpoint)).json()['question']
        question_text = tb_resp['body'][1:-1]
        answer = tb_resp['response']
        category = tb_resp['category']['name']
        value = tb_resp['value']

        reactor.callLater(ANSWER_DELAY, reveal_answer, client, channel, answer)

    except requests.exceptions.RequestException:
        return 'problem, check logs'

    return '[{}] For ${}: {}'.format(category, value, question_text)


@smokesignal.on('join')
def back_from_commercial(client, channel):
    client.msg(channel, 'aaaand we\'re back!')
