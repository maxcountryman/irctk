import sys

def reload_plugins(plugin):
    if plugin in sys.modules:
        reload(sys.modules[plugin])
