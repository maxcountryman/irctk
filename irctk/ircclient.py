'''
    irctk.ircclient
    ---------------
    
    Provides two classes, `TcpClient` and `IrcWrapper`.
    
    `TcpClient` is a TCP client tailored for IRC connections. It provides 
    processing for the data received by and sent to the server.
    
    `IrcWrapper` is a wrapper for some of the IRC protocol. This API is 
    incomplete but covers much of the core functionality needed to make and 
    sustain connections.
'''


import socket
import thread
import Queue
import time

from ssl import wrap_socket, SSLError


class TcpClient(object):
    '''This is a TCP client that has been adapted for IRC connections. The 
    recieving and sending methods, `_recv` and `_send`, are wrapped in threads 
    to allow for asynchronous communication.
    
    The `run` method is used to start the server and initiate the recieving 
    and sending threads. Before doing so a default socket timeout is set, 
    using the value of `self.timeout`. If self.ssl is True the socket is 
    wrapped accordingly.
    
    The `close` method is used to close a connection. In order to exit loops a 
    switch `self.shutdown` is used. Initially this is set to False but when 
    `close()` is called this attribute is set to True.
    
    TODO: In order to prevent the server from disconnecting us for flooding, 
    some kind of timed, rate-limiter should be implemented in the send loop.
    
    Also a logger should be implemented that would replace any print 
    statements that are currently being used for debug functionality. However 
    this is likely better as a project-wide implementation so for now it 
    remains on the TODO list.
    
    An instance of this class might look like this:
        
        client = TcpClient('irc.voxinfinitus.net', 6697, True)
        
        # start the client-connection to the server
        client.connect()
        
        # close the client-connection to the server
        client.close()
    '''
    
    def __init__(self, host, port, ssl=False, timeout=300.0, logger=None):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.inp = Queue.Queue()
        self.out = Queue.Queue()
        self.inp_buffer = ''
        self.out_buffer = ''
        self.shutdown = False
        self.timeout = timeout
        self.reconnect_on_error = True
        socket.setdefaulttimeout(self.timeout)
        self.logger = logger
    
    def connect(self, reconnect=False):
        '''This method initiates the socket connection by passing a tuple, 
        `server` containing the host and port, to the socket object and then 
        wraps our `_recv` and `_send` methods in threads.
        
        Necessarily `self.shutdown` is set to False in the event that it might 
        have been reset, e.g. in the case of a disconnect and reconnect.
        
        The default socket timeout is also set here. Our value here is 
        provided by `self.timeout`.
        
        Finally the two primary loops, `_send()` and `_recv()` are invoked as 
        threads.
        '''
        
        self.shutdown = False
        
        self.socket = socket.socket()
        if self.ssl:
            self.socket = wrap_socket(self.socket)
        
        server = (self.host, self.port)
        self.socket.connect(server)
        if not reconnect:
            thread.start_new_thread(self._recv, ())
            thread.start_new_thread(self._send, ())
    
    def close(self, wait=1.0):
        '''This method closes an open socket. As per the original UNIX spec, 
        the socket is first alerted of an imminent shutdown by calling 
        `shutdown()`. We then wait for `wait`-number of seconds. Finally we 
        call `close()` on the socket.
        '''
        
        self.shutdown = True
        
        self.socket.shutdown(1)
        time.sleep(wait)
        try:
            self.socket.close() #seems to cause a problem, errno 9
        except Exception:
            pass
    
    def reconnect(self, wait=1.0):
        '''This method will attempt to reconnect to a server. It should be 
        called contextually after some failure perhaps. If the reconnection 
        fails the error will be reported and execution will carry on.
        
        The `wait` parameter indicates the time in seconds to wait before 
        trying to reconnect. Default is 30.
        
        Before attempting to connect this method will try to terminate an 
        existing socket connection if one exists.
        '''
        
        try:
            self.close()
        except Exception, e:
            self.logger.debug('exception while closing old socket: ' + str(e))
        time.sleep(wait)
        self.connect(reconnect=True)
    
    def _recv(self, reconnect_wait=5.0, byte_size=4096):
        '''Internal method that processes incoming data.'''
        
        while True:
            
            try:
                if not self.shutdown:
                    data = self.socket.recv(byte_size)
            except (SSLError, socket.error, socket.timeout):
                if self.reconnect_on_error:
                    self.logger.error('Connection lost, reconnecting.')
                    self.reconnect(reconnect_wait)
                    self.inp.put('Error :Closing Link:\r\n')
                    reconnect_wait *= reconnect_wait
                    continue
                else:
                    self.close()
            
            self.inp_buffer += data
            
            while '\r\n' in self.inp_buffer and not self.shutdown:
                
                line, self.inp_buffer = self.inp_buffer.split('\r\n', 1)
                self.inp.put(line + '\r\n')
                self.logger.info(line)
    
    def _send(self):
        '''Internal method that processes outgoing data.'''
        
        while True:
            
            line = self.out.get(True).splitlines()
            if line:
                line = line[0]
                self.out_buffer += line.encode('utf-8', 'replace') + '\r\n'
                self.logger.info(line)
            
            while self.out_buffer and not self.shutdown:
                
                sent = self.socket.send(self.out_buffer)
                self.out_buffer = self.out_buffer[sent:]


class IrcWrapper(object):
    '''This class is a wrapper object for the modified TCP client, 
    `TcpClient`, which provides various convenience methods that wrap some 
    IRC functionality.
    
    An existing TCP connection of `TcpClient` is anticipated by this class. In 
    this way we can decouple the connection and wrapper in the event that we 
    want to reload or otherwise alter the wrapper logic.
    
    An instance of this class might look like:
        
        # setup a client-connection with SSL
        client = TcpClient('irc.voxinfinitus.net', 6697, True)
        
        # connect to the server
        client.connect()
        
        # define some channels to join
        channels = ['#voxinfinitus', '#testing']
        
        irc = IrcWrapper(client, 'Kaa', 'Kaa the Python', channels)
    '''
    
    def __init__(self, connection, nick, realname, channels, logger):
        self.connection = connection
        self.nick = nick
        self.realname = realname
        self.user = 'USER ' + nick + ' 3 * ' + realname
        self.channels = channels
        self.inp_buffer = ''
        self.out_buffer = ''
        self.lock = thread.allocate_lock()
        
        self.context = {}
        
    def _register(self):
        '''This internal method attempts to register the connection with the 
        server by sending the NICK and then USER commands as soon as the 
        connection object is received.
        '''
        
        lines = ['NICK ' + self.nick, self.user]
        self._send_lines(lines)
    
    def _send(self, wait=0.1, wait_time=1.0, wait_base=1.0, byte_size=8192):
        '''This internal method reads off of `self.out_buffer`, sending the 
        contents to the connection object's output queue.
        
        Here we use `time.sleep` to sleep `wait`-number of seconds. This 
        prevents the threads from running all the time and consequently 
        maxing out the CPU.
        
        TODO: rate limiter does not yet work. Perhaps a proper implementation 
        of the leaky bucket?
        '''
        
        while True:
            time.sleep(wait)
            while '\r\n' in self.out_buffer and not self.connection.shutdown:
                line, self.out_buffer = self.out_buffer.split('\r\n', 1)
                if len(self.out_buffer) >= byte_size:
                    wait_time *= wait_time
                    time.sleep(wait_time)
                elif wait_time > wait_base:
                    wait_time /= wait_time
                elif wait_time < wait_base:
                    wait_time = wait_base
                self.connection.out.put(line)
    
    def _recv(self, reconnect_wait=5.0):
        '''This internal method pulls data from the connection's input queue.
        It then places this information in a local input buffer and loops over 
        this buffer, line by line, parsing it via `_parse_line()`.
        
        Parsed lines are stored in `self.prefix`, 'self.command', and 
        'self.args'.
        
        In this loop we check to see if the connection has been properly 
        registered with the server and if so loop through the channels defined 
        in `self.channels`, sending a JOIN command for each respectively.
        
        Here we use `time.sleep` to sleep `wait`-number of seconds. This 
        prevents the threads from running all the time and consequently 
        maxing out the CPU.
        '''
        
        while True:
            self.inp_buffer += self.connection.inp.get()
            while '\r\n' in self.inp_buffer and not self.connection.shutdown:
                with self.lock:
                    self.line, self.inp_buffer = self.inp_buffer.split('\r\n', 1)
                    self.prefix, self.command, self.args = self._parse_line(self.line)
                    
                    self.sender = self.args[0]
                    self.message = self.args[-1]
                    
                    self.context = {
                        'prefix' : self.prefix, 
                        'command' : self.command, 
                        'args' : self.args,
                        'sender': self.sender if self.args else '',
                        'user': self.prefix.rsplit('!', 1)[0],
                        'hostmask': self.prefix.rsplit('!', 1)[-1],
                        'message': self.message if self.args else '',
                        'stale': False,
                        }
                    
                    if 'ERROR :Closing link:' in self.line:
                        self.connection.logger.error('Connection lost, reconnecting.')
                        self.connection.reconnect(reconnect_wait)
                        self.connection.inp.put('RECONNECT :server\r\n')
                        reconnect_wait *= reconnect_wait
                    
                    if self.command == 'PING':
                        self._send_line('PONG ' + ''.join(self.args))
                    elif self.command == '001' and self.channels:
                        for channel in self.channels:
                            self._send_line('JOIN ' + channel)
                    elif self.command == '433':
                        self.nick = self.nick + '_'
                        self._send_line('NICK ' + self.nick)
                    elif self.command == 'RECONNECT':
                        self._register()
    
    def _parse_line(self, line):
        '''This internal method takes a line as recieved from the IRC server 
        and parses it appropriately.
        
        Returns `prefix`, `command`, `args`.
        '''
        
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
    
    def _send_line(self, line):
        '''This internal method takes one parameter, `lines`, loops over it 
        and sends each element directly to the `_send()` loop. This is used 
        for sending raw messages to the server. Not for use outside of the 
        scope of this class!
        
        This method is not rate-limited. Use with caution.
        '''
        
        self.out_buffer += line + '\r\n'
    
    def _send_lines(self, lines):
        '''This internal method takes one parameter, `lines`, loops over it 
        and sends each element directly to the `_send()` loop. This is used 
        for sending raw messages to the server. Not for use outside of the 
        scope of this class!
        
        The a `rate` of lines to send may be specified, defaults to 5.0. This 
        corresponds to the `per` parameter, which detauls to 20.0. So a rate 
        of 5 lines per 20 seconds is the default, i.e. no more than 5 lines 
        in 20 seconds.
        '''
        
        for line in lines:
            self.out_buffer += line + '\r\n'
        
    def run(self):
        '''This method sets up the connection by sending the USER command to 
        the server we are connecting to. Once our client is acknowledged and 
        properly registered with the server we can loop through 
        `self.channels` and join the respective channels therein.
        '''
        
        self._register()
        thread.start_new_thread(self._recv, ())
        thread.start_new_thread(self._send, ())
    
    def send_command(self, command, args=[], prefix=None):
        '''This method provides a wrapper to an IRC command. It takes two 
        parameters, `command` and `args` which relate to their respective IRC 
        equivalents.
        
        The arguments are concatenated to the command and then sent along to 
        the connection queue.
        '''
        
        command = command + ' ' + ''.join(args)
        if prefix:
            command = prefix + command
        
        self._send_lines([command])
    
    def send_message(self, recipient, message, action=False, notice=False):
        '''TODO'''
        
        if action:
            self.send_action(recipient, message)
        elif notice:
            self.send_notice(recipient, message)
        else:
            self.send_command('PRIVMSG', [recipient + ' :' + message])
    
    def send_reply(self, message, action=False, line_limit=400):
        '''Warning: Deprecated. Use the reply method in bot.py instead.'''
        
        if self.context['sender'].startswith('#'):
            recipient = self.context['sender']
        else:
            recipient = self.context['user']
        
        messages = []
        def handle_long_message(message):
            message, extra = message[:line_limit], message[line_limit:]
            messages.append(message)
            if extra:
                handle_long_message(extra)
        handle_long_message(message)
        
        for message in messages:
            self.send_message(recipient, message, action)
    
    def send_notice(self, recipient, message):
        '''TODO'''
        
        self.send_command('NOTICE', [recipient + ' :' + message])
    
    def send_action(self, recipient, message):
        '''TODO'''
        
        message = chr(1) + 'ACTION ' + message + chr(1)
        self.send_message(recipient, message)
    
    def quit(self, message='kaa', wait=1.0):
        '''TODO'''
        
        self.send_command('QUIT', ':' + message)
        self.connection.close()
        time.sleep(wait)

