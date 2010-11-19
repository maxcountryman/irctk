import gevent
from gevent import sleep

from core.irc import Irc
from core.hooks import *

@subscribe('ping')
def ping(bot, parsed):
    bot.irc.cmd('PONG', parsed.command_args[0][1:])

@subscribe('396') # finished connecting, we can join
def join(bot, parsed):
    for channel in bot.channels:
        bot.irc.cmd('JOIN', channel, prefix=False)

@subscribe('join') # someone joined
def greet(bot, parsed):
    bot.irc.msg(parsed.command_args[0], 'You must die..human.')

@subscribe('quit') # someone quit
def quitted(bot, parsed):
    bot.irc.msg(parsed.command_args[0], 'Another "victim"...')

class Bot(object): # don't inherit from Irc, keeps things flat :D
    def __init__(self, server, nick, port=6667, ssl=False, channels=[]):
        self.channels = channels
        self.irc = Irc(server, nick, port, ssl)
        self._dispatch_events()

    def _dispatch_events(self):
        while True:
            event = self.irc.events.get()
            dispatch(self, event)

badass_bot = Bot('irc.voxinfinitus.net', 'Kaa_', channels=['#voxinfinitus','#landfill'])
