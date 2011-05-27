from voxbot.bot import Plugin

import urllib
import re

class Fika(Plugin):
    '''usage: ^fika'''
    
    def __init__(self, bot):
        super(Fika, self).__init__(bot)
        self._send_response()
    
    @Plugin.command('^fika')
    def _send_response(self, cmd, args):
        url = 'http://isitfika.net/index.php'
        result = urllib.urlopen(url)
        lines = result.read()
        if re.search("Nej", lines) == None:
            self.reply("It is fika")
        else:
            time = re.search("T\-([0-9]+)", lines).group(1)
            self.reply("It's not fika :( Still {0} minutes to go.".format(time))
