from core.hooks import subscribe

'''Core functionality.'''

@subscribe('ping')
def ping(bot, parsed_event):
    bot.irc.cmd('PONG', parsed_event.trailing)

@subscribe('376') # end MOTD, we can JOIN
def join(bot, parsed_event):
    for channel in bot.channels:
        bot.irc.cmd('JOIN', channel, prefix=False)
