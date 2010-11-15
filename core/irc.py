import logging
import os.path

import gevent
from gevent import socket
from gevent import sleep
from gevent import queue

import settings

logging.basicConfig(filename=os.path.join(settings.log_dir, "base.log"), level=logging.DEBUG)

class TCP(object):
    '''Handles TCP connections.'''

    def __init__(self, host, port, timeout=300):
        self.ibuffer = ''
        self.obuffer = ''
        self.iqueue = queue.Queue()
        self.oqueue = queue.Queue()
        self.socket = self.create_socket()
        self.host = host
        self.port = port
        self.timeout = timeout

    def create_socket(self):
        return socket.socket()

    def run(self):
        self.socket.connect((self.host, self.port))
        gevent.spawn(self.recv_loop)
        gevent.spawn(self.send_loop)

    def recv_from_socket(self, nbytes):
        return self.socket.recv(nbytes)
    
    def recv_loop(self):
        while True:
            data = self.recv_from_socket(4096)
            self.ibuffer += data
            while '\r\n' in self.ibuffer:
                line, self.ibuffer = self.ibuffer.split('\r\n', 1)
                self.iqueue.put(line)
                logging.debug("recv: " + line)
                print line

    def send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            logging.debug("send: " + line)
            print ">>> %r" % line
            self.obuffer += line.encode('utf-8', 'replace') + '\r\n'
            while self.obuffer:
                sent = self.socket.send(self.obuffer)
                self.obuffer = self.obuffer[sent:]

class IRCEvent(object):
    def __init__(self, hook, source, args, timeout):
        logging.debug("Event {0}, source: {1}, args: {2}".format(hook, source, args))
        self.hook = hook.lower()
        self.source = source
        self.args = args
        self.timeout = timeout

class IRC(object):
    '''Handles the IRC protocol.'''

    def __init__(self, server, nick, port=6667, channels=['']):
        self.server = server
        self.nick = nick
        self.port = port
        self.channels = channels
        self.out = queue.Queue() # responses from the server
        self.hooks = { "ping": self.pong, "396": self._396 }
        self.connect()
        
        # parallel event loop(s)
        self.jobs = [gevent.spawn(self.parse_loop)]
        gevent.joinall(self.jobs)

    def create_connection(self):
        return TCP(self.server, self.port)

    def connect(self):
        self.conn = self.create_connection()
        gevent.spawn(self.conn.run)
        self.set_nick(self.nick)
        sleep(1)
        self.cmd("USER",
                ['pybot', "3", "*",'Python Bot'])

    def parse_loop(self):
        while True:
            line = self.conn.iqueue.get()
            trailing = ""
            prefix = ""
            
            if line[0] == ":":
                line = line[1:].split(' ', 1)
                prefix = line[0]
                line = line[1]
            
            if " :" in line:
                line = line.split(" :", 1)
                trailing = line[1]
                line = line[0]
            args = line.split()
            command = args.pop(0)
            if trailing:
                args.append(trailing)
                
            event = IRCEvent(command, prefix, args, 5)
            try:
                t = gevent.with_timeout(event.timeout, self.call_hook, event)
            except gevent.Timeout, t:
                logging.exception("Hook call timed out!")

    def set_hook(self, hook, func):
        self.hooks[hook] = func
        
    def call_hook(self, event):
        if event.hook in self.hooks:
            self.hooks[event.hook](event)

    def pong(self, event):
        self.cmd("PONG", event.args)
        
    def _396(self, event): # finished connecting, we can join
        for channel in self.channels:
            self.join(channel)

    def set_nick(self, nick):
        self.cmd("NICK", [nick])

    def join(self, channel):
        self.cmd("JOIN", [channel])

    def cmd(self, command, params=None):
        if params:
            params[-1] = ':' + params[-1]
            self.send(command + ' ' + ' '.join(params))
        else:
            self.send(command)
            
    def send(self, str):
        self.conn.oqueue.put(str)


if __name__ == "__main__":
    bot = IRC('irc.voxinfinitus.net', 'Kaa_', 6667, ['#voxinfinitus','#landfill'])
