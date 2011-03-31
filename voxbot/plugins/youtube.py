from voxbot.bot import Plugin
from voxbot.utils import bitly

import urllib
import urlparse
import socket
import json

socket.setdefaulttimeout(5)

class Youtube(Plugin):
    '''usage: ^youtube [search terms]'''
    
    def __init__(self, bot):
        super(Youtube, self).__init__(bot)
        self._search()
    
    @Plugin.command('^youtube')
    def _search(self, *args):
        query = args[-1]
        
        url = urlparse.urlunsplit(
                (
                    'http', 
                    'gdata.youtube.com', 
                    '/feeds/api/videos', 
                    'v=2&alt=jsonc&q={0}'.format(query), 
                    ''
                    )
                )
        
        results = urllib.urlopen(url)
        results = json.loads(results.read())['data']['items'][0]
        
        if not results:
            self.reply('Request error: no results')
        else:
            url = 'http://www.youtube.com/watch?v={0}'.format(results['id'])
            url = bitly.shorten(url)['url']
            title = results['title']
            desc = results['description']
            lucky = title + ' -- ' + desc + ' -- ' + url
            self.reply(lucky)
