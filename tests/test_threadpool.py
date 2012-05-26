from irctk.threadpool import ThreadPool, Worker
from base import IrcTkTestCase


class ThreadPoolTestCase(IrcTkTestCase):
    def setUp(self):
        IrcTkTestCase.setUp(self)

        self.min_workers = 3
        self.tp = ThreadPool(self.min_workers)
        self.assertEqual(self.tp.min_workers, 3)
        self.assertEqual(self.tp.logger, None)
        self.assertEqual(self.tp.wait, 0.01)
        self.assertTrue(self.tp.daemon is not None)

        self.worker = Worker(self.tp.tasks, None)
        self.assertEqual(self.tp.tasks, self.worker.tasks)
        self.assertEqual(None, self.worker.logger)

    def foo(self, *args, **kwargs):
        return args or kwargs or 'bar'

    def bad_foo(self):
        raise Exception

    def test_enqueue_task(self):
        self.tp.enqueue_task('foo', 'bar')
        task = self.tp.tasks.get()
        self.assertEqual(('foo', ('bar',), {}), task)

        self.tp.enqueue_task('foo', 'bar', test=True)
        task = self.tp.tasks.get()
        self.assertEqual(('foo', ('bar',), {'test': True}), task)

    def test_spawn_worker(self):
        self.tp._spawn_worker()
        self.assertTrue(self.tp.too_few_workers)

        # spawn enough workers to surpass too_few_workers
        for i in range(3):
            self.tp._spawn_worker()
        self.assertFalse(self.tp.too_few_workers)
