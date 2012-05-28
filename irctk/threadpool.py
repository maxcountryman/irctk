# -*- coding: utf-8 -*-
'''
    irctk.threadpool
    ----------------

    A thread pool to be used with plugin dispatching.
'''

import threading
import Queue
import time

DEFAULT_SLEEP = 0.01


class Worker(threading.Thread):
    '''Provides a worker object.

    This class provides a thread worker object which is used by the ThreadPool
    object to execute tasks, i.e. functions.
    '''

    def __init__(self, tasks, logger):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.logger = logger
        self.daemon = True
        self.start()

    def run(self):  # pragma: no cover
        while True:
            func, args, kwargs = self.tasks.get()
            try:
                # try to execute the function
                func(*args, **kwargs)
            except Exception, e:
                # if we fail, raise the exception and log it
                error = 'Error while executing function in worker: {0} - {1}'
                self.logger.error(error.format(func.__name__, e),
                                  exc_info=True)
            finally:
                # no matter what, we need to set the task to done
                self.tasks.task_done()


class ThreadPool(threading.Thread):
    '''This class provides an interface to a thread pool mechanism. Tasks may
    be enqueued via :class:`enqueue_task`. Worker threads are added via
    :class:`spawn_worker`.

    A given number, i.e. `min_workers`, of workers will be spawned upon
    instantiation.

    Inherits from `threading.Thread`.

    Example usage might go something like this::

        def square(n):
            return n * 2

        thread_pool = ThreadPool(3, logger=logger)
        thread_pool.enqueue_task(square, 2)  # enqueue a func with args

    This will enqueue the above function and call it. In practical usage the
    function should serve as some kind of callback.
    '''

    def __init__(self, min_workers, logger=None, wait=DEFAULT_SLEEP):
        threading.Thread.__init__(self)
        self.tasks = Queue.Queue()
        self.min_workers = min_workers
        self.workers = 0
        self.logger = logger
        self.wait = wait
        self.daemon = True
        self.start()

    def _spawn_worker(self):
        self.workers += 1
        Worker(self.tasks, self.logger)

    def enqueue_task(self, func, *args, **kwargs):
        self.tasks.put((func, args, kwargs))

    @property
    def too_few_workers(self):
        return self.workers < self.min_workers

    def run(self):
        while True:
            time.sleep(self.wait)

            if self.workers < self.min_workers:
                self._spawn_worker()
