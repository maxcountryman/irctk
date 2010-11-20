from core.hooks import command
import urllib2

@command('google')
def google(bot, parsed_event):
        var = 'DEBUG'
        bot.irc.msg(parsed_event.command_args[0], '{0}'.format(var))
