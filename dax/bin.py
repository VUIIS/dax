""" File containing functions called by dax executables """
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import imp
import socket
import redcap
import logging
from datetime import datetime

import log
import XnatUtils
from dax_settings import  API_URL, API_KEY_DAX, API_KEY_XNAT, REDCAP_VAR

def set_logger(logfile, debug):
    """ function to set the logger """
    #Logger for logs
    if debug:
        logger = log.setup_debug_logger('dax', logfile)
    else:
        logger = log.setup_info_logger('dax', logfile)
    return logger

def launch_jobs(settings_path, logfile, debug, projects=None, sessions=None):
    """ function to launch tasks on the cluster """
    #Logger for logs
    logger = set_logger(logfile, debug)

    logger.info('Current Process ID: '+str(os.getpid()))
    logger.info('Current Process Name: dax.bin.update('+settings_path+')')
    # Load the settings file
    logger.info('loading settings from:'+settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the updates
    logger.info('running update, Start Time:'+str(datetime.now()))
    settings.myLauncher.launch_jobs(lockfile_prefix, projects, sessions)
    logger.info('finished update, End Time: '+str(datetime.now()))

def build(settings_path, logfile, debug, projects=None, sessions=None):
    """ function to build the database: scans inputs and  the assessors """
    #Logger for logs
    logger = set_logger(logfile, debug)

    logger.info('Current Process ID: '+str(os.getpid()))
    logger.info('Current Process Name: dax.bin.update('+settings_path+')')
    # Load the settings file
    logger.info('loading settings from:'+settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the updates
    logger.info('running update, Start Time:'+str(datetime.now()))
    settings.myLauncher.build(lockfile_prefix, projects, sessions)
    logger.info('finished update, End Time: '+str(datetime.now()))

def update_tasks(settings_path, logfile, debug, projects=None, sessions=None):
    """ function to run update for tasks """
    #Logger for logs
    logger = set_logger(logfile, debug)

    logger.info('Current Process ID: '+str(os.getpid()))
    logger.info('Current Process Name: dax.bin.update_open_tasks('+settings_path+')')
    # Load the settings file
    logger.info('loading settings from:'+settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the update
    logger.info('updating open tasks, Start Time:'+str(datetime.now()))
    settings.myLauncher.update_tasks(lockfile_prefix, projects, sessions)
    logger.info('finished open tasks, End Time: '+str(datetime.now()))

#function to send the data to the VUIIS XNAT Jobs redcap project about what is running
def save_job_redcap(data, record_id):
    """ save the jobid on redcap for stats """
    logger = logging.getLogger('dax')
    mess_format = """ ->Record {record_id} uploaded for <{name}> : {response}"""
    if API_URL and API_KEY_XNAT:
        try:
            job_redcap_project = redcap.Project(API_URL, API_KEY_XNAT)
            response = job_redcap_project.import_records([data])
            assert 'count' in response

            logger.info(mess_format.format(record_id=record_id,
                                           name=data['spider_module_name'],
                                           response=str(response['count'])))
            return 1
        except:
            return 0
    logger.info(' ->API_URL or API_KEY_XNAT not set')
    return 0

#create the data record for redcap
def create_record_redcap(project, sm_name):
    """ SM_name means the spider name or modules name
          name_v# or name_vDEV#
    """
    #data for redcap
    data = dict()
    #create the record_ID
    date = str(datetime.now())
    record_id = project+'-'+date.strip().replace(':', '_').replace('.', '_').replace(' ', '_')
    labels = sm_name.split('_v')
    #version in the name, if not it's 0
    if len(labels) > 1:
        # 2 for '_v'  + number of characters in the last labels that is the version number
        nb_c = 2 + len(labels[-1])
        name = sm_name[:-nb_c]
        version = 'v' + labels[-1]
    else:
        name = sm_name
        version = 'v0'

    #create the data for redcap
    data['record_id'] = record_id
    data['spider_module_name'] = name
    data['spider_module_version'] = version
    data['date'] = date
    data['xnat_project'] = project
    data['hostname'] = socket.gethostname()
    data['pi_lastname'] = pi_from_project(project)
    return data, record_id

def pi_from_project(project):
    """ get the pi name for the project """
    pi_name = ''
    try:
        xnat = XnatUtils.get_interface()
        proj = xnat.select.project(project)
        pi_name = proj.attrs.get('xnat:projectdata/pi/lastname')
    except:
        pass
    finally:
        xnat.disconnect()
        return pi_name

def upload_update_date_redcap(project_list, type_update, start_end):
    """
        project_list: projects from XNAT that corresponds to record on REDCap
        type_update : 1 for dax_build / 2 for dax_update_tasks / 3 for dax_launch
        start_end   : 1 for starting date / 2 for ending date
    """
    logger = logging.getLogger('dax')
    if API_URL and API_KEY_DAX and REDCAP_VAR:
        redcap_project = None
        try:
            redcap_project = redcap.Project(API_URL, API_KEY_DAX)
        except:
            logger.warn('Could not access redcap. Either wrong API_URL/API_KEY or redcap down.')

        if redcap_project:
            data = list()
            for project in project_list:
                to_upload = dict()
                to_upload[REDCAP_VAR['project']] = project
                if type_update == 1:
                    to_upload = set_variables_dax_manager(to_upload, 'dax_build', start_end)
                elif type_update == 2:
                    to_upload = set_variables_dax_manager(to_upload, 'dax_update_tasks', start_end)
                elif type_update == 3:
                    to_upload = set_variables_dax_manager(to_upload, 'dax_launch', start_end)
                data.append(to_upload)
            XnatUtils.upload_list_records_redcap(redcap_project, data)

def set_variables_dax_manager(record_data, field_prefix, start_end):
    """ set fields to upload to redcap for PID/dates (dax_manager) """
    if start_end == 1:
        key = REDCAP_VAR[field_prefix+'_start_date']
        record_data[key] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
        record_data[REDCAP_VAR[field_prefix+'_end_date']] = 'In Process'
        record_data[REDCAP_VAR[field_prefix+'_pid']] = str(os.getpid())
    elif start_end == 2:
        key = REDCAP_VAR[field_prefix+'_end_date']
        record_data[key] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    return record_data
