##Kaa

Kaa is a simple IRC framework for developing IRC-based applications.
Essentially it wraps a loosely coupled, modified TCP client and IRC wrapper.

##Installation

Simply download and install via pip: `sudo pip install kaa`

Or you may clone the repo and install with setuptools: `python setup.py install`

##Writing Your First App

Begin by import the framework bot object, called Kaa(). Assign this object to
a local variable, e.g. `bot`.
    
    from kaa import Kaa
    bot = Kaa()

You may set up configuration for your application via an external configuration 
file, such as `settings.cfg`, for instance. Several parameters are expected in
order to set up the connection. For instance your `settings.cfg` might look
something like this:
    
    SERVER = 'irc.voxinfinitus.net'
    PORT = 6667
    SSL = False
    TIMEOUT = 300
    NICK = 'hax0r'
    REALNAME = 'A Python Bot'
    CHANNELS = ['#voxinfinitus']
    
Then you can load this file into your app with the following:
    
    bot.config.from_pyfile('settings.cfg')

Plugins are realized in a slightly different way than some other IRC bots.
Although they are still loaded into the execution loop, there is no respository
of plugins. Instead you can hook in any function you like to the execution loop
by using a decorator:
    
    @bot.command('test')
    def test(*args):
        bot.irc.send_reply('Testing... 1, 2, 3!')

These commands may live anywhere you like. So if you prefer to split them out
into a separate file, that's no problem.

Finally you will want to run your app. To do so simply:
    
    if __name__ == '__main__':
        bot.run()

