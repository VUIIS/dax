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
from task import Task
from dax_settings import RESULTS_DIR, DEFAULT_ROOT_JOB_DIR, DEFAULT_QUEUE_LIMIT, DEFAULT_MAX_AGE

UPDATE_PREFIX = 'updated--'
UPDATE_FORMAT = "%Y-%m-%d %H:%M:%S"
BUILD_SUFFIX = 'BUILD_RUNNING.txt'
UPDATE_SUFFIX = 'UPDATE_RUNNING.txt'
LAUNCH_SUFFIX = 'LAUNCHER_RUNNING.txt'

#Logger to print logs
LOGGER = logging.getLogger('dax')

class Launcher(object):
    """ Launcher object to manage a list of projects from a settings file """
    def __init__(self, project_process_dict, project_modules_dict, priority_project=None,
                 queue_limit=DEFAULT_QUEUE_LIMIT, root_job_dir=DEFAULT_ROOT_JOB_DIR,
                 xnat_user=None, xnat_pass=None, xnat_host=None,
                 job_email=None, job_email_options='bae', max_age=DEFAULT_MAX_AGE):
        """ Init method """
        self.queue_limit = queue_limit
        self.root_job_dir = root_job_dir
        self.project_process_dict = project_process_dict
        self.project_modules_dict = project_modules_dict
        self.priority_project = priority_project
        self.job_email = job_email
        self.job_email_options = job_email_options
        self.max_age = max_age

        #Creating Folders for flagfile/pbs/outlog in RESULTS_DIR
        if not os.path.exists(RESULTS_DIR):
            os.mkdir(RESULTS_DIR)
        if not os.path.exists(os.path.join(RESULTS_DIR, 'PBS')):
            os.mkdir(os.path.join(RESULTS_DIR, 'PBS'))
        if not os.path.exists(os.path.join(RESULTS_DIR, 'OUTLOG')):
            os.mkdir(os.path.join(RESULTS_DIR, 'OUTLOG'))
        if not os.path.exists(os.path.join(RESULTS_DIR, 'FlagFiles')):
            os.mkdir(os.path.join(RESULTS_DIR, 'FlagFiles'))

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
    def launch_jobs(self, lockfile_prefix, project_local, sessions_local):
        """ Main Method to launch the tasks """
        LOGGER.info('-------------- Launch Tasks --------------\n')

        flagfile = os.path.join(RESULTS_DIR, 'FlagFiles', lockfile_prefix+'_'+LAUNCH_SUFFIX)
        project_list = self.init_script(flagfile, project_local, type_update=3, start_end=1)

        try:
            LOGGER.info('Connecting to XNAT at '+self.xnat_host)
            xnat = XnatUtils.get_interface(self.xnat_host, self.xnat_user, self.xnat_pass)

            LOGGER.info('Getting launchable tasks list...')
            task_list = self.get_tasks(xnat,
                                       self.is_launchable_tasks,
                                       project_list,
                                       sessions_local)

            LOGGER.info(str(len(task_list))+' tasks that need to be launched found')

            #Launch the task that need to be launch
            self.launch_tasks(task_list)

        finally:
            self.finish_script(xnat, flagfile, project_list, 3, 2, project_local)

    @staticmethod
    def is_launchable_tasks(assr_info):
        """ return True if the assessor is launchable """
        return assr_info['procstatus'] == task.NEED_TO_RUN

    def launch_tasks(self, task_list):
        """ launch the tasks in the list until the queue is full or the list empty """
        # Check number of jobs on cluster
        cur_job_count = cluster.count_jobs()
        if cur_job_count == -1:
            LOGGER.error('cannot get count of jobs from cluster')
            return

        LOGGER.info(str(cur_job_count)+' jobs currently in queue')

        # Launch until we reach cluster limit or no jobs left to launch
        while cur_job_count < self.queue_limit and len(task_list) > 0:
            cur_task = task_list.pop()

            # Confirm task is still ready to run
            if cur_task.get_status() != task.NEED_TO_RUN:
                continue

            mes_format = """  +Launching job:{label}, currently {count} jobs in cluster queue"""
            LOGGER.info(mes_format.format(label=cur_task.assessor_label,
                                          count=str(cur_job_count)))
            success = cur_task.launch(self.root_job_dir, self.job_email, self.job_email_options)
            if success != True:
                LOGGER.error('ERROR:failed to launch job')

            cur_job_count = cluster.count_jobs()
            if cur_job_count == -1:
                LOGGER.error('ERROR:cannot get count of jobs from cluster')
                return

    ################## UPDATE Main Method ##################
    def update_tasks(self, lockfile_prefix, project_local, sessions_local):
        """ Main method to Update the tasks """
        LOGGER.info('-------------- Update Tasks --------------\n')

        flagfile = os.path.join(RESULTS_DIR, 'FlagFiles', lockfile_prefix+'_'+UPDATE_SUFFIX)
        project_list = self.init_script(flagfile, project_local, type_update=2, start_end=1)

        try:
            LOGGER.info('Connecting to XNAT at '+self.xnat_host)
            xnat = XnatUtils.get_interface(self.xnat_host, self.xnat_user, self.xnat_pass)

            LOGGER.info('Getting task list...')
            task_list = self.get_tasks(xnat,
                                       self.is_updatable_tasks,
                                       project_list,
                                       sessions_local)

            LOGGER.info(str(len(task_list))+' open tasks found')

            LOGGER.info('Updating tasks...')
            for cur_task in task_list:
                LOGGER.info('     Updating task:'+cur_task.assessor_label)
                cur_task.update_status()

        finally:
            self.finish_script(xnat, flagfile, project_list, 2, 2, project_local)

    @staticmethod
    def is_updatable_tasks(assr_info):
        """ return True if the assessor is updatable """
        return assr_info['procstatus'] in task.OPEN_STATUS_LIST or\
               assr_info['qcstatus'] in task.OPEN_QC_LIST

    ################## BUILD Main Method ##################
    def build(self, lockfile_prefix, project_local, sessions_local):
        """ Main method to Update the tasks """
        LOGGER.info('-------------- Build --------------\n')

        flagfile = os.path.join(RESULTS_DIR, 'FlagFiles', lockfile_prefix+'_'+BUILD_SUFFIX)
        project_list = self.init_script(flagfile, project_local, type_update=1, start_end=1)

        try:
            LOGGER.info('Connecting to XNAT at '+self.xnat_host)
            xnat = XnatUtils.get_interface(self.xnat_host, self.xnat_user, self.xnat_pass)

            #Priority if set:
            if self.priority_project and not project_local:
                unique_list = set(self.project_process_dict.keys()+self.project_modules_dict.keys())
                project_list = self.get_project_list(list(unique_list))

            # Build projects
            for project_id in project_list:
                LOGGER.info('===== PROJECT:'+project_id+' =====')
                self.build_project(xnat, project_id, lockfile_prefix, sessions_local)

        finally:
            self.finish_script(xnat, flagfile, project_list, 1, 2, project_local)

    def build_project(self, xnat, project_id, lockfile_prefix, sessions_local):
        """ build the project """
        #Modules prerun
        LOGGER.info('  *Modules Prerun')
        if sessions_local:
            self.module_prerun(project_id, 'manual_update')
        else:
            self.module_prerun(project_id, lockfile_prefix)

        # Get lists of modules/processors per scan/exp for this project
        exp_mods, scan_mods = modules.modules_by_type(self.project_modules_dict[project_id])
        exp_procs, scan_procs = processors.processors_by_type(self.project_process_dict[project_id])

        # Check for new processors
        has_new = self.has_new_processors(xnat, project_id, exp_procs, scan_procs)

        # Get the list of sessions:
        sessions = self.get_sessions_list(xnat, project_id, sessions_local)

        # Update each session from the list:
        for sess_info in sessions:
            last_mod = datetime.strptime(sess_info['last_modified'][0:19], UPDATE_FORMAT)
            now_date = datetime.today()
            last_up = self.get_lastupdated(sess_info)

            #If sessions_local is set, skip checking the date
            if not has_new and last_up != None and \
               last_mod < last_up and not sessions_local and \
               now_date < last_mod+timedelta(days=int(self.max_age)):
                mess = """  +Session:{sess}: skipping, last_mod={mod},last_up={up}"""
                mess_str = mess.format(sess=sess_info['label'], mod=str(last_mod), up=str(last_up))
                LOGGER.info(mess_str)
            else:
                update_run_count = 0
                got_updated = False
                while update_run_count < 3 and not got_updated:
                    mess = """  +Session:{sess}: updating (count:{count})..."""
                    LOGGER.info(mess.format(sess=sess_info['label'], count=update_run_count))
                    # NOTE: we keep the starting time of the update
                    # and will check if something change during the update
                    update_start_time = datetime.now()
                    self.build_session(xnat, sess_info, exp_procs, scan_procs, exp_mods, scan_mods)
                    got_updated = self.set_session_lastupdated(xnat, sess_info, update_start_time)
                    update_run_count = update_run_count+1
                    LOGGER.debug('\n')

        if not sessions_local or sessions_local.lower() == 'all':
            # Modules after run
            LOGGER.debug('*Modules Afterrun')
            self.module_afterrun(xnat, project_id)

    def build_session(self, xnat, sess_info, sess_proc_list,
                      scan_proc_list, sess_mod_list, scan_mod_list):
        """ build the session """
        csess = XnatUtils.CachedImageSession(xnat,
                                             sess_info['project_label'],
                                             sess_info['subject_label'],
                                             sess_info['session_label'])
        session_info = csess.info()
        sess_obj = None

        # Modules on session
        LOGGER.debug('== Build modules for session ==')
        for sess_mod in sess_mod_list:
            LOGGER.debug('* Module: '+sess_mod.getname())
            if sess_mod.needs_run(csess, xnat):
                if sess_obj == None:
                    sess_obj = XnatUtils.get_full_object(xnat, session_info)

                sess_mod.run(session_info, sess_obj)

        # Scans
        LOGGER.debug('== Build modules/processors for scans in session ==')
        if scan_proc_list or scan_mod_list:
            for cscan in csess.scans():
                LOGGER.debug('+SCAN: '+cscan.info()['scan_id'])
                self.build_scan(xnat, cscan, scan_proc_list, scan_mod_list)

        # Processors
        LOGGER.debug('== Build processors for session ==')
        for sess_proc in sess_proc_list:
            if sess_proc.should_run(session_info):

                assr_name = sess_proc.get_assessor_name(csess)

                # Look for existing assessor
                proc_assr = None
                for assr in csess.assessors():
                    if assr.info()['label'] == assr_name:
                        proc_assr = assr

                if proc_assr == None:
                    # Create it if it doesn't exist
                    sess_task = sess_proc.get_task(xnat, csess, RESULTS_DIR)
                    self.log_updating_status(sess_proc.name, sess_task.assessor_label)
                    has_inputs, qcstatus = sess_proc.has_inputs(csess)
                    if has_inputs == 1:
                        sess_task.set_status(task.NEED_TO_RUN)
                        sess_task.set_qcstatus(task.JOB_PENDING)
                    elif has_inputs == -1:
                        sess_task.set_status(task.NO_DATA)
                        sess_task.set_qcstatus(qcstatus)
                elif proc_assr.info()['procstatus'] == task.NEED_INPUTS:
                    has_inputs, qcstatus = sess_proc.has_inputs(csess)
                    if has_inputs == 1:
                        sess_task = sess_proc.get_task(xnat, csess, RESULTS_DIR)
                        self.log_updating_status(sess_proc.name, sess_task.assessor_label)
                        sess_task.set_status(task.NEED_TO_RUN)
                        sess_task.set_qcstatus(task.JOB_PENDING)
                    elif has_inputs == -1:
                        sess_task = sess_proc.get_task(xnat, csess, RESULTS_DIR)
                        self.log_updating_status(sess_proc.name, sess_task.assessor_label)
                        sess_task.set_status(task.NO_DATA)
                        sess_task.set_qcstatus(qcstatus)
                    else:
                        # Leave as NEED_INPUTS
                        pass
                else:
                    # Other statuses handled by dax_update_tasks
                    pass

    @staticmethod
    def log_updating_status(procname, assessor_label):
        """ print as debug the status updating string """
        mess = """* Processor:{proc}: updating status: {label}"""
        mess_str = mess.format(proc=procname, label=assessor_label)
        LOGGER.debug(mess_str)

    def build_scan(self, xnat, cscan, scan_proc_list, scan_mod_list):
        """ build the scan """
        scan_info = cscan.info()
        scan_obj = None

        # Modules
        for scan_mod in scan_mod_list:
            LOGGER.debug('* Module: '+scan_mod.getname())
            if scan_mod.needs_run(cscan, xnat):
                if scan_obj == None:
                    scan_obj = XnatUtils.get_full_object(xnat, scan_info)

                scan_mod.run(scan_info, scan_obj)

        # Processors
        for scan_proc in scan_proc_list:
            if scan_proc.should_run(scan_info):
                assr_name = scan_proc.get_assessor_name(cscan)

                # Look for existing assessor
                proc_assr = None
                for assr in cscan.parent().assessors():
                    if assr.info()['label'] == assr_name:
                        proc_assr = assr

                # Create it if it doesn't exist
                if proc_assr == None or proc_assr.info()['procstatus'] == task.NEED_INPUTS:
                    scan_task = scan_proc.get_task(xnat, cscan, RESULTS_DIR)
                    self.log_updating_status(scan_proc.name, scan_task.assessor_label)
                    has_inputs, qcstatus = scan_proc.has_inputs(cscan)
                    if has_inputs == 1:
                        scan_task.set_status(task.NEED_TO_RUN)
                        scan_task.set_qcstatus(task.JOB_PENDING)
                    elif has_inputs == -1:
                        scan_task.set_status(task.NO_DATA)
                        scan_task.set_qcstatus(qcstatus)

                else:
                    # Other statuses handled by dax_update_open_tasks
                    pass

    def module_prerun(self, project_id, settings_filename=''):
        """ run the module prerun method """
        for mod in self.project_modules_dict[project_id]:
            mod.prerun(settings_filename)
        LOGGER.debug('\n')

    def module_afterrun(self, xnat, project_id):
        """ run the module afterrun method """
        for mod in self.project_modules_dict[project_id]:
            mod.afterrun(xnat, project_id)
        LOGGER.debug('\n')

    ################## Generic Methods ##################
    def init_script(self, flagfile, project_local, type_update, start_end):
        """ init script for any of the main function: build/update/launch """
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
        """ finish script for any of the main function: build/update/launch """
        if not project_local:
            self.unlock_flagfile(flagfile)
            #Set the date on REDCAP for update ending
            bin.upload_update_date_redcap(project_list, type_update, start_end)
        xnat.disconnect()
        LOGGER.info('Connection to XNAT closed')

    @staticmethod
    def lock_flagfile(lock_file):
        """ create the flagfile to lock the process """
        if os.path.exists(lock_file):
            return False
        else:
            open(lock_file, 'w').close()
            return True

    @staticmethod
    def unlock_flagfile(lock_file):
        """ remove the flagfile to unlock the process """
        if os.path.exists(lock_file):
            os.remove(lock_file)

    def get_tasks(self, xnat, is_valid_assessor, project_list=None, sessions_local=None):
        """ return list of tasks """
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
        """ return list of tasks for a project
            where each task agreee the is_valid_assessor conditions
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
        """ return processor if a match is found """
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
        """ return a task for the assessor in the info"""
        task_proc = self.match_proc(assr_info, sess_proc_list, scan_proc_list)

        if task_proc == None:
            LOGGER.warn('no matching processor found:'+assr_info['assessor_label'])
            return None
        else:
            # Get a new task with the matched processor
            assr = XnatUtils.get_full_object(xnat, assr_info)
            cur_task = Task(task_proc, assr, RESULTS_DIR)
            return cur_task

    @staticmethod
    def get_assessors_list(xnat, project_id, slocal):
        """ get the assessor list from XNAT and filter it if necessary """
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
        """ get the sessions list from XNAT and sort it.
            move the new sessions to the front
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
        """ get project list from the file priority + the other ones"""
        random_project = filter(lambda project: project not in self.priority_project, all_projects)
        return self.priority_project+random_project

    @staticmethod
    def get_lastupdated(info):
        """ return last updated date from XNAT """
        update_time = info['last_updated'][len(UPDATE_PREFIX):]
        if update_time == '':
            return None
        else:
            return datetime.strptime(update_time, UPDATE_FORMAT)

    @staticmethod
    def set_session_lastupdated(xnat, sess_info, update_start_time):
        """ set the last session update on XNAT
            return False if the session change and don't set the last update date
            return True otherwise
        """
        xsi_type = sess_info['xsiType']
        sess_obj = XnatUtils.get_full_object(xnat, sess_info)
        last_modified_xnat = sess_obj.attrs.get(xsi_type+'/meta/last_modified')
        last_mod = datetime.strptime(last_modified_xnat[0:19], '%Y-%m-%d %H:%M:%S')
        if last_mod > update_start_time:
            return False
        else:
            #format:
            update_str = (datetime.now()+timedelta(minutes=1)).strftime(UPDATE_FORMAT)
            # We set update to one minute into the future
            # since setting update field will change last modified time
            LOGGER.debug('setting last_updated for:'+sess_info['label']+' to '+update_str)
            sess_obj.attrs.set(xsi_type+'/original', UPDATE_PREFIX+update_str)
            return True

    @staticmethod
    def has_new_processors(xnat, project_id, exp_proc_list, scan_proc_list):
        """ check if has new processors """
        # Get unique list of assessors already in XNAT
        assr_list = XnatUtils.list_project_assessors(xnat, project_id)
        assr_type_set = set([x['proctype'] for x in assr_list])

        # Get unique list of processors prescribed for project
        proc_name_set = set([x.name for x in exp_proc_list+scan_proc_list])

        # Get list of processors that don't have assessors in XNAT yet
        diff_list = list(proc_name_set.difference(assr_type_set))

        # Are there any?
        return len(diff_list) > 0
