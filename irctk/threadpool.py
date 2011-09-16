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
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kwargs = self.tasks.get()
            try: 
                func(*args, **kwargs)
            except Exception, e:
                error = 'Worker error: {0}'.format(e)
                self.logger.error(error)
            self.tasks.task_done()


class ThreadPool(threading.Thread):
    '''This class provides an interface to a thread pool mechanism. Tasks may 
    be enqueued via `cls.enqueue_task`. Worker threads are added via 
    `cls.worker`.
    
    A given number, i.e. `workers`, of workers will be spawned upon 
    instantiation.
    
    Inherits from `threading.Thread`.
    '''
    
    def __init__(self, workers, logger, wait=0.1):
        threading.Thread.__init__(self)
        self.tasks = Queue.Queue(workers)
        self.workers = workers
        self.max_workers = workers
        self.number_of_workers = 0
        self.logger = logger
        self.wait = wait
        self.start()
        
    def enqueue_task(self, func, *args, **kwargs):
        task = (func, args, kwargs)
        self.tasks.put(task)
    
    def worker(self):
        Worker(self.tasks, self.logger)
    
    def run(self):
        while True:
            time.sleep(self.wait)
            
            for worker in range(self.workers):
                self.number_of_workers += 1
                
                if self.number_of_workers < self.max_workers:
                    self.worker() # spawn a worker
