# coding: utf-8 -*-.
'''Weather plugin'''

from voxbot.bot import Plugin
from voxbot.utils import bitly

import urllib
import urlparse
import socket
import json

socket.setdefaulttimeout(5)

class Weather(Plugin):
    '''usage: ^weather [city]'''
    
    def __init__(self, bot):
        super(Weather, self).__init__(bot)
        self._search()
    
    @Plugin.command('^weather')
    def _search(self, cmd, args):
        city = args
       
        url = urlparse.urlunsplit(
                (
                    'http', 
                    'free.worldweatheronline.com', 
                    '/feed/weather.ashx', 
                    'q={0}&format=json&num_of_days=2&key=4b0e5c9a1f092212110404'.format(city), 
                    None,
                    )
                )
        
        results = urllib.urlopen(url)
        results = json.loads(results.read())['data']
        city = results['request'][0]['query'].split(',', 1)[0]
        results = results['current_condition'][0]
        
        if not results:
            error = 'Request error: no results'
            self.reply(error)
            self.logger.warning(error)
        else:
            wind_speed = 'at ' + results['windspeedMiles'] + ' mph,'
            wind_dir = 'wind ' + results['winddir16Point']
            temp = results['temp_F'] + u'°F,'
            desc = results['weatherDesc'][0]['value'] + ','
            time = results['observation_time'] + ':'
            city = '{0}, current conditions:'.format(city)
            humd = results['humidity'] + '% humidity'
            report = ' '.join([city, temp, desc, wind_dir, wind_speed, humd])
            self.reply(report)
