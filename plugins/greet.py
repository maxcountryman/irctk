from gevent import sleep

from core.hooks import *

'''Sends a message when a user JOINs.'''

@subscribe('join') # someone joined
def greet(bot, parsed):
    sleep(1.3)
    if parsed.nick != bot.irc.nick:
        bot.irc.msg(parsed.trailing, 'Why hello there.. {0}'.format(parsed.nick))
