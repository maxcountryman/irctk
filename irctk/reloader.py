# -*- coding: utf-8 -*-
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
import inspect


class ReloadHandler(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)

        self.bot = bot
        self.plugin = self.bot.plugin
        self.logger = self.bot.logger

        self.daemon = True
        self.start()

    def _iter_module_files(self):
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

    def _reloader(self, wait=1.0):
        '''This reloader is based off of the Flask reloader which in turn is
        based off of the CherryPy reloader.
        '''

        mtimes = {}
        root_path = self.bot.root_path

        while True:
            fnames = []
            fnames.extend(self._iter_module_files())

            for filename in fnames:
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError, e:
                    self.logger.error('Reloader error: ' + str(e))
                    continue

                old_time = mtimes.get(filename)

                mtimes[filename] = mtime

                if old_time is None:
                    continue
                elif mtime > old_time:
                    self.logger.info('Changes detected; reloading')

                    local_fnames = \
                        set([fname for fname in fnames if root_path in fname])

                    # WARNING: here be dragons

                    # get the ID of the main thread
                    all_threads = dict([(th.name, th.ident)
                                        for th in threading.enumerate()])

                    main_thread_frame = \
                            sys._current_frames()[all_threads['MainThread']]

                    # the main thread stack should contain the frame containing
                    # the filename of the module the bot instance was
                    # instantiated in
                    bot_fname = \
                            inspect.getouterframes(main_thread_frame)[-1][1]

                    local_fnames.add(bot_fname)

                    # make sure we load __init__ first
                    local_fnames = sorted(list(local_fnames))

                    # reload local modules
                    for fname in local_fnames:
                        f = os.path.split(fname)[-1]
                        f = os.path.splitext(f)[0]

                        try:
                            imp.load_source(f, fname)
                        except Exception, e:
                            self.logger.error('Reload failed: ' + str(e))
                            continue

            time.sleep(wait)

    def run(self):
        self._reloader()
