#!/usr/bin/python

'''
Configuration for RecvQ Limiter
'''

''' 1000kB in 60s '''
t_limit = 60000 # in ms
b_limit = 1000000  # bytes

''' Maximum size (in bytes) of the waiting queue '''
waiting_queue_max = 0 # any false value == no limit
