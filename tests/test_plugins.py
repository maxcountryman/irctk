import unittest

from irctk.plugins import Context, PluginHandler


class ContextTestCase(unittest.TestCase):
    '''This test case is used to test the Context class methods.'''
    
    def setUp(self):
        line = {'line': 'foo'}
        args = {'args': 'bar'}
        self.context = Context(line, args)

    def test_context(self):
        self.assertEquals(self.context.line, {'line': 'foo'})
        self.assertEquals(self.context.args, {'args': 'bar'})


class PluginHandlerTestCase(unittest.TestCase):
    '''This test case is used to test the PluginHandler class methods.'''
    
    def setUp(self):
        self.config = {'PLUGINS': [], 'EVENTS': [], 'MIN_WORKERS': 3}
        self.logger = None
        self.thread_pool = None
        self.plugins = PluginHandler(self.config, self.logger, self.thread_pool)
    
    def flush_plugin_lists(self):
        self.config['PLUGINS'] = ['foo', 'bar']
        self.config['EVENTS'] = ['foo', 'bar']
        self.assertEquals(self.config['PLUGINS'], ['foo', 'bar'])
        self.assertEquals(self.config['EVENTS'], ['foo', 'bar'])
        
        self.plugins.flush_plugin_lists()
        self.assertEquals(self.config['PLUGINS'], [])
        self.assertEquals(self.config['EVENTS'], [])
    
    def test_add_plugin(self):
        self.plugins.add_plugin('hook', 'func1')
        self.plugins.add_plugin('hook', 'func2')
        self.assertEquals(self.config['PLUGINS'][0]['hook'], 'hook')
        self.assertEquals(self.config['PLUGINS'][0]['funcs'], ['func1', 'func2'])
        
        self.plugins.add_plugin('hook', 'func', event=True)
        self.assertEquals(self.config['EVENTS'][0]['hook'], 'hook')
        self.assertEquals(self.config['EVENTS'][0]['funcs'], ['func'])
    
    def test_remove_plugin(self):
        self.plugins.add_plugin('hook', 'func1')
        self.plugins.add_plugin('hook', 'func2')
        self.plugins.remove_plugin('hook', 'func1')
        self.assertEquals(self.config['PLUGINS'][0]['hook'], 'hook')
        self.assertEquals(self.config['PLUGINS'][0]['funcs'], ['func2'])
        
        self.plugins.remove_plugin('hook', 'func2')
        self.assertEquals(self.config['PLUGINS'], [])
        
    def test_update_plugins(self):
        plugin = {'hook': 'foo', 'funcs': 'bar'}
        self.plugins.update_plugins(plugin, 'PLUGINS')
        self.assertEquals(self.config['PLUGINS'][0], plugin)
    
    def test_enqueue_plugin(self):
        pass
    
    def test_dequeue_plugin(self):
        pass


if __name__ == '__main__':
    unittest.main()

