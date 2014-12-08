#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

def setup_debug_logger(name,logfile):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    
    if logfile:
        handler=logging.FileHandler(logfile,'w')
    else:
        handler=logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
    
def setup_info_logger(name,logfile):
    if logfile:
        handler=logging.FileHandler(logfile,'w')
    else:
        handler=logging.StreamHandler()
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
