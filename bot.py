import gevent

from core.irc import Irc
from core.hooks import *
from core.parser import *

class Bot(object):
    
    def __init__(self):
        jobs = [gevent.spawn(self.connect),gevent.spawn(self.parse)]
        gevent.joinall(jobs)
    
    def connect(self):
            self.irc = Irc('irc.voxinfinitus.net', 'Kaa', 6697, True, ['#voxinfinitus','#landfill'])

    def parse(self):
        while True: # magic loop
            event_queue = self.irc.conn.iqueue.get()
            parsed_shit = parse_raw_input(event_queue)
            pub = Dispatcher(parsed_shit)

    @subscribe('PING')
    def pong(inpu):
        self.irc.cmd('PONG', inpu.paramlist)

badass_bot = Bot()
