import os
import sys
import time
import thread
import imp
import inspect


class Reload(object):
    '''This reloader is based off of the Flask reloader which in turn is 
    based off of the CherryPy reloader.

    It runs continuously monitoring the plugin files for changes. It polls the
    files for changes every `interval` seconds. Interval is an class value and
    can be changed on the fly.
    '''
    interval = 1
    
    def __init__(self, config, logger):
        self.mtimes = {}
        self.config = config
        self.logger = logger
    
    def _iter_module_files(self):
        '''This generator method yields the source files for all imported
        modules.
        '''
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
                    yield os.path.abspath(filename)
    
    def _filter_plugin_list(self, plugin_list, filename):
        '''Filter all functions from the plugins in `plugin_list` that are
        defined in file `filename`. Removes the plugin from the list if it is
        empty after removing the functions.

        The list of removed plugins is returned and can be used to restore the
        changes.
        '''
        removed_plugins = {}
        for i in reversed(xrange(len(plugin_list))):
            hook = plugin_list[i]['hook']
            functions = plugin_list[i]['funcs']
            for x in reversed(xrange(len(functions))):
                if inspect.getabsfile(functions[x]) == filename:
                    self.logger.info('removing function from {0}'.format(hook))
                    if hook not in removed_plugins:
                        removed_plugins[hook] = []
                    removed_plugins[hook].append(functions.pop(x))
            if not plugin_list[i]['funcs']:
                del plugin_list[i]
        return removed_plugins
    
    def _repair_plugin_list(self, plugin_list, removed):
        '''Put the items _filter_plugin_list() returned back in the
        plugin_list.
        '''
        for key, value in removed.items():
            if key not in plugin_list:
                plugin_list[key] = []
            plugin_list[key].extend(value)
    
    def _reloader_loop(self):
        '''This internal method runs continuously monitoring the plugin files
        for changes. It polls the files for changes every `interval` seconds.
        Interval is an class value and can be changed on the fly.
        '''
        
        while True:
            for filename in self._iter_module_files():
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError, e:
                    self.logger.error('Reloader error: {0}'.format(e))
                    continue
                
                if filename in self.mtimes and mtime != self.mtimes[filename]:
                    self._reload_file(filename)
                
                self.mtimes[filename] = mtime
            
            time.sleep(self.interval)
    
    def _reload_file(self, filename):
        '''This internal method reloads the module loaded from `filename`.

        First all hooks defined in this file are removed from our lists. After
        reloading the file they should be back in. If there is an exception
        while reloading the file the changes are undone.
        '''
        
        self.logger.info('Changes detected; reloading {0}'.format(filename))

        removed_plugins = self._filter_plugin_list(self.config['PLUGINS'], filename)
        removed_events = self._filter_plugin_list(self.config['EVENTS'], filename)

        module = os.path.split(filename)[-1]
        module = os.path.splitext(module)[0]
        try:
            imp.load_source(module, filename)
        except Exception, e:
            self.logger.error('Failed loading plugin: ' + str(e))
            self._repair_plugin_list(self.config['PLUGINS'], removed_plugins)
            self._repair_plugin_list(self.config['EVENTS'], removed_events)
        
    def run(self):
        '''This method is used to start the monitoring thread.'''
        thread.start_new_thread(self._reloader_loop, ())
        self.logger.info('Plugin watcher and reloader started.')

