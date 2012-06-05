# ported from skybot

from kaa import bot
from kaa.utils import get_db_connection

from urllib import quote
from lxml import etree

import requests


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
                                (hostmask,)).fetchone()[0]
        if not location:
            return weather.__doc__

    url = 'http://www.google.com/ig/api?weather=' + quote(location)
    r = etree.fromstring(requests.get(url).content)
    r = r.find('weather')

    if r.find('problem_cause') is not None:
        return ('Couldn\'t retrieve weather for {0}.'.format(location))

    info = dict((e.tag, e.get('data')) for e in r.find('current_conditions'))
    info['city'] = r.find('forecast_information/city').get('data')
    info['high'] = r.find('forecast_conditions/high').get('data')
    info['low'] = r.find('forecast_conditions/low').get('data')

    if location:
        db.execute('insert or replace into weather(host, loc) values (?,?)',
                   (hostmask, location))
        db.commit()

    return ('{city}: {condition}, {temp_f}F/{temp_c}C (H:{high}F, L:{low}), '
            '{humidity}, {wind_condition}.'.format(**info))
