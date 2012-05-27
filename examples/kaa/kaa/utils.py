from kaa import bot

from itertools import groupby
from lxml import html

import json
import sqlite3

import requests

BITLY_LOGIN = bot.config['BITLY_LOGIN']
BITLY_KEY = bot.config['BITLY_KEY']


def get_db_connection(name=None):
    if name is None:
        name = '{0}.{1}.db'.format(bot.config['NICK'], bot.config['SERVER'])
    return sqlite3.connect(name, timeout=10)


def shortener(url):
    url = 'https://api-ssl.bitly.com/v3/shorten'
    r = requests.get(url, params=dict(longUrl=url,
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
        p.sort(key=lambda s: s[1])
        result = []
        for k, v in groupby(p, key=lambda s: s[1]):
            grouped = [v[0] for v in v]
            grouped[0] = '\x038' + grouped[0] + '\x03'
            if len(grouped) > 1:
                for i, hook in enumerate(grouped[1:]):
                    grouped[i+1] = '[\x032' + grouped[i+1] + '\x03]'
            result.append(' '.join(grouped))
        result.sort()
        p = ', '.join(result)
        return 'Plugins currently loaded: ' + p


@bot.command
def raw(context):
    '''.raw <command>'''
    if not context.line['prefix'] in bot.config.get('ADMINS', []):
        return
    if context.args:
        command = context.args.split(' ', 1)[0]
        args = list(context.args.split(' ', 1)[-1])
        bot.irc.send_command(command, args)
    else:
        return raw.__doc__


@bot.regex('[\?]')
def regex_test(context):
    if context.args == '?foo':
        return 'bar'
    if 'http' in context.args:
        url = context.args.split('?')[1]
        return shortener(url)


@bot.event('PRIVMSG')
def shorten(context):
    message = context.line['message']
    schemes = ('http://', 'https://', 'www.')
    contains_url = True in map(lambda scheme: scheme in message, schemes)

    if not contains_url:
        return

    urls = find_urls(message)

    titles_and_urls = []
    for url in urls:
        try:
            r = requests.get(url)
        except Exception:
            return 'unable to open url: ' + url

        parsed_page = html.parse(r.content)
        title = parsed_page.find('.//title')
        url = shortener(url)

        if title is not None:
            title = title.text
            titles_and_urls.append(title + ' - ' + url)
        else:
            titles_and_urls.append(url)

    for result in titles_and_urls:
        bot.reply(result, context.line)
