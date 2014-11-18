#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, imp
from datetime import datetime
from dax import log

def set_logger(logfile,debug):
    #Logger for logs
    if debug:
        logger = log.setup_debug_logger('dax',logfile)
    else:
        logger = log.setup_info_logger('dax',logfile)
    return logger
    
def update(settings_path,logfile,debug):
    #Logger for logs
    logger=set_logger(logfile,debug)
        
    logger.info('Current Process ID: '+str(os.getpid()))
    logger.info('Current Process Name: dax.bin.update('+settings_path+')')
    # Load the settings file
    logger.info('loading settings from:'+settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the updates
    logger.info('running update, Start Time:'+str(datetime.now()))
    settings.myLauncher.update(lockfile_prefix)
    logger.info('finished update, End Time: '+str(datetime.now()))

def update_open_tasks(settings_path,logfile,debug):
    #Logger for logs
    logger=set_logger(logfile,debug)
        
    logger.info('Current Process ID: '+str(os.getpid()))
    logger.info('Current Process Name: dax.bin.update_open_tasks('+settings_path+')')
    # Load the settings file
    logger.info('loading settings from:'+settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the update
    logger.info('updating open tasks, Start Time:'+str(datetime.now()))
    settings.myLauncher.update_open_tasks(lockfile_prefix)
    logger.info('finished open tasks, End Time: '+str(datetime.now()))
