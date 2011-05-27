from voxbot.bot import Plugin

class Uno(Plugin):
    '''usage: ^uno blabla'''

    def __init__(self, bot):
        super(Uno, self).__init__(bot)
        self._start_game()

    @Plugin.command('^uno')
    def _start_game(self, *args):
        self.reply("Uno game starting")

