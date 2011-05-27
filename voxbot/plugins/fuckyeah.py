from voxbot.bot import Plugin

import urllib

class FuckYeah(Plugin):
    '''usage: ^fuckyeah [something]'''
    
    def __init__(self, bot):
        super(FuckYeah, self).__init__(bot)
        self._fuq_ya()
    
    @Plugin.command('^fuckyeah')
    def _fuq_ya(self, cmd, args):
        if args:
            query = urllib.quote(args)
            self.reply('http://fuckyeahnouns.com/{0}'.format(query))
