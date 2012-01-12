##IrcTK

IrcTK is a little IRC framework for developing IRC-based applications.

The framework is designed to be simple and easy to use. In an effort to ease
the flow of development, changes you make to your application source are
automatically reloaded by the framework so during the course of development you
don't have to disconnect and reconnect as changes are made.

Plugins are a breeze to write. Simply decorate functions with the provided
methods. Plugins may be tied to a hook or an event, such as 'PRIVMSG'.
A confirguable thread pool manages dispatching of plugins to ensure the
applications are fast and responsive.

##Installation

Simply download and install via pip: `pip install irctk`

Alternatively easy_install may be used: `easy_install irctk`

##Writing Your First App

First you'll want to make a configuration file for you application. You can
save this as whatever you'd like, for this example we'll save ours as
`settings.cfg`. Several parameters are expected in order to set up the
connection. For instance your `settings.cfg` might look something like this:

    SERVER = 'irc.voxinfinitus.net'
    PORT = 6667
    SSL = False
    TIMEOUT = 300
    NICK = 'hax0r'
    REALNAME = 'A Python Bot'
    CHANNELS = ['#voxinfinitus']

Next you'll want to create a new file and call it `bot.py` or some other cool
name. He you'll import the framework bot object, called Bot(). Assign this
object to a local variable, e.g. `bot`.

    from irctk import Bot
    bot = Bot()

Remember the configuration file you just wrote? Using our instance of the bot
class you'll load it up with the following line:

    bot.config.from_pyfile('settings.cfg')

Plugins are realized in a slightly different way than some other IRC bots.
Although they are still loaded into the execution loop, there is no respository
of plugins. Instead you can hook in any function you like to the execution loop
by using a decorator:

    @bot.command('test')
    def test_plugin():
        return 'Testing... 1, 2, 3!'

These commands may live anywhere you like. So if you prefer to split them out
into a separate file, that's no problem.

Finally you will want to run your app. To do so simply add the below code to
the bottom of your module:

    if __name__ == '__main__':
        bot.run()

## What To Do Next?

State is exposed by recieving an argument in the definition of the plugin
function. Internally the framework will examine the plugin's function, as it's
recieved, to determine if it takes arguments. In such a case a special
dictionary of the plugin's state as found when called, is sent to the call of
the plugin's function.

This state object provides a convenient interface for handling how the plugin
behaves. For instance, we might define a plugin function that shows us this
state:

    @bot.command('debug')
    def show_state(context):
        '''This plugin function receives the state from the framework as
        `context` this allows us to do a lot of cool things!

        `context.args` is always any arguments passed to the plugin when called
        from IRC. For instance in the case of, `.foo bar`, context.args will be
        `bar`.

        `context.line` is a dictionary containing the parsed IRC line as found
        when the plugin was called.
        '''

        if context.args: # if the plugin was called with argument variables
            bot.reply(context.args, context.line) # show those arguments
            return str(context.line)              # show us the parsed line
        else:
            return str(context.line)

In the above example, `bot.reply` is a special method of the bot instance which
will automatically format a reply to the correct recipient, i.e. either a user
who has sent the bot a private message or the channel the plugin was called
from.


## Server Commands (Events to bind to)

Here's a quick list of various IRC server commands you can bind bot.event() to.
Bear in mind that this list may be missing some commands but that doesn't
prevent the program from being bound to such commands.

    PRIVMSG
    NOTICE
    WHO
    WHOIS
    WHOWAS
    NICK
    USER
    PART
    QUIT
    JOIN
    MODE
    TOPIC
    NAMES
    LIST
    INVITE
    KICK
    KILL
    PING
    PONG

There are others, feel free to add to this list! :) This may also be useful:
http://www.irchelp.org/irchelp/rfc/rfc.html

Here's a brief example of binding a function to a JOIN event:

    @bot.event('JOIN')
    def spammy_greeter(context):
        user = context.line['user']
        return 'Hi there, ' + user
