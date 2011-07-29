#!/usr/bin/python

'''
RecvQ Limiter
'''

import time
import sys

import recvq_settings as conf

def now():
    ''' returns time in milliseconds '''
    return time.time() * 1000

bytes = 0       # bytecount of all sent messages between now and conf.t_limit milliseconds ago
messages = []   # for messages sent

# returns size in bytes? i dont know
def sizeof(txt):
    return sys.getsizeof(txt)

# call in 'send' method used by bot to transmit output to irc
def send(msg):
    
    b = sizeof(msg)
    if not ok2go(b):
        wait(b, msg)
        return False

    log_message(b)
    return True

def log_message(b):
    global messages
    global bytes
    t = now()
    bytes += b
    messages.append((t, b))

def ok2go(b):
    clean()
    if b + bytes > conf.b_limit:
        return False
    return True

def clean():
    '''
    pass over the messages queue and remove expired messages
    '''
    global messages
    n = now()
    _messages = []
    for t, b in messages:
        if n - t > conf.t_limit:
            bytes -= b
        else:
            _messages.append((t,b))
    messages = _messages


'''
Call from a loop
'''
waiting = []
waiting_size = 0
def clear_waiting():
    global waiting
    i = 0
    good = []
    for b, m in waiting:
        if ok2go(b):
            good.append(m)
            log_message(b)
            waiting_size -= b
            i += 1
        else:
            break
    waiting = waiting[i:]
    return good

def wait(b, msg):
    waiting_queue_max = conf.waiting_queue_max
    if waiting_queue_max and waiting_size + b > waiting_queue_max:
        return
    waiting_size += b
    waiting.append(msg)
