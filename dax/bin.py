#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import imp
import socket
import os
import sys
import shutil
import re
import logging
from datetime import datetime

from lxml import etree

import redcap

import log
import XnatUtils
from dax_settings import  API_URL,API_KEY_DAX,API_KEY_XNAT,REDCAP_VAR

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
    settings.myLauncher.update(lockfile_prefix,None,None)
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
    settings.myLauncher.update_open_tasks(lockfile_prefix,None,None)
    logger.info('finished open tasks, End Time: '+str(datetime.now()))

##################################################################################################################
#                           Save in REDCap jobs running or last_update time and PID                              #
##################################################################################################################
#function to send the data to the VUIIS XNAT Jobs redcap project about what is running
def save_job_redcap(data,record_id):
    logger=logging.getLogger('dax')
    if API_URL and API_KEY_XNAT:
        try:
            job_redcap_project = redcap.Project(API_URL, API_KEY_XNAT)
            response = job_redcap_project.import_records([data])
            assert 'count' in response
            logger.info(' ->Record '+record_id+ ' uploaded for <'+data['spider_module_name']+'> : ' + str(response['count']))
            return 1
        except AssertionError as e:
            return 0
    logger.info(' ->API_URL or API_KEY_XNAT not set')
    return 0

#create the data record for redcap
def create_record_redcap(project,SM_name):
    """ SM_name means the spider name or modules name: name_v# or name_vDEV#
    """
    #data for redcap
    data=dict()
    #create the record_ID
    date=str(datetime.now())
    record_id=project+'-'+date.strip().replace(':','_').replace('.','_').replace(' ','_')
    labels=SM_name.split('_v')
    #version in the name, if not it's 0
    if len(labels)>1:
        # _v ( equals to 2 characters) + number of characters in the last labels that is the version number
        nb_c=2+len(labels[-1])
        name=SM_name[:-nb_c]
        version='v'+labels[-1]
    else:
        name=SM_name
        version='v0'

    #create the data for redcap
    data['record_id']=record_id
    data['spider_module_name']=name
    data['spider_module_version']=version
    data['date']=date
    data['xnat_project']=project
    data['hostname'] = socket.gethostname()
    data['pi_lastname'] = pi_from_project(project)
    return data,record_id

def pi_from_project(project):
    pi = ''
    try:
        xnat = XnatUtils.get_interface()
        proj = xnat.select.project(project)
        pi = proj.attrs.get('xnat:projectdata/pi/lastname')
    except:
        pass
    finally:
        xnat.disconnect()
        return pi

def upload_update_date_redcap(project_list,type_update,start_end):
    """ 
        project_list: projects from XNAT that corresponds to record on REDCap
        type_update : 1 for dax_update / 2 for dax_update_open_tasks
        start_end   : 1 for starting date / 2 for ending date
    """
    logger=logging.getLogger('dax')
    if API_URL and API_KEY_DAX and REDCAP_VAR:
        rc=None
        try:
            rc = redcap.Project(API_URL,API_KEY_DAX)
        except:
            logger.warn('Could not access redcap. Either wrong API_URL/API_KEY or redcap down. The last update PID and data will not be saved.')
        
        if rc:
            data=list()
            for project in project_list:
                to_upload=dict()
                to_upload[REDCAP_VAR['project']]=project
                if type_update==1 and start_end==1:
                    to_upload[REDCAP_VAR['update_start_date']]='{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) 
                    to_upload[REDCAP_VAR['update_end_date']]='In Process'
                    to_upload[REDCAP_VAR['update_pid']]=str(os.getpid())
                elif type_update==1 and start_end==2:
                    to_upload[REDCAP_VAR['update_end_date']]='{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
                elif type_update==2 and start_end==1:
                    to_upload[REDCAP_VAR['open_start_date']]='{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
                    to_upload[REDCAP_VAR['open_end_date']]='In Process'
                    to_upload[REDCAP_VAR['update_open_pid']]=str(os.getpid())
                elif type_update==2 and start_end==2:
                    to_upload[REDCAP_VAR['open_end_date']]='{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
                data.append(to_upload)
            XnatUtils.upload_list_records_redcap(rc,data)
