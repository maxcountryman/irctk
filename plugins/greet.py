from gevent import sleep
from random import choice

from core.hooks import *

@subscribe('join') # someone joined
def greet(bot, parsed_event):
    '''Sends a message when a user JOINs.'''

    greeting = ['Why hello there,', 'Welcome,', 'Hi,', 'Nice to see you,']
    greet = choice(greeting)
    sleep(1.3)

    if parsed_event.nick != bot.irc.nick:
        bot.irc.msg(parsed_event.trailing, '{0} {1}'.format(greet, parsed_event.nick))
