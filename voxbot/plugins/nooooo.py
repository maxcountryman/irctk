from voxbot.bot import Plugin

class Nooooo(Plugin):
    '''usage: ^no'''
    
    def __init__(self, bot):
        super(Nooooo, self).__init__(bot)
        self._debug()
    
    @Plugin.command('^no')
    def _debug(self, cmd, args):
        self.reply('http://bit.ly/k5wwyS')
