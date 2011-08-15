import unittest
import inspect
import thread

from kaa.bot import TestBot


class TestSettings(object):
    SERVER = 'irc.example.net'
    PORT = 6667
    SSL = False
    TIMEOUT = 300
    NICK = 'test'
    REALNAME = 'Test Bot'
    CHANNELS = ['#channel']


class BotTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bot = TestBot()
        self.bot.config.from_object(TestSettings)
    
    def test_config(self):
        self.assertTrue(isinstance(self.bot.config, dict))
        self.assertTrue(self.bot.config.get('SERVER'))
        self.assertTrue(self.bot.config.get('PORT'))
        self.assertTrue(isinstance(self.bot.config.get('PORT'), int))
        self.assertFalse(self.bot.config.get('SSL'))
        self.assertTrue(isinstance(self.bot.config.get('SSL'), bool))
        self.assertTrue(self.bot.config.get('TIMEOUT'))
        self.assertTrue(isinstance(self.bot.config.get('TIMEOUT'), int))
        self.assertTrue(self.bot.config.get('NICK'))
        self.assertTrue(self.bot.config.get('CHANNELS'))
        self.assertTrue(isinstance(self.bot.config.get('CHANNELS'), list))
    
    def test_create_command(self):
        @self.bot.command('test')
        def test_command():
            pass
        self.assertTrue(isinstance(self.bot.config['PLUGINS'], list))
        for plugin in self.bot.config['PLUGINS']:
            self.assertTrue(plugin.get('hook'))
            self.assertTrue(plugin.get('func'))
            if plugin['hook'] == 'test':
                plugin = plugin['func']
        self.assertTrue(inspect.isfunction(plugin))
    
    def test_create_event(self):
        @self.bot.event('JOIN')
        def test_event():
            pass
        self.assertTrue(isinstance(self.bot.config['EVENTS'], list))
        for event in self.bot.config['EVENTS']:
            self.assertTrue(event.get('hook'))
            self.assertTrue(event.get('func'))
            if event['hook'] == 'JOIN':
                event = event['func']
        self.assertTrue(inspect.isfunction(event))
    
    def test_ping(self):
        self.bot.irc.run()
        thread.start_new_thread(self.bot.run, ())
        line = 'PING :test\r\n'
        self.bot.connection.inp.put(line)
        self.assertTrue('PONG :test' in self.bot.irc.out_buffer)
        self.bot.shutdown = True
    
    def test_run_command(self):
        self.bot.irc.run()
        thread.start_new_thread(self.bot.run, ())
        line = ':nick!~user@127.0.0.1 PRIVMSG #channel :.test'
        self.bot.irc.out_buffer += line
        self.assertTrue(self.bot.irc.out_buffer != '')
        self.assertTrue(line in self.bot.irc.out_buffer)
        self.bot.shutdown = True


class ClientTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bot = TestBot()
    
    def test_run_client(self):
        pass
