import re

irc_prefix_rem = re.compile(r'(.*?) (.*?) (.*)').match
irc_noprefix_rem = re.compile(r'()(.*?) (.*)').match
irc_netmask_rem = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)').match
irc_param_ref = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)').findall

def parse_raw_input(line):
    '''Takes raw input, parses it.'''
    
    if line.startswith(':'):  # has a prefix
        prefix, command, params = irc_prefix_rem(line).groups()
    else:
        prefix, command, params = irc_noprefix_rem(line).groups()
    
    nick, user, host = irc_netmask_rem(prefix).groups()
    paramlist = irc_param_ref(params)
    lastparam = ''

    if paramlist:
        if paramlist[-1].startswith(':'):
            paramlist[-1] = paramlist[-1][1:]
        lastparam = paramlist[-1]

    return Input(command, params, prefix, nick, user, host, paramlist)

class Input(object):
    '''Stores parsed input.'''

    def __init__(self, command, params, prefix, nick, user, host, paramlist):
        self.command = command
        self.params = params
        self.prefix = prefix
        self.nick = nick
        self.user = user
        self.host = host
        self.paramlist = paramlist
