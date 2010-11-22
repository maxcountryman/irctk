from random import choice

from core.hooks import command

@command
def python(bot, parsed_event):
    quote_list = ['Twisted.','You have to use Twisted.','Three words: sqlite, sqlite, sqlite.','Needs more external modules.','That\'s not Pythonic, moron.','Never use lambda, ever.']
    quote = choice(quote_list)
    bot.irc.msg(parsed_event.command_args[0], '{0}'.format(quote))

