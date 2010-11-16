import logging
import os.path

import gevent
from gevent import socket
from gevent.ssl import wrap_socket
from gevent import sleep
from gevent import queue

import settings

logging.basicConfig(filename=os.path.join(settings.log_dir, "base.log"), level=logging.DEBUG)

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
        gevent.killall(jobs)

    def _recv_from_socket(self, nbytes):
        return self._socket.recv(nbytes)
    
    def _recv_loop(self):
        while True:
            data = self._recv_from_socket(4096)
            self._ibuffer += data
            while '\r\n' in self._ibuffer:
                line, self._ibuffer = self._ibuffer.split('\r\n', 1)
                self.iqueue.put(line)
                logging.debug(line)
                print line

    def _send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            logging.debug('>>> ' + line)
            print '>>> %r' % line
            self._obuffer += line.encode('utf-8', 'replace') + '\r\n'
            while self._obuffer:
                sent = self._socket.send(self._obuffer)
                self._obuffer = self._obuffer[sent:]

class SslTcp(Tcp):
    '''SSL wrapper for TCP connections, `timeout` is in secs.'''

    def _create_socket(self):
        return wrap_socket(Tcp._create_socket(self), server_side=False)

    def _recv_from_socket(self, nbytes):
        return self._socket.read(nbytes)

class Irc(object):
    '''Handles the IRC protocol. Pass true if using SSL.'''

    def __init__(self, server, nick, port=6667, ssl=False, channels=['']):
        self.server = server
        self.nick = nick
        self.port = port
        self.ssl = ssl
        self.channels = channels
        self.out = queue.Queue() # responses from the server
        self._hooks = { 'ping': self._pong, '376': self._396, '396': self._396, }
        self._connect()
        
        # parallel event loop
        self.jobs = [gevent.spawn(self._parse_loop)]
        gevent.joinall(self.jobs)

    def _create_connection(self):
        if self.ssl is False:
            return Tcp(self.server, self.port)
        else:
            return SslTcp(self.server, self.port)

    def _connect(self):
        self.conn = self._create_connection()
        gevent.spawn(self.conn.connect)
        self._set_nick(self.nick)
        sleep(1)
        self.cmd('USER',
                ['pybot', '3', '*','Python Bot'])

    def _parse_loop(self):
        while True:
            line = self.conn.iqueue.get()
            trailing = ''
            prefix = ''
            
            if line[0] == ':':
                line = line[1:].split(' ', 1)
                prefix = line[0]
                line = line[1]
            
            if ' :' in line:
                line = line.split(' :', 1)
                trailing = line[1]
                line = line[0]
            args = line.split()
            command = args.pop(0)
            if trailing:
                args.append(trailing)
                
            event = IrcEvent(command, prefix, args, 5)
            try:
                t = gevent.with_timeout(event.timeout, self._call_hook, event)
            except gevent.Timeout, t:
                logging.exception('Hook call timed out!')

    def set_hook(self, hook, func):
        self.hooks[hook] = func
        
    def _call_hook(self, event):
        if event.hook in self._hooks:
            self._hooks[event.hook](event)

    def _pong(self, event):
        self.cmd('PONG', event.args)

    def _376(self, event): # finished connecting (freenode)
        for channel in self.channels:
            self.join(channel)
   
    def _396(self, event): # finished connecting, we can join
        for channel in self.channels:
            self.join(channel)

    def _set_nick(self, nick):
        self.cmd('NICK', [nick])

    def join(self, channel):
        self.cmd('JOIN', [channel])

    def cmd(self, command, params=None):
        if params:
            params[-1] = ':' + params[-1]
            self._send(command + ' ' + ' '.join(params))
        else:
            self._send(command)
            
    def _send(self, s):
        self.conn.oqueue.put(s)

class IrcEvent(object):
    def __init__(self, hook, source, args, timeout):
        self.hook = hook.lower()
        self.source = source
        self.args = args
        self.timeout = timeout

if __name__ == '__main__':
    
    bot = lambda : Irc('irc.voxinfinitus.net', 'Kaa', 6697, True, ['#voxinfinitus','#landfill'])
    another_bot = lambda : Irc('irc.freenode.net', 'Kaa___', 6667, False, ['##devil'])
    
    jobs = [gevent.spawn(bot),gevent.spawn(another_bot)]
    gevent.joinall(jobs)
