# ported from skybot

from kaa import bot
from kaa.utils import get_db_connection


def db_init(db):
    db.execute('create table if not exists '
               'remember(chan, token, text)')
    db.commit()


def add_remember_token(db, chan, token, text):
    match = db.cursor().execute('select * from remember where '
                                'lower(token)=lower(?) and chan=?',
                                (token, chan)).fetchall()

    append = text.startswith('+')

    if match:
        old_text = get_remember_token(db, chan, token)
        if append:
            text = old_text + ' ' + text.split('+')[1]
        db.execute('update remember set text=? where token=? and chan=?',
                   (text, token, chan))
        db.commit()
        if not append:
            return 'overwrote: ' + old_text
        else:
            return 'appended to record'

    db.execute('replace into remember(chan, token, text) values(?,?,?)',
               (chan, token, text))
    db.commit()
    return 'remember record for {0} added'.format(token)


def get_remember_token(db, chan, token):
    return db.execute('select text from remember where lower(token)=lower(?) '
                      'and chan=? order by lower(token)',
                      (token, chan)).fetchall()[0][0]


@bot.command('r')
@bot.command
def remember(context):
    '.remember <token> <string>, .remember <token> +<string> (append)'
    chan = context.line['sender']

    db = get_db_connection()
    db_init(db)

    args = context.args.split(' ', 1)

    if not len(args) == 2:
        return 'not enough args given'

    token = args[0]
    text = args[1][:1024]

    return add_remember_token(db, chan, token, text)


@bot.regex('([\?])([a-zA-Z0-9]+)')
def recall(context):
    db = get_db_connection()
    db_init(db)

    chan = context.line['sender']
    token = context.line['regex_search'].groups()[1]

    return get_remember_token(db, chan, token)
