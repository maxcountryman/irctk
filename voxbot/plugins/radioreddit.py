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
    def _np(self, cmd=None, args=None):
        
        genres = ['rock', 'electronic', 'hiphop', 'random']
        if args in genres:
            json_results = \
                urllib.urlopen(
                    'http://radioreddit.com/api/{0}/status.json'.format(args)
                    )
        elif not args:
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
        if args:
            now_playing = \
                    'Now playing on the {0} stream: '.format(args[-1]) + result
            self.reply(now_playing)
        else:
            now_playing = 'Now playing on Radio Reddit: ' + result
            self.reply(now_playing)
    
    @Plugin.command('^status')
    def _status(self, cmd=None, args=None):
        
        url = 'http://radioreddit.com/api/'
        genres = ['rock', 'electronic', 'hiphop', 'random']
        
        if not args:
            urls = [url + '{0}/status.json'.format(genre) for genre in genres]
            urls.append(url + 'status.json')
            i = 0
            for url in urls:
                i += int(json.loads(urllib.urlopen(url).read())['listeners'])
            listeners = 'There are {0} listeners currently'.format(i)
            return self.reply(listeners)
        elif args == 'main':
            status = urllib.urlopen(url + 'status.json')
        elif args in genres:
            status = \
                urllib.urlopen(url + '{0}/status.json'.format(args))
        status = json.loads(status.read())['listeners']
        listeners = 'There are {0} listeners currently'.format(status)
        self.reply(listeners)
            
    @Plugin.command('^info')
    def _info(self, *args):
        info = 'Radio Reddit information: ' + \
                'http://radioreddit.com/about ' + \
                'http://radioreddit.com/faq ' + \
                'http://radioreddit.com/uploading ' + \
                'http://radioreddit.com/content/stream-schedules'
        self.reply(info)

