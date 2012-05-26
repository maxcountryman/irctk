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

    def _reloader(self, wait=1.0):
        '''This reloader is based off of the Flask reloader which in turn is
        based off of the CherryPy reloader.
        '''

        mtimes = {}

        while True:
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
                    filtered_lists = \
                            self.plugin.filter_plugin_lists(self.plugin_lists,
                                                            filename)

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
                        self.plugin.restore_plugin_lists(self.plugin_lists,
                                                         filtered_lists)
            time.sleep(wait)

    def run(self):
        self._reloader()
