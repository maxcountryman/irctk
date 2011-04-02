'''Simple debug plugin. Returns the command and args or command and command,
as a tuple.
'''

from voxbot.bot import Plugin

class Debug(Plugin):
    '''usage: ^debug [args]'''
    
    def __init__(self, bot):
        super(Debug, self).__init__(bot)
        self._debug()
    
    @Plugin.command('^debug')
    def _debug(self, *args):
        self.reply(str(args))
