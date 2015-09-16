#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

def setup_debug_logger(name, logfile):
    """Logger of level 10"""
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def setup_info_logger(name, logfile):
    """Logger of level 20"""
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def setup_critical_logger(name, logfile):
    """Logger of level 50"""
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.CRITICAL)
    logger.addHandler(handler)
    return logger

def setup_warning_logger(name, logfile):
    """Logger of level 30"""
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)
    return logger

def setup_error_logger(name, logfile):
    """Logger of level 40"""
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    return logger
