from voxbot.bot import Plugin

import urllib

class Yeah(Plugin):
    '''usage: ^yeah'''
    
    def __init__(self, bot):
        super(Yeah, self).__init__(bot)
        self._ya()
    
    @Plugin.command('^yeah')
    def _ya(self, *args):
        self.reply('http://bit.ly/klcUEq')
