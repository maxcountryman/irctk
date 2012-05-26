import unittest
import Queue

from irctk.ircclient import TcpClient, IrcWrapper


class TcpClientTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = TcpClient('127.0.0.1', '6697', True, logger=None)
        self.assertEqual(self.conn.host, '127.0.0.1')
        self.assertEqual(self.conn.port, '6697')
        self.assertTrue(self.conn.ssl)
        self.assertFalse(self.conn.shutdown)


class IrcWrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = Queue.Queue()
        self.conn.out = ''
        self.wrapper = IrcWrapper(self.conn,
                                  'test',
                                   'tester',
                                   None,
                                   ['#test'],
                                   None)
        self.assertTrue(self.wrapper.nick == 'test')
        self.assertTrue(self.wrapper.realname == 'tester')
        self.assertTrue(self.wrapper.channels == ['#test'])

    def test_register(self):
        self.wrapper._register()
        nick = 'NICK test\r\n'
        user = 'USER test 3 * tester\r\n'
        self.assertIn(nick, self.wrapper.out_buffer)
        self.assertIn(user, self.wrapper.out_buffer)
        self.assertEqual(nick,
                         self.wrapper.out_buffer.split('\r\n')[0] + '\r\n')
        self.assertEqual(user,
                         self.wrapper.out_buffer.split('\r\n')[1] + '\r\n')

    def test_send(self):
        pass

    def test_recv(self):
        pass

    def test_parse_line(self):
        line = 'PRIVMSG #testing :test message'
        prefix, command, args = self.wrapper._parse_line(line)
        self.assertEqual(prefix, '')
        self.assertEqual(command, 'PRIVMSG')
        self.assertEqual(args, ['#testing', 'test message'])

        line = \
            ':server.example.net NOTICE Auth :*** Looking up your hostname...'
        prefix, command, args = self.wrapper._parse_line(line)
        self.assertEqual(prefix, 'server.example.net')
        self.assertEqual(command, 'NOTICE')
        self.assertEqual(args, ['Auth', '*** Looking up your hostname...'])

    def test_send_line(self):
        line = 'test'
        self.wrapper._send_line(line)
        self.assertEqual('test\r\n', self.wrapper.out_buffer)

    def test_send_lines(self):
        lines = ['foo', 'bar', 'baz']
        expected_result = 'foo\r\nbar\r\nbaz\r\n'
        self.wrapper._send_lines(lines)
        self.assertEqual(expected_result, self.wrapper.out_buffer)

    def test_send_command(self):
        command = 'PRIVMSG'
        args = ['#test' + ' :' + 'test']
        expected_result = 'PRIVMSG #test :test\r\n'
        self.wrapper.send_command(command, args)
        self.assertEqual(expected_result, self.wrapper.out_buffer)

    def test_send_message(self):
        recipient = '#test'
        message = 'test'
        expected_result = 'PRIVMSG #test :test\r\n'
        self.wrapper.send_message(recipient, message)
        self.assertEqual(expected_result, self.wrapper.out_buffer)
        self.wrapper.out_buffer = ''

        recipient = '#test'
        message = 'dances'
        expected_result = 'PRIVMSG #test :\x01ACTION dances\x01\r\n'
        self.wrapper.send_message(recipient, message, action=True)
        self.assertEqual(expected_result, self.wrapper.out_buffer)
        self.wrapper.out_buffer = ''

        recipient = '#test'
        message = 'attention!'
        expected_result = 'NOTICE #test :attention!\r\n'
        self.wrapper.send_message(recipient, message, notice=True)
        self.assertEqual(expected_result, self.wrapper.out_buffer)

    def test_send_notice(self):
        pass

    def test_send_action(self):
        pass


if __name__ == '__main__':
    unittest.main()
