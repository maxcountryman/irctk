from kaa import bot

from urllib import quote

import requests

URL = 'http://eval.appspot.com/eval?statement={0}'


@bot.command('p')
@bot.command
def python(context):
    '.python <exp>'

    query = quote(context.args)

    try:
        r = requests.get(URL.format(query))
    except Exception, e:
        return str(e)

    data = r.text

    if data.startswith('Traceback (most recent call last):'):
        data = data.splitlines()[-1]
    return data
