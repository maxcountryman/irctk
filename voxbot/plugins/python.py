from voxbot.bot import Plugin

import urllib
import urlparse
import socket

socket.setdefaulttimeout(5)

class Python(Plugin):
    '''usage: ^python [python] (parsing at eval.appspot.com)'''
    
    def __init__(self, bot):
        super(Python, self).__init__(bot)
        self._send_python()
    
    @Plugin.command('^python')
    def _send_python(self, *args):
        query = args[-1] 
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
        try:
            response = urllib.urlopen(url).read().splitlines()
        except Exception, e:
            return self.reply(str(e))
        if not response[0] == 'Traceback (most recent call last):':
            self.reply(response[0])
        else:
            self.reply(response[-1])
