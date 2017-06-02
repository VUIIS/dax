#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" File containing functions called by dax executables """

from datetime import datetime
import imp
import logging
import os
import redcap
import yaml

from . import Launcher
from . import log
from . import XnatUtils
from .dax_settings import DAX_Settings
from .errors import DaxError
DAX_SETTINGS = DAX_Settings()


def set_logger(logfile, debug):
    """
    Set the logging depth

    :param logfile: File to log output to
    :param debug: Should debug depth be used?
    :return: logger object

    """
    # Logger for logs
    if debug:
        logger = log.setup_debug_logger('dax', logfile)
    else:
        logger = log.setup_info_logger('dax', logfile)
    return logger


def launch_jobs(settings_path, logfile, debug, projects=None, sessions=None,
                writeonly=False, pbsdir=None, force_no_qsub=False):
    """
    Method to launch jobs on the grid

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be launched
    :param sessions: Session(s) that need to be updated
    :param writeonly:  write the job files without submitting them
    :param pbsdir: folder to store the pbs file
    :param force_no_qsub: run the job locally on the computer (serial mode)
    :return: None

    """
    # Logger for logs
    logger = set_logger(logfile, debug)

    logger.info('Current Process ID: %s' % str(os.getpid()))
    logger.info('Current Process Name: dax.bin.update(%s)' % settings_path)
    # Load the settings file
    logger.info('loading settings from: %s' % settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the updates
    logger.info('running update, Start Time: %s' % str(datetime.now()))
    try:
        settings.myLauncher.launch_jobs(lockfile_prefix, projects, sessions,
                                        writeonly, pbsdir,
                                        force_no_qsub=force_no_qsub)
    except Exception as e:
        logger.critical('Caught exception launching jobs in bin.launch_jobs')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                e.message))
    logger.info('finished update, End Time: %s' % str(datetime.now()))


def build(settings_path, logfile, debug, projects=None, sessions=None,
          mod_delta=None, proj_lastrun=None):
    """
    Method that is responsible for running all modules and putting assessors
     into the database

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be built
    :param sessions: Session(s) that need to be built
    :return: None

    """
    # Logger for logs
    logger = set_logger(logfile, debug)

    logger.info('Current Process ID: %s' % str(os.getpid()))
    logger.info('Current Process Name: dax.bin.update(%s)' % settings_path)
    # Load the settings file
    logger.info('loading settings from: %s' % settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the updates
    logger.info('running build, Start Time: %s' % str(datetime.now()))
    try:
        settings.myLauncher.build(lockfile_prefix, projects, sessions,
                                  mod_delta=mod_delta, proj_lastrun=proj_lastrun)
    except Exception as e:
        logger.critical('Caught exception building Project in bin.build')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                e.message))

    logger.info('finished build, End Time: %s' % str(datetime.now()))


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
    # Logger for logs
    logger = set_logger(logfile, debug)

    logger.info('Current Process ID: %s' % str(os.getpid()))
    msg = 'Current Process Name: dax.bin.update_open_tasks(%s)'
    logger.info(msg % settings_path)
    # Load the settings file
    logger.info('loading settings from: %s' % settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the update
    logger.info('updating open tasks, Start Time: %s' % str(datetime.now()))
    try:
        settings.myLauncher.update_tasks(lockfile_prefix, projects, sessions)
    except Exception as e:
        logger.critical('Caught exception updating tasks in bin.update_tasks')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                e.message))

    logger.info('finished open tasks, End Time: %s' % str(datetime.now()))


def pi_from_project(project):
    """
    Get the last name of PI who owns the project on XNAT

    :param project: String of the ID of project on XNAT.
    :return: String of the PIs last name

    """
    pi_name = ''
    with XnatUtils.get_interface() as xnat:
        proj = xnat.select.project(project)
        pi_name = proj.attrs.get('xnat:projectdata/pi/lastname')

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
    dax_config = DAX_SETTINGS.get_dax_manager_config()
    logger = logging.getLogger('dax')
    if DAX_SETTINGS.get_api_url() and \
       DAX_SETTINGS.get_api_key_dax() and \
       dax_config:
        redcap_project = None
        try:
            redcap_project = redcap.Project(DAX_SETTINGS.get_api_url(),
                                            DAX_SETTINGS.get_api_key_dax())
        except:
            logger.warn('Could not access redcap. Either wrong DAX_SETTINGS. \
API_URL/API_KEY or redcap down.')

        if redcap_project:
            data = list()
            for project in project_list:
                to_upload = dict()
                to_upload[dax_config['project']] = project
                if type_update == 1:
                    to_upload = set_dax_manager(to_upload, 'dax_build',
                                                start_end)
                elif type_update == 2:
                    to_upload = set_dax_manager(to_upload, 'dax_update_tasks',
                                                start_end)
                elif type_update == 3:
                    to_upload = set_dax_manager(to_upload, 'dax_launch',
                                                start_end)
                data.append(to_upload)
            XnatUtils.upload_list_records_redcap(redcap_project, data)


def set_dax_manager(record_data, field_prefix, start_end):
    """
    Update the process id of what was running and when

    :param record_data: the REDCap record infor from Project.export_records()
    :param field_prefix: prefix to make field assignment simpler
    :param start_end: 1 if starting process, 2 if ending process
    :return: updated record_data to upload to REDCap

    """
    dax_config = DAX_SETTINGS.get_dax_manager_config()
    if start_end == 1:
        key = dax_config[field_prefix + '_start_date']
        record_data[key] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
        record_data[dax_config[field_prefix + '_end_date']] = 'In Process'
        record_data[dax_config[field_prefix + '_pid']] = str(os.getpid())
    elif start_end == 2:
        key = dax_config[field_prefix + '_end_date']
        record_data[key] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    return record_data


def read_yaml_settings(yaml_file):
    """
    Method to read the settings yaml file and generate the launcher object.

    :param yaml_file: path to yaml file defining the settings
    :return: launcher object
    """
    if not os.path.isfile(yaml_file):
        err = 'Path not found for {}'
        raise DaxError(err.format(yaml_file))

    with open(yaml_file, "r") as yaml_stream:
        try:
            doc = yaml.load(yaml_stream)
        except yaml.ComposerError:
            err = 'YAML File {} has more than one document. Please remove \
any duplicate "---" if you have more than one. It should only be at the \
beginning of your file.'
            raise DaxError(err.format(yaml_file))

        # Set Inputs from Yaml
        check_default_keys(yaml_file, doc)

        # Set attributs for settings:
        attrs = doc.get('attrs')

        # Read modules and processors:
        mods = dict()
        modules = doc.get('modules')
        for mod_dict in modules:
            mods[mod_dict.get('name')] = load_from_file(
                mod_dict.get('filepath'), mod_dict.get('arguments'))
        procs = dict()
        processors = doc.get('processors')
        for proc_dict in processors:
            procs[proc_dict.get('name')] = load_from_file(
                proc_dict.get('filepath'), proc_dict.get('arguments'))

        # YAML processors:
        yamlprocs = doc.get('yamlprocessors')

        # project:
        proj_mod = dict()
        proj_proc = dict()
        yaml_proc = dict()
        projects = doc.get('projects')
        for proj_dict in projects:
            project = proj_dict.get('project')
            if project:
                # modules:
                for mod_n in proj_dict.get('modules').split(','):
                    proj_mod[project] = mods[mod_n]
                # processors:
                for proc_n in proj_dict.get('processors').split(','):
                    proj_proc[project] = procs[proc_n]
                # yaml_proc:
                for yaml_n in proj_dict.get('yamlprocessors').split(','):
                    yaml_proc[project] = [_yp for _yp in yamlprocs
                                          if _yp.get('name') == yaml_n]

        # set in attrs:
        attrs['project_process_dict'] = proj_proc
        attrs['project_modules_dict'] = proj_mod
        attrs['yaml_dict'] = yaml_proc

    return Launcher(**attrs)


def check_default_keys(yaml_file, doc):
    """ Static method to raise error if key not found in dictionary from
    yaml file.
    :param yaml_file: path to yaml file defining the processor
    :param doc: doc dictionary extracted from the yaml file
    """
    for key in ['projects', 'attrs', 'modules', 'processors',
                'yamlprocessors']:
        raise_yaml_error_if_no_key(doc, yaml_file, key)


def raise_yaml_error_if_no_key(doc, yaml_file, key):
    """Method to raise an execption if the key is not in the dict
    :param doc: dict to check
    :param yaml_file: YAMLfile path
    :param key: key to search
    """
    if key not in doc.keys():
        err = 'YAML File {} does not have {} defined. See example.'
        raise DaxError(err.format(yaml_file, key))


def load_from_file(filepath, args):
    """
    Check if a file exists and if it's a python file
    :param filepath: path to the file to test
    :return: True the file pass the test, False otherwise
    """
    if not os.path.exists(filepath):
        raise DaxError('File %s does not exists.' % filepath)

    if filepath.endswith('.py'):
        test = imp.load_source('test', filepath)
        # Check if processor file
        try:
            return eval('test.{}(**args)'.format(test.__processor_name__))
        except AttributeError:
            pass

        # Check if it's a module
        try:
            return eval('test.{}(**args)'.format(
                os.path.basename(filepath)[:-3]))
        except AttributeError:
            pass

        err = '[ERROR] Module or processor or myLauncher object NOT FOUND in \
the python file {}.'
        print(err.format(filepath))
        return None
