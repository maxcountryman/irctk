from irctk import Bot

import unittest


class IrcTkTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = Bot()
