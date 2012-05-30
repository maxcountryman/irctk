# ported from skybot

from kaa import bot
from kaa.utils import get_db_connection
from kaa.timesince import timesince

import time


def db_init(db):
    db.execute('create table if not exists tell'
               '(user_to, user_from, message, chan, time,'
               'primary key(user_to, message))')
    db.commit()


def get_tells(db, user_to):
    return db.execute('select user_from, message, time, chan from tell where'
                      ' user_to=lower(?) order by time',
                      (user_to.lower(),)).fetchall()


@bot.event('PRIVMSG')
def tellinput(context):
    if 'showtells' in context.line['message'].lower():
        return

    nick = context.line['user']

    db = get_db_connection()
    db_init(db)

    tells = get_tells(db, nick)

    if tells:
        user_from, message, time, chan = tells[0]
        past = timesince(time)
        reply = '{0} said {1} ago in {2}: {3}'.format(user_from,
                                                      past,
                                                      chan,
                                                      message)
        if len(tells) > 1:
            reply += \
                    ' (+{0} more, .showtells to view)'.format((len(tells) - 1))

        db.execute('delete from tell where user_to=lower(?) and message=?',
                   (nick, message))
        db.commit()
        return reply


@bot.command
def showtells(context):
    '.showtells -- view all pending tell messages (sent in PM).'

    nick = context.line['user']

    db = get_db_connection()
    db_init(db)

    tells = get_tells(db, nick)

    if not tells:
        bot.reply('You have no pending tells.',
                  context,
                  recipient=nick,
                  notice=True)
        return

    for tell in tells:
        user_from, message, time, chan = tell
        past = timesince(time)
        bot.reply('{0} said {1} ago in {2}: {3}'.format(user_from,
                                                        past,
                                                        chan,
                                                        message),
                  context, recipient=nick, notice=True)

    db.execute('delete from tell where user_to=lower(?)', (nick,))
    db.commit()


@bot.command
def tell(context):
    '.tell <nick> <message>'

    db = get_db_connection()
    db_init(db)

    query = context.args.split(' ', 1)
    nick = context.line['user']
    chan = context.line['sender']

    if len(query) != 2:
        return tell.__doc__

    user_to = query[0].lower()
    message = query[1].strip()
    user_from = nick

    if chan.lower() == user_from.lower():
        chan = 'a pm'

    if user_to == user_from.lower():
        return 'No.'

    if db.execute('select count() from tell where user_to=?',
                  (user_to,)).fetchone()[0] >= 5:
        return 'That person has too many things queued.'

    try:
        db.execute('insert into tell(user_to, user_from, message, chan, '
                   'time) values(?,?,?,?,?)', (user_to,
                                               user_from,
                                               message,
                                               chan,
                                               time.time()))
        db.commit()
    except db.IntegrityError:
        return 'Message has already been queued.'
    return 'I\'ll pass that along.'
