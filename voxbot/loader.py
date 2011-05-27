'''Hacky plugin loader.'''

import imp
import sys
import os

def load_plugins(bot, plugins):
    '''Loads plugins from source files via imp based on the items in a list, 
    `plugins`.'''
    
    sys.path.insert(0, os.path.abspath('.'))
    os.chdir('.') 
    for p in plugins:
        path = 'voxbot/plugins/' + p.lower() + '.py'
        try:
            imp.load_source(p, path)
        except ImportError, e:
            error = 'Failed loading plugin \'{0}\' with error: {1}'.format(p, e)
            raise ImportError(error)
    return [sys.modules[p].__dict__[p](bot) for p in plugins] # run 'em

def reload_plugin(plugin):
    '''Reloads a plugin, `plugin`.'''
    
    if plugin in sys.modules:
        reload(sys.modules[plugin])
