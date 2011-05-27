from voxbot.bot import Plugin
from voxbot.utils import bitly

import lxml.html

MIN_LEN = 60

class Bitly(Plugin):
    '''usage: automatic'''
    
    def __init__(self, bot):
        super(Bitly, self).__init__(bot)
        self._shorten()
        self._title()
        
    @Plugin.command('http://', is_in=True)
    def _title(self, cmd, args):
        url = cmd
        url = lxml.html.parse(url)
        title = url.find('.//title').text
        self.reply(title)
        
    @Plugin.command('http://', is_in=True)
    def _shorten(self, cmd, args):
        print(cmd)
        url = cmd 
        if not url or ('bit.ly' in url) or ('.' not in url):
            print('shit shit')
            return
        url = bitly.shorten(url)['url']
        if not len(self.msgs) >= MIN_LEN:
            return
        self.reply(url)
