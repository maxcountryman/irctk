'''
    irctk.config
    ------------
    
    Sets up the configuration object.
'''


import imp
import os


class Config(dict):
    '''TODO'''
    
    def __init__(self, root_path, defaults=None):
        dict.__init__(self, defaults or {})
        self.root_path = root_path
    
    def from_pyfile(self, filename):
        filename = os.path.join(self.root_path, filename)
        d = imp.new_module('config')
        d.__file__ = filename
        execfile(filename, d.__dict__)
        self.from_object(d)
        return True
    
    def from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)
    
    def __repr__(self):
        return '<{0!r} {0!r}>'.format(self.__class__.__name__, dict.__repr__(self))
