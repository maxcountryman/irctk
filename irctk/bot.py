# -*- coding: utf-8 -*-
'''
    irctk.bot
    ---------

    This defines the main class, `Bot`, for use in creating new IRC bot apps.
'''

import os
import re
import time
import inspect
import thread

from irctk.logging import create_logger
from irctk.config import Config
from irctk.reloader import ReloadHandler
from irctk.plugins import PluginHandler
from irctk.ircclient import TcpClient, IrcWrapper


class Bot(object):
    # used to track the instance of the Bot class
    __shared_state = {}

    # initialize the logger as None
    logger = None

    # initlialize the config as None
    config = None

    # initalize the plugin as None
    plugin = None

    # initalize the reloader as None
    reloader = None

    # set our root path
    root_path = os.path.abspath('')

    # base configuration
    default_config = {'SERVER': '',
                      'PORT': 6667,
                      'PASSWORD': None,
                      'SSL': False,
                      'TIMEOUT': 300,
                      'NICK': '',
                      'USER': None,
                      'REALNAME': '',
                      'CHANNELS': [],
                      'PLUGINS': [],
                      'EVENTS': [],
                      'REGEX': [],
                      'MAX_WORKERS': 7,
                      'MIN_WORKERS': 3,
                      'CMD_PREFIX': '.'}

    def __init__(self):
        self.__dict__ = self.__shared_state

        if self.logger is None:
            self.logger = create_logger()

        # configure the bot instance
        if self.config is None:
            self.config = Config(self, self.root_path, self.default_config)
        else:
            # make sure we clear these upon reloads
            self.config['PLUGINS'] = []
            self.config['EVENTS'] = []
            self.config['REGEX'] = []

        # initialize the plugin handler
        if self.plugin is None:
            self.plugin = PluginHandler(self)

        # initalize the reload handler
        if self.reloader is None:
            self.reloader = ReloadHandler(self)

    def _create_connection(self):
        self.connection = TcpClient(self.config['SERVER'],
                                    self.config['PORT'],
                                    self.config['SSL'],
                                    self.config['TIMEOUT'],
                                    logger=self.logger)

        self.irc = IrcWrapper(self.connection,
                              self.config['NICK'],
                              self.config['REALNAME'],
                              self.config['PASSWORD'],
                              self.config['CHANNELS'],
                              logger=self.logger,
                              user=self.config['USER'])

    def _parse_input(self, wait=0.01):
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
        prefix = self.config['CMD_PREFIX']

        while True:
            time.sleep(wait)

            with self.irc.lock:
                args = self.irc.context.get('args')
                command = self.irc.context.get('command')
                message = self.irc.context.get('message')
                raw = self.irc.context.get('raw')

                while not self.context_stale and args:

                    # process regex
                    for regex in self.config['REGEX']:
                        hook = regex['hook']
                        search = re.search(hook, raw)
                        if not search:
                            continue
                        regex['context'] = dict(self.irc.context)
                        regex['context']['regex_search'] = search
                        self.plugin.enqueue_plugin(regex,
                                                   hook,
                                                   raw,
                                                   regex=True)

                    # process for a message
                    if message.startswith(prefix):
                        for plugin in self.config['PLUGINS']:
                            plugin['context'] = dict(self.irc.context)
                            hook = prefix + plugin['hook']
                            self.plugin.enqueue_plugin(plugin, hook, message)

                    # process for a command
                    if command and command.isupper():
                        for event in self.config['EVENTS']:
                            event['context'] = dict(self.irc.context)
                            hook = event['hook']
                            self.plugin.enqueue_plugin(event, hook, command)

                    # irc context consumed; mark it as such
                    self.irc.context['stale'] = True

    @property
    def context_stale(self):
        return self.irc.context.get('stale', True)

    def command(self, hook=None, **kwargs):
        '''This method provides a decorator that can be used to load a
        function into the global plugins list.

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
            self.plugin._update_plugin(plugin, 'PLUGINS')
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
            self.plugin._update_plugin(plugin, 'EVENTS')
            return func

        plugin['hook'] = hook
        plugin.update(kwargs)
        return wrapper

    def regex(self, hook, **kwargs):
        '''Takes a regular expression as a hook.'''
        plugin = {}

        def wrapper(func):
            plugin['funcs'] = [func]
            self.plugin._update_plugin(plugin, 'REGEX')
            return func

        plugin['hook'] = hook
        plugin.update(kwargs)
        return wrapper

    def add_command(self, hook, func):
        self.plugin._add_plugin(hook, func, command=True)

    def add_event(self, hook, func):
        self.plugin._add_plugin(hook, func, event=True)

    def add_regex(self, hook, func):
        self.plugin._add_plugin(hook, func, regex=True)

    def remove_command(self, hook, func):
        self.plugin._remove_plugin(hook, func, command=True)

    def remove_event(self, hook, func):
        self.plugin._remove_plugin(hook, func, event=True)

    def remove_regex(self, hook, func):
        self.plugin._remove_plugin(hook, func, regex=True)

    def reply(self, message, context, action=False, notice=False,
            recipient=None, line_limit=400):

        # conditionally set the recipient automatically
        if recipient is None:
            if context['sender'].startswith('#'):
                recipient = context['sender']
            else:
                recipient = context['user']

        def messages(message):
            message, extra = message[:line_limit], message[line_limit:]
            yield message
            if extra:
                for message in messages(extra):
                    yield message

        for message in messages(message):
            self.irc.send_message(recipient, message, action, notice)

    def run(self, wait=0.1):
        # create connection
        self._create_connection()

        # connect
        self.connection.connect()

        # start the irc wrapper
        self.irc.run()

        # start the input parsing loop in a new thread
        thread.start_new_thread(self._parse_input, ())

        while True:
            time.sleep(wait)
