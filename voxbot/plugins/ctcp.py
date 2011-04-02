'''Basic CTCP implementation.'''

from voxbot.bot import Plugin

class Ctcp(Plugin):
    '''usage: automatic'''
    
    def __init__(self, bot):
        super(Ctcp, self).__init__(bot)
        self._query()
        self._ctcp()
    
    @Plugin.command('^query')
    def _query(self, *args):
        target = args[-1]
        self.bot.ctcp_send(target, 'PING')
    
    def _ctcp(self):
        args = self.msgs
        if args.startswith(chr(1)) and 'PING' in args:
            ping = args[args.find('PING'):].split(' ', 1)[-1]
            ping = 'PING ' + ping
            self.bot.ctcp_reply(self.user, ping)
        elif args.startswith(chr(1)) and 'USERINFO' in args:
            info = 'Kaa the Python'
            self.bot.ctcp_reply(self.user, info)
        elif args.startswith(chr(1)) and 'TIME' in args:
            time = 'Time to get a new watch'
            self.bot.ctcp_reply(self.user, time)

