import gevent

from core.irc import Irc
from core.dispatcher import *
from core.dispatcher import subscribe
from core.dispatcher import Publish

if __name__ == '__main__':
    bot = lambda : Irc('irc.voxinfinitus.net', 'Kaa', 6697, True, ['#voxinfinitus','#landfill'])
    pub = lambda : Publish(bot, False) 
    
    @subscribe('PING')
    def pong(self, event):
        bot.cmd('PONG', event.args)

    jobs = [gevent.spawn(bot), gevent.spawn(pub)]
    gevent.joinall(jobs)
