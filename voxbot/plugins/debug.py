'''Simple debug plugin. Returns the command and args or command and command,
as a tuple.
'''

from voxbot.bot import Plugin
from voxbot.utils import rainbowify

class Debug(Plugin):
    '''usage: ^debug [args]'''
    
    def __init__(self, bot):
        super(Debug, self).__init__(bot)
        self._rainbow()
        self._none()
        self._debug()
    
    @Plugin.command('^rainbow')
    def _rainbow(self, *args, **kwargs):
        cmd = kwargs.get('cmd', '')
        args = kwargs.get('args', '')
        
        if not args:
            s = rainbowify('Where\'s me gold?')
            self.reply(s)
        else:
            s = rainbowify(args)
            self.reply(s)
    
    @Plugin.command('^debug')
    def _none(self, cmd=None, args=None):
        self.reply('thread test')

    @Plugin.command('^debug')
    def _debug(self, cmd=None, args=None):
        self.reply('cmd: {0} : args: {1}'.format(cmd, args))
        #self.reply('', channel='#voxinfinitus', action=True)
