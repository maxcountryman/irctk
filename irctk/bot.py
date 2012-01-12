'''
    irctk.bot
    ---------
    
    This defines the main class, `Bot`, for use in creating new IRC bot apps.
'''

import os
import time
import inspect
import thread

from .logging import create_logger
from .config import Config
from .reloader import ReloadHandler
from .plugins import PluginHandler
from .ircclient import TcpClient, IrcWrapper


class Bot(object):
    _instance = None
    root_path = os.path.abspath('')
    logger = create_logger()
    
    default_config = dict({
        'SERVER'      : 'irc.voxinfinitus.net',
        'PORT'        : 6697,
        'PASSWORD'    : None,
        'SSL'         : True,
        'TIMEOUT'     : 300,
        'NICK'        : 'Kaa',
        'REALNAME'    : 'Kaa the rock python',
        'CHANNELS'    : ['#voxinfinitus'],
        'PLUGINS'     : [],
        'EVENTS'      : [],
        'MAX_WORKERS' : 7,
        'MIN_WORKERS' : 3,
        })
    
    def __init__(self):
        self.config = Config(self.root_path, self.default_config)
        self.plugin = PluginHandler(self.config, self.logger, self.reply)
    
    def __new__(cls, *args, **kwargs):
        '''Here we override the `__new__` method in order to achieve a 
        singleton effect. In this way we can reload instances of the object 
        without having to worry about which instance we reference.'''
        
        if not cls._instance:
            cls._instance = super(Bot, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def _create_connection(self):
        self.connection = TcpClient(
                self.config['SERVER'], 
                self.config['PORT'],
                self.config['SSL'],
                self.config['TIMEOUT'],
                logger=self.logger,
                )
        
        self.irc = IrcWrapper(
                self.connection, 
                self.config['NICK'], 
                self.config['REALNAME'],
                self.config['PASSWORD'], 
                self.config['CHANNELS'],
                self.logger
                )
    
    def _parse_input(self, prefix='.', wait=0.01):
        '''This internal method handles the parsing of commands and events.
        Hooks for commands are prefixed with a character, by default `.`. This 
        may be overriden by specifying `prefix`.
        
        A context is maintained by our IRC wrapper, `IrcWrapper`; referenced 
        as `self.irc`. In order to prevent a single line from being parsed 
        repeatedly a variable `stale` is set to either True or False. 
        
        If the context is fresh, i.e. not `stale`, we loop over the line 
        looking for matches to plugins.
        
        Once the context is consumed, we set the context variable `stale` to 
        True.
        '''
        
        while True:
            time.sleep(wait)
            
            with self.irc.lock:
                context_stale = lambda : self.irc.context.get('stale')
                args = self.irc.context.get('args')
                command = self.irc.context.get('command')
                message = self.irc.context.get('message')
                while not context_stale() and args:
                    if message.startswith(prefix):
                        for plugin in self.config['PLUGINS']:
                            plugin['context'] = dict(self.irc.context)
                            hook = prefix + plugin['hook']
                            try:
                                self.plugin.enqueue_plugin(plugin, hook, message)
                            except Exception, e:
                                self.logger.error(str(e))
                                continue
                    if command and command.isupper():
                        for event in self.config['EVENTS']:
                            event['context'] = dict(self.irc.context)
                            hook = event['hook']
                            try:
                                self.plugin.enqueue_plugin(event, hook, command)
                            except Exception, e:
                                self.logger.error(str(e))
                                continue
                    
                    # we're done here, context is stale, give us fresh fruit!
                    self.irc.context['stale'] = True    
    
    def command(self, hook=None, **kwargs):
        '''This method provides a decorator that can be used to load a 
        function into the global plugins list.:
        
        If the `hook` parameter is provided the decorator will assign the hook 
        key to the value of `hook`, update the `plugin` dict, and then return 
        the wrapped function to the wrapper.
        
        Therein the plugin dictionary is updated with the `func` key whose 
        value is set to the wrapped function.
        
        Otherwise if no `hook` parameter is passed the, `hook` is assumed to 
        be the wrapped function and handled accordingly.
        '''
        
        plugin = {}
        
        def wrapper(func):
            plugin.setdefault('hook', func.func_name)
            plugin['funcs'] = [func]
            self.plugin.update_plugins(plugin, 'PLUGINS')
            return func
        
        if kwargs or not inspect.isfunction(hook):
            if hook:
                plugin['hook'] = hook
            plugin.update(kwargs)
            return wrapper
        else:
            return wrapper(hook)
    
    def event(self, hook, **kwargs):
        '''This method provides a decorator that can be used to load a 
        function into the global events list.
        
        It assumes one parameter, `hook`, i.e. the event you wish to bind 
        this wrapped function to. For example, JOIN, which would call the 
        function on all JOIN events.
        '''
        
        plugin = {}
        
        def wrapper(func):
            plugin['funcs'] = [func]
            self.plugin.update_plugins(plugin, 'EVENTS')
            return func
        
        plugin['hook'] = hook
        plugin.update(kwargs)
        return wrapper
    
    def add_command(self, hook, func):
        '''TODO'''
        
        self.plugin.add_plugin(hook, func, command=True)
    
    def add_event(self, hook, func):
        '''TODO'''
        
        self.plugin.add_plugin(hook, func, event=True)
    
    def remove_command(self, hook, func):
        '''TODO'''
        
        self.plugin.remove_plugin(hook, func, command=True)
    
    def remove_event(self, hook, func):
        '''TODO'''
        
        self.plugin.remove_plugin(hook, func, event=True)
    
    def reply(self, message, context, action=False, notice=False, line_limit=400):
        '''TODO'''
        
        if context['sender'].startswith('#'):
            recipient = context['sender']
        else:
            recipient = context['user']
        
        messages = []
        
        def handle_long_message(message):
            #truncate_at = message.rfind(' ', 1, line_limit) + 1
            message, extra = message[:line_limit], message[line_limit:]
            messages.append(message)
            if extra:
                handle_long_message(extra)
        
        handle_long_message(message)
        
        for message in messages:
            self.irc.send_message(recipient, message, action, notice)
    
    def run(self, wait=0.01):
        self._create_connection() # updates to the latest config
        
        self.connection.connect()
        self.irc.run() 
        
        thread.start_new_thread(self._parse_input, ())
        
        plugin_lists = [self.config['PLUGINS'], self.config['EVENTS']]
        self.reloader = ReloadHandler(plugin_lists, self.plugin, self.logger)
        
        while True:
            time.sleep(wait)

