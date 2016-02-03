""" File containing functions called by dax executables """
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import imp
import redcap
import logging
from datetime import datetime

import log
import XnatUtils
from dax_settings import  API_URL, API_KEY_DAX, REDCAP_VAR

def set_logger(logfile, debug):
    """
    Set the logging depth

    :param logfile: File to log output to
    :param debug: Should debug depth be used?
    :return: logger object

    """
    #Logger for logs
    if debug:
        logger = log.setup_debug_logger('dax', logfile)
    else:
        logger = log.setup_info_logger('dax', logfile)
    return logger

def launch_jobs(settings_path, logfile, debug, projects=None, sessions=None):
    """
    Method to launch jobs on the grid

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be launched
    :param sessions: Session(s) that need to be updated
    :return: None

    """
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
    """
    Method that is responsible for running all modules and putting assessors
     into the database

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be launched
    :param sessions: Session(s) that need to be updated
    :return: None

    """
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
    """
    Method that is responsible for updating a Task.

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be launched
    :param sessions: Session(s) that need to be updated
    :return: None

    """
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

def pi_from_project(project):
    """
    Get the last name of PI who owns the project on XNAT

    :param project: String of the ID of project on XNAT.
    :return: String of the PIs last name

    """
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
    Upload the timestamp of when bin ran on a project (start and finish).

    :param project_list: List of projects that were updated
    :param type_update: What type of process ran: dax_build (1),
     dax_update_tasks (2), dax_launch (3)
    :param start_end: starting timestamp (1) and ending timestamp (2)
    :return: None

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
    """
    Update the process id of what was running and when

    :param record_data: the REDCap record infor from Project.export_records()
    :param field_prefix: prefix to make field assignment simpler
    :param start_end: 1 if starting process, 2 if ending process
    :return: updated record_data to upload to REDCap

    """
    if start_end == 1:
        key = REDCAP_VAR[field_prefix+'_start_date']
        record_data[key] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
        record_data[REDCAP_VAR[field_prefix+'_end_date']] = 'In Process'
        record_data[REDCAP_VAR[field_prefix+'_pid']] = str(os.getpid())
    elif start_end == 2:
        key = REDCAP_VAR[field_prefix+'_end_date']
        record_data[key] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    return record_data
