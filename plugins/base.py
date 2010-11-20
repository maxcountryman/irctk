from core.hooks import subscribe

'''Core functionality.'''

@subscribe('ping')
def ping(bot, parsed):
    bot.irc.cmd('PONG', parsed.trailing)

@subscribe('396') # finished connecting, we can join
def join(bot, parsed):
    for channel in bot.channels:
        bot.irc.cmd('JOIN', channel, prefix=False)

@subscribe('376') # finished connecting, FreeNode
def join(bot, parsed):
    for channel in bot.channels:
        bot.irc.cmd('JOIN', channel, prefix=False)
