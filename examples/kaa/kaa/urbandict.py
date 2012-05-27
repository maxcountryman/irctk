from kaa import bot

from urllib import quote

import json

import requests

LINE_LIMIT = 1000


@bot.command('u')
@bot.command
def urbandict(context):
    url ='http://www.urbandictionary.com/iphone/search/define?term={0}'
    url = url.format(quote(context.args))
    r = requests.get(url)
    data = json.loads(r.content)
    if not data['list'][0].get('definition'):
        return 'no results found'
    data = data['list'][0]['definition'].splitlines()
    data = ' '.join(data)
    return data[:LINE_LIMIT]
