#! /usr/bin/env python

import os
import sys

import gevent
import yaml

from core.bot import Bot

if __name__ == '__main__':
    
    if not os.path.isfile('settings.yaml'):
        print 'Error: Could not find the settings file. Please create `settings.yaml` and fill it accordingly.'
        sys.exit()

    settings_array = yaml.load_all(open('settings.yaml'))
    
    spawn_bot = lambda setting: Bot(setting)

    jobs = [gevent.spawn(spawn_bot, setting) for setting in settings_array]
    gevent.joinall(jobs)

