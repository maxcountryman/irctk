import gevent

from core.irc import Irc
from core.dispatcher import *

@subscribe('ping')
def ping(bot, args):
    bot.cmd('PONG', args[1])

@subscribe('notice')
def start(bot, args):
    bot.cmd('USER', ['pybot', '3', '*', 'Python Bot'])
    bot.cmd('NICK', [bot.nick])

@subscribe('396')
def join(bot, args):
    for channel in bot.channels:
        bot.cmd('JOIN', [channel])

class Bot(Irc):
    def __init__(self, server, nick, port=6667, ssl=False, channels=[]):
        self.channels = channels
        jobs = [gevent.spawn(Irc.__init__, self, server, nick, port, ssl), gevent.spawn(self._parse_events)]
        gevent.joinall(jobs)
    
    def _parse_events(self):
        while True:
            event = self.events.get()
            dispatch(self, event)

vox = Bot('irc.voxinfinitus.net', 'bot___', channels=['#voxinfinitus'])
