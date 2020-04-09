#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys


def setup_debug_logger(name, logfile):
    """
    Sets up the debug logger

    :param name: Name of the logger
    :param logfile: file to store the log to. sys.stdout if no file define
    :return: logger object

    """
    fmt = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    formatter = logging.Formatter(fmt=fmt)

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
    """
    Sets up the info logger

    :param name: Name of the logger
    :param logfile: file to store the log to. sys.stdout if no file define
    :return: logger object

    """
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def setup_critical_logger(name, logfile):
    """
    Sets up the critical logger

    :param name: Name of the logger
    :param logfile: file to store the log to. sys.stdout if no file define
    :return: logger object

    """
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.CRITICAL)
    logger.addHandler(handler)
    return logger


def setup_warning_logger(name, logfile):
    """
    Sets up the warning logger

    :param name: Name of the logger
    :param logfile: file to store the log to. sys.stdout if no file define
    :return: logger object

    """
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)
    return logger


def setup_error_logger(name, logfile):
    """
    Sets up the error logger

    :param name: Name of the logger
    :param logfile: file to store the log to. sys.stdout if no file define
    :return: logger object

    """
    if logfile:
        handler = logging.FileHandler(logfile, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    return logger
