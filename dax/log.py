#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

def setup_debug_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
    
def setup_info_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
