import unittest

from irctk.bot import Bot


class BotTestCase(unittest.TestCase):
    '''This test case is used to test the Bot class methods.'''
    
    def setUp(self):
        self.bot = Bot()
    
    def test_update_plugins(self):
        pass
    
    def test_enqueue_plugin(self):
        pass
    
    def test_dequeue_plugin(self):
        pass
    
    def test_parse_input(self):
        pass
    
    def test_reloader_loop(self):
        pass
    
    def test_reloader(self):
        pass
    
    def test_command(self):
        pass
    
    def test_event(self):
        pass
    
    def test_reply(self):
        pass
    
    def test_run(self):
        pass


if __name__ == '__main__':
    unittest.main()

