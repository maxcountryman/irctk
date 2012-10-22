# -*- coding: utf-8 -*-
'''
    irctk.reloader
    --------------

    Almost entirely lifted from Flask. Thanks!
'''

import os
import subprocess
import sys
import thread
import time


def _iter_module_files():
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


def _reloader_stat_loop(logger, extra_files=None, interval=1):
    from itertools import chain
    mtimes = {}
    while True:
        for filename in chain(_iter_module_files(), extra_files or ()):
            try:
                mtime = os.stat(filename).st_mtime
            except OSError:
                continue

            old_time = mtimes.get(filename)
            if old_time is None:
                mtimes[filename] = mtime
                continue
            elif mtime > old_time:
                message = ' * Detected change in {filename}, reloading'
                logger.info(message.format(filename=filename))
                sys.exit(3)
        time.sleep(interval)


def restart_with_reloader(logger):
    while True:
        logger.info(' * Restarting with reloader')
        args = [sys.executable] + sys.argv
        new_environ = os.environ.copy()
        new_environ['IRCTK_RUN_MAIN'] = 'true'

        exit_code = subprocess.call(args, env=new_environ)
        if exit_code != 3:
            return exit_code


def run_with_reloader(main_func, logger, extra_files=None, interval=1):
    import signal
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))

    if os.environ.get('IRCTK_RUN_MAIN') == 'true':
        thread.start_new_thread(main_func, ())
        try:
            _reloader_stat_loop(logger, extra_files, interval)
        except KeyboardInterrupt:
            return
    try:
        sys.exit(restart_with_reloader(logger))
    except KeyboardInterrupt:
        pass
