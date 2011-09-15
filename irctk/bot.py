'''
    irctk.bot
    ---------
    
    This defines the main class, `Bot`, for use in creating new IRC bot apps.
'''

import os
import sys
import time
import inspect
import thread
import Queue
import imp

from .config import Config
from .ircclient import TcpClient, IrcWrapper, IrcTestClient


class Context(object):
    def __init__(self, line, args):
        self.line = line
        self.args = args


class Bot(object):
    _instance = None
    root_path = os.path.abspath('')
    work_queue = Queue.Queue()
    return_queue = Queue.Queue()
    worker_pool = []
    
    default_config = dict({
        'SERVER': 'irc.voxinfinitus.net',
        'PORT': 6697,
        'SSL': True,
        'TIMEOUT': 300,
        'NICK': 'Kaa',
        'REALNAME': 'Kaa the rock python',
        'CHANNELS': ['#voxinfinitus'],
        'PLUGINS': [],
        'EVENTS': [],
        'WORKERS': 2
        })
    
    def __init__(self):
        self.config = Config(self.root_path, self.default_config)
    
    def __new__(cls, *args, **kwargs):
        '''Here we override the `__new__` method in order to achieve a 
        singleton effect. In this way we can reload instances of the object 
        without having to worry about which instance we reference.'''
        
        if not cls._instance:
            cls._instance = super(Bot, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def _update_plugins(self, plugins, plugin):
        '''Updates a given list containing plugins, `plugins`, with a plugin 
        dictionary object, `plugin`.
        
        Usually used to update the PLUGINS or EVENTS list in the configuration 
        object.
        '''
        
        if not self.config.get(plugins):
            self.config[plugins] = []
        return self.config[plugins].append(plugin)
    
    def _dispatch_plugin(self, plugin, hook, context):
        '''TODO'''
        
        if context == hook or context.startswith(hook + ' '):
            plugin_args = plugin['context']['message'].split(hook, 1)[-1].strip()
            plugin_context = Context(plugin['context'], plugin_args)
            
            self.work_queue.put((plugin, plugin_context))
    
    def _handle_plugin_result(self):
        '''TODO'''
        
        while not self.return_queue.empty():
            message, plugin_context, action, notice = self.return_queue.get()
            if message:
                self.reply(message, plugin_context.line, action, notice)
    
    def _handle_worker_threads(self, wait=5.0):
        '''TODO'''
        
        idle_workers = 0
        
        def handle_threads(idle_workers):
            
            time.sleep(wait) # replaces time delta offsets, so execution is 
            
            pool_length = len(self.worker_pool)
            workers = self.config['WORKERS']
            total_workers = workers - pool_length
            
            if pool_length < workers:
                for worker in range(total_workers):
                    ident = self._spawn_worker()
                    spawning = 'Spawning worker {0}; too few workers'.format(ident)
                    self.logger.info(spawning)
            
            if not self.work_queue.empty():
                ident = self._spawn_worker()
                spawning = 'Spawning worker {0}'.format(ident)
                self.logger.info(spawning)
            
            if self.work_queue.all_tasks_done.acquire(0):
                self.work_queue.all_tasks_done.release()
                if pool_length > workers:
                    idle_workers += 1
                    idlers = 'We have {0} idle workers.'.format(idle_workers)
                    self.logger.info(idlers)
            
            if idle_workers > workers and idle_workers > 0:
                ident = self.worker_pool.pop(0)
                idle_workers -= 1
                self.logger.info('Killing idle worker {0}'.format(ident))
        
        handle_threads(idle_workers)
    
    def _parse_input(self, prefix='.'):
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
            time.sleep(0.01)
            
            self._handle_worker_threads()
            
            with self.irc.lock:
                context_stale = self.irc.context.get('stale')
                args = self.irc.context.get('args')
                command = self.irc.context.get('command')
                message = self.irc.context.get('message')
                while not context_stale and args:
                    if message.startswith(prefix):
                        for plugin in self.config['PLUGINS']:
                            plugin['context'] = self.irc.context # set context
                            hook = prefix + plugin['hook']
                            try:
                                self._dispatch_plugin(plugin, hook, message)
                            except Exception, e:
                                self.logger.error(str(e))
                                continue
                    if command and command.isupper():
                        for event in self.config['EVENTS']:
                            event['context'] = self.irc.context
                            hook = event['hook']
                            try:
                                self._dispatch_plugin, (event, hook, command)
                            except Exception, e:
                                self.logger.error(str(e))
                                continue
                    
                    # we're done here, context is stale, give us fresh fruit!
                    context_stale = self.irc.context['stale'] = True
                
                # Finaly handle messages returned from the plugins.
                self._handle_plugin_result()
    
    def _reloader_loop(self, wait=1.0):
        '''This reloader is based off of the Flask reloader which in turn is 
        based off of the CherryPy reloader.
        
        This internal method takes on parameter, `wait`, the wait time given 
        in seconds. The default value is set to one second.
        '''
        
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
    
    def _reloader(self, fnames, wait=1.0):
        '''This reloader is based off of the Flask reloader which in turn is 
        based off of the CherryPy reloader.
        
        This internal method takes two paramters, `fnames` and `wait.` Here 
        we loop over a list of file names, `fnames`, using `os.stat` to 
        determine if the mtime of the file has been changed. If so we use 
        `imp.load_source` to reload the module.
        
        The `fnames` parameter should be a list of files names to be parsed by 
        the reloader.
        
        The `wait` parameter specifies the time in seconds to run 
        `time.sleep()`.
        ''' 
        
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
    
    def _spawn_worker(self):
        '''TODO'''
        
        ident = thread.start_new_thread(self._plugin_worker,
                                       (self.work_queue, self.return_queue)
                                       )
        self.worker_pool.append(ident)
        return ident
    
    def _plugin_worker(self, work_queue, return_queue):
        ''' Polls the work_queue for jobs, runs them and places the result on the
        return_queue.
        '''
        
        try:
            while thread.get_ident() in self.worker_pool:
                plugin, plugin_context = work_queue.get(True)
                takes_args = inspect.getargspec(plugin['func']).args
                
                action = False
                if plugin.get('action') == True:
                    action = True
                
                notice = False
                if plugin.get('notice') == True:
                    notice = True
                
                if takes_args:
                    message = plugin['func'](plugin_context)
                else:
                    message = plugin['func']()
                return_queue.put((message, plugin_context, action, notice))
                self.work_queue.task_done()
        # Catch all exceptions so we can notify the pool we died.
        except Exception, e:
            error = 'Error {0} in worker thread; exiting.'.format(e)
            self.logger.error(error)
            self.worker_pool.pop(thread.get_ident())
            raise e
    
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
            self._update_plugins('PLUGINS', plugin)
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
            self._update_plugins('EVENTS', plugin)
            return f
        
        plugin['hook'] = hook
        plugin.update(kwargs)
        return wrapper
    
    def reply(self, message, context, action=False, notice=False, line_limit=400):
        '''TODO'''
        
        if context['sender'].startswith('#'):
            recipient = context['sender']
        else:
            recipient = context['user']
        
        messages = []
        def handle_long_message(message):
            message, extra = message[:line_limit], message[line_limit:]
            messages.append(message)
            if extra:
                handle_long_message(extra)
        handle_long_message(message)
        
        for message in messages:
            self.irc.send_message(recipient, message, action, notice)
    
    def run(self, wait=0.01):
        
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
        
        # Set the worker thread pool up.
        for worker in range(self.config['WORKERS']):
            self._spawn_worker()
        
        self.connection.connect()
        self.irc.run()
        
        thread.start_new_thread(self._parse_input, ())
        thread.start_new_thread(self._reloader_loop, ())
        
        while True:
            time.sleep(wait)


class TestBot(Bot):
    shutdown = False
    
    def __init__(self):
        self.config = Config(self.root_path, self.default_config)
        self.irc = IrcTestClient(
                self.config['NICK'], 
                self.config['REALNAME'], 
                self.config['CHANNELS']
                )
        self.connection = self.irc.connection
    
    def run(self):
        
        thread.start_new_thread(self._parse_input, ())
        
        while not self.shutdown:
            time.sleep(0.01)

