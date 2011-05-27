from voxbot import irc
from voxbot import loader

import json
import sys
import os
import imp
import string
import gevent

class Bot(object):
    
    def __init__(self, settings):
        self.irc = irc.Irc(settings)
        self.settings = settings
        self._event_loop()
    
    def _respond(self, msg):
        if not self.sender == self.irc.nick:
            self.irc.msg(self.sender, msg)
        else:
            self.irc.reply(self.user, msg)
        
    def _event_loop(self):
        '''Main event loop. All the magic happens here.'''
        
        while True:
            bot = self.irc
            logger = self.irc.logger
            line = self.irc.lines.get()
            msgs = line['args'][-1]
            self.sender = line['args'][0]
            self.user = line['prefix'].split('!', 1)[0]
            owners = self.settings['owners']
            plugins = self.settings['plugins']
            
            try:
                jobs = [gevent.spawn(loader.load_plugins, bot, [p]) \
                        for p in plugins]
                gevent.joinall(jobs)
                if msgs.startswith('^reload') and self.user in owners:
                    self.settings = Config('config.py').config.SETTINGS
                    plugins = self.settings['plugins']
                    plugin = msgs[msgs.find('^reload'):].split(' ', 1)[-1]
                    
                    if not plugin == '^reload' and plugin in plugins:
                        loader.reload_plugin('voxbot.' + plugin)
                        self._respond('Reloading {0}'.format(plugin))
                    else:
                        for plugin in plugins:
                            loader.reload_plugin('voxbot.' + plugin)
                        self._respond('Reloading plugins')
                        
                if msgs.startswith('^help'):
                    loaded = ' '.join(plugins)
                    plugin = msgs[msgs.find('^help'):].split(' ', 1)[-1]
                    plugin = string.capitalize(plugin)
                    
                    if plugin == '^help':
                        self._respond('Plugins loaded: ' + loaded)
                    elif plugin in plugins:
                        p = [p for p in plugins if p == plugin]
                        p = ''.join(p)
                        info = sys.modules[p].__dict__[p].__doc__
                        self._respond(str(info))
                    else:
                        self._respond('Plugin not found')
                        
            except Exception, e: # catch all exceptions, don't die for plugins
                logger.error('Error loading plugins: ' + str(e))


class Config(object):
    '''This class returns a config object from a file, `filename`.'''
    
    def __init__(self, filename):
        self.config = self.from_pyfile(filename)
    
    def from_pyfile(self, filename):
        filename = os.path.join(os.path.abspath('.'), filename)
        
        try:
            imp.load_source('config', filename)
            config = sys.modules['config'].__dict__['Config']
            return config
        except ImportError, e:
            print('Config error: ' + e) # not ideal, should be logger


class Plugin(object):
    '''This is a base class from which plugins may inherit. It provides some
    normalized variables which aim to make writing plugins a sane endevour.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.owners = self.bot.settings['owners']
        self.msgs = self.bot.line['args'][-1]
        self.sender = self.bot.line['args'][0]
        self.command = self.bot.line['command']
        self.prefix =  self.bot.line['prefix']
        self.user = self.prefix.split('!')[0]
    
    def reply(self, msg=None, channel=None, action=None):
        '''Directs a response to either a channel or user. If `channel`,
        overrides the target, if `action`, wraps `msg` with ACTION escapes.
        '''
        
        LINE_LIMIT = 255
        
        if not msg:
            msg = 'Error: Received an empty string'
        elif action or (msg.startswith(chr(1)) and action != False):
            msg =  chr(1) + 'ACTION ' + msg + chr(1)
        
        msgs = [msg[i:i + LINE_LIMIT] for i in range(0, len(msg), LINE_LIMIT)]
        
        if channel:
            return [self.bot.msg(channel, msg) for msg in msgs]
        if self.sender != self.bot.nick:
            [self.bot.msg(self.sender, msg) for msg in msgs]
        else:
            [self.bot.reply(self.user, msg) for msg in msgs]
    
    @staticmethod
    def command(cmd, is_in=False):
        '''Used for decorating commands. Should contain the command string.
        
        Like this:
        
            @Plugin.command('^my_command')
            def my_command(*args, **kwargs):
                pass # do some cool stuff here
        '''
        
        def _dec(f):
            from functools import wraps
            @wraps(f)
            def _wrap(self, *args, **kwargs):
                _cmd = self.msgs[self.msgs.find(cmd):].split(' ', 1)[0]
                args = self.msgs[self.msgs.find(cmd):].split(' ', 1)[-1]
                if _cmd == args:
                    args = None
                if (is_in and cmd in self.msgs) or self.msgs.startswith(cmd):
                    return f(self, cmd=_cmd, args=args)
            return _wrap
        return _dec
    
    @staticmethod
    def event(event):
        '''Used for decorating commands that are triggered by an event, such as 
        JOIN or PART. Should contain the server command, e.g. JOIN.
        
        Like this:
        
            @Plugin.command('JOIN')
            def on_join(*args, **kwargs):
                pass # do some cool stuff here
        '''
        
        def _dec(f):
            def _wrap(self, *args, **kwargs):
                args = self.msgs
                if event in self.command:
                    return f(self, args)
            return _wrap
        return _dec
