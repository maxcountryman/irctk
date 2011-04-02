Kaa
===
A simple, modular IRC bot
-------------------------
Kaa is a simple, modular IRC bot written in Python using Gevent.

Setup
-----
Grab the source, I recommend using pip to install. The requirements.txt should 
get you set up.

Writing a Plugin
----------------
Plugins are easy to write. Begin by importing the Plugin super class:

`from voxbot.bot import Plugin`

For convenience, `Plugin` provides a decorator for commands, 
`@Plugin.command()`. This should be used to assign a command to a function. It 
will automatically return a tuple to your function. The first element of the 
tuple will be the command and the second will either be the command, if there 
are no args after the command, or the args that follow the command.

    class Myplugin(Plugin):
        '''usage: ^my_command [args]'''
        
        def __init__(self, bot)
            super(Myplugin, self).__init__(bot)
            self.my_command()
            
        @Plugin.command('^my_command')
        def my_command(self, *args)
            if args[0] != args[-1]
                self.reply(str(args[-1]))

Because the super class provides several shortcuts, such as `reply()`, it's 
often recommended to use `super()` to make sure these are available in your
plugin class.

In order to use the plugin you will need to add it to the list of configured
plugins to load. Typically something like this should work, saved as config.py:

    class Config(object):
    
        SETTINGS = {
            'server': 'irc.voxinfinitus.net', 
            'nick': 'Kaa', 
            'realname': 'Kaa the Python', 
            'port': 6697, 
            'ssl': True, 
            'channels': ['#testing',],
            'plugins': ['Myplugin'],
            'owners': ['foobar']
        }
