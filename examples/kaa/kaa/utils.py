from kaa import bot
from kaa.wikipedia import wiki_re
from kaa.youtube import youtube_re

from StringIO import StringIO
from itertools import groupby
from lxml import html

import json
import sqlite3
import re

import requests

BITLY_LOGIN = bot.config['BITLY_LOGIN']
BITLY_KEY = bot.config['BITLY_KEY']


def get_db_connection(name=None):
    if name is None:
        name = '{0}.{1}.db'.format(bot.config['NICK'], bot.config['SERVER'])
    return sqlite3.connect(name, timeout=10)


def shortener(url):
    api_url = 'https://api-ssl.bitly.com/v3/shorten'
    r = requests.get(api_url,
                     params=dict(longUrl=url,
                     format='json',
                     login=BITLY_LOGIN,
                     apiKey=BITLY_KEY))
    data = json.loads(r.content)['data']
    if data:
        return data['url']
    return 'error shortening url'


def find_urls(message, urls=None):
    message = message + ' '
    extra = None

    if urls is None:
        urls = []

    if 'http' in message:
        url, extra = message[message.index('http'):].split(' ', 1)
        urls.append(url)
    elif 'www.' in message:
        url, extra = message[message.index('www.'):].split(' ', 1)
        urls.append(url)

    if extra:
        find_urls(extra)

    return urls


@bot.command('.')
@bot.command('help')
@bot.command
def usage(context):
    '''.usage <plugin>'''
    plugin = context.args
    if plugin:
        for p in bot.config['PLUGINS']:
            if plugin == p['hook']:
                return p['funcs'][0].__doc__
    else:
        p = [(p['hook'], p['funcs']) for p in bot.config['PLUGINS']]
        p.sort(key=lambda t: t[1])
        result = []
        # group by function
        for k, v in groupby(p, key=lambda t: t[1]):
            grouped = [v[0] for v in v]
            grouped[0] = '\x02' + grouped[0] + '\x02'
            if len(grouped) > 1:
                # shortcuts/secondary
                for i, hook in enumerate(grouped[1:]):
                    grouped[i+1] = '[' + grouped[i+1] + ']'
            result.append(' '.join(grouped))
        result.sort()
        p = ', '.join(result)
        return 'Plugins currently loaded: ' + p


@bot.command
def raw(context):
    '''.raw <command>'''
    if not context.line['hostmask'] in bot.config.get('ADMINS', []):
        return
    if context.args:
        command = context.args.split(' ', 1)[0]
        args = list(context.args.split(' ', 1)[-1])
        bot.irc.send_command(command, args)
    else:
        return raw.__doc__


@bot.event('PRIVMSG')
def shorten(context):
    message = context.line['message']
    schemes = ('http://', 'https://', 'www.')
    contains_url = True in map(lambda scheme: scheme in message, schemes)

    if not contains_url:
        return

    wiki = re.search(wiki_re, message)
    if wiki is not None:
        return

    youtube = re.search(youtube_re, message)
    if youtube is not None:
        return

    if 'bit.ly' in message or 'i.imgur.com' in message:
        return

    urls = find_urls(message)

    titles_and_urls = []
    for url in urls:
        try:
            r = requests.get(url)
        except Exception, e:
            bot.logger.warning('Opening {url} raised {error}'.format(url=url,
                                                                     error=e))
            continue

        parsed_page = html.parse(StringIO(r.content))
        title = parsed_page.find('.//title')
        url = shortener(url)

        if url is None:
            continue
        elif title is not None:
            title = title.text.strip()
            titles_and_urls.append(title + ' - ' + url)
        else:
            titles_and_urls.append(url)

    for result in titles_and_urls:
        bot.reply(result, context.line)
