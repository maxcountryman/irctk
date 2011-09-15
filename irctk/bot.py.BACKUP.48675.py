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
<<<<<<< HEAD
import time
=======
import imp
>>>>>>> 1a3aea064ec7f0ab1ebec0a8727ff65c096ba35e

from ssl import wrap_socket

from .logging import create_logger

logger = create_logger()


<<<<<<< HEAD
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
=======
class Bot(object):
    _instance = None
    root_path = os.path.abspath('')
    work_queue = Queue.Queue()
    return_queue = Queue.Queue()
    worker_pool = []
    
    default_config = dict({
        'SERVER': 'irc.voxinfinitus.net',
        'PORT': 6697,
        'SSL': True,
        'TIMEOUT': 300,
        'NICK': 'Kaa',
        'REALNAME': 'Kaa the rock python',
        'CHANNELS': ['#voxinfinitus'],
        'PLUGINS': [],
        'EVENTS': [],
        'WORKERS': 2
        })
>>>>>>> 1a3aea064ec7f0ab1ebec0a8727ff65c096ba35e
    
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
    
    def __init__(self, host, port, ssl=False, timeout=300):
        self.ssl = ssl
        self.host = host
        self.port = port
        self.inp = Queue.Queue()
        self.out = Queue.Queue()
        self.inp_buffer = ''
        self.out_buffer = ''
        self.shutdown = False
        self.timeout = timeout
        socket.setdefaulttimeout(self.timeout)
        self.logger = logger
    
    def connect(self):
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
        thread.start_new_thread(self._recv, ())
        thread.start_new_thread(self._send, ())
    
<<<<<<< HEAD
    def close(self, wait=1):
        '''This method closes an open socket. As per the original UNIX spec, 
        the socket is first alerted of an imminent shutdown by calling 
        `shutdown()`. We then wait for `wait`-number of seconds. Finally we 
        call `close()` on the socket.
        '''
        
        self.shutdown = True
        
        self.socket.shutdown(1)
        time.sleep(wait)
        self.socket.close()
    
    def reconnect(self, wait=1):
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
            time.sleep(wait)
            self.connect()
        except Exception, e:
            self.logger.debug('exception during reconnect: ' + str(e))
    
    def _recv(self):
        '''Internal method that processes incoming data.'''
        
        while True:
            
            data = self.socket.recv(4096)
            self.inp_buffer += data
            
            while '\r\n' in self.inp_buffer and not self.shutdown:
                
                line, self.inp_buffer = self.inp_buffer.split('\r\n', 1)
                self.inp.put(line + '\r\n')
                self.logger.info(line)
    
    def _send(self):
        '''Internal method that processes outgoing data.'''
        
        while True:
            
            line = self.out.get().splitlines()
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
=======
    def _dispatch_plugin(self, plugin, hook, context):
        '''TODO'''
        
        if context == hook or context.startswith(hook + ' '):
            plugin_args = plugin['context']['message'].split(hook, 1)[-1].strip()
            plugin_context = Context(plugin['context'], plugin_args)
            
            self.work_queue.put((plugin, plugin_context))
    
    def _handle_plugin_messages(self):
        while not self.return_queue.empty():
            message, plugin_context, action, notice = self.return_queue.get()
            if message:
                self.reply(message, plugin_context.line, action, notice)
>>>>>>> 1a3aea064ec7f0ab1ebec0a8727ff65c096ba35e
    
    An instance of this class might look like:
        
        # setup a client-connection with SSL
        client = TcpClient('irc.voxinfinitus.net', 6697, True)
        
        # connect to the server
        client.connect()
        
        # define some channels to join
        channels = ['#voxinfinitus', '#testing']
        
<<<<<<< HEAD
        irc = IrcWrapper(client, 'Kaa', 'Kaa the Python', channels)
    '''
    
    def __init__(self, connection, nick, realname, channels):
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
    
    def _send(self, wait=0.01, rate=3.0, per=60.0):
        '''This internal method reads off of `self.out_buffer`, sending the 
        contents to the connection object's output queue.
        
        Here we use `time.sleep` to sleep `wait`-number of seconds. This 
        prevents the threads from running all the time and consequently 
        maxing out the CPU.
        
        TODO: rate limiter does not yet work. Perhaps a proper implementation 
        of the leaky bucket?
        '''
        
        wait_time = 1.0
        while True:
            time.sleep(wait)
            while '\r\n' in self.out_buffer and not self.connection.shutdown:
                line, self.out_buffer = self.out_buffer.split('\r\n', 1)
                if len(self.out_buffer) >= 8192:
                    wait_time *= wait_time
                    time.sleep(wait_time)
                elif wait_time > 1.0:
                    wait_time /= wait_time
                elif wait_time < 1.0:
                    wait_time = 1.0
                self.connection.out.put(line)
    
    def _recv(self, wait=0.01):
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
            time.sleep(wait)
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
                    
                    if self.command == 'PING':
                        self._send_line('PONG ' + ''.join(self.args))
                    if self.command == '001' and self.channels:
                        for channel in self.channels:
                            self._send_line('JOIN ' + channel)
                    if self.command == '433':
                        self.nick = self.nick + '_'
                        self._send_line('NICK ' + self.nick)
    
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
=======
        last_check = time.time()
        idle_workers = 0
        while True:
            time.sleep(0.10)
            
            if len(self.worker_pool) < self.config['WORKERS']:
                for x in range(self.config['WORKERS'] - len(self.worker_pool)):
                    ident = self._spawn_worker()
                    self.logger.info('Spawned worker %d because there are to little.' % ident)
            if not self.work_queue.empty():
                ident = self._spawn_worker()
                self.logger.info('Spawned worker %d because we have to much work to do.' % ident)
            elif (time.time() - last_check) > 10:
                last_check = time.time()
                if self.work_queue.all_tasks_done.acquire(0):
                    self.work_queue.all_tasks_done.release()
                    if len(self.worker_pool) > self.config['WORKERS']:
                        idle_workers += 1
                        self.logger.info('We have %d idle workers.' % idle_workers)
            
            if idle_workers > self.config['WORKERS']:
                ident = self.worker_pool.pop(0)
                idle_workers -= 1
                self.logger.info('Killed left over worker %d.' % ident)
            
            with self.irc.lock:
                context_stale = self.irc.context.get('stale')
                args = self.irc.context.get('args')
                command = self.irc.context.get('command')
                message = self.irc.context.get('message')
                while not context_stale and args:
                    if message.startswith(prefix):
                        for plugin in self.config['PLUGINS']:
                            plugin['context'] = self.irc.context # set context
                            hook = prefix + plugin['hook']
                            try:
                                self._dispatch_plugin(plugin, hook, message)
                            except Exception, e:
                                self.logger.error(str(e))
                                continue
                    if command and command.isupper():
                        for event in self.config['EVENTS']:
                            event['context'] = self.irc.context
                            hook = event['hook']
                            try:
                                thread.start_new_thread(self._dispatch_plugin, (event, hook, command))
                            except Exception, e:
                                self.logger.error(str(e))
                                continue
                    
                    # we're done here, context is stale, give us fresh fruit!
                    context_stale = self.irc.context['stale'] = True
                    # Finaly handle messages returned from the plugins.
                    #self._handle_plugin_messages()
                self._handle_plugin_messages()
>>>>>>> 1a3aea064ec7f0ab1ebec0a8727ff65c096ba35e
    
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
    
<<<<<<< HEAD
    def send_message(self, recipient, message, action=False, notice=False):
        '''TODO'''
=======
    def command(self, hook=None, **kwargs):
        '''This method provides a decorator that can be used to load a 
        function into the global plugins list.:
        
        If the `hook` parameter is provided the decorator will assign the hook 
        key to the value of `hook`, update the `plugin` dict, and then return 
        the wrapped function to the wrapper.
        
        Therein the plugin dictionary is updated with the `func` key whose 
        value is set to the wrapped function.
        
        Otherwise if no `hook` parameter is passed the, `hook` is assumed to 
        be the wrapped function and handled accordingly.
        '''
        
        plugin = {}
        
        def wrapper(f):
            plugin.setdefault('hook', f.func_name)
            plugin['func'] = f
            plugin['help'] = f.__doc__ if f.__doc__ else 'no help provided'
            self._update_plugins('PLUGINS', plugin)
            return f
        
        if kwargs or not inspect.isfunction(hook):
            if hook:
                plugin['hook'] = hook
            plugin.update(kwargs)
            return wrapper
        else:
            return wrapper(hook)
    
    def event(self, hook, **kwargs):
        '''This method provides a decorator that can be used to load a 
        function into the global events list.
        
        It assumes one parameter, `hook`, i.e. the event you wish to bind 
        this wrapped function to. For example, JOIN, which would call the 
        function on all JOIN events.
        '''
        
        plugin = {}
        
        def wrapper(f):
            plugin['func'] = f
            self._update_plugins('EVENTS', plugin)
            return f
        
        plugin['hook'] = hook
        plugin.update(kwargs)
        return wrapper
    
    def reply(self, message, context, action=False, notice=False, line_limit=400):
        '''TODO'''
        
        if context['sender'].startswith('#'):
            recipient = context['sender']
        else:
            recipient = context['user']
        
        messages = []
        def handle_long_message(message):
            message, extra = message[:line_limit], message[line_limit:]
            messages.append(message)
            if extra:
                handle_long_message(extra)
        handle_long_message(message)
        
        for message in messages:
            self.irc.send_message(recipient, message, action, notice)
    
    def run(self, wait=0.01):
>>>>>>> 1a3aea064ec7f0ab1ebec0a8727ff65c096ba35e
        
        if action:
            self.send_action(recipient, message)
        elif notice:
            self.send_notice(recipient, message)
        else:
            self.send_command('PRIVMSG', [recipient + ' :' + message])
    
    def send_reply(self, message, action=False, line_limit=400):
        '''Warning: Deprecated. Use the reply method in bot.py instead.'''
        
        #get context
        
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
        
<<<<<<< HEAD
        self.send_command('NOTICE', [recipient + ' :' + message])
    
    def send_action(self, recipient, message):
        '''TODO'''
=======
        # Set the worker thread pool up.
        for x in range(self.config['WORKERS']):
            self._spawn_worker()
        
        self.connection.connect()
        self.irc.run()
>>>>>>> 1a3aea064ec7f0ab1ebec0a8727ff65c096ba35e
        
        message = chr(1) + 'ACTION ' + message + chr(1)
        self.send_message(recipient, message)
    
    def quit(self, message='kaa'):
        '''TODO'''
        
        self.send_command('QUIT', ':' + message)
        self.connection.close()
        time.sleep(1)


<<<<<<< HEAD
class IrcTestClient(IrcWrapper):
=======
    def _spawn_worker(self):
        ident = thread.start_new_thread(self._plugin_worker,
                                       (self.work_queue, self.return_queue))
        self.worker_pool.append(ident)
        return ident

    def _plugin_worker(self, work_queue, return_queue):
        ''' Pols the work_queue for jobs, runs them and places the result on the
        return_queue.'''
        try:
            while thread.get_ident() in self.worker_pool:
                plugin, plugin_context = work_queue.get(True)
                takes_args = inspect.getargspec(plugin['func']).args
                
                action = False
                if plugin.get('action') == True:
                    action = True
                
                notice = False
                if plugin.get('notice') == True:
                    notice = True
                
                if takes_args:
                    message = plugin['func'](plugin_context)
                else:
                    message = plugin['func']()
                return_queue.put((message, plugin_context, action, notice))
                self.work_queue.task_done()
        # Catch all exceptions so we can notify the pool we died.
        except Exception, e:
            message = 'Error in worker thread, Exiting.'
            self.logger.error(message)
            self.logger.error(str(e))
            self.worker_pool.remove(thread.get_ident())
            raise


class TestBot(Bot):
    shutdown = False
    
    def __init__(self):
        self.config = Config(self.root_path, self.default_config)
        self.irc = IrcTestClient(
                self.config['NICK'], 
                self.config['REALNAME'], 
                self.config['CHANNELS']
                )
        self.connection = self.irc.connection
>>>>>>> 1a3aea064ec7f0ab1ebec0a8727ff65c096ba35e
    
    def __init__(self, nick, realname, channels):
        self.connection = Queue.Queue()
        self.connection.out = Queue.Queue()
        self.connection.inp = Queue.Queue()
        self.nick = nick
        self.realname = realname
        self.user = 'USER ' + nick + ' 3 * ' + realname
        self.channels = channels
        self.inp_buffer = ''
        self.out_buffer = ''
        
        self.context = {}
        
    def _send(self, wait=0.01):
        
        while True:
            try:
                time.sleep(wait)
                while '\r\n' in self.out_buffer:
                    line, self.out_buffer = self.out_buffer.split('\r\n', 1)
                    self.connection.out.put(line)
            except Exception:
                pass

