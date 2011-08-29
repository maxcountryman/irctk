'''
    irctk.logger
    ------------
    
    Creates the logging object `logger`.
'''

from __future__ import absolute_import

import logging

FORMAT = '%(asctime)s %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'

def create_logger():
    logger = logging.getLogger('irctk')
    logger.setLevel(logging.DEBUG)
    
    #fh = logging.FileHandler('kaa.log')
    #fh.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    
    ch.setFormatter(formatter)
    #fh.setFormatter(formatter)
    
    logger.addHandler(ch)
    #logger.addHandler(fh)
    
    return logger
