from voxbot.bot import Plugin
from voxbot.utils import bitly

MIN_LEN = 60

class Bitly(Plugin):
    '''usage: automatic'''
    
    def __init__(self, bot):
        super(Bitly, self).__init__(bot)
        self._shorten()
    
    @Plugin.command('http://')
    def _shorten(self, *args):
        url = args[-1]
        if 'bit.ly' in url or '.' not in url:
            return
        url = bitly.shorten(url)['url']
        if not len(self.msgs) >= MIN_LEN:
            return
        self.reply(url)
