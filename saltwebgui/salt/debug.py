# -*- coding: utf-8 -*-
"""Debug helper function"""
#import inspect

DEBUG = 1

def debug(information):
    """If in debug-mode print information on output"""
    if DEBUG == 0:
        return
    elif DEBUG == 1:
        print information
    elif DEBUG == 2:
        #print inspect.stack()
        print information

