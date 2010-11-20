from gevent import sleep

from core.hooks import *

'''Sends a message when a user JOINs.'''

@subscribe('join') # someone joined
def greet(bot, parsed_event):
    sleep(1.3)
    if parsed_event.nick != bot.irc.nick:
        bot.irc.msg(parsed_event.trailing, 'Why hello there.. {0}'.format(parsed_event.nick))
