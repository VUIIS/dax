#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""errors.py

Method related to errors and Custom Exceptions.
"""

import netrc
import sys


__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ['DaxError', 'DaxXnatError', 'DaxProcessorError',
           'DaxSetupError', 'DaxNetrcError', 'DaxUploadError',
           'XnatAuthentificationError', 'XnatUtilsError', 'XnatAccessError',
           'XnatToolsError', 'XnatToolsUserError',
           'ClusterLaunchException', 'ClusterCountJobsException',
           'ClusterJobIDException',
           'AutoProcessorError']


# DAX error:
class DaxError(Exception):
    """Basic exception for errors raised by dax."""


# DAX XNAT error:
class DaxXnatError(DaxError):
    """Basic exception for errors related to XNAT raised by dax."""


# DAX Processor error:
class DaxProcessorError(DaxError):
    """Basic exception for errors related to processor raised by dax."""


# dax_setup errors
class DaxSetupError(DaxError, ValueError):
    """DaxSetup exception."""
    def __init__(self, message):
        Exception.__init__(self, 'Error in dax setup: %s' % message)


# Launcher errors:
class DaxUploadError(DaxError):
    """Custom exception raised with dax upload."""
    def __init__(self, message):
        Exception.__init__(self, 'Error with dax upload: %s' % message)


# Dax netrc errors
class DaxNetrcError(netrc.NetrcParseError):
    """Basic exception for errors related to DAX_Netrc raised by dax."""


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


class XnatToolsError(DaxError):
    """Xnat Tools Exception."""
    def __init__(self, message):
        Exception.__init__(self, 'Error in xnat_tools: %s' % message)


class XnatToolsUserError(DaxError):
    """Xnat Tools Exception."""
    def __init__(self, script, message):
        print(('\n%s: error: %s' % (script, message)))
        sys.exc_info()[-1]
        sys.exit(self)


class XnatAccessError(DaxXnatError, ValueError):
    """XNAT access exception if item does not exist."""
    def __init__(self, message):
        Exception.__init__(self, 'Error to access XNAT object: %s' % message)


# Cluster errors
class ClusterError(DaxError):
    """Basic exception for errors related to cluster raised by dax."""


class ClusterLaunchException(ClusterError):
    """Custom exception raised when launch on the grid failed"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to launch job on the grid.')


class ClusterCountJobsException(ClusterError):
    """Custom exception raised when attempting to get the number of
    jobs fails"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to fetch number of '
                                 'jobs from the grid.')


class ClusterJobIDException(ClusterError):
    """Custom exception raised when attempting to get the job id failed"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to get job id.')


# Task:
class NeedInputsException(DaxError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NoDataException(DaxError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Processor Exception:
class AutoProcessorError(DaxProcessorError):
    pass
