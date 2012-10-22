#!/usr/bin/env python

import socket

import argparse
import logging
import os
import Queue
import thread
import time

from ssl import wrap_socket

pid = str(os.getpid())
pidfile = '/tmp/irctk_connect.pid'

with open(pidfile, 'w') as f:
    f.write(pid)

parser = argparse.ArgumentParser(description='Maintains a connection to an IRC'
                                             ' server.')
parser.add_argument('host',
                    help='The host to connect to')
parser.add_argument('port',
                    type=int,
                    help='The port to connect on')
parser.add_argument('-x',
                    '--ssl',
                    dest='ssl',
                    default=False,
                    help='Whether or not to use SSL/TLS')
parser.add_argument('-t',
                    '--timeout',
                    dest='timeout',
                    default=300,
                    type=int,
                    help='Socket connection timeout')
parser.add_argument('nick',
                    help='The NICK')
parser.add_argument('realname',
                    help='The REALNAME')
parser.add_argument('-p',
                    '--password',
                    dest='password',
                    help='Server password')
parser.add_argument('-c',
                    '--channels',
                    dest='channels',
                    nargs='+',
                    help='Space-separated list of channels to join')


class Tcp(object):
    def __init__(self, host, port, ssl, timeout, logger=None):
        self.timeout = timeout

        self.host = host
        self.port = port
        self.ssl = ssl

        self.inp = Queue.Queue()
        self.out = Queue.Queue()
        self.inp_buffer = ''
        self.out_buffer = ''

        self.logger = logger

    def connect(self):
        self.s = socket.socket()
        self.s.settimeout(self.timeout)
        if self.ssl:
            self.s = wrap_socket(self.s)

        self.s.connect((self.host, self.port))

        thread.start_new_thread(self._recv, ())
        thread.start_new_thread(self._send, ())

    def _recv(self, size=4096):
        while True:
            data = self.s.recv(size)
            self.inp_buffer += data

            while '\r\n' in self.inp_buffer:
                line, self.inp_buffer = self.inp_buffer.split('\r\n', 1)
                self.inp.put(line + '\r\n')
                self.logger.info(line)
            time.sleep(.1)

    def _send(self):
        while True:
            line = self.out.get(True).splitlines()
            if line:
                line = line[0]
                self.out_buffer += line + '\r\n'
                self.logger.info(line)

            while self.out_buffer:
                self.out_buffer = self.out_buffer
                sent = self.s.send(self.out_buffer)
                self.out_buffer = self.out_buffer[sent:]
            time.sleep(.1)


class ClientBridge(object):
    def __init__(self, server, nick, realname, password, channels, logger):
        self.server = server

        self.nick = nick
        self.realname = realname
        self.password = password
        self.user = 'USER ' + nick + ' 3 * ' + realname
        self.channels = channels

        self.inp_buffer = ''
        self.out_buffer = ''

        self.logger = logger

        # TODO: pass these in
        self.upstream_socket = '/tmp/irctk_upstream'
        self.downstream_socket = '/tmp/irctk_downstream'

        # get rid of lingering streams
        if os.path.exists(self.upstream_socket):
            os.remove(self.upstream_socket)

        self.upstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.upstream.bind(self.upstream_socket)
        self.upstream.listen(1)

        # client connects like this
        #
        #self.upstream_bridge = socket(AF_UNIX, SOCK_STREAM)
        #self.upstream_bridge.connect('/tmp/irctk_upstream')

    def connect(self):
        thread.start_new_thread(self._send, ())
        thread.start_new_thread(self._recv, ())
        thread.start_new_thread(self._bind_upstream, ())

        self._register()

    def _bind_upstream(self, size=1024):
        '''Continually bind to a socket and forward received data to the
        server.'''
        while True:
            upstream_conn, addr = self.upstream.accept()
            data = upstream_conn.recv(size)

            if data:
                self.out_buffer += data + '\r\n'
            upstream_conn.close()

    def _send(self):
        '''Send the contents of `self.out_buffer` to the server's output
        queue.'''
        while True:
            while '\r\n' in self.out_buffer:
                line, self.out_buffer = self.out_buffer.split('\r\n', 1)
                self.server.out.put(line)
            time.sleep(.1)

    def _recv(self):
        '''Parse contents off of the server's input queue.'''
        while True:
            self.inp_buffer += self.server.inp.get()
            while '\r\n' in self.inp_buffer:
                line, self.inp_buffer = self.inp_buffer.split('\r\n', 1)

                try:
                    # attempt to open up a connection to a client and send data
                    downstream_bridge = socket.socket(socket.AF_UNIX,
                                                      socket.SOCK_STREAM)
                    downstream_bridge.connect(self.downstream_socket)
                    downstream_bridge.send(line + '\r\n')
                except socket.error, e:
                    self.logger.warning(str(e))

                if 'PING' in line:
                    self.send_line('PONG ' + line.split(':', 1)[-1])
                if ' 001 ' in line:
                    for channel in self.channels:
                        self.send_line('JOIN ' + channel)

            time.sleep(.1)

    def _register(self):
        '''Register a connection with an IRC server.'''
        lines = []
        if self.password is not None:
            lines.append('PASS ' + self.password)
        lines += ['NICK ' + self.nick, self.user]
        self.send_lines(lines)

    def send_line(self, line):
        '''Append a string `line` to `self.out_buffer` and delineate with
        `\r\n`.'''
        self.out_buffer += line + '\r\n'

    def send_lines(self, lines):
        '''Send a list of lines, wrapping `self.send_line`.'''
        for line in lines:
            self.send_line(line)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    args = parser.parse_args()
    server = Tcp(args.host, args.port, args.ssl, args.timeout, logger)
    bridge = ClientBridge(server,
                          args.nick,
                          args.realname,
                          args.password,
                          args.channels,
                          logger)

    server.connect()
    bridge.connect()

    while True:
        time.sleep(.1)

    os.unlink(pidfile)
