import unittest

from irctk.plugins import Context, PluginHandler


class ContextTestCase(unittest.TestCase):
    def setUp(self):
        line = {'line': 'foo'}
        args = {'args': 'bar'}
        self.context = Context(line, args)

    def test_context(self):
        self.assertEqual(self.context.line, {'line': 'foo'})
        self.assertEqual(self.context.args, {'args': 'bar'})


class PluginHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.config = {'PLUGINS': [], 'EVENTS': [], 'MIN_WORKERS': 3}
        self.logger = None
        self.thread_pool = None
        self.plugins = \
                PluginHandler(self.config, self.logger, self.thread_pool)

    def flush_plugin_lists(self):
        self.config['PLUGINS'] = ['foo', 'bar']
        self.config['EVENTS'] = ['foo', 'bar']
        self.assertEqual(self.config['PLUGINS'], ['foo', 'bar'])
        self.assertEqual(self.config['EVENTS'], ['foo', 'bar'])

        self.plugins.flush_plugin_lists()
        self.assertEqual(self.config['PLUGINS'], [])
        self.assertEqual(self.config['EVENTS'], [])

    def test_add_plugin(self):
        self.plugins.add_plugin('hook', 'func1')
        self.plugins.add_plugin('hook', 'func2')
        self.assertEqual(self.config['PLUGINS'][0]['hook'], 'hook')
        self.assertEqual(self.config['PLUGINS'][0]['funcs'],
                         ['func1', 'func2'])

        self.plugins.add_plugin('hook', 'func', event=True)
        self.assertEqual(self.config['EVENTS'][0]['hook'], 'hook')
        self.assertEqual(self.config['EVENTS'][0]['funcs'], ['func'])

    def test_remove_plugin(self):
        self.plugins.add_plugin('hook', 'func1')
        self.plugins.add_plugin('hook', 'func2')
        self.plugins.remove_plugin('hook', 'func1')
        self.assertEqual(self.config['PLUGINS'][0]['hook'], 'hook')
        self.assertEqual(self.config['PLUGINS'][0]['funcs'], ['func2'])

        self.plugins.remove_plugin('hook', 'func2')
        self.assertEqual(self.config['PLUGINS'], [])

    def test_update_plugins(self):
        plugin = {'hook': 'foo', 'funcs': 'bar'}
        self.plugins.update_plugins(plugin, 'PLUGINS')
        self.assertEqual(self.config['PLUGINS'][0], plugin)

    def test_enqueue_plugin(self):
        pass

    def test_dequeue_plugin(self):
        pass


if __name__ == '__main__':
    unittest.main()
