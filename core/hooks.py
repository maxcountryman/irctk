from collections import defaultdict

cmd_hooks = {} # store functions in a standard dictionary
sub_hooks = defaultdict(list) # store functions in a list associated with a hook

def command(hook=None):
    '''Associate a command hook with a function. For example `@command('google')`
       should call a given function with `google` hook, alternatively using 
       `@command` should use `func.func_name` as the hook. Uses cmd_hooks dict.
    '''

    def command_wrapper(func):
        if hook is None and (func.func_name in cmd_hooks or hook in cmd_hooks):
            raise ValueError('Duplicate command hook found.')
        elif hook is None:
            cmd_hooks[func.func_name] = func
        else:
            cmd_hooks[hook] = func
        return func

    return command_wrapper

def subscribe(hook):
    '''Subscribe a function or functions to an event. For example 
       `@subscribe('JOIN')` should call a given function or functions with the 
       `JOIN` hook. Uses sub_hook dict.
    '''

    def subscribe_wrapper(func):
        sub_hooks[hook].append(func)
        return func
    
    return subscribe_wrapper

def handle(bot, event):
    return Handler(bot, event)

class Handler(object):
    '''Determines if an event is directed to subscriptions or commands.'''

    def __init__(self, bot, event, command=False, cmd_prefix=False):
        self.bot = bot
        self.nick = ':' + bot.irc.nick
        self.event = str(event.args.trailing)
        self.command = command
        self.cmd_prefix = cmd_prefix
        _sieve = self._sieve()
        _sieve_prefixed = self._sieve_prefixed()
        _dispatch(bot, event, _sieve, _sieve_prefixed)

    def _sieve(self):
        self.command = self.event.startswith(self.bot.irc.nick)
        return self.command

    def _sieve_prefixed(self):
        if self.event.startswith(self.bot.cmd_prefix):
            self.cmd_prefix = True
            return True
        else:
            self.command = False
            return False

def _dispatch(bot, event, sieve, sieve_prefixed):
    '''Dispatch hooks in respone to events.'''

    if sieve:
        try:
            func = cmd_hooks[event.args.trailing.split(': ')[1].split(' ')[0]]
            func(bot, event.args)
        except KeyError:
            pass
    elif sieve_prefixed:
        try:
            print event.args.trailing.split(' ')[0].split('{0}'.format(bot.cmd_prefix))
            func = cmd_hooks[event.args.trailing.split(' ')[0].split('{0}'.format(bot.cmd_prefix))[-1]]
            func(bot, event.args)
        except KeyError:
            pass
    else:
        for func in sub_hooks[event.hook]:
            func(bot, event.args)
