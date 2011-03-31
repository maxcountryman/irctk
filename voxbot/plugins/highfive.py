from voxbot.bot import Plugin

class Highfive(Plugin):
    '''usage: automatic'''
    
    def __init__(self, bot):
        super(Highfive, self).__init__(bot)
        self._respond()
    
    @Plugin.command('^ACTION high fives {0}'.format(self.bot.nick))
    def _respond(self):
        self.bot.does(self.sender, 'high fives ' + self.user)

