from voxbot.bot import Plugin

class Beer(Plugin):
    '''usage: ^beer'''
    
    def __init__(self, bot):
        super(Beer, self).__init__(bot)
        self._a_cold_one()
    
    @Plugin.command('^beer')
    def _a_cold_one(self, *args):
        self.reply(chr(1) + 'ACTION ' + 'hands {0} a cold one'.format(self.user) + chr(1))
