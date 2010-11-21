from random import choice
import cPickle

from core.hooks import *

@command('quote')
def quotes(bot, parsed_event):
    quote_list = cPickle.load(open('quotes.pickle'))
    quote = choice(quote_list)
    bot.irc.msg(parsed_event.command_args[0], '{0}'.format(quote))

@command('addquote')
def addquote(bot, parsed_event):
    quote_list = cPickle.load(open('quotes.pickle'))
    if parsed_event.trailing.startswith(bot.irc.nick):
        parsed_event.trailing.strip(bot.irc.nick)
    if parsed_event.trailing.partition(' ')[-1] and parsed_event.trailing.partition(' ')[-1] != 'addquote':
        add_quote = parsed_event.trailing.partition(' ')[-1]
        bot.irc.msg(parsed_event.command_args[0], 'Added quote: {0}'.format(add_quote))
    else:
        return
    quote_list.append('{0}'.format(add_quote))
    cPickle.dump(quote_list, open('quotes.pickle', 'w'))
