from voxbot.bot import Plugin

class Drinks(Plugin):
    '''usage: ^beer or ^wine or ^scotch'''
    
    def __init__(self, bot):
        super(Drinks, self).__init__(bot)
        self._a_cold_one()
        self._fine_vines()
        self._gentlemens_drink()
        self._spiked_aqua()
        self._candy_land()
        self._ten_tacos()
    
    @Plugin.command('^ganja')
    def _ten_tacos(self, cmd, args):
        self.reply('hands {0} a joint'.format(self.user), action=True)
    
    @Plugin.command('^lsd')
    def _candy_land(self, cmd, args):
        self.reply('hands {0} some blotter'.format(self.user), action=True)
    
    @Plugin.command('^beer')
    def _a_cold_one(self, cmd, args):
        if args:
            self.reply('hands {0} a cold one'.format(args), action=True)
        else:
            self.reply('hands {0} a cold one'.format(self.user), action=True)
    
    @Plugin.command('^wine')
    def _fine_vines(self, cmd, args):
        self.reply('hands {0} a glass'.format(self.user), action=True)
    
    @Plugin.command('^scotch')
    def _gentlemens_drink(self, cmd, args):
        self.reply('hands {0} a scotch on the rocks'.format(self.user), action=True)
    
    @Plugin.command('^water')
    def _spiked_aqua(self, cmd, args):
        self.reply('hands {0} an electric water'.format(self.user), action=True)
