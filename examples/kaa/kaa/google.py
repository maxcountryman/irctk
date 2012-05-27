from kaa import bot
from kaa.utils import shortener

from urllib import quote

import json
import requests

URL = ('http://ajax.googleapis.com/ajax/services/search/'
       '{0}?v=1.0&safe=off&q={1}')


def search(query, kind='web'):
    r = requests.get(URL.format(kind, quote(query)))
    data = json.loads(r.content)
    return data


@bot.command('g')
@bot.command
def google(context):
    data = search(context.args)
    if not data['responseData']['results']:
        return 'no results found'
    first_result = data['responseData']['results'][0]
    ret = first_result['titleNoFormatting'] + \
          ' - ' + shortener(first_result['unescapedUrl'])
    return ret


@bot.command
def gis(context):
    data = search(context.args, 'images')['responseData']['results']
    if not data:
        return 'no images found'
    return data[0]['unescapedUrl']
