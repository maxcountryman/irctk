#!/usr/bin/env python
import gevent

from voxbot import bot, settings

jobs = [gevent.spawn(bot, settings)]
try:
    gevent.joinall(jobs)
finally:
    gevent.killall(jobs)

class MyPlugin(Plugin):
    '''usage: ^my_command [args]'''
    
    def __init__(self, bot):
        super(MyPlugin, self).__init__(bot)
        self.my_command()
    
    @Plugin.command('^my_command')
    def my_command(self, *args):
        if args[0] != args[-1]:
            self.reply(str(args[-1]))
