'''
    irctk.threadpool
    ----------------
    
    A thread pool to be used with plugin dispatching.
'''

import threading
import Queue
import time


class Worker(threading.Thread):
    '''This class may be used to create new worker threads and is used by the 
    thread pool class to do as such. It will take a given queue, `tasks`, and 
    extract from it the next task. This operation assumes the task is a 
    function packed in the form, func, args, kwargs. Upon extracting the task 
    the function is executed and the queue notified the task was completed.
    
    Inherits from `threading.Thread`.
    '''
    
    def __init__(self, tasks, logger):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.logger = logger
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kwargs = self.tasks.get()
            try:
                func(*args, **kwargs)
            except Exception, e:
                print e
                error = 'Error while executing function in worker: {0} - {1}'.format(func.__name__, e)
                self.logger.error(error)
            finally:
                self.tasks.task_done()


class ThreadPool(threading.Thread):
    '''This class provides an interface to a thread pool mechanism. Tasks may 
    be enqueued via `cls.enqueue_task`. Worker threads are added via 
    `cls.spawn_worker`.
    
    A given number, i.e. `min_workers`, of workers will be spawned upon 
    instantiation.
    
    Inherits from `threading.Thread`.
    
    Example usage might go something like this:
        
        def square(x):
            return x * x
        
        thread_pool = ThreadPool(3, 7, logger=logger)
        thread_pool.enqueue_task(square, 2) # enqueue a func with args
        
    This will enqueue the above function and call it. In practical usage the 
    function should serve as some kind of callback.
    '''
    
    def __init__(self, min_workers, logger=None, wait=0.01):
        threading.Thread.__init__(self)
        self.tasks = Queue.Queue()
        self.min_workers = min_workers
        self.workers = 0
        self.logger = logger
        self.wait = wait
        self.daemon = True
        self.start()
        
    def enqueue_task(self, func, *args, **kwargs):
        task = (func, args, kwargs)
        self.tasks.put(task)
    
    def _spawn_worker(self):
        Worker(self.tasks, self.logger)
    
    def run(self):
        while True:
            time.sleep(self.wait)
            
            too_few_workers = lambda : self.workers < self.min_workers
            
            if too_few_workers():
                self.workers += 1
                self._spawn_worker()

