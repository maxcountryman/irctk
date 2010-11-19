import gevent
from gevent import socket
from gevent.ssl import wrap_socket
from gevent import sleep
from gevent import queue

from parser import parse_raw_input

class Tcp(object):
    '''
    Handles TCP connections, `timeout` is in secs. Access output and
    send input via `iqueue` and `oqueue` respectively.
    '''

    def __init__(self, host, port, timeout=300):
        self.host = host
        self.port = port
        self.timeout = timeout

        self._ibuffer = ''
        self._obuffer = ''
        self.iqueue = queue.Queue()
        self.oqueue = queue.Queue()
        self._socket = self._create_socket()

    def _create_socket(self):
        return socket.socket()

    def connect(self):
        self._socket.connect((self.host, self.port))

        jobs = [gevent.spawn(self._recv_loop), gevent.spawn(self._send_loop)]
        gevent.joinall(jobs)

    def disconnect(self):
        self._socket.close()

    def _recv_from_socket(self, nbytes):
        return self._socket.recv(nbytes)
    
    def _recv_loop(self):
        while True:
            data = self._recv_from_socket(4096)
            self._ibuffer += data
            while '\r\n' in self._ibuffer:
                line, self._ibuffer = self._ibuffer.split('\r\n', 1)
                self.iqueue.put(line)
                print line

    def _send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            print '>>> %r' % line
            self._obuffer += line.encode('utf-8', 'replace') + '\r\n'
            while self._obuffer:
                sent = self._socket.send(self._obuffer)
                self._obuffer = self._obuffer[sent:]

class SslTcp(Tcp):
    '''SSL wrapper for TCP connections.'''

    def _create_socket(self):
        return wrap_socket(Tcp._create_socket(self), server_side=False)

    def _recv_from_socket(self, nbytes):
        return self._socket.read(nbytes)

import gevent
from gevent import socket
from gevent.ssl import wrap_socket
from gevent import sleep
from gevent import queue

import settings

class Tcp(object):
    '''
    Handles TCP connections, `timeout` is in secs. Access output and
    send input via `iqueue` and `oqueue` respectively.
    '''

    def __init__(self, host, port, timeout=300):
        self._ibuffer = ''
        self._obuffer = ''
        self.iqueue = queue.Queue()
        self.oqueue = queue.Queue()
        self._socket = self._create_socket()
        self.host = host
        self.port = port
        self.timeout = timeout

    def _create_socket(self):
        return socket.socket()

    def connect(self):
        self._socket.connect((self.host, self.port))

        jobs = [gevent.spawn(self._recv_loop), gevent.spawn(self._send_loop)]
        gevent.joinall(jobs)

    def disconnect(self):
        self._socket.close()

    def _recv_from_socket(self, nbytes):
        return self._socket.recv(nbytes)
    
    def _recv_loop(self):
        while True:
            data = self._recv_from_socket(4096)
            self._ibuffer += data
            while '\r\n' in self._ibuffer:
                line, self._ibuffer = self._ibuffer.split('\r\n', 1)
                self.iqueue.put(line)

    def _send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            self._obuffer += line.encode('utf-8', 'replace') + '\r\n'
            while self._obuffer:
                sent = self._socket.send(self._obuffer)
                self._obuffer = self._obuffer[sent:]

class SslTcp(Tcp):
    '''SSL wrapper for TCP connections.'''

    def _create_socket(self):
        return wrap_socket(Tcp._create_socket(self), server_side=False)

    def _recv_from_socket(self, nbytes): # why is this necessary?
        return self._socket.read(nbytes)

class Irc(object):
    '''Handles the IRC protocol. Pass true if using SSL.'''

    def __init__(self, server, nick, port=6667, ssl=False):
        self.server = server
        self.nick = nick
        self.port = port
        self.ssl = ssl
        self.events = queue.Queue() # responses from the server
        
        self._connect()
        gevent.spawn(self._parse_loop)

    def _create_connection(self):
        transport = SslTcp if self.ssl else Tcp
        return transport(self.server, self.port)

    def _connect(self):
        self.conn = self._create_connection()
        gevent.spawn(self.conn.connect)
        self._set_nick(self.nick) # see comment directly below
        self.cmd('USER', 'pybot', '3', '*', 'Python Bot') # it's just cleaner, KISS

    def _parse_loop(self):
        while True:
            line = self.conn.iqueue.get()
            print line
            parsed = parse_raw_input(line)
            event = IrcEvent(parsed.command, parsed)
            self.events.put(event)

    def _set_nick(self, nick):
        self.cmd('NICK', nick, prefix=False)

    def msg(self, target, text):
        self.cmd('PRIVMSG', target, text, prefix=True)

    def cmd(self, command, *args, **kwargs):
        '''Send a command to server, prefix=True adds the ':' prefix.'''

        if args and kwargs:
            self._send(command + ' ' + ' '.join(args[:-1]) + ' :' + args[-1])
        elif args:
            print args
            self._send(command + ' ' + ' '.join(args))
        else:
            self._send(command)
            
    def _send(self, s):
        print 'send: {0}'.format(s)
        self.conn.oqueue.put(s)

class IrcEvent(object):
    def __init__(self, hook, args):
        self.hook = hook.lower()
        self.args = args # prefixed

if __name__ == '__main__': # keep this for debugging please :)
    
    bot = lambda : Irc('irc.voxinfinitus.net', 'Kaa', 6697, True, ['#voxinfinitus','#landfill'])
    
    jobs = [gevent.spawn(bot)]
    gevent.joinall(jobs)
