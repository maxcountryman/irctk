def parse_raw_input(line):
    '''Takes raw input, parses it.'''
    trailing, nick, user, host, command_args = (None, None, None, None, None)
    
    if line.startswith(':'):
        prefix, line = line[1:].split(' ', 1)
        if '@' in prefix:
            nick, user, host = prefix.replace('@', '!').split('!')
    
    if ' :' in line:
        line, trailing = line.split(' :', 1)
    line = line.split()
    command = line.pop(0)
    command_args = line
    
    return Input(nick, user, host, command, command_args, trailing)

class Input(object):
    '''Stores parsed input.'''

    def __init__(self, nick, user, host, command, command_args, trailing):
        self.nick = nick
        self.user = user
        self.host = host
        self.command = command
        self.command_args = command_args
        self.trailing = trailing
