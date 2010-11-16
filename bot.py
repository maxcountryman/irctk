from core.irc import Irc

import gevent

if __name__ == '__main__':

    bot = lambda : Irc('irc.voxinfinitus.net', 'Kaa', 6697, True, ['#voxinfinitus','#landfill'])
    another_bot = lambda : Irc('irc.freenode.net', 'Kaa_', 6667, False, ['#landfill'])
    
    jobs = [gevent.spawn(bot),gevent.spawn(another_bot)]
    gevent.joinall(jobs)
