#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" launcher.py that represents the main object called by the executables """

from datetime import datetime, timedelta
import logging
import sys
import os
import traceback
import tempfile
import time

from . import lockfiles
from . import processors, modules, XnatUtils, task, cluster, processors_v3
from .task import Task, ClusterTask, XnatTask, mkdirp
from .dax_settings import DAX_Settings, DAX_Netrc
from .errors import (ClusterCountJobsException, ClusterLaunchException,
                     DaxXnatError, DaxLauncherError)
from . import yaml_doc
from .processor_graph import ProcessorGraph
from .utilities import find_with_pred, groupby_to_dict

__copyright__ = 'Copyright 2019 Vanderbilt University. All Rights Reserved'
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


def check_res_dir(resdir):
    check_dir(os.path.join(resdir, 'DISKQ'))
    check_dir(os.path.join(os.path.join(resdir, 'DISKQ'), 'INPUTS'))
    check_dir(os.path.join(os.path.join(resdir, 'DISKQ'), 'OUTLOG'))
    check_dir(os.path.join(os.path.join(resdir, 'DISKQ'), 'BATCH'))
    check_dir(os.path.join(resdir, 'FlagFiles'))


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
                 resdir,
                 project_process_dict=dict(),
                 project_modules_dict=dict(),
                 yaml_dict=dict(),
                 priority_project=None,
                 queue_limit=10,
                 queue_limit_pending=10,
                 limit_pendinguploads=1,
                 launch_delay_sec=1,
                 root_job_dir='/tmp',
                 xnat_user=None, xnat_pass=None, xnat_host=None, cr=None,
                 job_email=None, job_email_options='FAIL', job_rungroup=None,
                 launcher_type='diskq-combined',
                 job_template='~/job_template.txt',
                 smtp_host=None,
                 timeout_emails=None,
                 project_sgp_processors={}):
        """
        Entry point for the Launcher class

        :param project_process_dict: dictionary associating project & processes
        :param project_modules_dict: dictionary associating project & modules
        :param priority_project: list of project to describe the priority
        :param queue_limit: maximum number of jobs in the queue
        :param queue_limit_pending: maximum pending jobs in the queue
        :param limit_pendinguploads: maximum number of uploads waiting
        :param launch_delay_sec: time to wait between job launches
        :param root_job_dir: root directory for jobs
        :param xnat_host: XNAT Host url. By default, use env variable.
        :param cr: True if the host is an XNAT CR instance (will default to
        :False if not specified)
        :param xnat_user: XNAT User ID. By default, use env variable.
        :param xnat_pass: XNAT Password. By default, use env variable.
        :param job_email: job email address for report
        :param job_email_options: email options for the jobs
        :param job_rungroup: cluster group to run the job under
        :param max_age: maximum time before updating again a session
        :return: None
        """
        self.queue_limit = queue_limit
        self.queue_limit_pending = queue_limit_pending
        self.limit_pendinguploads = limit_pendinguploads
        self.launch_delay_sec = launch_delay_sec
        self.root_job_dir = root_job_dir
        self.resdir = resdir
        self.smtp_host = smtp_host
        self.timeout_emails = timeout_emails

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

        # TODO: should this self be here, I don't think so - bdb 2022-04-05
        self.yaml_dict = yaml_dict if yaml_dict is not None else dict()

        # Add processors to project_process_dict:
        for project, yaml_objs in list(yaml_dict.items()):
            for yaml_obj in yaml_objs:
                if isinstance(yaml_obj, processors_v3.Processor_v3):
                    proc = yaml_obj
                elif isinstance(yaml_obj, processors.AutoProcessor):
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

        self.project_sgp_processors = project_sgp_processors

        if isinstance(priority_project, list):
            self.priority_project = priority_project
        elif isinstance(priority_project, str):
            self.priority_project = priority_project.split(',')
        else:
            self.priority_project = None

        self.job_email = job_email
        self.job_email_options = job_email_options
        self.job_rungroup = job_rungroup
        self.launcher_type = launcher_type
        self.job_template = job_template

        # Create Folders for flagfile/pbs/outlog in RESULTS_DIR
        check_res_dir(resdir)

        self.xnat_host = xnat_host
        if not self.xnat_host:
            self.xnat_host = os.environ['XNAT_HOST']

        # CR flag: don't want something like 'cr: blah blah' in the settings
        # file turning the cr flag on
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
                self.xnat_pass = eval(
                    input(msg % (self.xnat_host, self.xnat_user)))
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

        LOGGER.info('-------------- Launch Tasks --------------')
        LOGGER.info('launcher_type = %s' % self.launcher_type)

        flagfile = os.path.join(os.path.join(self.resdir, 'FlagFiles'),
                                '%s_%s' % (lockfile_prefix, LAUNCH_SUFFIX))

        project_list = self.init_script(flagfile, project_local,
                                        type_update=3, start_end=1)

        if project_list is None or len(project_list) == 0:
            LOGGER.info('no projects to launch')
        else:
            msg = 'Loading task queue from: %s'
            LOGGER.info(msg % os.path.join(self.resdir, 'DISKQ'))
            task_list = load_task_queue(
                self.resdir,
                status=task.NEED_TO_RUN,
                proj_filter=project_list,
                sess_filter=sessions_local)

            msg = '%s tasks that need to be launched found'
            LOGGER.info(msg % str(len(task_list)))
            self.launch_tasks(task_list, force_no_qsub=force_no_qsub)

        self.finish_script(flagfile, project_list, 3, 2, project_local)

    @staticmethod
    def is_launchable_tasks(assr_info):
        """
        Check if a task is launchable

        :param assr_info: dictionary containing procstatus for the assessor
        :return: True if tasks need to be launch, False otherwise.
        """
        return assr_info['procstatus'] == task.NEED_TO_RUN

    def launch_tasks(self, task_list, force_no_qsub=False):
        """
        Launch tasks from the passed list until the queue is full or
         the list is empty

        :param task_list: list of task to launch
        :param force_no_qsub: run the job locally on the computer (serial mode)
        :return: None
        """
        launched, pending, pendinguploads = cluster.count_jobs(self.resdir,force_no_qsub)
        if not force_no_qsub:
            LOGGER.info(
                'Cluster: %d/%d total, %d/%d pending, %d/%d pending uploads',
                launched, self.queue_limit,
                pending, self.queue_limit_pending,
                pendinguploads, self.limit_pendinguploads
                )

        # Launch until we reach cluster limit or no jobs left to launch
        _launchcnt = 0
        _launchmax = len(task_list)
        while(
                launched < self.queue_limit and
                pending < self.queue_limit_pending and
                pendinguploads < self.limit_pendinguploads and
                len(task_list) > 0
                ):

            cur_task = task_list.pop()

            LOGGER.info('Launching job: %s', cur_task.assessor_label)

            try:
                success = cur_task.launch(force_no_qsub=force_no_qsub)
            except Exception as E:
                LOGGER.critical(
                    'Caught exception launching job %s',
                    cur_task.assessor_label
                    )
                LOGGER.critical(
                    'Exception class %s caught with message %s',
                    E.__class__, str(E)
                    )
                LOGGER.critical(traceback.format_exc())
                success = False

            if not success:
                LOGGER.error('ERROR: failed to launch job')
                raise ClusterLaunchException

            _launchcnt = _launchcnt + 1
            time.sleep(self.launch_delay_sec)

            launched, pending, pendinguploads = cluster.count_jobs(self.resdir,force_no_qsub)
            if not force_no_qsub:
                LOGGER.info(
                    'Cluster: %d/%d total, %d/%d pending, %d/%d pending uploads',
                    launched, self.queue_limit,
                    pending, self.queue_limit_pending,
                    pendinguploads, self.limit_pendinguploads
                    )

        if not force_no_qsub:
            LOGGER.info(
                'Launched %d of %d jobs. Stopping', _launchcnt, _launchmax
                )


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

        LOGGER.info('-------------- Update Tasks --------------')
        LOGGER.info('launcher_type = %s' % self.launcher_type)

        flagfile = os.path.join(os.path.join(self.resdir, 'FlagFiles'),
                                '%s_%s' % (lockfile_prefix, UPDATE_SUFFIX))
        project_list = self.init_script(flagfile, project_local,
                                        type_update=2, start_end=1)

        if project_list is None or len(project_list) == 0:
            LOGGER.info('no projects to launch')
        else:
            msg = 'Loading task queue from: %s'
            LOGGER.info(msg % os.path.join(self.resdir, 'DISKQ'))
            task_list = load_task_queue(self.resdir, proj_filter=project_list)

            LOGGER.info('%s tasks found.' % str(len(task_list)))

            LOGGER.info('Updating tasks...')
            for cur_task in task_list:
                LOGGER.info('Updating task: %s' % cur_task.assessor_label)
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
              mod_delta=None, proj_lastrun=None, start_sess=None):
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

        LOGGER.info('-------------- Build --------------')
        LOGGER.info('launcher_type = %s' % self.launcher_type)
        LOGGER.info('mod delta = %s' % str(mod_delta))

        flagfile = os.path.join(os.path.join(self.resdir, 'FlagFiles'),
                                '%s_%s' % (lockfile_prefix, BUILD_SUFFIX))
        project_list = self.init_script(flagfile, project_local,
                                        type_update=1, start_end=1)

        LOGGER.info('Connecting to XNAT at %s' % self.xnat_host)
        with XnatUtils.get_interface(
            self.xnat_host,
            self.xnat_user,
            self.xnat_pass,
            self.smtp_host,
            self.timeout_emails
        ) as intf:

            if not XnatUtils.has_dax_datatypes(intf):
                err = 'error: dax datatypes are not installed on xnat <%s>'
                raise DaxXnatError(err % (self.xnat_host))

            # Priority if set:
            if self.priority_project and not project_local:
                unique_list = set(list(self.project_process_dict.keys()) +
                    list(self.project_modules_dict.keys()) +
                    list(self.project_sgp_processors.keys()))
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
                                       mod_delta=mod_delta, lastrun=lastrun,
                                       start_sess=start_sess)

                    if len(self.get_subjgenproc_processors(project_id)) > 0:
                        # The project has SGP processors so we build them
                        self.build_project_subjgenproc(intf, project_id)

                except Exception as E:
                    err1 = 'Caught exception building project %s'
                    err2 = 'Exception class %s caught with message %s'
                    LOGGER.critical(err1 % project_id)
                    LOGGER.critical(err2 % (E.__class__, str(E)))
                    LOGGER.critical(traceback.format_exc())

        self.finish_script(flagfile, project_list, 1, 2, project_local)

    def build_project(self, intf, project_id, lockfile_prefix, sessions_local,
                      mod_delta=None, lastrun=None, start_sess=None):
        """
        Build the project

        :param intf: pyxnat.Interface object
        :param project_id: project ID on XNAT
        :param lockfile_prefix: prefix for flag file to lock the launcher
        :param sessions_local: list of sessions to launch tasks
        :return: None
        """

        # TODO: make a project settings to store, processors,
        #       modules, etc

        # Get lists of modules/processors per scan/exp for this project
        proj_mods = self.project_modules_dict.get(project_id, None)
        proj_procs = self.project_process_dict.get(project_id, None)
        exp_mods, scan_mods = modules.modules_by_type(proj_mods)
        auto_procs = processors.processors_by_type(proj_procs)
        auto_procs = ProcessorGraph.order_processors(auto_procs, LOGGER)

        if proj_mods:
            # Modules prerun
            LOGGER.info('* Modules Prerun')
            if sessions_local:
                self.module_prerun(project_id, 'manual_update')
            else:
                self.module_prerun(project_id, lockfile_prefix)

        if mod_delta:
            lastmod_delta = str_to_timedelta(mod_delta)
        else:
            lastmod_delta = None

        # get the list of processors for this project
        processor_types = set([x.name for x in auto_procs])

        LOGGER.info('* Loading list of sessions from XNAT for project')
        sess_list = self.get_sessions_list(intf, project_id, sessions_local)

        # Skip to session
        if start_sess:
            for i, sess in enumerate(sess_list):
                if sess['label'] == start_sess:
                    LOGGER.info('starting index=' + str(i))
                    sess_list = sess_list[i:]
                    break

        # Group by subject
        sessions_by_subject = groupby_to_dict(
            sess_list, lambda x: x['subject_id'])

        # check for processor types that are new to this project
        assr_types = intf.list_project_assessor_types(project_id)
        has_new = (len(processor_types.difference(assr_types)) > 0)
        LOGGER.debug(assr_types)
        LOGGER.debug('has_new=' + str(has_new))

        for subject_id, sessions in list(sessions_by_subject.items()):
            # Get the cached session objects for this subject

            sessions_to_update = dict()

            # Check which sessions (if any) require an update:
            for sess_info in sessions:
                if has_new:
                    # Don't skip any sessions
                    pass
                elif lastrun:
                    last_mod = datetime.strptime(
                        sess_info['last_modified'][0:19], UPDATE_FORMAT)

                    if last_mod < lastrun:
                        mess = "+ Session %s:skipping not modified since last run, last_mod=%s, last_run=%s"
                        LOGGER.info(mess % (sess_info['label'], str(last_mod),
                                            str(lastrun)))
                        continue

                elif lastmod_delta:
                    last_mod = datetime.strptime(
                        sess_info['last_modified'][0:19], UPDATE_FORMAT)
                    now_date = datetime.today()
                    if now_date > last_mod + lastmod_delta:
                        mess = "+ Session %s:skipping not modified within delta, last_mod=%s"
                        LOGGER.info(mess % (sess_info['label'], str(last_mod)))
                        continue
                    else:
                        LOGGER.info('+ Session {}:modified, last_mod={}'.format(
                            sess_info['label'], str(last_mod)))

                # Append session to list of sessions to update
                sessions_to_update[sess_info['ID']] = sess_info

            if len(sessions_to_update) == 0:
                continue

            # build a full list of sessions for the subject: they may be needed
            # even if not all sessions are getting updated
            mess = "+ Subject %s: loading XML for %s session(s)..."
            LOGGER.info(mess % (sessions[0]['subject_label'], len(sessions)))
            cached_sessions = [XnatUtils.CachedImageSession(
                intf, x['project_label'], x['subject_label'],
                x['session_label']) for x in sessions]

            if len(cached_sessions) > 1:
                cached_sessions = sorted(
                    cached_sessions,
                    key=lambda s: s.creation_timestamp(), reverse=True)

            # update each of the sessions that require it
            for sess_info in list(sessions_to_update.values()):
                try:
                    # TODO: BenM - ensure that this code is robust to subjects
                    # without sessions and sessions without assessors / scans
                    mess = "+ Session %s: building..."
                    LOGGER.info(mess % sess_info['label'])
                    self.build_session(
                        intf, sess_info, auto_procs, exp_mods, scan_mods,
                        sessions=cached_sessions)
                except Exception as E:
                    err1 = 'Caught exception building sessions %s'
                    err2 = 'Exception class %s caught with message %s'
                    LOGGER.critical(err1 % sess_info['session_label'])
                    LOGGER.critical(err2 % (E.__class__, str(E)))
                    LOGGER.critical(traceback.format_exc())

        if not sessions_local or sessions_local.lower() == 'all':
            # Modules after run
            LOGGER.debug('* Modules Afterrun')
            try:
                self.module_afterrun(intf, project_id)
            except Exception as E:
                err2 = 'Exception class %s caught with message %s'
                LOGGER.critical('Caught exception after running modules')
                LOGGER.critical(err2 % (E.__class__, str(E)))
                LOGGER.critical(traceback.format_exc())

    def build_project_subjgenproc(self, xnat, project, includesubj=None):
        """
            Build the project

            :param xnat: pyxnat.Interface object
            :param project: project ID on XNAT
            :param includesubj: specific subjects to build, otherwise all
            :return: None
        """
        LOGFORMAT = '%(asctime)s:%(levelname)s:%(module)s:%(message)s'
        stdouthandler = logging.StreamHandler(sys.stdout)
        stdouthandler.setFormatter(logging.Formatter(LOGFORMAT))
        LOGGER.addHandler(stdouthandler)
        LOGGER.setLevel(logging.DEBUG)

        pdata = {}
        pdata['name'] = project
        pdata['scans'] = XnatUtils.load_scan_data(xnat, [project])
        pdata['assessors'] = XnatUtils.load_assr_data(xnat, [project])
        pdata['sgp'] = XnatUtils.load_sgp_data(xnat, project)

        LOGGER.debug('calling build_sgp_processors')
        self.build_sgp_processors(xnat, pdata, includesubj)

    def build_sgp_processors(self, xnat, project_data, includesubj=None):
        project = project_data['name']
        sgp_processors = self.get_subjgenproc_processors(project)
        subjects = project_data['sgp'].SUBJECT.unique()

        # Filter list if specified
        if includesubj:
            LOGGER.debug('no subjects specified, including all')
            subjects = [x for x in subjects if x in includesubj]

        if len(sgp_processors) == 0:
            LOGGER.debug('no sgp processors')
            return

        for subj in sorted(subjects):
            for processor in sgp_processors:
                # Get list of inputs sets (not yet matched with existing)
                inputsets = processor.parse_subject(subj, project_data)

                for inputs in inputsets:
                    if inputs == {}:
                        # print('empty set, skipping')
                        return

                    # Get(create) assessor with given inputs and proc type
                    # TODO: extract subject data only
                    (assr, info) = processor.get_assessor(
                        xnat, subj, inputs, project_data)

                    # TODO: apply reproc or rerun if needed
                    # (assr,info) = undo_processing()
                    # (assr,info) = reproc_processing()

                    if info['PROCSTATUS'] in [task.NEED_TO_RUN, task.NEED_INPUTS]:
                        # print('building task')
                        (assr, info) = self.build_task(
                            assr, info, processor, project_data)

                        # print('assr after=', info)
                    else:
                        LOGGER.info('already built:{}'.format(info['ASSR']))

    def build_task(self, assr, info, processor, project_data):
        resdir = self.resdir
        old_proc_status = info['PROCSTATUS']
        old_qc_status = info['QCSTATUS']
        jobdir = self.root_job_dir

        try:
            cmds = processor.build_cmds(
                assr,
                info,
                project_data,
                jobdir,
                resdir)

            batch_file = self.batch_path(info['ASSR'])
            outlog = self.outlog_path(info['ASSR'])

            batch = cluster.PBS(
                batch_file,
                outlog,
                cmds,
                processor.walltime_str,
                processor.memreq_mb,
                processor.ppn,
                processor.env,
                self.job_email,
                self.job_email_options,
                self.job_rungroup,
                self.xnat_host,
                processor.job_template)

            LOGGER.info('writing:' + batch_file)
            batch.write()

            # Set new statuses to be updated
            new_proc_status = task.JOB_RUNNING
            new_qc_status = task.JOB_PENDING

            # Write processor spec file for version 3
            try:
                LOGGER.debug('writing processor spec file')
                filename = self.processor_spec_path(info['ASSR'])
                mkdirp(os.path.dirname(filename))
                processor.write_processor_spec(filename)
            except AttributeError as err:
                # older processor does not have version
                LOGGER.debug('procyamlversion not found'.format(err))

        except task.NeedInputsException as e:
            new_proc_status = task.NEED_INPUTS
            new_qc_status = e.value
        except task.NoDataException as e:
            new_proc_status = task.NO_DATA
            new_qc_status = e.value

        # Update on xnat
        if new_proc_status != old_proc_status:
            assr.attrs.set(
                'proc:subjgenprocdata/procstatus', new_proc_status)

        if new_qc_status != old_qc_status:
            assr.attrs.set(
                'proc:subjgenprocdata/validation/status', new_qc_status)

        # Update local info
        info['PROCSTATUS'] = new_proc_status
        info['QCSTATUS'] = new_qc_status

        return (assr, info)

    # TODO:BenM/assessor_of_assessor/modify from here for one to many
    # processor to assessor mapping
    def build_session(self, intf, sess_info, auto_proc_list,
                      sess_mod_list, scan_mod_list,
                      sessions):
        """
        Build a session

        :param intf: pyxnat.Interface object
        :param sess_info: python dictionary from XnatUtils.list_sessions method
        :param auto_proc_list: list of processors running
        :param sess_mod_list: list of modules running on a session
        :param scan_mod_list: list of modules running on a scan
        :return: None
        """
        csess = find_with_pred(
            sessions, lambda s: sess_info['label'] == s.session_id())

        init_timestamp = csess.cached_timestamp

        # Create log file for this build of this session
        now_time = datetime.strftime(datetime.now(), '%Y%m%d-%H%M%S')
        sess_label = csess.label()
        tmp_dir = tempfile.mkdtemp()
        tmp_name = '{}_build_log-{}.txt'.format(sess_label, now_time)
        tmp_file = os.path.join(tmp_dir, tmp_name)
        handler = logging.FileHandler(tmp_file, 'w')
        handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s'))
        LOGGER.addHandler(handler)

        if sess_mod_list or scan_mod_list:
            # Modules
            mod_count = 0
            while mod_count < 3:
                mess = """== Build modules (count:{count}) =="""
                LOGGER.debug(mess.format(count=mod_count))
                if sess_mod_list:
                    self.build_session_modules(intf, csess, sess_mod_list)
                if scan_mod_list:
                    for cscan in csess.scans():
                        LOGGER.debug('+SCAN: ' + cscan.info()['scan_id'])
                        self.build_scan_modules(intf, cscan, scan_mod_list)

                reloaded = csess.refresh()
                if not reloaded:
                    break

                mod_count += 1

        # Auto Processors
        if auto_proc_list:
            LOGGER.debug('== Build auto processors ==')
            self.build_auto_processors(csess, auto_proc_list, sessions)

        # Close sess log
        LOGGER.handlers.pop()

        # Upload build log only if session was changed
        csess.refresh()
        final_timestamp = csess.cached_timestamp
        LOGGER.debug('initial timestamp={}, final timestamp={}'.format(
            init_timestamp, final_timestamp))
        if final_timestamp > init_timestamp:
            res_obj = csess.full_object().resource('BUILD_LOGS')
            LOGGER.debug('uploading session log:' + tmp_file)
            XnatUtils.upload_file_to_obj(tmp_file, res_obj)
        else:
            LOGGER.debug('session not modified, not uploading build log')

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
                    LOGGER.critical(err2 % (E.__class__, str(E)))
                    LOGGER.critical(traceback.format_exc())

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
                    LOGGER.critical(err2 % (E.__class__, str(E)))
                    LOGGER.critical(traceback.format_exc())

    def build_auto_processors(self, csess, auto_proc_list, sessions):
        """ Build yaml-based processors.

        :param xnat: pyxnat.Interface object
        :param csess: CachedObject for Session (XnatUtils)
        :param auto_proc_list: list of yaml processors
        :return: None
        """
        # sess_info = csess.info()
        xnat_session = csess.full_object()

        for auto_proc in auto_proc_list:
            # return a mapping between the assessor input sets and existing
            # assessors that map to those input sets

            # BDB 6/5/21
            # For now, we will not process pet sessions here, but will
            # include them as additional params for mr sessions.
            if csess.datatype() == 'xnat:petSessionData':
                LOGGER.debug('pet session, skipping auto processors')
                continue
            else:
                pets = [x for x in sessions if x.datatype() == 'xnat:petSessionData']
                mrs = [x for x in sessions if x.datatype() != 'xnat:petSessionData']

            mapping = auto_proc.parse_session(csess, mrs, pets)

            if mapping is None:
                continue

            for inputs, p_assrs in mapping:
                if len(p_assrs) == 0:
                    assessor = auto_proc.create_assessor(
                        xnat_session, inputs, relabel=True)
                    assessors = [(
                        assessor, assessor.label(),
                        task.NEED_TO_RUN, task.DOES_NOT_EXIST)]

                    csess.refresh()
                else:
                    assessors = []
                    for p in p_assrs:
                        # BDB 6/5/21 is there ever more than one assessor here?
                        info = p.info()
                        procstatus = info['procstatus']
                        qcstatus = info['qcstatus']
                        assessors.append((
                            p.full_object(), p.label(), procstatus, qcstatus))

                for assessor in assessors:
                    procstatus = assessor[2]
                    qcstatus = assessor[3]
                    if task_needs_to_run(procstatus, qcstatus):
                        xtask = XnatTask(auto_proc, assessor[0], self.resdir,
                                         os.path.join(self.resdir, 'DISKQ'))

                        if task_needs_status_update(qcstatus):
                            xtask.update_status()

                        LOGGER.debug('building task: ' + xtask.assessor_label)
                        (proc_status, qc_status) = xtask.build_task(
                            assessor[0], sessions,
                            self.root_job_dir,
                            self.job_email,
                            self.job_email_options,
                            self.job_rungroup)
                        deg = 'proc_status=%s, qc_status=%s'
                        LOGGER.debug(deg % (proc_status, qc_status))

                        # Refresh the cached session since we just modified it
                        csess.refresh()
                    else:
                        # TODO: check that it actually exists in QUEUE
                        LOGGER.debug('already built: ' + assessor[1])

    def batch_path(self, assessor_label):
        return os.path.join(
            self.resdir,
            'DISKQ',
            'BATCH',
            '{}.slurm'.format(assessor_label))

    def outlog_path(self, assessor_label):
        return os.path.join(
            self.resdir,
            'DISKQ',
            'OUTLOG',
            '{}.txt'.format(assessor_label))

    def processor_spec_path(self, assessor):
        return os.path.join(self.resdir, 'DISKQ', 'processor', assessor)

    def get_subjgenproc_processors(self, project):
        # Get the processors for this project
        proc = self.project_sgp_processors.get(project, [])

        # Filter to only include subjgenproc
        # proc = [x for x in proc if x.xsitype == 'proc:subjgenprocdata']

        return proc

    def set_subjgenproc_processors(self, project, processors):
        # Get the processors for this project
        self.sgp_processors[project] = processors

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
                LOGGER.critical(err2 % (E.__class__, str(E)))
                LOGGER.critical(traceback.format_exc())

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
                LOGGER.critical(err2 % (E.__class__, str(E)))
                LOGGER.critical(traceback.format_exc())

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
                    list(self.project_sgp_processors.keys()) +
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
            success = lockfiles.lock_flagfile(flagfile)
            if not success:
                LOGGER.warn('failed to get lock. Already running.')
                exit(1)

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
            lockfiles.unlock_flagfile(flagfile)

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
        auto_procs = processors.processors_by_type(pp_dict)

        # Get lists of assessors for this project
        assr_list = self.get_assessors_list(xnat, project_id, sessions_local)

        # Match each assessor to a processor, get a task, and add to list
        for assr_info in assr_list:
            if is_valid_assessor(assr_info):
                cur_task = self.generate_task(xnat, assr_info, auto_procs)
                if cur_task:
                    task_list.append(cur_task)

        return task_list

    @staticmethod
    def match_proc(assr_info, auto_proc_list):
        """
        Check if an assessor is a match with the processors

        :param assr_info: dictionary containing the assessor info
                          (See XnatUtils.list_assessors)
        :param auto_proc_list: list of processors running
        :return: processor if found, None otherwise
        """
        # Look for a match in yaml processors
        for auto_proc in auto_proc_list:
            if auto_proc.xsitype == assr_info['xsiType'] and \
                    auto_proc.name == assr_info['proctype']:
                return auto_proc

        return None

    def generate_task(self, xnat, assr_info, auto_proc_list):
        """
        Generate a task for the assessor in the info

        :param xnat: pyxnat.Interface object
        :param assr_info: dictionary containing the assessor info
                          (See XnatUtils.list_assessors)
        :param auto_proc_list: list of yaml processors
        :return: task if processor and assessor match, None otherwise
        """
        task_proc = self.match_proc(assr_info, auto_proc_list)

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
            cur_task = Task(task_proc, assr, self.resdir)
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
        assr_list = xnat.list_project_assessors(project_id)

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
        list_sessions = xnat.get_sessions_minimal(project_id)

        if slocal and slocal.lower() != 'all':
            # filter the list and keep the match between both list:
            val = slocal.split(',')
            list_sessions = list(
                [x for x in list_sessions if x['label'] in val])
            if not list_sessions:
                warn = 'No session from XNAT matched the sessions given: %s .'
                LOGGER.warn(warn % slocal)

        # TODO: sort by last modified
        sorted_list = list_sessions
        new_sessions_label = [sess['label'] for sess in list_sessions]
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
    def has_new_processors(assessors, proc_types):
        """
        Method to check whether, given a list of assessors, there are processor
        types that are new relative to the list of assessors (the proc type
        doesn't appear in the set of assessor proc types).
        :param assessors: a list of assessors, typically from a session or
        subject
        :param proc_types: a set of processor types to check against assessors
        :return: Boolean indicating whether the proc_types set has proc types
        that aren't in the assessors list
        """
        assr_types = set(x['proctype'] for x in assessors)
        return len(proc_types.difference(assr_types)) > 0

# =============================================================================
def load_task_queue(resdir, status=None, proj_filter=None, sess_filter=None):
    """ Load the task queue for DiskQ"""
    task_list = list()
    diskq_dir = os.path.join(resdir, 'DISKQ')

    # TODO: handle subjgenproc assessors, conveniently it works implicitly, but
    # should also handle subject filters
    for t in os.listdir(os.path.join(diskq_dir, 'BATCH')):
        if proj_filter or sess_filter:
            assr = XnatUtils.AssessorHandler(t)
            if proj_filter and assr.get_project_id() not in proj_filter:
                LOGGER.debug('ignoring:' + t)
                continue

            if sess_filter and assr.get_session_label() not in sess_filter:
                LOGGER.debug('ignoring:' + t)
                continue

        LOGGER.debug('loading:' + t)
        task = ClusterTask(os.path.splitext(t)[0], resdir, diskq_dir)
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
