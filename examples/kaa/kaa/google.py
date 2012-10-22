from kaa import bot
from kaa.utils import shortener
from kaa.wikipedia import wiki_re, wiki_search
from kaa.youtube import youtube_re, get_video_description

from urllib import quote
from HTMLParser import HTMLParser

import re
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

    url = first_result['unescapedUrl']

    # special handling for Wikipedia
    wiki = re.search(wiki_re, url)
    if wiki:
        ret = wiki_search(context.args)
        bot.logger.info(context.args)
        bot.logger.info(ret)
        if ret != 'no results found':
            return ret

    # special handling for YouTube
    youtube = re.search(youtube_re, url)
    if youtube:
        vid_id = youtube.groups()[-1]
        desc = get_video_description(vid_id)
        return '{0} -- {1}'.format(desc, url)

    title = first_result['titleNoFormatting']
    title = HTMLParser.unescape.__func__(HTMLParser, title)

    ret = title + ' - ' + shortener(url)
    ret += ' ({0})'.format(first_result['visibleUrl'])

    return ret


@bot.command
def gis(context):
    data = search(context.args, 'images')['responseData']['results']
    if not data:
        return 'no images found'
    return data[0]['unescapedUrl']
