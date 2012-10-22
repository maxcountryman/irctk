# -*- coding: utf-8 -*-
'''
    irctk.irc
    ---------

    IRC abstraction layer.
'''

import socket
import thread
import time
import os


class Irc(object):
    def __init__(self, bridge_socket, logger):
        self.logger = logger

        # the Unix domain socket to connect to
        self.bridge_socket = bridge_socket

        self.inp_buffer = ''
        self.out_buffer = ''

        self.lock = thread.allocate_lock()
        self.context = {}

        if os.path.exists('/tmp/irctk_downstream'):
            os.remove('/tmp/irctk_downstream')

        self.downstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.downstream.bind('/tmp/irctk_downstream')
        self.downstream.listen(1)

    def _connect_upstream(self):
        while True:
            try:
                self.upstream_bridge = socket.socket(socket.AF_UNIX,
                                                     socket.SOCK_STREAM)
                self.upstream_bridge.connect(self.bridge_socket)
            except socket.error:
                pass
            time.sleep(.1)

    def _parse_context(self):
        while True:
            while '\r\n' in self.inp_buffer:
                with self.lock:
                    line, self.inp_buffer = self.inp_buffer.split('\r\n', 1)

                    prefix, command, args = self.parse_line(line)
                    sender, message = args[0], args[-1]

                    self.context = {'prefix': prefix,
                                    'command': command,
                                    'args': args,
                                    'sender': sender if args else '',
                                    'user': prefix.rsplit('!', 1)[0],
                                    'hostmask': prefix.rsplit('!', 1)[-1],
                                    'message': message if args else '',
                                    'raw': line,
                                    'stale': False}
            time.sleep(.1)

    def _send(self):
        while True:
            while '\r\n' in self.out_buffer:
                line, self.out_buffer = self.out_buffer.split('\r\n', 1)
                self.logger.info(line)
                try:
                    self.upstream_bridge.send(line.encode('utf-8', 'ignore'))
                except (socket.error, AttributeError), e:
                    self.logger.warning(str(e))
            time.sleep(.1)

    def _recv(self, size=1024):
        while True:
            upstream_conn, addr = self.downstream.accept()
            data = upstream_conn.recv(size)
            self.logger.info(data.replace('\r\n', ''))
            if data:
                self.inp_buffer += data.decode('utf-8', 'ignore')
            time.sleep(.1)

    def connect(self):
        thread.start_new_thread(self._connect_upstream, ())
        thread.start_new_thread(self._send, ())
        thread.start_new_thread(self._recv, ())
        thread.start_new_thread(self._parse_context, ())

    def parse_line(self, line):
        prefix = ''
        trailing = []
        if not line:
            raise Exception('Received an empty line from the server.')

        if line[0] == ':':
            prefix, line = line[1:].split(' ', 1)

        if line.find(' :') != -1:
            line, trailing = line.split(' :', 1)
            args = line.split()
            args.append(trailing)
        else:
            args = line.split()

        command = args.pop(0)
        return prefix, command, args

    def send_line(self, line):
        self.out_buffer += line + '\r\n'

    def send_lines(self, lines):
        for line in lines:
            self.send_line(line)

    def send_command(self, command, args=[], prefix=None):
        command = command + ' ' + ''.join(args)
        if prefix:
            command = prefix + command

        return self.send_lines([command])

    def send_message(self, recipient, message, action=False, notice=False):
        if action:
            return self.send_action(recipient, message)
        elif notice:
            return self.send_notice(recipient, message)
        else:
            return self.send_command('PRIVMSG', [recipient + ' :' + message])

    def send_notice(self, recipient, message):
        return self.send_command('NOTICE', [recipient + ' :' + message])

    def send_action(self, recipient, message):
        message = chr(1) + 'ACTION ' + message + chr(1)
        return self.send_message(recipient, message)
