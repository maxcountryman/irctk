from voxbot.bot import Plugin

import urllib
import urlparse
import socket

socket.setdefaulttimeout(30)

class Python(Plugin):
    '''usage: ^python [python] (parsing at eval.appspot.com)'''
    
    def __init__(self, bot):
        super(Python, self).__init__(bot)
        self._parse_python()
    
    @Plugin.command('^python')
    def _parse_python(self, *args, **kwargs):
        query = kwargs.get('args', '')
        query = urllib.quote(query)
        url = urlparse.urlunsplit(
                (
                    'http', 
                    'eval.appspot.com', 
                    'eval', 
                    'statement={0}'.format(query), 
                    ''
                    )
                )
        print url
        try:
            response = urllib.urlopen(url).read()
        except Exception, e:
            return self.reply(str(e))
        if not response.startswith('Traceback (most recent call last):'):
            self.reply(response)
        else:
            response = response.splitlines()
            self.reply(response[-1])
