#!/usr/bin/env python
import gevent

from voxbot import bot, settings

jobs = [gevent.spawn(bot, settings)]

try:
    gevent.joinall(jobs)
finally:
    gevent.killall(jobs)
