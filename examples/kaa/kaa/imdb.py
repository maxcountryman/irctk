# ported from skybot

from kaa import bot

from urllib import quote

import json

import requests


@bot.command('i')
@bot.command
def imdb(context):
    '''.imdb <movie> -- gets information about <movie> from IMDb'''

    r = requests.get('http://www.imdbapi.com/?t=' + quote(context.args))
    content = json.loads(r.content)

    if content['Response'] == 'Movie Not Found':
        return 'movie not found'
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/{imdbID}'.format(**content)

        out = '\x02{Title}\x02 ({Year}) ({Genre}): {Plot}'
        if content['Runtime'] != 'N/A':
            out += ' \x02{Runtime}\x02.'
        if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
            out += ' \x02{imdbRating}/10\x02 with \x02{imdbVotes}\x02 votes.'
        out += ' {URL}'
        return out.format(**content)
    else:
        return 'unknown error'
