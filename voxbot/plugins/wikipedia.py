'''Wikipedia plugin'''

from voxbot.bot import Plugin

import subprocess
import urllib

class Wikipedia(Plugin):
    '''usage: ^wiki [search terms]'''
    
    def __init__(self, bot):
        super(Wikipedia, self).__init__(bot)
        self._search()
    
    @Plugin.command('^wiki')
    def _search(self, *args):
        q = args[-1]
        q = subprocess.os.popen('dig +short txt {0}.wp.dg.cx'.format(q)).read()
        q = q.decode('string-escape')
        q = urllib.unquote(q)
        q = ''.join([c for c in q][:q.find('" "')]) + ''.join([c for c in q][q.find('" "')+3:])
        q = q[1:-1]
        q = q[0:-1]
        
        if not q:
            error = 'Request error: no results'
            self.reply(error)
            self.logger.warning(error)
        else:
            self.reply(q)
