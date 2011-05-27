'''A plugin for Google's search API. Returns the first result, i.e. 
"Feeling Lucky?"'''

from voxbot.bot import Plugin
from voxbot.utils import bitly, unescape

import urllib
import urlparse
import socket
import json

socket.setdefaulttimeout(5)

class Google(Plugin):
    '''usage: ^google [args]'''
    
    def __init__(self, bot):
        super(Google, self).__init__(bot)
        self._search()
    
    @Plugin.command('^google')
    def _search(self, cmd=None, args=None):
        query = args
        
        url = urlparse.urlunsplit(
                (
                    'http', 
                    'ajax.googleapis.com', 
                    '/ajax/services/search/web', 
                    'v=1.0&q={0}'.format(query), 
                    None,
                    )
                )
        
        results = urllib.urlopen(url)
        results = json.loads(results.read())['responseData']['results']
        
        if not results:
            error = 'Request error: no results'
            self.reply(error)
            self.logger.warning(error)
        else:
            url = urllib.unquote(results[0]['url'])
            url = bitly.shorten(url)['url']
            title = unescape(results[0]['titleNoFormatting'])
            lucky = title + ' -- ' + url 
            self.reply(lucky) 
