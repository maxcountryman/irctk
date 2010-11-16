import core.irc
from core import *

import gevent

if __name__ == '__main__':

    irc = irc.Irc

    bot = lambda : irc('irc.voxinfinitus.net', 'Kaa', 6697, True, ['#voxinfinitus','#landfill'])
    another_bot = lambda : irc('irc.freenode.net', 'Kaa_', 6667, False, ['#landfill'])
    
    jobs = [gevent.spawn(bot),gevent.spawn(another_bot)]
    gevent.joinall(jobs)
