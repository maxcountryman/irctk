from voxbot.bot import Plugin

class Action(Plugin):
    '''usage: ^me (channel) [action]'''
    
    def __init__(self, bot):
        super(Action, self).__init__(bot)
        self._send_action()
    
    @Plugin.command('^me')
    def _send_action(self, *args, **kwargs):
        args = kwargs.get('args', '')
        
        if not args:
            return
        
        s = args 
        if s.startswith('#'):
            args = s[s.find('#'):].split(' ', 1)[-1]
            chan = s[s.find('#'):].split(' ', 1)[0]
            self.reply(args, channel=chan, action=True)
        else:
            s = chr(1) + 'ACTION ' + s + chr(1)
            self.reply(s)
