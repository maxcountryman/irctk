'''Hacky plugin loader.'''

import imp
import sys
import os

def load_plugins(bot, plugins):
    '''Loads plugins from source files via imp based on the items in a list, 
    `plugins`.'''
    
    logger = bot.logger
    
    sys.path.insert(0, os.path.abspath('.'))
    #os.chdir('.') 
    for p in plugins:
        try:
            imp.load_source(p, 'voxbot/plugins/' + p.lower() + '.py')
        except ImportError, e:
            logger.warning('Failed loading plugin with error: ' + e)
    return [sys.modules[p].__dict__[p](bot) for p in plugins] # run 'em

