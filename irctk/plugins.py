# -*- coding: utf-8 -*-
'''
    irctk.plugins
    -------------

    Logic for handling plugin registration and processing.
'''

import inspect
import re

from irctk.threadpool import ThreadPool
from irctk.utils import cached_property


class Context(object):
    def __init__(self, line, args):
        self.line = line
        self.args = args


class PluginHandler(object):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.logger = self.bot.logger

    @cached_property
    def thread_pool(self):
        thread_pool = \
                ThreadPool(self.config['MIN_WORKERS'], logger=self.logger)
        return thread_pool

    def _add_plugin(self, hook, func, command=True, event=False, regex=False):
        '''Allows plugins to be added in the scope of a function.'''
        plugin = {}

        plugin.setdefault('hook', hook)
        plugin.setdefault('funcs', [])

        self.logger.debug(str(plugin['funcs']))

        # add plugin functions
        for i, f in enumerate(plugin['funcs']):
            if f.name == func.name:
                plugin['funcs'][i] = func
            else:
                plugin['funcs'] += [func]

        if command:
            plugin_list = 'PLUGINS'

        if event:
            command = False  # don't process as a command and an event
            plugin_list = 'EVENTS'

        if regex:
            command = False
            plugin_list = 'REGEX'

        self.update_plugin(plugin, plugin_list)

    def _remove_plugin(self, hook, func, command=True, event=False,
            regex=False):
        '''Allows plugins to be removed in the scope of a function.'''
        if command:
            plugin_list = 'PLUGINS'

        if event:
            command = False  # don't process as a command and an event
            plugin_list = 'EVENTS'

        if regex:
            command = False
            plugin_list = 'REGEX'

        plugin_list = self.config[plugin_list]

        hook_found = lambda: hook == existing_plugin['hook']
        func_found = lambda: func in existing_plugin['funcs']

        for existing_plugin in plugin_list:
            if hook_found() and func_found():
                existing_plugin['funcs'].remove(func)

                if not existing_plugin['funcs']:
                    plugin_list.remove(existing_plugin)

    def _update_plugin(self, plugin, plugin_list):
        # contruct plugin list on bot config object if necessary
        if not self.config.get(plugin_list):
            self.config[plugin_list] = []

        # retrive the specified plugin list
        plugin_list = self.config[plugin_list]

        for i, existing_plugin in enumerate(plugin_list):
            if plugin['hook'] == existing_plugin['hook']:
                plugin_list[i]['funcs'] += plugin['funcs']

        def iter_list_hooks():
            for existing_plugin in plugin_list:
                yield existing_plugin['hook']

        if not plugin['hook'] in iter_list_hooks():
            plugin_list.append(plugin)

    def enqueue_plugin(self, plugin, hook, context, regex=False):
        search = None
        if regex:
            search = re.search(hook, context)
            plugin_args = plugin['context']['message']
            plugin['context']['regex_search'] = search
        elif not regex and (context == hook or context.startswith(hook + ' ')):
            plugin_args = \
                    plugin['context']['message'].split(hook, 1)[-1].strip()
        else:
            return

        plugin_context = Context(plugin['context'], plugin_args)
        task = (self.dequeue_plugin, plugin, plugin_context)
        self.thread_pool.enqueue_task(*task)

    def dequeue_plugin(self, plugin, plugin_context):
        for func in plugin['funcs']:
            takes_args = inspect.getargspec(func).args

            action = plugin.get('action', False)
            notice = plugin.get('notice', False)

            try:
                if takes_args:
                    message = func(plugin_context)
                else:
                    message = func()

                if message is None:
                    continue

            except Exception, e:
                self.logger.warning(e, exc_info=True)
                continue

            if message:
                self.bot.reply(message, plugin_context.line, action, notice)
