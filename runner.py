#! /usr/bin/env python

import os, sys

import gevent
import yaml

from core.bot import Bot

# better find a way to normalize plugin imports
from plugins.base import *
from plugins.greet import *
from plugins.google import *
from plugins.quotes import *

if __name__ == '__main__':
    
    if not os.path.isfile('settings.yaml'):
        print 'Error: Could not find the settings file. Please create `settings.yaml` and fill it accordingly.'
        sys.exit()
    
    bots = []
    settings_array = yaml.load_all(open('settings.yaml'))
    for setting in settings_array:
        print setting
        bots.append((lambda : Bot(setting)))

    jobs = [gevent.spawn(bot) for bot in bots]
    gevent.joinall(jobs)
