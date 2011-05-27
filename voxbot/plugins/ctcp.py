'''Basic CTCP implementation.'''

from voxbot.bot import Plugin

import time

class Ctcp(Plugin):
    '''usage: automatic'''
    
    def __init__(self, bot):
        super(Ctcp, self).__init__(bot)
        self._query()
        self._ctcp_ping()
        self._ctcp_time()
        self._ctcp_userinfo()
        self._ctcp_version()
        self._ctcp_source()
        self._ctcp_cake()
    
    @Plugin.command('^query')
    def _query(self, *args, **kwargs):
        target = kwargs.get('args', '').split(' ', 1)[0]
        self.bot.ctcp_send(target, 'PING')
    
    def _ctcp_ping(self):
        args = self.msgs
        if args.startswith(chr(1)) and 'PING' in args:
            ping = args[args.find('PING'):].split(' ', 1)[-1]
            ping = 'PING ' + ping
            self.bot.ctcp_reply(self.user, ping)
    
    def _ctcp_time(self):
        args = self.msgs
        if args.startswith(chr(1)) and 'TIME' in args:
            self.bot.ctcp_reply(self.user, time.ctime())
    
    def _ctcp_userinfo(self):
        args = self.msgs
        if args.startswith(chr(1)) and 'USERINFO' in args:
            self.bot.ctcp_reply(self.user, 'USERINFO')
    
    def _ctcp_version(self):
        args = self.msgs
        if args.startswith(chr(1)) and 'VERSION' in args:
            self.bot.ctcp_reply(self.user, 'Kaa the Python')
    
    def _ctcp_source(self):
        args = self.msgs
        if args.startswith(chr(1)) and 'SOURCE' in args:
            self.bot.ctcp_reply(
                    self.user, 
                    'https://github.com/maxcountryman/kaa'
                    )
    
    def _ctcp_cake(self):
        args = self.msgs
        if args.startswith(chr(1)) and 'CAKE' in args:
            self.bot.ctcp_reply(self.user, 'LIE')


