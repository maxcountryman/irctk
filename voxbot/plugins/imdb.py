from voxbot.bot import Plugin
from voxbot.utils import bitly

import urllib
import json
import socket

socket.setdefaulttimeout(15)

class Imdb(Plugin):
    '''usage: ^imbd [search terms]'''
    
    def __init__(self, bot):
        super(Imdb, self).__init__(bot)
        self._send_response()
    
    @Plugin.command('^imdb')
    def _send_response(self, cmd=None, args=None):
            query = args 
            query = urllib.quote(query)
            url = 'http://www.imdbapi.com/?t={0}'.format(query)
            result = json.load(urllib.urlopen(url))
            
            if result['Response'] == 'True':
                film_id = result['ID']
                film_url = 'http://www.imdb.com/title/' + film_id
                film_url = bitly.shorten(film_url)['url']
                title = result['Title']
                desc = result['Plot']
                self.bot.msg(
                        self.sender, 
                        title + ' -- ' + desc + ' -- ' + film_url
                        )
