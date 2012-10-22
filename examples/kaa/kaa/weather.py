# ported from skybot

from kaa import bot
from kaa.utils import get_db_connection

from urllib import quote

import requests
import json

WUNDERGROUND_API_URL = 'http://api.wunderground.com/api/'
WUNDERGROUND_API_KEY = '7b1620be0fa1b756'
WUNDERGROUND_CONDITIONS = (WUNDERGROUND_API_URL + WUNDERGROUND_API_KEY
        + '/conditions/q/')
WUNDERGROUND_FORECAST = (WUNDERGROUND_API_URL + WUNDERGROUND_API_KEY
        + '/forecast/q/')


@bot.command('w')
@bot.command
def weather(context):
    '.weather <location>'

    db = get_db_connection()

    location = context.args
    hostmask = context.line['prefix'].split('!', 1)[-1]

    db.cursor().execute('create table if not exists ' \
                        'weather(host primary key, loc)')

    if not location:
        location = \
            db.cursor().execute('select loc from weather where host=lower(?)',
                                (hostmask,)).fetchone()
        if not location:
            return weather.__doc__
        location = location[0]

    r = requests.get(WUNDERGROUND_CONDITIONS + quote(location) + '.json')
    info = json.loads(r.content).get('current_observation', None)

    if info is None:
        return 'Location not found or multiple cities match'

    r = requests.get(WUNDERGROUND_FORECAST + quote(location) + '.json')
    forecast = json.loads(r.content)
    high = forecast[u'forecast']['simpleforecast']['forecastday'][0]['high']
    temperature_high = high['fahrenheit'] + ' F (' + high['celsius'] + ' C)'
    temperature_high = 'High: ' + temperature_high
    info['temperature_high'] = temperature_high

    if location:
        db.execute('insert or replace into weather(host, loc) values (?,?)',
                   (hostmask, location))
        db.commit()

    return ('{display_location[city]}: {weather}, {temperature_string}, '
            '{temperature_high} Humidity: {relative_humidity}, '
            'Wind: {wind_string}.'.format(**info))
