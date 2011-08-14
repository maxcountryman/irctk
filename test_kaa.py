import unittest
import inspect

from kaa import Kaa


class BotTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bot = Kaa()
        
    def test_config(self):
        self.assertTrue(isinstance(self.bot.config, dict))
    
    def test_event(self):
        @self.bot.event('JOIN')
        def on_join():
            pass
        self.assertTrue(isinstance(self.bot.config['EVENTS'], list))
        for event in self.bot.config['EVENTS']:
            if event['hook'] == 'JOIN':
                event = event['func']
        self.assertTrue(inspect.isfunction(event))
