import unittest
import Queue

from irctk.ircclient import TcpClient, IrcWrapper


class ConnTestCase(unittest.TestCase):
    '''This test case is used to test the TCP client methods.'''
    
    def setUp(self):
        self.conn = TcpClient('127.0.0.1', '6697', True)
        self.assertTrue(self.conn.host == '127.0.0.1')
        self.assertTrue(self.conn.port == '6697')
        self.assertTrue(self.conn.ssl)
        self.assertFalse(self.conn.shutdown)


class IrcWrapperCase(unittest.TestCase):
    '''This test case is used to test the IRC wrapper methods.'''
    
    def setUp(self):
        self.conn = Queue.Queue()
        self.conn.out = ''
        self.wrapper = IrcWrapper(self.conn, 'test', 'tester', ['#test'])
        self.assertTrue(self.wrapper.nick == 'test')
        self.assertTrue(self.wrapper.realname == 'tester')
        self.assertTrue(self.wrapper.channels == ['#test'])
    
    def test_register(self):
        self.wrapper._register()
        nick = 'NICK test\r\n'
        user = 'USER test 3 * tester\r\n'
        self.assertTrue((nick and user) in self.wrapper.out_buffer)
        self.assertEqual(nick, self.wrapper.out_buffer.split('\r\n')[0] + '\r\n')
        self.assertEqual(user, self.wrapper.out_buffer.split('\r\n')[1] + '\r\n')
    
    def test_send(self):
        pass
    
    def test_recv(self):
        pass
    
    def test_parse_line(self):
        pass
    
    def test_send_line(self):
        pass
    
    def test_send_lines(self):
        pass
    
    def test_run(self):
        pass
    
    def test_send_command(self):
        pass
    
    def test_send_message(self):
        pass
    
    def test_send_notice(self):
        pass
    
    def test_send_action(self):
        pass


if __name__ == '__main__':
    unittest.main()
