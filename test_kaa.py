import unittest
import inspect

from kaa import Kaa


class BotTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bot = Kaa()
        
    def test_config(self):
        self.assertTrue(isinstance(self.bot.config, dict))
    
    def test_command(self):
        @self.bot.command('test')
        def test_command():
            pass
        self.assertTrue(isinstance(self.bot.config['PLUGINS'], list))
        for plugin in self.bot.config['PLUGINS']:
            assert(plugin['hook'])
            assert(plugin['func'])
            if plugin['hook'] == 'test':
                plugin = plugin['func']
        self.assertTrue(inspect.isfunction(plugin))
    
    def test_event(self):
        @self.bot.event('JOIN')
        def test_event():
            pass
        self.assertTrue(isinstance(self.bot.config['EVENTS'], list))
        for event in self.bot.config['EVENTS']:
            assert(event['hook'])
            assert(event['func'])
            if event['hook'] == 'JOIN':
                event = event['func']
        self.assertTrue(inspect.isfunction(event))
