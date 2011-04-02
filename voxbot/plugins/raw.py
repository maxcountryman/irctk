'''A plugin that allows owners to send commands in raw to the server.'''

from voxbot.bot import Plugin

class Raw(Plugin):
    '''usage: ^raw [args] (owners only)'''
    
    def __init__(self, bot):
        super(Raw, self).__init__(bot)
        self._send_raw()
    
    @Plugin.command('^raw')
    def _send_raw(self, *args):
        if not self.user in self.owners:
            return self.reply('You do not have proper privileges')
        else: 
            s = args[-1] 
            self.bot._send(s)
