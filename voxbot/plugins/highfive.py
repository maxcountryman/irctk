from voxbot.bot import Plugin

class HighFive(Plugin):
    '''usage: automatic'''
    
    def __init__(self, bot):
        super(HighFive, self).__init__(bot)
        self._respond()
    
    def _respond(self):
        if self.msgs.startswith(chr(1) + 'ACTION high fives {0}'.format(self.bot.nick)):
            self.bot.does(self.sender, 'high fives ' + self.user)

