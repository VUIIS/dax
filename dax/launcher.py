#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" launcher.py that represents the main object called by the executables """

from builtins import input
from builtins import str
from builtins import object
from past.builtins import basestring

from datetime import datetime, timedelta
import logging
import redcap
import sys
import os
import traceback

from . import processors, modules, XnatUtils, task, cluster
from .task import Task, ClusterTask, XnatTask
from .dax_settings import DAX_Settings, DAX_Netrc
from .errors import (ClusterCountJobsException, ClusterLaunchException,
                     DaxXnatError, DaxLauncherError)
from . import yaml_doc
from .processor_graph import ProcessorGraph

try:
    basestring
except NameError:
    basestring = str

__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ['Launcher']
DAX_SETTINGS = DAX_Settings()
UPDATE_PREFIX = 'updated--'
UPDATE_FORMAT = "%Y-%m-%d %H:%M:%S"
BUILD_SUFFIX = 'BUILD_RUNNING.txt'
UPDATE_SUFFIX = 'UPDATE_RUNNING.txt'
LAUNCH_SUFFIX = 'LAUNCHER_RUNNING.txt'
# Logger to print logs
LOGGER = logging.getLogger('dax')


def str_to_timedelta(delta_str):
    if len(delta_str) <= 1:
        raise ValueError('invalid timedelta string value')

    val = int(delta_str[:-1])
    if delta_str.endswith('s'):
        return timedelta(seconds=val)
    elif delta_str.endswith('m'):
        return timedelta(minutes=val)
    elif delta_str.endswith('h'):
        return timedelta(hours=val)
    elif delta_str.endswith('d'):
        return timedelta(days=val)
    else:
        raise ValueError('invalid timedelta string value')


def check_dir(dir_path):
    try:
        os.makedirs(dir_path)
    except OSError:
        if not os.path.isdir(dir_path):
            raise

def task_needs_to_run(procstatus, qcstatus):
    return\
        procstatus in [task.NEED_TO_RUN, task.NEED_INPUTS] or\
        qcstatus in [task.RERUN, task.REPROC, task.DOES_NOT_EXIST]

def task_needs_status_update(qcstatus):
    return qcstatus in [task.RERUN, task.REPROC]

class Launcher(object):
    """ Launcher object to manage a list of projects from a settings file """

    def __init__(self,
                 project_process_dict=dict(),
                 project_modules_dict=dict(),
                 yaml_dict=dict(),
                 priority_project=None,
                 queue_limit=DAX_SETTINGS.get_queue_limit(),
                 root_job_dir=DAX_SETTINGS.get_root_job_dir(),
                 xnat_user=None, xnat_pass=None, xnat_host=None, cr=None,
                 job_email=None, job_email_options='bae', max_age=7,
                 launcher_type=DAX_SETTINGS.get_launcher_type(),
                 skip_lastupdate=None):

        """
        Entry point for the Launcher class

        :param project_process_dict: dictionary associating project & processes
        :param project_modules_dict: dictionary associating project & modules
        :param priority_project: list of project to describe the priority
        :param queue_limit: maximum number of jobs in the queue
        :param root_job_dir: root directory for jobs
        :param xnat_host: XNAT Host url. By default, use env variable.
        :param cr: True if the host is an XNAT CR instance (will default to False if not specified)
        :param xnat_user: XNAT User ID. By default, use env variable.
        :param xnat_pass: XNAT Password. By default, use env variable.
        :param job_email: job email address for report
        :param job_email_options: email options for the jobs
        :param max_age: maximum time before updating again a session
        :return: None
        """
        self.queue_limit = queue_limit
        self.root_job_dir = root_job_dir

        # Processors:
        if not isinstance(project_process_dict, dict):
            err = 'project_process_dict set but it is not a dictionary with \
project name as a key and list of processors objects as values.'
            raise DaxLauncherError(err)
        self.project_process_dict = (project_process_dict
                                     if project_process_dict is not None
                                     else dict())

        # Modules:
        if not isinstance(project_modules_dict, dict):
            err = 'project_modules_dict set but it is not a dictionary with \
project name as a key and list of processors objects as values.'
            raise DaxLauncherError(err)
        self.project_modules_dict = (project_modules_dict
                                     if project_modules_dict is not None
                                     else dict())

        # YAML dict:
        if not isinstance(yaml_dict, dict):
            err = 'Yaml_files set but it is not a dictionary with project \
name as a key and list of yaml filepaths as values.'
            raise DaxLauncherError(err)
        self.yaml_dict = yaml_dict if yaml_dict is not None else dict()

        # Add processors to project_process_dict:
        for project, yaml_objs in list(yaml_dict.items()):
            for yaml_obj in yaml_objs:
                if isinstance(yaml_obj, processors.AutoProcessor):
                    proc = yaml_obj
                elif isinstance(yaml_obj, str):
                    # TODO: BenM/general_refactor/this logic should be handled
                    # further up the call stack - launchers should be provided
                    # AutoProcessors rather than strings for yaml files
                    yaml_obj = yaml_doc.YamlDoc().from_file(yaml_obj)
                    proc = processors.AutoProcessor(XnatUtils, yaml_obj)
                elif isinstance(yaml_obj.yaml_doc.YamlDoc):
                    proc = processors.AutoProcessor(XnatUtils, yaml_obj)
                else:
                    err = 'yaml_obj of type {} is unsupported'
                    raise DaxLauncherError(err.format(type(yaml_obj)))

                if project not in self.project_process_dict:
                    self.project_process_dict[project] = [proc]
                else:
                    self.project_process_dict[project].append(proc)

        if isinstance(priority_project, list):
            self.priority_project = priority_project
        elif isinstance(priority_project, basestring):
            self.priority_project = priority_project.split(',')
        else:
            self.priority_project = None
        self.job_email = job_email
        self.job_email_options = job_email_options
        self.max_age = DAX_SETTINGS.get_max_age()
        self.launcher_type = launcher_type
        if not skip_lastupdate or not skip_lastupdate.lower().startswith('y'):
            self.skip_lastupdate = False
        else:
            self.skip_lastupdate = True

        # Creating Folders for flagfile/pbs/outlog in RESULTS_DIR
        res_dir = DAX_SETTINGS.get_results_dir()
        if launcher_type in ['diskq-xnat', 'diskq-cluster', 'diskq-combined']:
            check_dir(os.path.join(res_dir, 'DISKQ'))
            check_dir(os.path.join(os.path.join(res_dir, 'DISKQ'), 'INPUTS'))
            check_dir(os.path.join(os.path.join(res_dir, 'DISKQ'), 'OUTLOG'))
            check_dir(os.path.join(os.path.join(res_dir, 'DISKQ'), 'BATCH'))
            check_dir(os.path.join(res_dir, 'FlagFiles'))
        else:
            check_dir(res_dir)
            check_dir(os.path.join(res_dir, 'FlagFiles'))
            check_dir(os.path.join(res_dir, 'OUTLOG'))
            check_dir(os.path.join(res_dir, 'PBS'))

        self.xnat_host = xnat_host
        if not self.xnat_host:
            self.xnat_host = os.environ['XNAT_HOST']

        # CR flag: don't want something like 'cr: blah blah' in the settings file turning the cr flag on
        if str(cr).upper() == 'TRUE':
            self.cr = True
        else:
            self.cr = False

        LOGGER.info(
            'XNAT CR status: cr=%s, self.cr=%s' % (str(cr), str(self.cr)))

        # User:
        if not xnat_user:
            netrc_obj = DAX_Netrc()
            user, password = netrc_obj.get_login(self.xnat_host)
            self.xnat_user = user
            self.xnat_pass = password
        else:
            self.xnat_user = xnat_user
            if not xnat_pass:
                msg = 'Please provide password for host <%s> and user <%s>: '
                self.xnat_pass = input(msg % (self.xnat_host,
                                              self.xnat_user))
            else:
                self.xnat_pass = xnat_pass

    # LAUNCH Main Method
    def launch_jobs(self, lockfile_prefix, project_local, sessions_local,
                    writeonly=False, pbsdir=None, force_no_qsub=False):
        """
        Main Method to launch the tasks

        :param lockfile_prefix: prefix for flag file to lock the launcher
        :param project_local: project to run locally
        :param sessions_local: list of sessions to launch tasks
         associated to the project locally
        :param writeonly: write the job files without submitting them
        :param pbsdir: folder to store the pbs file
        :param force_no_qsub: run the job locally on the computer (serial mode)
        :return: None

        """
        if self.launcher_type == 'diskq-xnat':
            err = 'cannot launch jobs with this launcher type: %s'
            raise DaxLauncherError(err % self.launcher_type)

        LOGGER.info('-------------- Launch Tasks --------------\n')
        LOGGER.info('launcher_type = %s' % self.launcher_type)

        intf = None
        res_dir = DAX_SETTINGS.get_results_dir()
        flagfile = os.path.join(os.path.join(res_dir, 'FlagFiles'),
                                '%s_%s' % (lockfile_prefix, LAUNCH_SUFFIX))

        project_list = self.init_script(flagfile, project_local,
                                        type_update=3, start_end=1)

        if self.launcher_type in ['diskq-cluster', 'diskq-combined']:
            msg = 'Loading task queue from: %s'
            LOGGER.info(msg % os.path.join(res_dir, 'DISKQ'))
            task_list = load_task_queue(
                status=task.NEED_TO_RUN,
                proj_filter=list(set(
                    self.project_process_dict.keys() + self.project_modules_dict.keys())))

            msg = '%s tasks that need to be launched found'
            LOGGER.info(msg % str(len(task_list)))
            self.launch_tasks(task_list, force_no_qsub=force_no_qsub)
        else:
            LOGGER.info('Connecting to XNAT at %s' % self.xnat_host)
            with XnatUtils.get_interface(self.xnat_host, self.xnat_user,
                                         self.xnat_pass) as intf:

                if not XnatUtils.has_dax_datatypes(intf):
                    err = 'dax datatypes are not installed on xnat <%s>'
                    raise DaxXnatError(err % (self.xnat_host))

                LOGGER.info('Getting launchable tasks list...')
                task_list = self.get_tasks(intf,
                                           self.is_launchable_tasks,
                                           project_list,
                                           sessions_local)

                msg = '%s tasks that need to be launched found'
                LOGGER.info(msg % str(len(task_list)))

                # Launch the task that need to be launch
                self.launch_tasks(task_list, writeonly, pbsdir,
                                  force_no_qsub=force_no_qsub)

        self.finish_script(flagfile, project_list, 3, 2, project_local)

    @staticmethod
    def is_launchable_tasks(assr_info):
        """
        Check if a task is launchable

        :param assr_info: dictionary containing procstatus for the assessor
        :return: True if tasks need to be launch, False otherwise.
        """
        return assr_info['procstatus'] == task.NEED_TO_RUN

    def launch_tasks(self, task_list, writeonly=False, pbsdir=None,
                     force_no_qsub=False):
        """
        Launch tasks from the passed list until the queue is full or
         the list is empty

        :param task_list: list of task to launch
        :param writeonly: write the job files without submitting them
        :param pbsdir: folder to store the pbs file
        :param force_no_qsub: run the job locally on the computer (serial mode)
        :return: None
        """
        if force_no_qsub:
            LOGGER.info('No qsub - Running job locally on your computer.')
        else:
            # Check number of jobs on cluster
            cjobs = cluster.count_jobs()
            if cjobs == -1:
                LOGGER.error('cannot get count of jobs from cluster')
                return

            if cluster.command_found(cmd=DAX_SETTINGS.get_cmd_submit()):
                LOGGER.info('%s jobs currently in queue' % str(cjobs))

        # Launch until we reach cluster limit or no jobs left to launch
        while (cjobs < self.queue_limit or writeonly) and len(task_list) > 0:
            cur_task = task_list.pop()

            # Confirm task is still ready to run
            # I don't think that we need to make this get here.
            # We've already filtered the assessors as need to run.
            # if cur_task.get_status() != task.NEED_TO_RUN:
            #     continue

            if writeonly:
                msg = "  +Writing PBS file for job:%s, currently %s jobs in \
cluster queue"
                LOGGER.info(msg % (cur_task.assessor_label,
                                   str(cjobs)))
            else:
                msg = '  +Launching job:%s, currently %s jobs in cluster queue'
                LOGGER.info(msg % (cur_task.assessor_label, str(cjobs)))

            try:
                if self.launcher_type in ['diskq-cluster',
                                          'diskq-combined']:
                    success = cur_task.launch(force_no_qsub=force_no_qsub)
                else:
                    success = cur_task.launch(self.root_job_dir,
                                              self.job_email,
                                              self.job_email_options,
                                              self.xnat_host,
                                              writeonly, pbsdir,
                                              force_no_qsub=force_no_qsub)
            except Exception as E:
                LOGGER.critical('Caught exception launching job %s'
                                % cur_task.assessor_label)
                LOGGER.critical('Exception class %s caught with message %s'
                                % (E.__class__, E.message))
                LOGGER.critical(traceback.format_exc())

                success = False

            if not success:
                LOGGER.error('ERROR: failed to launch job')
                raise ClusterLaunchException

            cjobs = cluster.count_jobs()

            if cjobs == -1:
                LOGGER.error('ERROR: cannot get count of jobs from cluster')
                raise ClusterCountJobsException

    # UPDATE Main Method
    def update_tasks(self, lockfile_prefix, project_local, sessions_local):
        """
        Main method to Update the tasks

        :param lockfile_prefix: prefix for flag file to lock the launcher
        :param project_local: project to run locally
        :param sessions_local: list of sessions to update tasks associated
         to the project locally
        :return: None

        """
        if self.launcher_type == 'diskq-xnat':
            err = 'cannot update jobs with this launcher type: %s'
            raise DaxLauncherError(err % self.launcher_type)

        LOGGER.info('-------------- Update Tasks --------------\n')
        LOGGER.info('launcher_type = %s' % self.launcher_type)

        intf = None
        res_dir = DAX_SETTINGS.get_results_dir()
        flagfile = os.path.join(os.path.join(res_dir, 'FlagFiles'),
                                '%s_%s' % (lockfile_prefix, UPDATE_SUFFIX))
        project_list = self.init_script(flagfile, project_local,
                                        type_update=2, start_end=1)

        if self.launcher_type in ['diskq-cluster', 'diskq-combined']:
            msg = 'Loading task queue from: %s'
            LOGGER.info(msg % os.path.join(res_dir, 'DISKQ'))
            task_list = load_task_queue(
                proj_filter=list(self.project_process_dict.keys()))

            LOGGER.info('%s tasks found.' % str(len(task_list)))

            LOGGER.info('Updating tasks...')
            for cur_task in task_list:
                LOGGER.info('Updating task: %s' % cur_task.assessor_label)
                cur_task.update_status()
        else:
            LOGGER.info('Connecting to XNAT at %s' % self.xnat_host)
            with XnatUtils.get_interface(self.xnat_host, self.xnat_user,
                                         self.xnat_pass) as intf:

                if not XnatUtils.has_dax_datatypes(intf):
                    err = 'error: dax datatypes are not installed on xnat <%s>'
                    raise DaxXnatError(err % (self.xnat_host))

                LOGGER.info('Getting task list...')
                task_list = self.get_tasks(intf,
                                           self.is_updatable_tasks,
                                           project_list,
                                           sessions_local)

                LOGGER.info('%s open tasks found' % str(len(task_list)))
                LOGGER.info('Updating tasks...')
                for cur_task in task_list:
                    msg = '     Updating task: %s'
                    LOGGER.info(msg % cur_task.assessor_label)
                    cur_task.update_status()

        self.finish_script(flagfile, project_list, 2, 2, project_local)

    @staticmethod
    def is_updatable_tasks(assr_info):
        """
        Check if a task is updatable.

        :param assr_info: dictionary containing procstatus/qcstatus
        :return: True if tasks need to be update, False otherwise.

        """
        good_proc = assr_info['procstatus'] in task.OPEN_STATUS_LIST
        good_qc = assr_info['qcstatus'] in task.OPEN_QA_LIST
        return good_proc or good_qc

    # BUILD Main Method
    def build(self, lockfile_prefix, project_local, sessions_local,
              mod_delta=None, proj_lastrun=None):
        """
        Main method to build the tasks and the sessions

        :param lockfile_prefix: prefix for flag file to lock the launcher
        :param project_local: project to run locally
        :param sessions_local: list of sessions to launch tasks
         associated to the project locally
        :return: None

        """
        if self.launcher_type == 'diskq-cluster':
            err = 'cannot build jobs with this launcher type: %s'
            raise DaxLauncherError(err % self.launcher_type)

        LOGGER.info('-------------- Build --------------\n')
        LOGGER.info('launcher_type = %s' % self.launcher_type)
        LOGGER.info('mod delta = %s' % str(mod_delta))

        res_dir = DAX_SETTINGS.get_results_dir()
        flagfile = os.path.join(os.path.join(res_dir, 'FlagFiles'),
                                '%s_%s' % (lockfile_prefix, BUILD_SUFFIX))
        project_list = self.init_script(flagfile, project_local,
                                        type_update=1, start_end=1)

        LOGGER.info('Connecting to XNAT at %s' % self.xnat_host)
        with XnatUtils.get_interface(self.xnat_host, self.xnat_user,
                                     self.xnat_pass) as intf:

            if not XnatUtils.has_dax_datatypes(intf):
                err = 'error: dax datatypes are not installed on xnat <%s>'
                raise DaxXnatError(err % (self.xnat_host))

            # Priority if set:
            if self.priority_project and not project_local:
                unique_list = set(list(self.project_process_dict.keys()) +
                                  list(self.project_modules_dict.keys()))
                project_list = self.get_project_list(list(unique_list))

            # Build projects
            for project_id in project_list:
                LOGGER.info('===== PROJECT: %s =====' % project_id)
                try:
                    if ((proj_lastrun) and
                            (project_id in proj_lastrun) and
                            (proj_lastrun[project_id] is not None)):
                        lastrun = proj_lastrun[project_id]
                    else:
                        lastrun = None

                    self.build_project(intf, project_id, lockfile_prefix,
                                       sessions_local,
                                       mod_delta=mod_delta, lastrun=lastrun)
                except Exception as E:
                    err1 = 'Caught exception building project %s'
                    err2 = 'Exception class %s caught with message %s'
                    LOGGER.critical(err1 % project_id)
                    LOGGER.critical(err2 % (E.__class__, E.message))
                    LOGGER.critical(traceback.format_exc())

        self.finish_script(flagfile, project_list, 1, 2, project_local)

    def build_project(self, intf, project_id, lockfile_prefix, sessions_local,
                      mod_delta=None, lastrun=None):
        """
        Build the project

        :param intf: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param lockfile_prefix: prefix for flag file to lock the launcher
        :param sessions_local: list of sessions to launch tasks
        :return: None
        """
        # Modules prerun
        LOGGER.info('  * Modules Prerun')
        if sessions_local:
            self.module_prerun(project_id, 'manual_update')
        else:
            self.module_prerun(project_id, lockfile_prefix)

        # TODO: make a project settings to store skip_lastupdate, processors,
        #       modules, etc

        # Get lists of modules/processors per scan/exp for this project
        proj_mods = self.project_modules_dict.get(project_id, None)
        proj_procs = self.project_process_dict.get(project_id, None)
        exp_mods, scan_mods = modules.modules_by_type(proj_mods)
        # TODO: BenM/assessor_of_assessor/get old scan/session processors and
        # a separate list of autoprocessors. Autoprocessors get their own code
        # path and parameter for the call to build_session. Probably need to
        # move order processors call into processors_by_type
        # exp_procs, scan_procs = processors.processors_by_type(proj_procs)
        # exp_procs = ProcessorGraph.order_processors(proj_procs, LOGGER)
        # scan_procs = []
        # TODO: BenM/assessor_of_assessor/uncomment this when ready and remove
        # above calls
        session_procs, scan_procs, auto_procs =\
            processors.processors_by_type(proj_procs)
        auto_procs = ProcessorGraph.order_processors(auto_procs, LOGGER)


        if mod_delta:
            lastmod_delta = str_to_timedelta(mod_delta)
        else:
            lastmod_delta = None

        # Check for new processors
        has_new = self.has_new_processors(intf, project_id, session_procs,
                                          scan_procs)

        # Get the list of sessions:
        sessions = self.get_sessions_list(intf, project_id, sessions_local)

        # Update each session from the list:
        for sess_info in sessions:
            if not self.skip_lastupdate and not has_new and not sessions_local:
                last_mod = datetime.strptime(sess_info['last_modified'][0:19],
                                             UPDATE_FORMAT)
                now_date = datetime.today()
                last_up = self.get_lastupdated(sess_info)
                if last_up is not None and \
                        last_mod < last_up and \
                        now_date < last_mod + timedelta(days=int(self.max_age)):
                    mess = "  + Session %s: skipping, last_mod=%s,last_up=%s"
                    mess_str = mess % (sess_info['label'], str(last_mod),
                                       str(last_up))
                    LOGGER.info(mess_str)
                    continue

            elif lastrun:
                last_mod = datetime.strptime(sess_info['last_modified'][0:19],
                                             UPDATE_FORMAT)
                if last_mod < lastrun:
                    mess = "  + Session %s:skipping not modified since last run,\
 last_mod=%s, last_run=%s"
                    LOGGER.info(mess % (sess_info['label'], str(last_mod),
                                        str(lastrun)))
                    continue

            elif lastmod_delta:
                last_mod = datetime.strptime(sess_info['last_modified'][0:19],
                                             UPDATE_FORMAT)
                now_date = datetime.today()
                if now_date > last_mod + lastmod_delta:
                    mess = "  + Session %s:skipping not modified within delta,\
 last_mod=%s"
                    LOGGER.info(mess % (sess_info['label'], str(last_mod)))
                    continue
                else:
                    LOGGER.info('lastmod = %s' % str(last_mod))

            mess = "  + Session %s: building..."
            LOGGER.info(mess % sess_info['label'])

            if not self.skip_lastupdate:
                update_start_time = datetime.now()

            try:
                self.build_session(intf, sess_info,
                                   session_procs, scan_procs, auto_procs,
                                   exp_mods, scan_mods)
            except Exception as E:
                err1 = 'Caught exception building sessions %s'
                err2 = 'Exception class %s caught with message %s'
                LOGGER.critical(err1 % sess_info['session_label'])
                LOGGER.critical(err2 % (E.__class__, E.message))
                LOGGER.critical(traceback.format_exc())

            try:
                if not self.skip_lastupdate:
                    self.set_session_lastupdated(intf, self.cr, sess_info,
                                                 update_start_time)
            except Exception as E:
                err1 = 'Caught exception setting session timestamp %s'
                err2 = 'Exception class %s caught with message %s'
                LOGGER.critical(err1 % sess_info['session_label'])
                LOGGER.critical(err2 % (E.__class__, E.message))
                LOGGER.critical(traceback.format_exc())

        if not sessions_local or sessions_local.lower() == 'all':
            # Modules after run
            LOGGER.debug('* Modules Afterrun')
            try:
                self.module_afterrun(intf, project_id)
            except Exception as E:
                err2 = 'Exception class %s caught with message %s'
                LOGGER.critical('Caught exception after running modules')
                LOGGER.critical(err2 % (E.__class__, E.message))
                LOGGER.critical(traceback.format_exc())


    # TODO:BenM/assessor_of_assessor/modify from here for one to many
    # processor to assessor mapping
    def build_session(self, intf, sess_info,
                      sess_proc_list, scan_proc_list, auto_proc_list,
                      sess_mod_list, scan_mod_list):
        """
        Build a session


        :param intf: pyxnat.Interface object
        :param sess_info: python ditionary from XnatUtils.list_sessions method
        :param sess_proc_list: list of processors running on a session
        :param scan_proc_list: list of processors running on a scan
        :param sess_mod_list: list of modules running on a session
        :param scan_mod_list: list of modules running on a scan
        :return: None
        """
        csess = XnatUtils.CachedImageSession(intf,
                                             sess_info['project_label'],
                                             sess_info['subject_label'],
                                             sess_info['session_label'])

        # Modules
        mod_count = 0
        while mod_count < 3:
            mess = """== Build modules (count:{count}) =="""
            LOGGER.debug(mess.format(count=mod_count))
            # NOTE: we keep starting time to check if something changes below
            start_time = datetime.now()
            if sess_mod_list:
                self.build_session_modules(intf, csess, sess_mod_list)
            if scan_mod_list:
                for cscan in csess.scans():
                    LOGGER.debug('+SCAN: ' + cscan.info()['scan_id'])
                    self.build_scan_modules(intf, cscan, scan_mod_list)

            # TODO: BenM/xnat refactor/this test should be encapsulated into a
            # session object
            if not sess_was_modified(intf, sess_info, start_time):
                break

            csess.reload()
            mod_count += 1

        # Scan Processors
        LOGGER.debug('== Build scan processors ==')
        if scan_proc_list:
            for cscan in csess.scans():
                LOGGER.debug('+SCAN: ' + cscan.info()['scan_id'])
                self.build_scan_processors(intf, cscan, scan_proc_list)

        # Session Processors
        LOGGER.debug('== Build session processors ==')
        if sess_proc_list:
            self.build_session_processors(intf, csess, sess_proc_list)

        # Auto Processors
        LOGGER.debug('== Build auto processors ==')
        if auto_proc_list:
            self.build_auto_processors(intf, csess, auto_proc_list)


    def build_session_processors(self, xnat, csess, sess_proc_list):
        """ Build Session processors.

        :param xnat: pyxnat.Interface object
        :param csess: CachedObject for Session (XnatUtils)
        :param sess_proc_list: list of processors running on a session
        :return: None
        """
        sess_info = csess.info()
        res_dir = DAX_SETTINGS.get_results_dir()

        for sess_proc in sess_proc_list:
            if not sess_proc.should_run(sess_info):
                continue

            p_assr, assr_name = sess_proc.get_assessor(csess)

            if self.launcher_type in ['diskq-xnat', 'diskq-combined']:
                if p_assr is None or \
                   p_assr.info()['procstatus'] == task.NEED_INPUTS or \
                   p_assr.info()['qcstatus'] in [task.RERUN, task.REPROC]:
                    assessor = csess.full_object().assessor(assr_name)
                    xtask = XnatTask(sess_proc, assessor, res_dir,
                                     os.path.join(res_dir, 'DISKQ'))

                    if p_assr is not None and \
                       p_assr.info()['qcstatus'] in [task.RERUN, task.REPROC]:
                        xtask.update_status()

                    LOGGER.debug('building task:' + assr_name)
                    (proc_status, qc_status) = xtask.build_task(
                        csess,
                        self.root_job_dir,
                        self.job_email,
                        self.job_email_options)
                    deg = 'proc_status=%s, qc_status=%s'
                    LOGGER.debug(deg % (proc_status, qc_status))
                else:
                    # TODO: check that it actually exists in QUEUE
                    LOGGER.debug('skipping, already built: %s' % assr_name)
            else:
                if p_assr is None or \
                   p_assr.info()['procstatus'] == task.NEED_INPUTS:
                    sess_task = sess_proc.get_task(xnat, csess, res_dir)
                    log_updating_status(sess_proc.name,
                                        sess_task.assessor_label)
                    has_inputs, qcstatus = sess_proc.has_inputs(csess)
                    try:
                        if has_inputs == 1:
                            sess_task.set_status(task.NEED_TO_RUN)
                            sess_task.set_qcstatus(task.JOB_PENDING)
                        elif has_inputs == -1:
                            sess_task.set_status(task.NO_DATA)
                            sess_task.set_qcstatus(qcstatus)
                        else:
                            sess_task.set_qcstatus(qcstatus)
                    except Exception as E:
                        err1 = 'Caught exception building session %s while \
setting assessor status'
                        err2 = 'Exception class %s caught with message %s'
                        LOGGER.critical(err1 % sess_info['session_label'])
                        LOGGER.critical(err2 % (E.__class__, E.message))
                        LOGGER.critical(traceback.format_exc())
                else:
                    # Other statuses handled by dax_update_tasks
                    pass


    def build_session_modules(self, xnat, csess, sess_mod_list):
        """
        Build a session

        :param xnat: pyxnat.Interface object
        :param sess_info: python ditionary from XnatUtils.list_sessions method
        :param sess_mod_list: list of modules running on a session
        :return: None
        """
        sess_obj = None
        sess_info = csess.info()
        for sess_mod in sess_mod_list:
            LOGGER.debug('* Module: ' + sess_mod.getname())
            if sess_mod.needs_run(csess, xnat):
                if sess_obj is None:
                    sess_obj = csess.full_object()

                try:
                    sess_mod.run(sess_info, sess_obj)
                except Exception as E:
                    err1 = 'Caught exception building session module %s'
                    err2 = 'Exception class %s caught with message %s'
                    LOGGER.critical(err1 % sess_info['session_label'])
                    LOGGER.critical(err2 % (E.__class__, E.message))
                    LOGGER.critical(traceback.format_exc())

    # TODO: BenM/assessor_of_assessors/the list of candidate assessors is
    # generated by the available artefacts in the session. We should only
    # need to create the assessor if it doesn't exist, so Task/XnatTask can
    # lose the rechecking
    def build_scan_processors(self, xnat, cscan, scan_proc_list):
        """
        Build the scan

        :param xnat: pyxnat.Interface object
        :param cscan: CachedImageScan from XnatUtils
        :param scan_proc_list: list of processors running on a scan
        :param scan_mod_list: list of modules running on a scan
        :return: None
        """
        scan_info = cscan.info()
        res_dir = DAX_SETTINGS.get_results_dir()

        # Processors
        for scan_proc in scan_proc_list:
            if not scan_proc.should_run(scan_info):
                continue

            p_assr, assr_name = scan_proc.get_assessor(cscan)

            if self.launcher_type in ['diskq-xnat', 'diskq-combined']:
                if p_assr is None or \
                   p_assr.info()['procstatus'] in [task.NEED_INPUTS,
                                                   task.NEED_TO_RUN] or \
                   p_assr.info()['qcstatus'] in [task.RERUN, task.REPROC]:
                    # TODO: get session object directly
                    scan = XnatUtils.get_full_object(xnat, scan_info)
                    assessor = scan.parent().assessor(assr_name)
                    xtask = XnatTask(scan_proc, assessor, res_dir,
                                     os.path.join(res_dir, 'DISKQ'))

                    if p_assr is not None and \
                       p_assr.info()['qcstatus'] in [task.RERUN, task.REPROC]:
                        xtask.update_status()

                    LOGGER.debug('building task:' + assr_name)
                    (proc_status, qc_status) = xtask.build_task(
                        cscan,
                        self.root_job_dir,
                        self.job_email,
                        self.job_email_options)
                    deg = 'proc_status=%s, qc_status=%s'
                    LOGGER.debug(deg % (proc_status, qc_status))
                else:
                    # TODO: check that it actually exists in QUEUE
                    LOGGER.debug('skipping, already built:' + assr_name)
            else:
                if p_assr is None or \
                   p_assr.info()['procstatus'] == task.NEED_INPUTS:
                    scan_task = scan_proc.get_task(xnat, cscan, res_dir)
                    log_updating_status(scan_proc.name,
                                        scan_task.assessor_label)
                    has_inputs, qcstatus = scan_proc.has_inputs(cscan)
                    try:
                        if has_inputs == 1:
                            scan_task.set_status(task.NEED_TO_RUN)
                            scan_task.set_qcstatus(task.JOB_PENDING)
                        elif has_inputs == -1:
                            scan_task.set_status(task.NO_DATA)
                            scan_task.set_qcstatus(qcstatus)
                        else:
                            scan_task.set_qcstatus(qcstatus)
                    except Exception as E:
                        err1 = 'Caught exception building sessions %s'
                        err2 = 'Exception class %s caught with message %s'
                        LOGGER.critical(err1 % scan_info['session_label'])
                        LOGGER.critical(err2 % (E.__class__, E.message))
                        LOGGER.critical(traceback.format_exc())
                else:
                    # Other statuses handled by dax_update_open_tasks
                    pass

    def build_scan_modules(self, xnat, cscan, scan_mod_list):
        """ Build Scan modules.

        :param xnat: pyxnat.Interface object
        :param csan: CachedObject for scan (XnatUtils)
        :param scan_mod_list: list of modules running on a scan
        :return: None
        """
        scan_info = cscan.info()
        scan_obj = None

        # Modules
        for scan_mod in scan_mod_list:
            LOGGER.debug('* Module: ' + scan_mod.getname())
            if scan_mod.needs_run(cscan, xnat):
                if scan_obj is None:
                    scan_obj = cscan.full_object()

                try:
                    scan_mod.run(scan_info, scan_obj)
                except Exception as E:
                    err1 = 'Caught exception building session scan module \
in session %s'
                    err2 = 'Exception class %s caught with message %s'
                    LOGGER.critical(err1 % scan_info['session_label'])
                    LOGGER.critical(err2 % (E.__class__, E.message))
                    LOGGER.critical(traceback.format_exc())


    def build_auto_processors(self, xnat, csess, sess_proc_list):
        """ Build yaml-based processors.

        :param xnat: pyxnat.Interface object
        :param csess: CachedObject for Session (XnatUtils)
        :param sess_proc_list: list of yaml processors
        :return: None
        """
        sess_info = csess.info()
        res_dir = DAX_SETTINGS.get_results_dir()
        xnat_session = csess.full_object()

        for sess_proc in sess_proc_list:
            if not sess_proc.should_run(sess_info):
                continue

            # TODO: use mod time to decide if we need to reload
            csess.reload()

            # return a mapping between the assessor input sets and existing
            # assessors that map to those input sets
            sess_proc.parse_session(csess)
            mapping = sess_proc.get_assessor_mapping()

            if mapping is None:
                continue
                
            if self.launcher_type in ['diskq-xnat', 'diskq-combined']:
                for inputs, p_assrs in mapping:
                    if len(p_assrs) == 0:
                        assessor = sess_proc.create_assessor(xnat_session,
                                                             inputs, relabel=True)
                        assessors =\
                            [(assessor, task.NEED_TO_RUN, task.DOES_NOT_EXIST)]
                    else:
                        assessors = []
                        for p in p_assrs:
                            info = p.info()
                            procstatus = info['procstatus']
                            qcstatus = info['qcstatus']
                            assessors.append(
                                (p.full_object(), procstatus, qcstatus))

                    for assessor in assessors:
                        procstatus = assessor[1]
                        qcstatus = assessor[2]
                        if task_needs_to_run(procstatus, qcstatus):
                            xtask = XnatTask(sess_proc, assessor[0], res_dir,
                                             os.path.join(res_dir, 'DISKQ'))

                            if task_needs_status_update(qcstatus):
                                xtask.update_status()

                            LOGGER.debug(
                                'building task: ' + assessor[0].label())
                            (proc_status, qc_status) = xtask.build_task(
                                assessor[0],
                                self.root_job_dir,
                                self.job_email,
                                self.job_email_options)
                            deg = 'proc_status=%s, qc_status=%s'
                            LOGGER.debug(deg % (proc_status, qc_status))
                        else:
                            # TODO: check that it actually exists in QUEUE
                            LOGGER.debug(
                                'skipping, already built: ' +
                                assessor[0].label())
            else:
                for inputs, p_assrs in mapping:
                    if len(p_assrs) == 0:
                        assessor = sess_proc.create_assessor(xnat_session,
                                                             inputs)
                        assessors =\
                            [(assessor, task.NEED_TO_RUN, task.DOES_NOT_EXIST)]
                    else:
                        assessors = []
                        for p in p_assrs:
                            info = p.info()
                            procstatus = info['procstatus']
                            qcstatus = info['qcstatus']
                            assessors.append(
                                (p.full_object(), procstatus, qcstatus))

                    for assessor in assessors:
                        procstatus = assessor[1]
                        qcstatus = assessor[2]
                        if task_needs_to_run(procstatus, qcstatus):
                            sess_task =\
                                task.Task(sess_proc, assessor[0], res_dir)

                            log_updating_status(sess_proc.name,
                                                sess_task.assessor_label)
                            has_inputs, qcerrors =\
                                sess_proc.has_inputs(assessor[0])
                            try:
                                if has_inputs == 1:
                                    sess_task.set_status(task.NEED_TO_RUN)
                                    sess_task.set_qcstatus(task.JOB_PENDING)
                                else:
                                    errorstr =\
                                        '\n'.join((q[1] for q in qcerrors))
                                    sess_task.set_qcstatus(errorstr)
                                    if has_inputs == -1:
                                        sess_task.set_status(task.NO_DATA)
                            except Exception as E:
                                err1 = 'Caught exception building session %s while \
        setting assessor status'
                                err2 = 'Exception class %s caught with message %s'
                                LOGGER.critical(err1 % sess_info['session_label'])
                                LOGGER.critical(err2 % (E.__class__, E.message))
                                LOGGER.critical(traceback.format_exc())
                        else:
                            # Other statuses handled by dax_update_tasks
                            pass


    def module_prerun(self, project_id, settings_filename=''):
        """
        Run the module prerun method

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param settings_filename: Settings file name for temp dir
        :return: None
        """
        for mod in self.project_modules_dict.get(project_id, list()):
            try:
                mod.prerun(settings_filename)
            except Exception as E:
                err1 = 'Caught exception in module prerun for project %s'
                err2 = 'Exception class %s caught with message %s'
                LOGGER.critical(err1 % project_id)
                LOGGER.critical(err2 % (E.__class__, E.message))
                LOGGER.critical(traceback.format_exc())

        #LOGGER.debug('\n')

    def module_afterrun(self, xnat, project_id):
        """
        Run the module afterrun method

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :return: None
        """
        for mod in self.project_modules_dict.get(project_id, list()):
            try:
                mod.afterrun(xnat, project_id)
            except Exception as E:
                err1 = 'Caught exception in module prerun for project %s'
                err2 = 'Exception class %s caught with message %s'
                LOGGER.critical(err1 % project_id)
                LOGGER.critical(err2 % (E.__class__, E.message))
                LOGGER.critical(traceback.format_exc())

        LOGGER.debug('\n')

    # Generic Methods
    def init_script(self, flagfile, project_local, type_update, start_end):
        """
        Init script for any of the main methods: build/update/launch

        :param flagfile: flag file for the method to run
        :param project_local: project to run locally
        :param type_update: What type of process ran: dax_build (1),
         dax_update_tasks (2), dax_launch (3)
        :param start_end: starting timestamp (1) and ending timestamp (2)
        :return: None
        """
        # Get default project list for XNAT out of the module/process dict
        ulist = set(list(self.project_process_dict.keys()) +
                    list(self.project_modules_dict.keys()))
        project_list = sorted(ulist)
        if project_local:
            if ',' in project_local:
                mess = """too much projects ID given to the option\
--project : {proj}. Only for one project."""
                mess_str = mess.format(proj=project_local)
                LOGGER.error(mess_str)
                exit(1)
            elif project_local in project_list:
                # Updating session for a specific project
                project_list = [project_local]
            else:
                mess = """failed to run locally on project {proj}.\
The project is not part of the settings."""
                mess_str = mess.format(proj=project_local)
                LOGGER.error(mess_str)
                exit(1)
        else:
            success = self.lock_flagfile(flagfile)
            if not success:
                LOGGER.warn('failed to get lock. Already running.')
                exit(1)
            # Set the date on REDCAP for update starting
            upload_update_date_redcap(project_list, type_update, start_end)
        return project_list

    def finish_script(self, flagfile, project_list, type_update,
                      start_end, project_local):
        """
        Finish script for any of the main methods: build/update/launch

        :param flagfile: flag file for the method to run
        :param project_list: List of projects that were updated by the method
        :param type_update: What type of process ran: dax_build (1),
         dax_update_tasks (2), dax_launch (3)
        :param start_end: starting timestamp (1) and ending timestamp (2)
        :param project_local: project to run locally
        :return: None
        """
        if not project_local:
            self.unlock_flagfile(flagfile)
            # Set the date on REDCAP for update ending
            upload_update_date_redcap(project_list, type_update, start_end)

    @staticmethod
    def lock_flagfile(lock_file):
        """
        Create the flagfile to lock the process

        :param lock_file: flag file use to lock the process
        :return: True if the file didn't exist, False otherwise
        """
        if os.path.exists(lock_file):
            return False
        else:
            open(lock_file, 'w').close()
            return True

    @staticmethod
    def unlock_flagfile(lock_file):
        """
        Remove the flagfile to unlock the process

        :param lock_file: flag file use to lock the process
        :return: None
        """
        if os.path.exists(lock_file):
            os.remove(lock_file)

    def get_tasks(self, xnat, is_valid_assessor, project_list=None,
                  sessions_local=None):
        """
        Get list of tasks for a projects list

        :param xnat: pyxnat.Interface object
        :param is_valid_assessor: method to validate the assessor
        :param project_list: List of projects to search tasks from
        :param sessions_local: list of sessions to update tasks associated
         to the project locally
        :return: list of tasks
        """
        task_list = list()

        if not project_list:
            projects = list(self.project_process_dict.keys())
            # Priority:
            if self.priority_project:
                project_list = self.get_project_list(projects)
            else:
                project_list = list(projects)

        # iterate projects
        for project_id in project_list:
            LOGGER.info('===== PROJECT:%s =====' % project_id)
            task_list.extend(self.get_project_tasks(xnat,
                                                    project_id,
                                                    sessions_local,
                                                    is_valid_assessor))

        return task_list

    def get_project_tasks(self, xnat, project_id, sessions_local,
                          is_valid_assessor):
        """
        Get list of tasks for a specific project where each task agrees
         the is_valid_assessor conditions

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param sessions_local: list of sessions to update tasks associated
         to the project locally
        :param is_valid_assessor: method to validate the assessor
        :return: list of tasks
        """
        task_list = list()

        # Get lists of processors for this project
        pp_dict = self.project_process_dict.get(project_id, None)
        sess_procs, scan_procs, auto_procs =\
            processors.processors_by_type(pp_dict)

        # Get lists of assessors for this project
        assr_list = self.get_assessors_list(xnat, project_id, sessions_local)

        # Match each assessor to a processor, get a task, and add to list
        for assr_info in assr_list:
            if is_valid_assessor(assr_info):
                cur_task = self.generate_task(xnat, assr_info, sess_procs,
                                              scan_procs, auto_procs)
                if cur_task:
                    task_list.append(cur_task)

        return task_list

    @staticmethod
    def match_proc(assr_info, sess_proc_list, scan_proc_list, auto_proc_list):
        """
        Check if an assessor is a match with the processors

        :param assr_info: dictionary containing the assessor info
                          (See XnatUtils.list_assessors)
        :param sess_proc_list: list of processors running on a session
        :param scan_proc_list: list of processors running on a scan
        :return: processor if found, None otherwise
        """
        # Look for a match in sess processors
        for sess_proc in sess_proc_list:
            if sess_proc.xsitype == assr_info['xsiType'] and \
                    sess_proc.name == assr_info['proctype']:
                return sess_proc

        # Look for a match in scan processors
        for scan_proc in scan_proc_list:
            if scan_proc.xsitype == assr_info['xsiType'] and \
                    scan_proc.name == assr_info['proctype']:
                return scan_proc

        # Look for a match in yaml processors
        for auto_proc in auto_proc_list:
            if auto_proc.xsitype == assr_info['xsiType'] and \
                    auto_proc.name == assr_info['proctype']:
                return auto_proc

        return None

    def generate_task(self, xnat, assr_info,
                      sess_proc_list, scan_proc_list, auto_proc_list):
        """
        Generate a task for the assessor in the info

        :param xnat: pyxnat.Interface object
        :param assr_info: dictionary containing the assessor info
                          (See XnatUtils.list_assessors)
        :param sess_proc_list: list of processors running on a session
        :param scan_proc_list: list of processors running on a scan
        :param auto_proc_list: list of yaml processors
        :return: task if processor and assessor match, None otherwise
        """
        task_proc = self.match_proc(assr_info,
                                    sess_proc_list,
                                    scan_proc_list,
                                    auto_proc_list)

        if task_proc is None:
            warn = 'no matching processor found: %s'
            LOGGER.warn(warn % assr_info['assessor_label'])
            return None
        else:
            # Get a new task with the matched processor
            assr = xnat.select_assessor(assr_info['project_id'],
                                        assr_info['subject_id'],
                                        assr_info['session_id'],
                                        assr_info['ID'])
            cur_task = Task(task_proc, assr, DAX_SETTINGS.get_results_dir())
            return cur_task

    @staticmethod
    def get_assessors_list(xnat, project_id, slocal):
        """
        Get the assessor list from XNAT and filter it if necessary

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param slocal: session selected by user
        :return: list of assessors for a project
        """
        # Get lists of assessors for this project
        assr_list = XnatUtils.list_project_assessors(xnat, project_id)

        # filter the assessors to the sessions given as parameters if given
        if slocal and slocal.lower() != 'all':
            # filter the list and keep the match between both list:
            val = slocal.split(',')
            assr_list = [x for x in assr_list if x['session_label'] in val]
            if not assr_list:
                warn = 'No processes on XNAT matched the sessions given: %s .'
                LOGGER.warn(warn % slocal)
                sys.exit(1)

        return assr_list

    @staticmethod
    def get_sessions_list(xnat, project_id, slocal):
        """
        Get the sessions list from XNAT and sort it.
         Move the new sessions to the front.

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param slocal: session selected by user
        :return: list of sessions sorted for a project
        """
        list_sessions = xnat.get_sessions(project_id)
        if slocal and slocal.lower() != 'all':
            # filter the list and keep the match between both list:
            val = slocal.split(',')
            list_sessions = [x for x in list_sessions if x['label'] in val]
            if not list_sessions:
                warn = 'No session from XNAT matched the sessions given: %s .'
                LOGGER.warn(warn % slocal)

        # Sort sessions: first the new sessions that have never been updated
        sorted_list = [s for s in list_sessions if not s['last_updated']]
        new_sessions_label = [sess['label'] for sess in sorted_list]
        for session in list_sessions:
            if not session['label'] in new_sessions_label:
                sorted_list.append(session)

        return sorted_list

    def get_project_list(self, all_projects):
        """
        Get project list from the file priority + the other ones

        :param all_projects: list of all the projects in the settings file
        :return: list of project sorted to update
        """
        random_project = [x for x in all_projects
                          if x not in self.priority_project]
        return self.priority_project + random_project

    @staticmethod
    def get_lastupdated(info):
        """
        Get the last updated date from XNAT

        :param info: dictionary of an assessor
        :return: date in UPDATE_PREFIX if last updated date found
         None otherwise
        """
        update_time = info['last_updated'][len(UPDATE_PREFIX):]
        if update_time == '':
            return None
        else:
            return datetime.strptime(update_time, UPDATE_FORMAT)

    @staticmethod
    def set_session_lastupdated(xnat, cr, sess_info, update_start_time):
        """
        Set the last session update on XNAT

        :param xnat: pyxnat.Interface object
        :param cr: True if the host is an XNAT CR instance
        :param sess_info: dictionary of session information
        :param update_start_time: date when the update started
        :return: False if the session change(don't set the last update date),
                 True otherwise
        """
        xsi_type = sess_info['xsiType']
        sess_obj = xnat.select_experiment(sess_info['project_id'],
                                          sess_info['subject_id'],
                                          sess_info['session_id'])
        xsi_uri = '%s/meta/last_modified' % xsi_type
        last_modified_xnat = sess_obj.attrs.get(xsi_uri)
        d_format = '%Y-%m-%d %H:%M:%S'
        last_mod = datetime.strptime(last_modified_xnat[0:19], d_format)
        if last_mod > update_start_time:
            return False

        # format:
        update_str = (datetime.now() +
                      timedelta(minutes=1)).strftime(UPDATE_FORMAT)
        # We set update to one minute into the future
        # since setting update field will change last modified time
        deg = 'setting last_updated for: %s to %s'
        LOGGER.debug(deg % (sess_info['label'], update_str))
        try:
            if cr:
                LOGGER.critical(
                    'CR does not seem to allow changing of session timestamp, what do we do?')
            else:
                sess_obj.attrs.set('%s/original' % xsi_type,
                                   UPDATE_PREFIX + update_str, params={
                        "event_reason": "DAX setting session_lastupdated"})
        except Exception as E:
            err1 = 'Caught exception setting update timestamp for session %s'
            err2 = 'Exception class %s caught with message %s'
            LOGGER.critical(err1 % sess_info['session_label'])
            LOGGER.critical(err2 % (E.__class__, E.message))
            LOGGER.critical(traceback.format_exc())

        return True

    @staticmethod
    def has_new_processors(xnat, project_id, sess_proc_list, scan_proc_list):
        """
        Check if has new processors

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param sess_proc_list: list of processors running on a session
        :param scan_proc_list: list of processors running on a scan
        :return: True if has new processors, False otherwise
        """
        # Get unique list of assessors already in XNAT
        assr_list = XnatUtils.list_project_assessors(xnat, project_id)
        assr_type_set = set([x['proctype'] for x in assr_list])

        # Get unique list of processors prescribed for project
        proc_name_set = set([x.name for x in sess_proc_list + scan_proc_list])

        # Get list of processors that don't have assessors in XNAT yet
        diff_list = list(proc_name_set.difference(assr_type_set))

        # Are there any?
        return len(diff_list) > 0


# TODO: BenM/assessor_of_assessor/check path.txt to get the project_id
def load_task_queue(status=None, proj_filter=None):
    """ Load the task queue for DiskQ"""
    task_list = list()
    diskq_dir = os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ')
    results_dir = DAX_SETTINGS.get_results_dir()

    for t in os.listdir(os.path.join(diskq_dir, 'BATCH')):
        # TODO:complete filtering by project/subject/session/type
        if proj_filter:
            assr = XnatUtils.AssessorHandler(t)
            if assr.get_project_id() not in proj_filter:
                LOGGER.debug('ignoring:' + t)
                continue

        LOGGER.debug('loading:' + t)
        task = ClusterTask(os.path.splitext(t)[0], results_dir, diskq_dir)
        LOGGER.debug('status = ' + task.get_status())

        if not status or task.get_status() == status:
            LOGGER.debug('adding task to list:' + t)
            task_list.append(task)

    return task_list


def get_sess_lastmod(xnat, sess_info):
    """ Get the session last modified date."""
    xsi_type = sess_info['xsiType']
    sess_obj = xnat.select_experiment(sess_info['project_label'],
                                      sess_info['subject_label'],
                                      sess_info['session_label'])
    last_modified_xnat = sess_obj.attrs.get('%s/meta/last_modified' % xsi_type)
    last_mod = datetime.strptime(last_modified_xnat[0:19], '%Y-%m-%d %H:%M:%S')
    return last_mod


def sess_was_modified(xnat, sess_info, build_start_time):
    """
    Compare modified time with start time
    :param xnat: pyxnat.Interface object
    :param sess_info: dictionary of session information
    :param update_start_time: date when the update started
    :return: False if the session change and don't set the last update date,
             True otherwise
    """
    last_mod = get_sess_lastmod(xnat, sess_info)
    return (last_mod > build_start_time)


def log_updating_status(procname, assessor_label):
    """
    Print as debug the status updating string
    :param procname: process name
    :param assessors_label: assessor label
    :return: None
    """
    mess = """* Processor:{proc}: updating status: {label}"""
    mess_str = mess.format(proc=procname, label=assessor_label)
    LOGGER.debug(mess_str)


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
        except Exception:
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
