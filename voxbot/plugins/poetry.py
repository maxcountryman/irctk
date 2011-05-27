from voxbot.bot import Plugin

class Poetry(Plugin):
    '''usage: ^poetry'''
    
    def __init__(self, bot):
        super(Poetry, self).__init__(bot)
        self._debug()
    
    @Plugin.command('^poetry')
    def _debug(self, *args):
        self.reply('http://www.youtube.com/watch?v=G2zDW9me-IY')
