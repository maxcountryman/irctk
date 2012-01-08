'''
    irctk.plugins
    -------------
    
    Logic for handling plugin registration and processing.
'''

import inspect

from .threadpool import ThreadPool


class Context(object):
    def __init__(self, line, args):
        self.line = line
        self.args = args


class PluginHandler(object):
    def __init__(self, config, logger, reply_method):
        self.config = config
        self.logger = logger
        self.thread_pool = ThreadPool(self.config['MIN_WORKERS'], logger=self.logger)
        self._reply = reply_method
    
    def add_plugin(self, hook, func, command=True, event=False):
        '''TODO'''
        
        plugin = {}
        
        plugin.setdefault('hook', hook)
        plugin['funcs'] = [func]
        
        if event:
            command = False # don't process as a command and an event
            plugin_list = 'EVENTS'
        
        if command:
            plugin_list = 'PLUGINS'
        
        self.update_plugins(plugin, plugin_list)
        
    def remove_plugin(self, hook, func, command=True, event=False):
        '''TODO'''
        
        if event:
            command = False
            plugin_list = 'EVENTS'
        
        if command:
            plugin_list = 'PLUGINS'
        
        plugin_list = self.config[plugin_list]
        
        hook_found = lambda : hook == existing_plugin['hook']
        func_found = lambda : func in existing_plugin['funcs']
        
        for existing_plugin in plugin_list:
            if hook_found() and func_found():
                existing_plugin['funcs'].remove(func)
                
                if not existing_plugin['funcs']:
                    plugin_list.remove(existing_plugin)
    
    def update_plugins(self, plugin, plugin_list):
        '''This internal method updates a given list containing plugins, 
        `plugin_list`, with a plugin dictionary object, `plugin`.
        
        Usually used to update the `PLUGINS` or `EVENTS` list in the 
        configuration dict.
        '''
        
        if not self.config.get(plugin_list):
            self.config[plugin_list] = []
        
        plugin_list = self.config[plugin_list]
        
        for i, existing_plugin in enumerate(plugin_list):
            if plugin['hook'] == existing_plugin['hook']:
                plugin_list[i]['funcs'] += plugin['funcs']
        
        def iter_list_hooks():
            for existing_plugin in plugin_list:
                yield existing_plugin['hook']
        
        if not plugin['hook'] in iter_list_hooks():
            plugin_list.append(plugin)
        
        #for i, existing_plugin in enumerate(self.config[plugin_list]):
        #    if existing_plugin['func'].__name__ == plugin['func'].__name__:
        #        self.config[plugin_list][i] = plugin
        
        #if not plugin in self.config[plugin_list]:
        #self.config[plugin_list].append(plugin)
    
    def enqueue_plugin(self, plugin, hook, context):
        '''This method takes a plugin, hook, and context, as 
        `plugin`, `hook`, and `context`. Checking to see if the context is 
        equivalent to the hook or begins with the hook plus a space, in the 
        second case, indicating a plugin passed with arguments. If such 
        conditions are met the plugin is enqueued in the thread pool.
        '''
        
        if context == hook or context.startswith(hook + ' '):
            plugin_args = plugin['context']['message'].split(hook, 1)[-1].strip()
            plugin_context = Context(plugin['context'], plugin_args)
            
            task = (self.dequeue_plugin, plugin, plugin_context)
            self.thread_pool.enqueue_task(*task)
            #self._dequeue_plugin(plugin, plugin_context)
    
    def dequeue_plugin(self, plugin, plugin_context):
        '''This method assumes that a plugin and plugin context are 
        passed to it as `plugin` and `plugin_context`. It is intended to be 
        called as a plugin is being dequeued, i.e. from a thread pool as 
        called by a worker thread thereof. 
        
        The plugin and plugin context are checked against several conditions 
        that will ultimately affect the formatting of the final message.
        
        if the plugin function does return a message, that message is 
        formatted and sent back to the server via `cls.reply`.
        '''
        
        for func in plugin['funcs']:
            takes_args = inspect.getargspec(func).args
            
            action = False
            if plugin.get('action') == True:
                action = True
            
            notice = False
            if plugin.get('notice') == True:
                notice = True
            
            if takes_args:
                message = func(plugin_context)
            else:
                message = func()
            
            if message:
                self._reply(message, plugin_context.line, action, notice)
    
    def filter_plugin_lists(self, plugin_lists, filename):
        '''TODO'''
        
        filtered_lists = []
        for plugin_list in plugin_lists:
            filtered_list = self._filter_plugin_list(plugin_list, filename)
            filtered_lists.append(filtered_list)
        return filtered_lists
    
    def _filter_plugin_list(self, plugin_list, filename):
        '''TODO'''
        
        def func_is_in_file(func, filename): 
            return inspect.getabsfile(func) == filename
        
        filtered_plugins = {}
        for i, plugin in enumerate(plugin_list):
            
            hook  = plugin['hook']
            funcs = plugin['funcs']
            for j, func in enumerate(funcs):
                if func_is_in_file(func, filename):
                    if not hook in filtered_plugins:
                        filtered_plugins[hook] = []
                    filtered_plugins[hook].append(funcs.pop(j))
            
            if not funcs: # no functions, so delete the hook
                del plugin_list[i]
        
        return filtered_plugins
    
    def restore_plugin_lists(self, plugin_lists, filtered_lists):
        '''TODO'''
        
        for plugin_list in plugin_lists:
            #plugin_list = [] # reset the list
            for filtered_list in filtered_lists:
                self._restore_plugin_list(plugin_list, filtered_list)
        
    def _restore_plugin_list(self, plugin_list, filtered_list):
        '''TODO'''
        
        for plugin in plugin_list:
            for hook, funcs in filtered_list.items():
                if hook not in plugin_list:
                    plugin[hook] = []
                plugin[hook] = funcs
