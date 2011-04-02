'''Plugin for radio reddit's API.'''

from voxbot.bot import Plugin
from voxbot.utils import bitly

import urllib
import json

class RadioReddit(Plugin):
    '''usage: ^np [stream]; ^status [stream]; ^info'''
    
    def __init__(self, bot):
        super(RadioReddit, self).__init__(bot)
        self._np()
        self._status()
        self._info()
        
    @Plugin.command('^np')
    def _np(self, *args):
        
        genres = ['rock', 'electronic', 'hiphop']
        if args[-1] in genres:
            json_results = \
                urllib.urlopen(
                    'http://radioreddit.com/api/{0}/status.json'.format(args[-1])
                    )
        elif args[0] == args[-1]:
            json_results = \
                urllib.urlopen('http://radioreddit.com/api/status.json')
        results = json.loads(json_results.read())['songs']['song'][0]
        url = str(results['reddit_url'])
        result = \
            chr(2) + results['title'] + chr(2) \
            + ' -- ' + \
            results['artist'] \
            + ' ' + \
            '(Redditor: {0})'.format(results['redditor']) \
            + ' ' + \
            bitly.shorten(url)['url']
        if args[0] != args[-1]:
            now_playing = \
                    'Now playing on the {0} stream: '.format(args[-1]) + result
            self.reply(now_playing)
        else:
            now_playing = 'Now playing on Redio Reddit: ' + result
            self.reply(now_playing)
    
    @Plugin.command('^status')
    def _status(self, *args):
        
        genres = ['rock', 'electronic', 'hiphop']
        if args[-1] == 'main':
            json_results = \
                urllib.urlopen(
                    'http://radioreddit.com/api/status.json'
                    )
            result = json.loads(json_results.read())['listeners']
            listeners = 'There are {0} listeners currently'.format(result)
            self.reply(listeners)
        elif args[-1] in genres:
            json_results = \
                urllib.urlopen(
                    'http://radioreddit.com/api/{0}/status.json'.format(args[-1])
                    )
            result = json.loads(json_results.read())['listeners']
            listeners = 'There are {0} listeners currently'.format(result)
            self.reply(listeners)
        else: 
            main_results = \
                    urllib.urlopen(
                            'http://radioreddit.com/api/status.json'
                            )
            rock_results = \
                    urllib.urlopen(
                            'http://radioreddit.com/api/rock/status.json'
                            )
            electronic_results = \
                    urllib.urlopen(
                            'http://radioreddit.com/api/electronic/status.json'
                            )
            hiphop_results = \
                    urllib.urlopen(
                            'http://radioreddit.com/api/hiphop/status.json'
                            )
            main = int(json.loads(main_results.read())['listeners'])
            rock = int(json.loads(rock_results.read())['listeners'])
            electronic = int(json.loads(electronic_results.read())['listeners'])
            hiphop = int(json.loads(hiphop_results.read())['listeners'])
            result = main + rock + electronic + hiphop
            listeners = 'There are {0} listeners currently'.format(result)
            self.reply(listeners)
            
    @Plugin.command('^info')
    def _info(self, *args):
        info = 'Radio Reddit information: ' + \
                'http://radioreddit.com/about ' + \
                'http://radioreddit.com/faq'
        self.reply(info)

