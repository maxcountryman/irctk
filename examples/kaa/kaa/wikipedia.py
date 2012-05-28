# ported from skybot

from kaa import bot

from urllib import quote
from StringIO import StringIO

from lxml import etree

import re

import requests

api_prefix = 'http://en.wikipedia.org/w/api.php'
search_url = api_prefix + '?action=opensearch&format=xml'

paren_re = re.compile('\s*\(.*\)$')


@bot.command('wi')
@bot.command('wiki')
@bot.command
def wikipedia(context):
    '''.wikipedia <query>'''
    query = quote(context.args)
    r = requests.get(search_url, params=dict(search=query))
    data = etree.fromstring(StringIO(r.text))

    ns = '{http://opensearch.org/searchsuggest2}'
    items = data.findall(ns + 'Section/' + ns + 'Item')

    if items == []:
        if data.find('error') is not None:
            return 'error: {code}: {info}'.format(data.find('error').attrib)
        else:
            return 'no results found'

    def extract(item):
        return [item.find(ns + e).text for e in ('Text', 'Description', 'Url')]

    title, desc, url = extract(items[0])

    if 'may refer to' in desc:
        title, desc, url = extract(items[1])

    title = paren_re.sub('', title)

    if title.lower() not in desc.lower():
        desc = title + desc

    desc = re.sub('\s+', ' ', desc).strip()  # remove excess spaces

    if len(desc) > 300:
        desc = desc[:300] + '...'

    return '{0} -- {1}'.format(desc, quote(url, ':/'))
