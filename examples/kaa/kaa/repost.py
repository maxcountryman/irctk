# ported from skybot

from kaa import bot
from kaa.utils import get_db_connection
from kaa.timesince import timesince

import math
import time

expiration_period = 60 * 60 * 24 * 7  # 1 week


def db_init(db):
    db.execute('create table if not exists urlhistory'
               '(chan, url, nick, time)')
    db.commit()


def insert_history(db, chan, url, nick):
    db.execute('insert into urlhistory(chan, url, nick, time) '
               'values(?,?,?,?)', (chan, url, nick, time.time()))
    db.commit()


def get_history(db, chan, url):
    db.execute('delete from urlhistory where time < ?',
               (time.time() - expiration_period,))
    return db.execute('select nick, time from urlhistory where '
                      'chan=? and url=? order by time desc',
                      (chan, url)).fetchall()


def nicklist(nicks):
    nicks = sorted(dict(nicks), key=unicode.lower)
    if len(nicks) <= 2:
        return ' and '.join(nicks)
    else:
        return ', and '.join((', '.join(nicks[:-1]), nicks[-1]))


def format_reply(history):
    if not history:
        return

    last_nick, recent_time = history[0]
    last_time = timesince.timesince(recent_time)

    if len(history) == 1:
        return '{0} linked that {1} ago.'.format(last_nick, last_time)

    hour_span = math.ceil((time.time() - history[-1][1]) / 3600)
    hour_span = '{0:.0f} hours'.format(hour_span if hour_span > 1 else 'hour')

    history_len = len(history)
    ordinal = ['once', 'twice', '%d times'.format(history_len)]
    ordinal[min(history_len, 3) - 1]

    if len(dict(history)) == 1:
        last = 'last linked {0} ago'.format(last_time)
    else:
        last = 'last linked by {0} {1} ago'.format(last_nick, last_time)

    out = 'that url has been posted {0} in the past {1} by {2} ({3}).'
    out = out.format(ordinal, hour_span, nicklist(history), last)

    return out


@bot.regex('([a-zA-Z]+://|www\.)[^ ]+')
def urlinput(context):
    match = context.line['regex_search']
    chan = context.line['sender']
    nick = context.line['sender']

    db = get_db_connection()

    db_init(db)

    url = match.group().encode('utf-8', 'ignore')
    url = url.decode('utf-8')
    history = get_history(db, chan, url)
    insert_history(db, chan, url, nick)

    inp = match.string.lower()

    for name in dict(history):
        if name.lower() in inp:  # person was probably quoting a line
            return               # that had a link. don't remind them.

    if nick not in dict(history):
        return format_reply(history)
