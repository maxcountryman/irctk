import gevent
from gevent import sleep

from core.irc import Irc
from core.hooks import *

@subscribe('ping')
def ping(bot, args):
    bot.irc.cmd('PONG', args[1])

@subscribe('396') # finished connecting, we can join
def join(bot, args):
    for channel in bot.channels:
        bot.irc.cmd('JOIN', [channel])

@subscribe('join') # someone joined
def greet(bot, args):
    channel = str(args[1])
    chn = channel[1:-1]
    c = chn[1:-1]
    sleep(1.5)
    bot.irc.msg(c, 'You must die..human.')

@subscribe('quit') # someone quit
def greet(bot, args):
    channel = str(args[1])
    chn = channel[1:-1]
    c = chn[1:-1]
    sleep(1.5)
    bot.irc.msg(c, 'Another "victim"...')

class Bot(object): # don't inherit from Irc, keeps things flat :D
    def __init__(self, server, nick, port=6667, ssl=False, channels=[]):
        self.channels = channels
        self.irc = Irc(server, nick, port, ssl)
        self._dispatch_events()

    def _dispatch_events(self):
        while True:
            event = self.irc.events.get()
            dispatch(self, event)

badass_bot = Bot('irc.voxinfinitus.net', 'Kaa', 6697, True, channels=['#voxinfinitus','#landfill'])
