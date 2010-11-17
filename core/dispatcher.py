import inspect 
import gevent

from core.irc import Irc # I lied, needed for dispatching commands with Irc.send()

cmd_hooks = {}
sub_hooks = defaultdict(list)

def command(arg=None):
    '''Associate a command hook with a function. For example `@command('google')`
       should call a given function with `google` hook. Uses cmd_hooks dict.
    '''

    def command_wrapper(func):
        if func.func_name in cmd_hooks:
            raise ValueError
        else:
            cmd_hooks[func.func_name] = func
        return func
        
    if inspect.isfunction(arg):
        return command_wrapper
    else:
        return command_wrapper(arg)

def subscribe(hook):
    '''Subscribe a function or functions to an event. For example 
       `@subscribe('JOIN')` should call a given function or functions with the 
       `JOIN` hook. Uses sub_hook dict.
    '''

    def subscribe_wrapper(func):
        sub_hooks[hook] = [func]
        return subscribe_wrapper

class Dispatcher():
    '''Publish functions associated with hooks. Load subscriptions with 
       `load()`.
    '''

    def __init__(self):
        self._publish()
    
    def _publish(): # publish subscribed events and commands
        pass #implement this

    def load(): # load subscriptions
        pass # implement this
