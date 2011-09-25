'''
    irctk.threadpool
    ----------------
    
    A thread pool to be used with plugin dispatching.
'''

import sys
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
    
    def __init__(self, tasks, logger, timeout):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.busy = False
        self.tasks = tasks
        self.logger = logger
        self.timeout = timeout
        self.daemon = True
        self.start()
    
    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None
    
    def localtrace(self, frame, why, arg):
        if self.busy and (time.time() - self.start_time > self.timeout):
            if why == 'line':
                raise SystemExit()
        return self.localtrace
    
    def run(self):
        sys.settrace(self.globaltrace)
        while not self.shutdown:
            func, args, kwargs = self.tasks.get()
            try:
                self.busy = True
                self.start_time = time.time()
                func(*args, **kwargs)
            except SystemExit:
                self.logger.info('Worker terminated for misbehaving.')
                sys.exit()
            except Exception, e:
                error = 'Worker error: {0}'.format(e)
                self.logger.error(error)
            finally:
                self.busy = False
            self.tasks.task_done()
        else:
            sys.exit()


class ThreadPool(threading.Thread):
    '''This class provides an interface to a thread pool mechanism. Tasks may 
    be enqueued via `cls.enqueue_task`. Worker threads are added via 
    `cls.worker`.
    
    A given number, i.e. `workers`, of workers will be spawned upon 
    instantiation.
    
    Inherits from `threading.Thread`.
    '''
    
    def __init__(self, min_workers, logger, max_workers=11, timeout=300, wait=0.01):
        threading.Thread.__init__(self)
        self.tasks = Queue.Queue()
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.timeout = timeout
        self.workers = []
        self.logger = logger
        self.wait = wait
        self.daemon = True
        self.start()
        
    def enqueue_task(self, func, *args, **kwargs):
        task = (func, args, kwargs)
        self.tasks.put(task)
    
    def _new_worker(self):
        self.logger.info('Starting new worker.')
        new_worker = Worker(self.tasks, self.logger, self.timeout)
        self.workers.append(new_worker)
    
    def _kill_worker(self):
        self.logger.info('Stopping worker.')
        i = 0
        while i < len(self.workers):
            worker = self.workers[i]
            if not worker.shutdown:
                worker.shutdown = True
                break
            else:
                i += 1
    
    def run(self):
        while True:
            time.sleep(self.wait)

            for i in xrange(len(self.workers) - 1):
                if not self.workers[i].is_alive():
                    del self.workers[i]
            
            idle_workers = lambda : len([worker for worker in self.workers \
                                        if not worker.busy and not worker.shutdown])
            too_few_workers = lambda : len(self.workers) < self.min_workers
            more_workers_ok = lambda : len(self.workers) < self.max_workers
            too_many_workers = lambda : idle_workers() > self.min_workers
            
            if too_few_workers():
                self._new_worker() # spawn a worker
            
            if idle_workers() < self.min_workers and more_workers_ok():
                self._new_worker()
            
            if too_many_workers():
                self._kill_worker()

