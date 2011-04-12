from voxbot.bot import Plugin

import urllib
import re

class Fika(Plugin):
    '''usage: ^fika'''
    
    def __init__(self, bot):
        super(Fika, self).__init__(bot)
        self._send_response()
    
    @Plugin.command('^fika')
    def _send_response(self, *args):
		url = 'http://isitfika.net/index.php'
		result = urllib.urlopen(url)
		lines = result.read().split("\n")
		found = False
		for l in lines:
			if re.search("Nej", l) != None:
				found = True

		if found:
			self.bot.msg(self.sender, "It's not fika :(")
			print "Not fika :("
		else:
			self.bot.msg(self.sender, "It is fika!")
			print "Fika!"
