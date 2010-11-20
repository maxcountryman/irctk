#! /usr/bin/env python

import gevent

from core.bot import Bot
from plugins.base import *
from plugins.greet import *
from plugins.google import *

if __name__ == '__main__':
    badass_bot = lambda : Bot('irc.voxinfinitus.net', 'Kaa_', channels=['#voxinfinitus','#landfill'])
    #kickass_bot = lambda : Bot('irc.freenode.net', 'Kaa_', channels=['#freebsdsecured','#landfill'])

    jobs = [gevent.spawn(badass_bot)]
    gevent.joinall(jobs)
