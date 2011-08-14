'''
    kaa.bot
    -------
    
    This defines the main class, `Kaa`, for use in creating new IRC bot apps.
'''

import os
import sys
import time
import inspect
import thread
import imp

from .config import Config
from .ircclient import TcpClient, IrcWrapper


class Kaa(object):
    _instance = None
    root_path = os.path.abspath('')
    
    default_config = dict({
        'SERVER': 'irc.voxinfinitus.net',
        'PORT': 6697,
        'SSL': True,
        'TIMEOUT': 300,
        'NICK': 'Kaa',
        'REALNAME': 'Kaa the rock python',
        'CHANNELS': ['#voxinfinitus'],
        'PLUGINS': [],
        'EVENTS': []
        })
    
    def __init__(self):
        self.config = Config(self.root_path, self.default_config)
    
    def __new__(cls, *args, **kwargs):
        '''Here we override the `__new__` method in order to achieve a 
        singleton effect. In this way we can reload instances of the object 
        without having to worry about which instance we reference.'''
        
        if not cls._instance:
            cls._instance = super(Kaa, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def _update_plugins(self, plugin):
        '''Appends a dictionary object, `plugin` to the `PLUGINS` value, i.e. 
        a list.
        '''
        
        if not self.config.get('PLUGINS'):
            self.config['PLUGINS'] = []
        return self.config['PLUGINS'].append(plugin)
    
    def _update_events(self, event):
        '''Appends a dictionary object, 'event', to the `EVENTS` value, i.e. 
        a list.
        '''
        
        if not self.config.get('PLUGINS'):
            self.config['EVENTS'] = []
        return self.config['EVENTS'].append(event)
    
    def _parse_input(self, prefix='.'):
        '''TODO'''
        
        while True:
            time.sleep(0.01)
            
            context_stale = self.irc.context.get('stale')
            args = self.irc.context.get('args')
            while not context_stale and args:
                command = self.irc.context.get('command')
                args = self.irc.context.get('args')
                message = args[-1]
                
                if message.startswith(prefix):
                    for plugin in self.config['PLUGINS']:
                        
                        # help for plugins, i.e. doc strings
                        _help = prefix + 'help'
                        help_hook = message.split(' ', 1)[-1]
                        if message.startswith(_help) and plugin.get(help_hook):
                            hook = message.split(' ', 1)[-1]
                            if plugin.get(hook):
                                self.irc.send_reply(plugin['help'])
                            else:
                                self.irc.send_reply('plugin not found')
                        
                        hook = plugin['hook']
                        hook = prefix + hook
                        #self.logger.debug('{0}'.format(str(plugin)))
                        
                        if message == hook or message.startswith(hook + ' '):
                            _args = message.split(hook, 1)[-1].strip()
                            
                            # run the plugin in a thread?
                            if plugin.get('threaded'):
                                if inspect.getargspec(plugin['func']).args:
                                    thread.start_new_thread(plugin['func'], (_args,))
                                else:
                                    thread.start_new_thread(plugin['func'], ())
                            else:
                                try:
                                    if inspect.getargspec(plugin['func']).args:
                                        plugin['func'](_args)
                                    else:
                                        plugin['func']()
                                except Exception, e:
                                    self.logger.error(str(e))
                                    continue
                
                if command and command.isupper():
                    for event in self.config['EVENTS']:
                        hook = event['hook']
                        
                        if command == hook:
                            _args = message.split(hook, 1)[-1].strip()
                            try:
                                self.logger.info(event)
                                event['func'](_args)
                            except Exception, e:
                                self.logger.error(str(e))
                                continue
                
                # we're done here, context is stale, give us fresh fruit!
                context_stale = self.irc.context['stale'] = True
    
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
        
        def wrapper(f):
            plugin.setdefault('hook', f.func_name)
            plugin['func'] = f
            plugin['help'] = f.__doc__ if f.__doc__ else 'no help provided'
            self._update_plugins(plugin)
            return f
        
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
        
        def wrapper(f):
            plugin['func'] = f
            self._update_events(kwargs)
            return f
        
        plugin['hook'] = hook
        plugin.update(kwargs)
        return wrapper
    
    def _reloader_loop(self, wait=1):
        '''Flask, CherryPy, reloader.py'''
        
        def iter_module_files():
            for module in sys.modules.values():
                filename = getattr(module, '__file__', None)
                if filename:
                    old = None
                    while not os.path.isfile(filename):
                        old = filename
                        filename = os.path.dirname(filename)
                        if filename == old:
                            break
                    else:
                        if filename[-4:] in ('.pyc', '.pyo'):
                            filename = filename[:-1]
                        yield filename
        
        fnames = []
        fnames.extend(iter_module_files())
        self._reloader(fnames, wait=wait)
    
    def _reloader(self, fnames, wait=1):
        mtimes = {}
        
        while True:
            for filename in fnames:
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError:
                    continue
                
                old_time = mtimes.get(filename)
                if old_time is None:
                    mtimes[filename] = mtime
                elif mtime > old_time:
                    mtimes[filename] = mtime
                    
                    self.logger.info('Changes detected; reloading {0}'.format(filename))
                    
                    f = filename.split('/')[-1].split('.')[0]
                    try:
                        imp.load_source(f, filename)
                    except Exception, e:
                        self.logger.error('Failed loading plugin: ' + str(e))
                        continue
                    finally:
                        mtimes[filename] = mtime
                        
            time.sleep(wait)
    
    def run(self):
        
        self.connection = TcpClient(
                self.config['SERVER'], 
                self.config['PORT'], 
                self.config['SSL'], 
                self.config['TIMEOUT']
                )
        
        self.irc = IrcWrapper(
                self.connection, 
                self.config['NICK'], 
                self.config['REALNAME'], 
                self.config['CHANNELS']
                )
        
        self.logger = self.connection.logger
        
        self.connection.connect()
        self.irc.run()
        
        thread.start_new_thread(self._parse_input, ())
        thread.start_new_thread(self._reloader_loop, ())
        
        while True:
            time.sleep(0.01)

