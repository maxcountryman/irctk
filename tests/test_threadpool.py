import unittest
import Queue

from irctk.threadpool import ThreadPool, Worker


class WorkerTestCase(unittest.TestCase):
    '''This test case tests the Worker class methods.'''
    
    def setUp(self):
        def foo():
            pass
        q = Queue.Queue()
        q.put([foo, [], {}])
        self.tasks = q
        self.logger = None
        self.worker = Worker(self.tasks, self.logger)
        
        self.assertEquals(self.worker.logger, None)
        self.assertTrue(self.worker.daemon)
    
    def test_run(self):
        pass


class ThreadPoolTestCase(unittest.TestCase):
    '''This test case tests the ThreadPool class methods.'''
    
    def setUp(self):
        self.min_workers = 3
        self.logger = None
        self.tp = ThreadPool(self.min_workers, self.logger)
        
        self.assertEquals(self.tp.min_workers, 3)
        self.assertEquals(self.tp.logger, None)
        self.assertEquals(self.tp.wait, 0.01)
        self.assertTrue(self.tp.daemon)
    
    def test_enqueue_task(self):
        self.tp.enqueue_task('foo', 'bar')
        task = self.tp.tasks.get()
        self.assertEquals(('foo', ('bar',), {}), task)
        
        test = 'test'
        self.tp.enqueue_task('foo', 'bar', test=True)
        task = self.tp.tasks.get()
        self.assertEquals(('foo', ('bar',), {'test': True}), task)
    
    def test_worker(self):
        pass
    
    def test_run(self):
        pass

if __name__ == '__main__':
    unittest.main()

