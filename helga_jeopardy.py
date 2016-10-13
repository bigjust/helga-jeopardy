from helga.plugins import command

@command('jeopardy', help='HALP')
def jeopardy (client, channel, nick, message, cmd, args):
    return 'Success!'
