from voxbot.bot import Plugin
from voxbot.utils import bitly
from wordnik import Wordnik

import urllib
import urlparse
import socket
import json

socket.setdefaulttimeout(5)

class Dict(Plugin):
    '''usage: ^dict [word]'''
    
    def __init__(self, bot):
        super(Dict, self).__init__(bot)
        api_key = 'fe5551798340efd8e52320db20103aa284241a2ccaea01d6f'
        user = 'voxinfinitus'
        pw = 'v0x'
        self._dict = Wordnik(api_key, user, pw)
        self._define()
    
    @Plugin.command('^dict')
    def _define(self, *args, **kwargs):
        query = kwargs.get('args', '')
        results = self._dict.word_get_definitions('{0}'.format(query), limit=1)
        results = json.loads(results)
        
        if not results:
            error = 'Request error: no results'
            self.reply(error)
            self.logger.warning(error)
        else:
            defi = results[0]['text']
            part = results[0]['partOfSpeech']
            word = results[0]['word']
            result = \
                    chr(2) + word + chr(2) + \
                    ' -- ' + \
                    part + \
                    ' -- ' + \
                    defi
            self.reply(result)
