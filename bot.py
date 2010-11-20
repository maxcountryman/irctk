import gevent
from gevent import sleep

from core.irc import Irc
from core.hooks import *

@subscribe('ping')
def ping(bot, parsed):
    bot.irc.cmd('PONG', parsed.trailing)

@subscribe('396') # finished connecting, we can join
def join(bot, parsed):
    for channel in bot.channels:
        bot.irc.cmd('JOIN', channel, prefix=False)

@subscribe('join') # someone joined
def greet(bot, parsed):
    sleep(1.3)
    if parsed.nick != bot.irc.nick:
        bot.irc.msg(parsed.trailing, 'Why hello there.. {0}'.format(parsed.nick))

#@subscribe('part') # someone parted
#def quit(bot, parsed):
#    sleep(.6)
#    bot.irc.msg(parsed.trailing, 'We will take care of {0} later..'.format(parsed.nick))

class Bot(object): # don't inherit from Irc, keeps things flat :D
    '''Instantiates Irc, loops over `Irc.conn.iqueue` and sends data through 
       `dispatch()`. Pass True if using SSL/TLS.
    '''

    def __init__(self, server, nick, port=6667, ssl=False, channels=[]):
        self.channels = channels
        self.irc = Irc(server, nick, port, ssl)
        self._dispatch_events()

    def _dispatch_events(self):
        while True: # magic loop
            event = self.irc.events.get()
            dispatch(self, event)

badass_bot = Bot('irc.voxinfinitus.net', 'Kaa', channels=['#voxinfinitus','#landfill'])
