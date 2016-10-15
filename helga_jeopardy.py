import requests

from helga.plugins import command

@command('j', help='jeopardy!')
def jeopardy(client, channel, nick, message, cmd, args):
    try:
        tb_resp = requests.get('http://www.trivialbuzz.com/api/v1/questions/random.json')
        question_text = tb_resp.json()['question']['body']
    except requests.exceptions.RequestException:
        return 'problem, check logs'

    return question_text
