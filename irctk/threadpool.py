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
    
    def __init__(self, workers, logger, max_workers=11, wait=0.05):
        threading.Thread.__init__(self)
        self.tasks = Queue.Queue()
        self.workers = workers
        self.max_workers = max_workers
        self.number_of_workers = 0
        self.logger = logger
        self.wait = wait
        self.daemon = True
        self.start()
        
    def enqueue_task(self, func, *args, **kwargs):
        task = (func, args, kwargs)
        self.tasks.put(task)
    
    def worker(self):
        Worker(self.tasks, self.logger)
    
    def run(self):
        while True:
            time.sleep(self.wait)
            
            too_few_workers = lambda : self.number_of_workers < self.workers
            more_workers_ok = lambda : self.number_of_workers < self.max_workers
            too_many_workers = lambda : self.number_of_workers > self.workers
            
            if too_few_workers():
                self.number_of_workers += 1
                self.worker() # spawn a worker
            
            #if not self.tasks.empty() and more_workers_ok():
            #    self.number_of_workers += 1
            #    self.worker()
            
            #if self.tasks.empty() and too_many_workers():
            #    self.number_of_workers -= 1
