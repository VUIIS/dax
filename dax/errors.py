#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""errors.py

Method related to errors and Custom Exceptions.
"""

import netrc

__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ['DaxError', 'DaxXnatError', 'DaxSetupError', 'DaxNetrcError',
           'XnatAuthentificationError', 'XnatUtilsError', 'XnatAccessError',
           'ClusterLaunchException', 'ClusterCountJobsException',
           'ClusterJobIDException']


# DAX error:
class DaxError(Exception):
    """Basic exception for errors raised by dax."""


# DAX XNAT error:
class DaxXnatError(DaxError):
    """Basic exception for errors related to XNAT raised by dax."""


# dax_setup errors
class DaxSetupError(DaxError, ValueError):
    """DaxSetup exception."""
    def __init__(self, message):
        Exception.__init__(self, 'Error in dax_setup: %s' % message)


# Dax netrc errors
class DaxNetrcError(netrc.NetrcParseError):
    """Basic exception for errors related to dax raised by dax."""


# Launcher errors:
class DaxLauncherError(DaxError):
    """Custom exception raised with dax launcher."""
    def __init__(self, message):
        Exception.__init__(self, 'Error with Launcher: %s' % message)


# XnatUtils errors
class XnatAuthentificationError(DaxXnatError):
    """Custom exception raised when xnat connection failed."""
    def __init__(self, host=None, user=None):
        msg = 'ERROR: XNAT Authentification failed. Check logins.'
        if host:
            msg = '%s. Host: %s' % (msg, host)
            if user:
                msg = '%s / User: %s' % (msg, user)
        Exception.__init__(self, msg)


class XnatUtilsError(DaxXnatError):
    """XnatUtils exception."""
    def __init__(self, message):
        Exception.__init__(self, 'Error in XnatUtils: %s' % message)


class XnatAccessError(DaxXnatError, ValueError):
    """XNAT access exception if item does not exist."""
    def __init__(self, message):
        Exception.__init__(self, 'Error to access XNAT object: %s' % message)


# Cluster errors
class ClusterLaunchException(Exception):
    """Custom exception raised when launch on the grid failed"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to launch job on the grid.')


class ClusterCountJobsException(DaxError):
    """Custom exception raised when attempting to get the number of
    jobs fails"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to fetch number of '
                                 'jobs from the grid.')


class ClusterJobIDException(DaxError):
    """Custom exception raised when attempting to get the job id failed"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to get job id.')
