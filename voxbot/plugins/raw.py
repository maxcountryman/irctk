from voxbot.bot import Plugin

class Raw(Plugin):
    '''usage: ^raw [args] (owners only)'''
    
    def __init__(self, bot):
        super(Raw, self).__init__(bot)
        self._send_raw()
    
    @Plugin.command('^raw')
    def _send_raw(self, *args):
        if self.user in self.owners:
            s = args[-1] 
            self.bot._send(s)
