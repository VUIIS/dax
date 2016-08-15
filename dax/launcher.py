""" launcher.py that represents the main object called by the executables """
#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

import os
import sys
import logging
from datetime import datetime, timedelta

import processors
import modules
import XnatUtils
import task
import cluster
import bin
from task import Task, ClusterTask, XnatTask
from dax_settings import DAX_Settings
DAX_SETTINGS = DAX_Settings()

UPDATE_PREFIX = 'updated--'
UPDATE_FORMAT = "%Y-%m-%d %H:%M:%S"
BUILD_SUFFIX = 'BUILD_RUNNING.txt'
UPDATE_SUFFIX = 'UPDATE_RUNNING.txt'
LAUNCH_SUFFIX = 'LAUNCHER_RUNNING.txt'

#Logger to print logs
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

class Launcher(object):
    """ Launcher object to manage a list of projects from a settings file """
    def __init__(self, project_process_dict, project_modules_dict, priority_project=None,
                 queue_limit=DAX_SETTINGS.get_queue_limit(), root_job_dir=DAX_SETTINGS.get_root_job_dir(),
                 xnat_user=None, xnat_pass=None, xnat_host=None,
                 job_email=None, job_email_options='bae', max_age=7,
                 launcher_type=DAX_SETTINGS.get_launcher_type(),
                 skip_lastupdate=None):

        """
        Entry point for the Launcher class

        :param project_process_dict: dictionary associating XNAT project with processes
        :param project_modules_dict: dictionary associating XNAT project with modules
        :param priority_project: list of project to describe the priority
        :param queue_limit: maximum number of jobs in the queue
        :param root_job_dir: root directory for jobs
        :param xnat_host: XNAT Host url. By default, use env variable.
        :param xnat_user: XNAT User ID. By default, use env variable.
        :param xnat_pass: XNAT Password. By default, use env variable.
        :param job_email: job email address for report
        :param job_email_options: email options for the jobs
        :param max_age: maximum time before updating again a session
        :return: None
        """
        self.queue_limit = queue_limit
        self.root_job_dir = root_job_dir
        self.project_process_dict = project_process_dict
        self.project_modules_dict = project_modules_dict
        self.priority_project = priority_project
        self.job_email = job_email
        self.job_email_options = job_email_options
        self.max_age = DAX_SETTINGS.get_max_age()
        self.launcher_type = launcher_type
        if not skip_lastupdate or not skip_lastupdate.lower().startswith('y'):
            self.skip_lastupdate = False
        else:
            self.skip_lastupdate =True

        # Creating Folders for flagfile/pbs/outlog in RESULTS_DIR
        if launcher_type in ['diskq-xnat', 'diskq-cluster', 'diskq-combined']:
            check_dir(os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ'))
            check_dir(os.path.join(os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ'), 'INPUTS'))
            check_dir(os.path.join(os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ'), 'OUTLOG'))
            check_dir(os.path.join(os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ'), 'BATCH'))
            check_dir(os.path.join(DAX_SETTINGS.get_results_dir(), 'FlagFiles'))
        else:
            check_dir(DAX_SETTINGS.get_results_dir())
            check_dir(os.path.join(DAX_SETTINGS.get_results_dir(), 'FlagFiles'))
            check_dir(os.path.join(DAX_SETTINGS.get_results_dir(), 'OUTLOG'))
            check_dir(os.path.join(DAX_SETTINGS.get_results_dir(), 'PBS'))

        # Add empty lists for projects in one list but not the other
        for proj in self.project_process_dict.keys():
            if proj not in self.project_modules_dict:
                self.project_modules_dict[proj] = list()

        for proj in self.project_modules_dict.keys():
            if proj not in self.project_process_dict:
                self.project_process_dict[proj] = list()

        try:
            if xnat_user == None:
                self.xnat_user = os.environ['XNAT_USER']
            else:
                self.xnat_user = xnat_user

            if xnat_pass == None:
                self.xnat_pass = os.environ['XNAT_PASS']
            else:
                self.xnat_pass = xnat_pass

            if xnat_host == None:
                self.xnat_host = os.environ['XNAT_HOST']
            else:
                self.xnat_host = xnat_host

        except KeyError as err:
            LOGGER.error("You must set the environment variable %s" % str(err))
            sys.exit(1)

    ################## LAUNCH Main Method ##################
    def launch_jobs(self, lockfile_prefix, project_local, sessions_local, writeonly=False, pbsdir=None):
        """
        Main Method to launch the tasks

        :param lockfile_prefix: prefix for flag file to lock the launcher
        :param project_local: project to run locally
        :param sessions_local: list of sessions to launch tasks
         associated to the project locally
        :param writeonly: write the job files without submitting them
        :param pbsdir: folder to store the pbs file
        :return: None

        """
        if self.launcher_type == 'diskq-xnat':
            LOGGER.error('cannot launch jobs with this launcher type:' + self.launcher_type)
            return

        LOGGER.info('-------------- Launch Tasks --------------\n')
        LOGGER.info('launcher_type = '+self.launcher_type)

        xnat = None
        flagfile = os.path.join(os.path.join(DAX_SETTINGS.get_results_dir(), 'FlagFiles'), lockfile_prefix + '_' + LAUNCH_SUFFIX)

        project_list = self.init_script(flagfile, project_local, type_update=3, start_end=1)

        try:
            if self.launcher_type in ['diskq-cluster', 'diskq-combined']:
                LOGGER.info('Loading task queue from:' + os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ'))
                task_list = load_task_queue(status=task.NEED_TO_RUN)

                LOGGER.info(str(len(task_list)) + ' tasks that need to be launched found')
                self.launch_tasks(task_list)
            else:
                LOGGER.info('Connecting to XNAT at ' + self.xnat_host)
                xnat = XnatUtils.get_interface(self.xnat_host, self.xnat_user, self.xnat_pass)

                if not XnatUtils.has_dax_datatypes(xnat):
                    raise Exception('error: dax datatypes are not installed on your xnat <%s>' % (self.xnat_host))

                LOGGER.info('Getting launchable tasks list...')
                task_list = self.get_tasks(xnat,
                                           self.is_launchable_tasks,
                                           project_list,
                                           sessions_local)

                LOGGER.info(str(len(task_list))+' tasks that need to be launched found')

                # Launch the task that need to be launch
                self.launch_tasks(task_list, writeonly, pbsdir)
        finally:
            self.finish_script(xnat, flagfile, project_list, 3, 2, project_local)

    @staticmethod
    def is_launchable_tasks(assr_info):
        """
        Check if a task is launchable

        :param assr_info: dictionary containing procstatus for the assessor
        :return: True if tasks need to be launch, False otherwise.
        """
        return assr_info['procstatus'] == task.NEED_TO_RUN

    def launch_tasks(self, task_list, writeonly=False, pbsdir=None):
        """
        Launch tasks from the passed list until the queue is full or the list is empty

        :param task_list: list of task to launch
        :param writeonly: write the job files without submitting them
        :param pbsdir: folder to store the pbs file
        :return: None
        """
        # Check number of jobs on cluster
        cur_job_count = cluster.count_jobs()
        if cur_job_count == -1:
            LOGGER.error('cannot get count of jobs from cluster')
            return

        LOGGER.info(str(cur_job_count)+' jobs currently in queue')

        # Launch until we reach cluster limit or no jobs left to launch
        while (cur_job_count < self.queue_limit or writeonly) and len(task_list) > 0:
            cur_task = task_list.pop()

            # Confirm task is still ready to run
            # I don't think that we need to make this get here. We've already
            # filtered the assessors as need to run.
            # if cur_task.get_status() != task.NEED_TO_RUN:
            #     continue

            if writeonly:
                mes_format = """  +Writing PBS file for job:{label}, currently {count} jobs in cluster queue"""
                LOGGER.info(mes_format.format(label=cur_task.assessor_label,
                                              count=str(cur_job_count)))
            else:
                mes_format = """  +Launching job:{label}, currently {count} jobs in cluster queue"""
                LOGGER.info(mes_format.format(label=cur_task.assessor_label,
                                              count=str(cur_job_count)))

            try:
                if self.launcher_type in ['diskq-cluster', 'diskq-combined']:
                    success = cur_task.launch()
                else:
                    success = cur_task.launch(self.root_job_dir, self.job_email, self.job_email_options, self.xnat_host, writeonly, pbsdir)
            except Exception as E:
                LOGGER.critical('Caught exception launching job %s' % cur_task.assessor_label)
                LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))
                success = False

            if not success:
                LOGGER.error('ERROR:failed to launch job')
                raise cluster.ClusterLaunchException

            cur_job_count = cluster.count_jobs()
            if cur_job_count == -1:
                LOGGER.error('ERROR:cannot get count of jobs from cluster')
                raise cluster.ClusterCountJobsException

    ################## UPDATE Main Method ##################
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
            LOGGER.error('cannot update jobs with this launcher type:' + self.launcher_type)
            return

        LOGGER.info('-------------- Update Tasks --------------\n')
        LOGGER.info('launcher_type = '+self.launcher_type)

        xnat = None
        flagfile = os.path.join(os.path.join(DAX_SETTINGS.get_results_dir(), 'FlagFiles'), lockfile_prefix + '_' + UPDATE_SUFFIX)
        project_list = self.init_script(flagfile, project_local, type_update=2, start_end=1)

        try:
            if self.launcher_type in ['diskq-cluster', 'diskq-combined']:
                LOGGER.info('Loading task queue from:' + os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ'))
                task_list = load_task_queue()

                LOGGER.info(str(len(task_list)) + ' tasks found.')

                LOGGER.info('Updating tasks...')
                for cur_task in task_list:
                    LOGGER.info('Updating task:' + cur_task.assessor_label)
                    cur_task.update_status()
            else:
                LOGGER.info('Connecting to XNAT at ' + self.xnat_host)
                xnat = XnatUtils.get_interface(self.xnat_host, self.xnat_user, self.xnat_pass)

                if not XnatUtils.has_dax_datatypes(xnat):
                    raise Exception('error: dax datatypes are not installed on your xnat <%s>' % (self.xnat_host))

                LOGGER.info('Getting task list...')
                task_list = self.get_tasks(xnat,
                                           self.is_updatable_tasks,
                                           project_list,
                                           sessions_local)

                LOGGER.info(str(len(task_list))+' open tasks found')
                LOGGER.info('Updating tasks...')
                for cur_task in task_list:
                    LOGGER.info('     Updating task:' + cur_task.assessor_label)
                    cur_task.update_status()
        finally:
            self.finish_script(xnat, flagfile, project_list, 2, 2, project_local)

    @staticmethod
    def is_updatable_tasks(assr_info):
        """
        Check if a task is updatable.

        :param assr_info: dictionary containing procstatus/qcstatus for the assessor
        :return: True if tasks need to be update, False otherwise.

        """
        return assr_info['procstatus'] in task.OPEN_STATUS_LIST or\
               assr_info['qcstatus'] in task.OPEN_QA_LIST

    ################## BUILD Main Method ##################
    def build(self, lockfile_prefix, project_local, sessions_local, mod_delta=None):
        """
        Main method to build the tasks and the sessions

        :param lockfile_prefix: prefix for flag file to lock the launcher
        :param project_local: project to run locally
        :param sessions_local: list of sessions to launch tasks
         associated to the project locally
        :return: None

        """
        if self.launcher_type == 'diskq-cluster':
            LOGGER.error('cannot build jobs with this launcher type:' + self.launcher_type)
            return

        LOGGER.info('-------------- Build --------------\n')
        LOGGER.info('launcher_type = '+self.launcher_type)
        LOGGER.info('mod delta='+str(mod_delta))

        flagfile = os.path.join(os.path.join(DAX_SETTINGS.get_results_dir(), 'FlagFiles'), lockfile_prefix + '_' + BUILD_SUFFIX)
        project_list = self.init_script(flagfile, project_local, type_update=1, start_end=1)

        try:
            LOGGER.info('Connecting to XNAT at '+self.xnat_host)
            xnat = XnatUtils.get_interface(self.xnat_host, self.xnat_user, self.xnat_pass)

            if not XnatUtils.has_dax_datatypes(xnat):
                raise Exception('error: dax datatypes are not installed on your xnat <%s>' % (self.xnat_host))

            #Priority if set:
            if self.priority_project and not project_local:
                unique_list = set(self.project_process_dict.keys()+self.project_modules_dict.keys())
                project_list = self.get_project_list(list(unique_list))

            # Build projects
            for project_id in project_list:
                LOGGER.info('===== PROJECT:'+project_id+' =====')
                try:
                    self.build_project(xnat, project_id, lockfile_prefix, sessions_local, mod_delta=mod_delta)
                except Exception as E:
                    LOGGER.critical('Caught exception building project  %s' % project_id)
                    LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))

        finally:
            self.finish_script(xnat, flagfile, project_list, 1, 2, project_local)

    def build_project(self, xnat, project_id, lockfile_prefix, sessions_local, mod_delta=None):
        """
        Build the project

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param lockfile_prefix: prefix for flag file to lock the launcher
        :param sessions_local: list of sessions to launch tasks
        :return: None
        """
        
        #Modules prerun
        LOGGER.info('  *Modules Prerun')
        if sessions_local:
            self.module_prerun(project_id, 'manual_update')
        else:
            self.module_prerun(project_id, lockfile_prefix)
            
        # TODO: make a project settings to store skip_lastupdate, processors, modules, etc

        # Get lists of modules/processors per scan/exp for this project
        exp_mods, scan_mods = modules.modules_by_type(self.project_modules_dict[project_id])
        exp_procs, scan_procs = processors.processors_by_type(self.project_process_dict[project_id])

        if mod_delta:
            lastmod_delta = str_to_timedelta(mod_delta)
        else:
            lastmod_delta = None

        # Check for new processors
        has_new = self.has_new_processors(xnat, project_id, exp_procs, scan_procs)

        # Get the list of sessions:
        sessions = self.get_sessions_list(xnat, project_id, sessions_local)

        # Update each session from the list:
        for sess_info in sessions:
            if not self.skip_lastupdate and not has_new and not sessions_local:
                last_mod = datetime.strptime(sess_info['last_modified'][0:19], UPDATE_FORMAT)
                now_date = datetime.today()
                last_up = self.get_lastupdated(sess_info)
                if last_up != None and \
                    last_mod < last_up and \
                    now_date < last_mod + timedelta(days=int(self.max_age)):
                    mess = """  +Session:{sess}: skipping, last_mod={mod},last_up={up}"""
                    mess_str = mess.format(sess=sess_info['label'], mod=str(last_mod), up=str(last_up))
                    LOGGER.info(mess_str)
                    continue
                
            elif lastmod_delta:
                last_mod = datetime.strptime(sess_info['last_modified'][0:19], UPDATE_FORMAT)
                now_date = datetime.today()
                if now_date > last_mod + lastmod_delta:
                    mess = """+Session:{sess}:skipping not modified within delta, last_mod={mod}"""
                    mess_str = mess.format(sess=sess_info['label'], mod=str(last_mod))
                    LOGGER.info(mess_str)
                    continue
                else:
                    print('lastmod='+str(last_mod))
                    
            mess = """  +Session:{sess}: building..."""
            LOGGER.info(mess.format(sess=sess_info['label']))

            if not self.skip_lastupdate:
                update_start_time = datetime.now()

            try:
                self.build_session(xnat, sess_info, exp_procs, scan_procs, exp_mods, scan_mods)
            except Exception as E:
                LOGGER.critical('Caught exception building sessions %s' % sess_info['session_label'])
                LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))
            
            try:
                if not self.skip_lastupdate:
                    self.set_session_lastupdated(xnat, sess_info, update_start_time)
            except Exception as E:
                LOGGER.critical('Caught exception setting session timestamp %s' % sess_info['session_label'])
                LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))

        if not sessions_local or sessions_local.lower() == 'all':
            # Modules after run
            LOGGER.debug('*Modules Afterrun')
            try:
                self.module_afterrun(xnat, project_id)
            except Exception as E:
                LOGGER.critical('Caught exception after running modules %s')
                LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))

    def build_session(self, xnat, sess_info, sess_proc_list,
                      scan_proc_list, sess_mod_list, scan_mod_list):
        """
        Build a session

        :param xnat: pyxnat.Interface object
        :param sess_info: python ditionary from XnatUtils.list_sessions method
        :param sess_proc_list: list of processors running on a session
        :param scan_proc_list: list of processors running on a scan
        :param sess_mod_list: list of modules running on a session
        :param scan_mod_list: list of modules running on a scan
        :return: None
        """
        csess = XnatUtils.CachedImageSession(xnat,
                                             sess_info['project_label'],
                                             sess_info['subject_label'],
                                             sess_info['session_label'])
        session_info = csess.info()
        sess_obj = None

        # Modules
        mod_count = 0
        while mod_count < 3:
            mess = """== Build modules (count:{count}) =="""
            LOGGER.debug(mess.format(count=mod_count))
            # NOTE: we keep starting time to check if something changes below
            start_time = datetime.now()
            if sess_mod_list:
                self.build_session_modules(xnat, csess, sess_mod_list)
            if scan_mod_list:
                for cscan in csess.scans():
                    LOGGER.debug('+SCAN: ' + cscan.info()['scan_id'])
                    self.build_scan_modules(xnat, cscan, scan_mod_list)

            if not sess_was_modified(xnat, sess_info, start_time):
                break

            csess.reload()
            mod_count += 1

        # Scan Processors
        LOGGER.debug('== Build scan processors ==')
        if scan_proc_list:
            for cscan in csess.scans():
                LOGGER.debug('+SCAN: ' + cscan.info()['scan_id'])
                self.build_scan_processors(xnat, cscan, scan_proc_list)

        # Session Processors
        LOGGER.debug('== Build session processors ==')
        if sess_proc_list:
            self.build_session_processors(xnat, csess, sess_proc_list)

    def build_session_processors(self, xnat, csess, sess_proc_list):
        sess_info = csess.info()

        for sess_proc in sess_proc_list:
            if not sess_proc.should_run(sess_info):
                continue

            assr_name = sess_proc.get_assessor_name(csess)

            # Look for existing assessor
            proc_assr = None
            for assr in csess.assessors():
                if assr.info()['label'] == assr_name:
                    proc_assr = assr
                    break

            if self.launcher_type in ['diskq-xnat', 'diskq-combined']:
                if proc_assr == None or proc_assr.info()['procstatus'] == task.NEED_INPUTS or proc_assr.info()['qcstatus'] in [task.RERUN, task.REPROC]:
                    assessor = csess.full_object().assessor(assr_name)
                    xtask = XnatTask(sess_proc, assessor, DAX_SETTINGS.get_results_dir(), os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ'))
                    
                    if proc_assr != None and proc_assr.info()['qcstatus'] in [task.RERUN, task.REPROC]:
                        xtask.update_status()
                    
                    LOGGER.debug('building task:' + assr_name)
                    (proc_status, qc_status) = xtask.build_task(
                        csess,
                        self.root_job_dir,
                        self.job_email,
                        self.job_email_options)
                    LOGGER.debug('proc_status=' + proc_status + ', qc_status=' + qc_status)
                else:
                    # TODO: check that it actually exists in QUEUE
                    LOGGER.debug('skipping, already built:' + assr_name)
            else:
                if proc_assr == None or proc_assr.info()['procstatus'] == task.NEED_INPUTS:
                    sess_task = sess_proc.get_task(xnat, csess, DAX_SETTINGS.get_results_dir())
                    log_updating_status(sess_proc.name, sess_task.assessor_label)
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
                        LOGGER.critical('Caught exception building session %s '
                                        'while setting assessor status' %
                                        sess_info['session_label'])
                        LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))
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
                if sess_obj == None:
                    sess_obj = csess.full_object()

                try:
                    sess_mod.run(sess_info, sess_obj)
                except Exception as E:
                    LOGGER.critical('Caught exception building session module %s' % sess_info['session_label'])
                    LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))

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

        # Processors
        for scan_proc in scan_proc_list:
            if not scan_proc.should_run(scan_info):
                continue

            assr_name = scan_proc.get_assessor_name(cscan)

            # Look for existing assessor
            proc_assr = None
            for assr in cscan.parent().assessors():
                if assr.info()['label'] == assr_name:
                    proc_assr = assr

            if self.launcher_type in ['diskq-xnat', 'diskq-combined']:
                if proc_assr == None or proc_assr.info()['procstatus'] in [task.NEED_INPUTS, task.NEED_TO_RUN] or proc_assr.info()['qcstatus'] in [task.RERUN, task.REPROC]:
                    # TODO: get session object directly
                    scan = XnatUtils.get_full_object(xnat, scan_info)
                    assessor = scan.parent().assessor(assr_name)
                    xtask = XnatTask(scan_proc, assessor, DAX_SETTINGS.get_results_dir(), os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ'))
                    
                    if proc_assr != None and proc_assr.info()['qcstatus'] in [task.RERUN, task.REPROC]:
                        xtask.update_status()
                        
                    LOGGER.debug('building task:' + assr_name)
                    (proc_status, qc_status) = xtask.build_task(
                        cscan,
                        self.root_job_dir,
                        self.job_email,
                        self.job_email_options)
                    LOGGER.debug('proc_status=' + proc_status + ', qc_status=' + qc_status)
                else:
                    # TODO: check that it actually exists in QUEUE
                    LOGGER.debug('skipping, already built:' + assr_name)
            else:
                if proc_assr == None or proc_assr.info()['procstatus'] == task.NEED_INPUTS:
                    scan_task = scan_proc.get_task(xnat, cscan, DAX_SETTINGS.get_results_dir())
                    log_updating_status(scan_proc.name, scan_task.assessor_label)
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
                        LOGGER.critical('Caught exception building sessions  %s' % scan_info['session_label'])
                        LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))
                else:
                    # Other statuses handled by dax_update_open_tasks
                    pass


    def build_scan_modules(self, xnat, cscan, scan_mod_list):

        scan_info = cscan.info()
        scan_obj = None

        # Modules
        for scan_mod in scan_mod_list:
            LOGGER.debug('* Module: ' + scan_mod.getname())
            if scan_mod.needs_run(cscan, xnat):
                if scan_obj == None:
                    scan_obj = XnatUtils.get_full_object(xnat, scan_info)

                
                try:
                    scan_mod.run(scan_info, scan_obj)
                except Exception as E:
                    LOGGER.critical('Caught exception building session scan module in session %s' % scan_info['session_label'])
                    LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))

    def module_prerun(self, project_id, settings_filename=''):
        """
        Run the module prerun method

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param settings_filename: name of the settings file used to name temp dir
        :return: None
        """
        for mod in self.project_modules_dict[project_id]:
            try:
                mod.prerun(settings_filename)
            except Exception as E:
                LOGGER.critical('Caught exception in module prerun for project %s' % project_id)
                LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))
        LOGGER.debug('\n')

    def module_afterrun(self, xnat, project_id):
        """
        Run the module afterrun method

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :return: None
        """
        for mod in self.project_modules_dict[project_id]:
            try:
                mod.afterrun(xnat, project_id)
            except Exception as E:
                LOGGER.critical('Caught exception in module prerun for project %s' % project_id)
                LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))
        LOGGER.debug('\n')

    ################## Generic Methods ##################
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
        if project_local:
            if ',' in project_local:
                mess = """too much projects ID given to the option\
--project : {proj}. Only for one project."""
                mess_str = mess.format(proj=project_local)
                LOGGER.error(mess_str)
                exit(1)
            elif project_local in self.project_process_dict.keys():
                #Updating session for a specific project
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
            #Get default project list for XNAT out of the module and process dict
            ulist = set(self.project_process_dict.keys()+self.project_modules_dict.keys())
            project_list = sorted(ulist)
            #Set the date on REDCAP for update starting
            bin.upload_update_date_redcap(project_list, type_update, start_end)
        return project_list

    def finish_script(self, xnat, flagfile, project_list, type_update, start_end, project_local):
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
            #Set the date on REDCAP for update ending
            bin.upload_update_date_redcap(project_list, type_update, start_end)
            
        if xnat:
            xnat.disconnect()
            LOGGER.info('Connection to XNAT closed')

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

    def get_tasks(self, xnat, is_valid_assessor, project_list=None, sessions_local=None):
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
            #Priority:
            if self.priority_project:
                project_list = self.get_project_list(self.project_process_dict.keys())
            else:
                project_list = list(self.project_process_dict.keys())

        # iterate projects
        for project_id in project_list:
            LOGGER.info('===== PROJECT:'+project_id+' =====')
            task_list.extend(self.get_project_tasks(xnat,
                                                    project_id,
                                                    sessions_local,
                                                    is_valid_assessor))

        return task_list

    def get_project_tasks(self, xnat, project_id, sessions_local, is_valid_assessor):
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
        pp_dict = self.project_process_dict[project_id]
        sess_procs, scan_procs = processors.processors_by_type(pp_dict)

        # Get lists of assessors for this project
        assr_list = self.get_assessors_list(xnat, project_id, sessions_local)

        # Match each assessor to a processor, get a task, and add to list
        for assr_info in assr_list:
            if is_valid_assessor(assr_info):
                cur_task = self.generate_task(xnat, assr_info, sess_procs, scan_procs)
                if cur_task:
                    task_list.append(cur_task)

        return task_list

    @staticmethod
    def match_proc(assr_info, sess_proc_list, scan_proc_list):
        """
        Check if an assessor is a match with the processors

        :param assr_info: dictionary containing the assessor info (See XnatUtils.list_assessors)
        :param sess_proc_list: list of processors running on a session
        :param scan_proc_list: list of processors running on a scan
        :return: processor if found, None otherwise
        """
        # Look for a match in sess processors
        for sess_proc in sess_proc_list:
            if sess_proc.xsitype == assr_info['xsiType'] and\
               sess_proc.name == assr_info['proctype']:
                return sess_proc

        # Look for a match in scan processors
        for scan_proc in scan_proc_list:
            if scan_proc.xsitype == assr_info['xsiType'] and\
               scan_proc.name == assr_info['proctype']:
                return scan_proc

        return None

    def generate_task(self, xnat, assr_info, sess_proc_list, scan_proc_list):
        """
        Generate a task for the assessor in the info

        :param xnat: pyxnat.Interface object
        :param assr_info: dictionary containing the assessor info (See XnatUtils.list_assessors)
        :param sess_proc_list: list of processors running on a session
        :param scan_proc_list: list of processors running on a scan
        :return: task if processor and assessor match, None otherwise
        """
        task_proc = self.match_proc(assr_info, sess_proc_list, scan_proc_list)

        if task_proc == None:
            LOGGER.warn('no matching processor found:'+assr_info['assessor_label'])
            return None
        else:
            # Get a new task with the matched processor
            assr = XnatUtils.get_full_object(xnat, assr_info)
            cur_task = Task(task_proc, assr,  DAX_SETTINGS.get_results_dir())
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

        #filter the assessors to the sessions given as parameters if given
        if slocal and slocal.lower() != 'all':
            #filter the list and keep the match between both list:
            assr_list = filter(lambda x: x['session_label'] in slocal.split(','), assr_list)
            if not assr_list:
                LOGGER.warn('No processes from XNAT matched the sessions given: '+slocal+' .')
                sys.exit(1)

        return assr_list

    @staticmethod
    def get_sessions_list(xnat, project_id, slocal):
        """
        Get the sessions list from XNAT and sort it. Move the new sessions to the front.

        :param xnat: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param slocal: session selected by user
        :return: list of sessions sorted for a project
        """
        list_sessions = XnatUtils.list_sessions(xnat, project_id)
        if slocal and slocal.lower() != 'all':
            #filter the list and keep the match between both list:
            list_sessions = filter(lambda x: x['label'] in slocal.split(','), list_sessions)
            if not list_sessions:
                LOGGER.warn('No session from XNAT matched the sessions given: '+slocal+' .')

        #Sort sessions: first the new sessions that have never been updated
        sorted_list = [sess for sess in list_sessions if not sess['last_updated']]
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
        random_project = filter(lambda project: project not in self.priority_project, all_projects)
        return self.priority_project+random_project

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
    def set_session_lastupdated(xnat, sess_info, update_start_time):
        """
        Set the last session update on XNAT

        :param xnat: pyxnat.Interface object
        :param sess_info: dictionary of session information
        :param update_start_time: date when the update started
        :return: False if the session change and don't set the last update date, True otherwise
        """
        xsi_type = sess_info['xsiType']
        sess_obj = XnatUtils.get_full_object(xnat, sess_info)
        last_modified_xnat = sess_obj.attrs.get(xsi_type+'/meta/last_modified')
        last_mod = datetime.strptime(last_modified_xnat[0:19], '%Y-%m-%d %H:%M:%S')
        if last_mod > update_start_time:
            return False

        # format:
        update_str = (datetime.now()+timedelta(minutes=1)).strftime(UPDATE_FORMAT)
        # We set update to one minute into the future
        # since setting update field will change last modified time
        LOGGER.debug('setting last_updated for:' + sess_info['label'] + ' to ' + update_str)
        try:
            sess_obj.attrs.set(xsi_type + '/original', UPDATE_PREFIX + update_str)
        except Exception as E:
                LOGGER.critical('Caught exception setting update timestamp for session %s' % sess_info['session_label'])
                LOGGER.critical('Exception class %s caught with message %s' %(E.__class__, E.message))

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
        proc_name_set = set([x.name for x in sess_proc_list+scan_proc_list])

        # Get list of processors that don't have assessors in XNAT yet
        diff_list = list(proc_name_set.difference(assr_type_set))

        # Are there any?
        return len(diff_list) > 0

def load_task_queue(status=None):
    task_list = list()
    diskq_dir = os.path.join(DAX_SETTINGS.get_results_dir(), 'DISKQ')
    results_dir = DAX_SETTINGS.get_results_dir()

    for t in os.listdir(os.path.join(diskq_dir, 'BATCH')):
        # task_path = os.path.join(BATCH_DIR, t)

        LOGGER.debug('loading:' + t)
        task = ClusterTask(os.path.splitext(t)[0], results_dir, diskq_dir)
        LOGGER.debug('status = ' + task.get_status())

        # TODO:filter based on project, subject, session, type
        if not status or task.get_status() == status:
            LOGGER.debug('adding task to list:' + t)
            task_list.append(task)

    return task_list

def get_sess_lastmod(xnat, sess_info):
    xsi_type = sess_info['xsiType']
    sess_obj = XnatUtils.get_full_object(xnat, sess_info)
    last_modified_xnat = sess_obj.attrs.get(xsi_type + '/meta/last_modified')
    last_mod = datetime.strptime(last_modified_xnat[0:19], '%Y-%m-%d %H:%M:%S')
    return last_mod

def sess_was_modified(xnat, sess_info, build_start_time):
    """
    Compare modified time with start time
    :param xnat: pyxnat.Interface object
    :param sess_info: dictionary of session information
    :param update_start_time: date when the update started
    :return: False if the session change and don't set the last update date, True otherwise
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
