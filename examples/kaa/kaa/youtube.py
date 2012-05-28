# ported from skybot

from kaa import bot

from urllib import quote

import re
import json
import time
import locale

import requests

youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-z0-9]+)', re.I)
youtube_re = re.compile(*youtube_re)

base_url = 'http://gdata.youtube.com/feeds/api/'
url = base_url + 'videos/{0}?v=2&alt=jsonc'
search_api_url = base_url + 'videos?v=2&alt=jsonc&max-results=1'
video_url = "http://youtube.com/watch?v={0}"


def get_video_description(vid_id):
    r = requests.get(url.format(vid_id))
    data = json.loads(r.content)

    if data.get('error'):
        return

    data = data['data']

    out = '\x02{title}\x02'.format(**data)

    if not data.get('duration'):
        return out

    out += ' - length \x02'
    length = data['duration']
    if length / 3600:  # > 1 hour
        out += '{0}h '.format(length / 3600)
    if length / 60:
        out += '{0}m '.format(length / 60 % 60)
    out +='"{0}s\x02'.format(length % 60)

    if 'rating' in data:
        out += \
            ' - rated \x02{rating:.2f}/5.0\x02 ({ratingCount})'.format(**data)

    # The use of str.decode() prevents UnicodeDecodeError with some locales
    # See http://stackoverflow.com/questions/4082645/
    if 'viewCount' in data:
        formated_locale = locale.format('%d', data['viewCount'], 1)
        formated_locale = formated_locale.decode('utf-8')
        out += ' - \x02{0}\x02 views'.format(formated_locale)

    upload_time = time.strptime(data['uploaded'], '%Y-%m-%dT%H:%M:%S.000Z')
    out += ' - \x02{0}\x02 on \x02{1}\x02'.format(data['uploader'],
                time.strftime('%Y.%m.%d', upload_time))

    if 'contentRating' in data:
        out += ' - \x034NSFW\x02'

    return out


@bot.regex(youtube_re)
def youtube_url(context):
    print 'test'
    print context.line['regex_search']
    print context.line['regex_search'].groups()
    vid_id = context.line['regex_search'].groups()[0]
    return get_video_description(vid_id)


@bot.command('y')
@bot.command
def youtube(context):
    '.youtube <query>'

    query = quote(context.args)

    r = requests.get(search_api_url, params=dict(q=query))

    data = json.loads(r.content)

    if 'error' in data:
        return 'error performing search'

    if data['data']['totalItems'] == 0:
        return 'no results found'

    vid_id = data['data']['items'][0]['id']

    return get_video_description(vid_id) + ' - ' + video_url.format(vid_id)
