from base import IrcTkTestCase
from mock import Mock


class ConfigTestCase(IrcTkTestCase):
    def setUp(self):
        IrcTkTestCase.setUp(self)
        obj = Mock()
        obj.SERVER = 'irc.voxinfinitus.net'
        obj.PORT = 6667
        obj.SSL = False
        obj.TIMEOUT = 300
        obj.NICK = 'hax0r'
        obj.REALNAME = 'A Python Bot'
        obj.CHANNELS = ['#voxinfinitus']
        self.obj = obj

    def test_from_pyfile(self):
        self.bot.config.from_pyfile('tests/data/settings.cfg')
        self.assertEqual(self.bot.config['SERVER'], 'irc.voxinfinitus.net')
        self.assertEqual(self.bot.config['PORT'], 6667)
        self.assertEqual(self.bot.config['SSL'], False)
        self.assertEqual(self.bot.config['NICK'], 'hax0r')
        self.assertEqual(self.bot.config['REALNAME'], 'A Python Bot')
        self.assertEqual(self.bot.config['CHANNELS'], ['#voxinfinitus'])

    def test_from_pyfile_bad_filepath(self):
        self.assertRaises(IOError,
                          self.bot.config.from_pyfile,
                          ('some/bad/path/settings.cfg'))

    def test_from_object(self):
        self.bot.config.from_object(self.obj)
        self.assertEqual(self.bot.config['SERVER'], 'irc.voxinfinitus.net')
        self.assertEqual(self.bot.config['PORT'], 6667)
        self.assertEqual(self.bot.config['SSL'], False)
        self.assertEqual(self.bot.config['NICK'], 'hax0r')
        self.assertEqual(self.bot.config['REALNAME'], 'A Python Bot')
        self.assertEqual(self.bot.config['CHANNELS'], ['#voxinfinitus'])
