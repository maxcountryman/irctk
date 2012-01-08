'''
    irctk.reloader
    --------------
    
    Logic for dyanmic reloading upon file changes.
'''


import os
import sys
import time
import threading
import imp


class ReloadHandler(threading.Thread):
    def __init__(self, plugin_lists, plugin_handler, logger):
        threading.Thread.__init__(self)
        self.plugin_lists = plugin_lists
        self.plugin = plugin_handler
        self.logger = logger
        self.daemon = True
        self.start()
    
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
    
    def _reloader(self, fnames, wait):
        '''This reloader is based off of the Flask reloader which in turn is 
        based off of the CherryPy reloader.
        
        This internal method takes two paramters, `fnames` and `wait.` Here 
        we loop over a list of file names, `fnames`, using `os.stat` to 
        determine if the mtime of the file has been changed. If so we use 
        `imp.load_source` to reload the module.
        
        The `fnames` parameter should be a list of files names to be parsed by 
        the reloader.
        
        A callback function, `callback` may be provided as a function to be 
        called when the file is reloaded.
        
        The `wait` parameter specifies the time in seconds to run 
        `time.sleep()`.
        ''' 
        
        mtimes = {}
        
        while True:
            for filename in fnames:
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError, e:
                    self.logger.error('Reloader error: ' + e)
                    continue
                
                old_time = mtimes.get(filename)
                if old_time is None:
                    mtimes[filename] = mtime
                elif mtime > old_time:
                    mtimes[filename] = mtime
                    
                    self.logger.info('Changes detected; reloading ' + filename)
                    filtered_lists = self.plugin.filter_plugin_lists(self.plugin_lists, filename)
                    
                    f = os.path.split(filename)[-1]
                    f = os.path.splitext(f)[0]
                    
                    try:
                        imp.load_source(f, filename)
                    except Exception, e:
                        self.logger.error('Failed loading plugin: ' + str(e))
                        continue
                    finally:
                        mtimes[filename] = mtime
                    
                    if filtered_lists:
                        self.plugin.restore_plugin_lists(self.plugin_lists, filtered_lists)
                        
            time.sleep(wait)
    
    def run(self):
        self._reloader_loop()
