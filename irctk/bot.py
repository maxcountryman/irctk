# -*- coding: utf-8 -*-
'''
    irctk.bot
    ---------

    A "bot" application layer sitting on top of an IRC connection.
'''

import inspect
import logging
import os
import re
import shlex
import subprocess
import time

from irctk.config import Config
from irctk.irc import Irc
from irctk.plugins import PluginHandler
from irctk.reloader import run_with_reloader


class Bot(object):
    # set our root path
    root_path = os.path.abspath('')

    # base configuration
    default_config = {'SERVER': '',
                      'PORT': 6667,
                      'PASSWORD': None,
                      'SSL': False,
                      'TIMEOUT': 300,
                      'NICK': '',
                      'REALNAME': '',
                      'CHANNELS': [],
                      'PLUGINS': [],
                      'EVENTS': [],
                      'REGEX': [],
                      'MAX_WORKERS': 7,
                      'MIN_WORKERS': 3,
                      'CMD_PREFIX': '.',
                      'UPSTREAM_BRIDGE': '/tmp/irctk_upstream'}

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.config = Config(self, self.root_path, self.default_config)
        self.plugin = PluginHandler(self)


    def _parse_input(self, interval=.1):
        prefix = self.config['CMD_PREFIX']

        while True:
            with self.irc.lock:
                context = self.irc.context

                args = context.get('args')
                command = context.get('command')
                message = context.get('message')
                raw = context.get('raw')

                while args and not self.irc.context.get('stale', True):
                    # process regex
                    for regex in self.config['REGEX']:
                        hook = regex['hook']
                        search = re.search(hook, raw)
                        if not search:
                            continue
                        regex['context'] = dict(context)
                        regex['context']['regex_search'] = search
                        self.plugin.enqueue_plugin(regex,
                                                    hook,
                                                    raw,
                                                    regex=True)

                    # process message
                    if message.startswith(prefix):
                        for plugin in self.config['PLUGINS']:
                            plugin['context'] = dict(context)
                            hook = prefix + plugin['hook']
                            self.plugin.enqueue_plugin(plugin, hook, message)

                    # process command
                    if command and command.isupper():
                        for event in self.config['EVENTS']:
                            event['context'] = dict(context)
                            hook = event['hook']
                            self.plugin.enqueue_plugin(event, hook, command)
                    self.irc.context['stale'] = True
            time.sleep(interval)

    def connect(self):
        self.irc = Irc(self.config['UPSTREAM_BRIDGE'], self.logger)
        bridge_cmd = ('nohup python {mod} {host} {port} {nick} {realname} -x '
                '{ssl} -ch {channels} &')
        channels = ''.join(' "' + c + '"' for c in self.config['CHANNELS'])

        # check for the pid of the server bridge
        if not os.path.isfile('/tmp/irctk_connect.pid'):
            with open('/tmp/irctk_connect.pid', 'w') as f:
                f.write('')
        else:
            with open('/tmp/irctk_connect.pid', 'r') as f:
                pid = int(f.read())
                try:
                    os.kill(pid, 0)
                except OSError:
                    # attempt to launch the server bridge if it's not running
                    from irctk import connection
                    cmd = bridge_cmd.format(mod=connection.__file__,
                                            host=self.config['SERVER'],
                                            port=self.config['PORT'],
                                            nick=self.config['NICK'],
                                            realname=self.config['REALNAME'],
                                            ssl=int(self.config['SSL']),
                                            channels=channels)
                    print cmd
                    subprocess.Popen(shlex.split(cmd))

        self.irc.connect()
        self._parse_input()

    def command(self, hook=None, **kwargs):
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
        plugin = {}

        def wrapper(func):
            plugin['funcs'] = [func]
            self.plugin._update_plugin(plugin, 'EVENTS')
            return func

        plugin['hook'] = hook
        plugin.update(kwargs)
        return wrapper

    def regex(self, hook, **kwargs):
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
            recipient=None, line_limit=450):

        # conditionally set the recipient automatically
        if recipient is None:
            if context['sender'].startswith('#'):
                recipient = context['sender']
            else:
                recipient = context['user']

        def messages(msg):
            message, extra = msg[:line_limit], msg[line_limit:]

            if not extra:
                yield message

            if extra:
                yield message.rsplit(' ', 1)[0]
                extra = message.rsplit(' ', 1)[-1] + extra
                for msg in messages(extra):
                    yield msg

        for msg in messages(message):
            self.irc.send_message(recipient, msg, action, notice)

    def run(self):
        run_with_reloader(self.connect, self.logger)
