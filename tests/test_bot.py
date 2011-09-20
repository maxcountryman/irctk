import unittest

from irctk.bot import Bot


class BotTestCase(unittest.TestCase):
    '''This test case is used to test the Bot class methods.'''
    
    def setUp(self):
        self.bot = Bot()
        self.assertNotEquals(self.bot._instance, None)
        #self.assertTrue(isinstance(self.bot, None))
        self.assertTrue(self.bot.root_path)
        self.assertTrue(self.bot.logger)
        self.assertTrue(self.bot.default_config)
        self.assertTrue(self.bot.config)
        self.assertTrue(self.bot.plugin)
    
    def test_create_connection(self):
        self.bot._create_connection()
        self.assertTrue(self.bot.connection)
        self.assertTrue(self.bot.irc)
    
    def test_parse_input(self):
        pass
    
    def test_reloader_loop(self):
        pass
    
    def test_reloader(self):
        pass
    
    def test_command(self):
        @self.bot.command
        def foo():
            return 'bar'
        
        func = foo
        self.assertEqual(self.bot.config['PLUGINS'][0], {'funcs': [func], 'hook': 'foo'})
    
    def test_event(self):
        @self.bot.event('JOIN')
        def foo():
            return 'bar'
        
        func = foo
        self.assertEqual(self.bot.config['EVENTS'][0], {'funcs': [func], 'hook': 'JOIN'})
    
    def test_reply(self):
        pass
    
    def test_run(self):
        pass


if __name__ == '__main__':
    unittest.main()

