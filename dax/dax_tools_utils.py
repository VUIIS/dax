#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions used by dax_tools like in dax_upload/dax_test/dax_setup.
"""

from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
from builtins import filter
from builtins import input
from builtins import str
from builtins import zip
from builtins import range
from builtins import object

from collections import OrderedDict
import configparser
import csv
from datetime import datetime
from email.mime.text import MIMEText
import getpass
import glob
import imp
import itertools
import json
import logging
import os
import platform
import random
import readline
import shutil
import smtplib
import socket
import stat
import subprocess as sb
import sys
import time
import traceback

from multiprocessing import Pool

from . import bin
from . import launcher
from . import log
from . import modules
from . import processors
from . import task
from . import xnat_tools_utils
from . import XnatUtils
from . import assessor_utils
from . import yaml_doc
from .dax_settings import (DAX_Settings, DAX_Netrc, DEFAULT_DATATYPE,
                           DEFAULT_FS_DATATYPE)
from .errors import (DaxUploadError, AutoProcessorError, DaxSetupError,
                     DaxError, DaxNetrcError)

from .task import (READY_TO_COMPLETE, COMPLETE, UPLOADING, JOB_FAILED,
                   JOB_PENDING, NEEDS_QA)
from .task import ClusterTask
from .XnatUtils import XnatUtilsError
from .version import VERSION as __version__
from .git_revision import git_revision as __git_revision__


# Global Variables
LOGGER = logging.getLogger('dax')


# Global variables for setup:
def complete(text, state):
    """Function to help tab completion path when using dax_setup."""
    return (glob.glob(text + '*') + [None])[state]


readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

BASH_PROFILE_XNAT = """# Xnat Host for default dax executables:
{export_cmd}
"""

ADMIN_DEFAULTS = OrderedDict([
    ('user_home', os.path.expanduser('~')),
    ('admin_email', ''),
    ('smtp_host', ''),
    ('smtp_from', ''),
    ('smtp_pass', ''),
    ('xsitype_include', 'proc:genProcData')])

CLUSTER_DEFAULTS = OrderedDict([
    ('cmd_submit', 'qsub'),
    ('prefix_jobid', ''),
    ('suffix_jobid', ''),
    ('cmd_count_nb_jobs', ''),
    ('cmd_get_job_status', ''),
    ('queue_status', ''),
    ('running_status', ''),
    ('complete_status', ''),
    ('cmd_get_job_memory', ''),
    ('cmd_get_job_walltime', ''),
    ('cmd_get_job_node', ''),
    ('job_extension_file', '.pbs'),
    ('job_template', ''),
    ('email_opts', 'a'),
    ('gateway', socket.gethostname()),
    ('root_job_dir', '/tmp'),
    ('queue_limit', '400'),
    ('results_dir', os.path.join(os.path.expanduser('~'),
                                 'RESULTS_XNAT_SPIDER')),
    ('max_age', '14'),
    ('launcher_type', 'xnatq-combined'),
    ('skip_lastupdate', '')])

CODE_PATH_DEFAULTS = OrderedDict([
    ('processors_path', ''),
    ('spiders_path', ''),
    ('modules_path', '')])

DAX_MANAGER_DEFAULTS = OrderedDict([
    ('api_url', ''),
    ('api_key_dax', ''),
    ('project', 'dax_project'),
    ('settingsfile', 'dax_settings_full_path'),
    ('masimatlab', 'dax_masimatlab'),
    ('tmp', 'dax_tmp_directory'),
    ('logsdir', 'dax_logs_path'),
    ('user', 'dax_cluster_user'),
    ('gateway', 'dax_gateway'),
    ('email', 'dax_cluster_email'),
    ('queue', 'dax_queue_limit'),
    ('priority', 'dax_proj_order'),
    ('email_opts', 'dax_job_email_options'),
    ('dax_build_start_date', 'dax_build_start_date'),
    ('dax_build_end_date', 'dax_build_end_date'),
    ('dax_build_pid', 'dax_build_pid'),
    ('dax_update_tasks_start_date', 'dax_update_tasks_start_date'),
    ('dax_update_tasks_end_date', 'dax_update_tasks_end_date'),
    ('dax_update_tasks_pid', 'dax_update_tasks_pid'),
    ('dax_launch_start_date', 'dax_launch_start_date'),
    ('dax_launch_end_date', 'dax_launch_end_date'),
    ('dax_launch_pid', 'dax_launch_pid'),
    ('max_age', 'dax_max_age'),
    ('skip_lastupdate', 'dax_skip_lastupdate'),
    ('admin_email', 'dax_email_address')])

DEFAULTS = {'admin': ADMIN_DEFAULTS,
            'cluster': CLUSTER_DEFAULTS,
            'code_path': CODE_PATH_DEFAULTS,
            'dax_manager': DAX_MANAGER_DEFAULTS}

INI_HEADER = """;dax_settings.ini contains all the variables to set dax on your system.
;It contains 4 sections define by [].

;The first one is [admin] defining the High level admin information.
; E.g. email address. xsitype_include needs to define the datatypes for DAX
; (Default: proc:genProcData).

;The second is [cluster] for deep information about the cluster.
; This should include commands that are grid-specific to get job id,
; walltime usage etc. Additionally, there are several templates that
; needed to be specified. See readthedocs for a description.

;The third one is [code_path] for Python script extension information.
; To import in dax all the spiders, processors and modules from those folders.
; You don't have to set a path if you don't want to give those paths.

;The fourth and last one is [dax_manager] that defines the REDCap
; infrastructure (options). Dax_manager uses REDCap to automatically generate
; settings for project. This section will help you set the API for your redcap
; project and all the variable on REDCap. If you don't know anything about it
; Leave all attributes to defaults value.

"""

# Sentence to write when message prompt for user
OPTIONS_DESCRIPTION = {
    'user_home': {'msg': 'Please enter your home directory: ',
                  'is_path': True},
    'admin_email': {'msg': 'Please enter email address for admin. \
All emails will get sent here: ', 'is_path': False},
    'smtp_from': {'msg': 'Please enter an email address where emails \
should be sent from: ', 'is_path': False},
    'smtp_host': {'msg': 'Please enter the SMTP host associated to your \
email address: ', 'is_path': False},
    'smtp_pass': {'msg': 'Please enter the password associated to your \
email address: ', 'is_path': False, 'confidential': True},
    'xsitype_include': {'msg': 'Please enter the xsitypes you would like DAX \
to access in your XNAT instance: ', 'is_path': False},
    'cmd_submit': {'msg': 'What command is used to submit your batch file? \
[e.g., qsub, sbatch]: ', 'is_path': False},
    'prefix_jobid': {'msg': 'Please enter a string to print before the \
job id after submission: ', 'is_path': False},
    'suffix_jobid': {'msg': 'Please enter a string to print after the \
job id after submission: ', 'is_path': False},
    'cmd_count_nb_jobs': {'msg': 'Please enter the full path to text file \
containing the command used to count the number of jobs in the queue: ',
                          'is_path': True},
    'cmd_get_job_status': {'msg': 'Please enter the full path to text file \
containing the command used to check the running status of a job: ',
                           'is_path': True},
    'queue_status': {'msg': 'Please enter the string the job scheduler would \
use to indicate that a job is "in the queue": ', 'is_path': False},
    'running_status': {'msg': 'Please enter the string the job scheduler \
would use to indicate that a job is "running": ', 'is_path': False},
    'complete_status': {'msg': 'Please enter the string the job scheduler \
would use to indicate that a job is "complete": ', 'is_path': False},
    'cmd_get_job_memory': {'msg': 'Please enter the full path to the text \
file containing the command used to see how much memory a job used: ',
                           'is_path': True},
    'cmd_get_job_walltime': {'msg': 'Please enter the full path to the text \
file containing the command used to see how much walltime a job used: ',
                             'is_path': True},
    'cmd_get_job_node': {'msg': 'Please enter the full path to the text file \
containing the command used to see which node a job used: ',
                         'is_path': True},
    'job_extension_file': {'msg': 'Please enter an extension for the job \
batch file: ', 'is_path': False},
    'job_template': {'msg': 'Please enter the full path to the text file \
containing the template used to generate the batch script: ',
                     'is_path': True},
    'email_opts': {'msg': 'Please provide the options for the email \
notification for a job as defined by your grid scheduler: ', 'is_path': False},
    'gateway': {'msg': 'Please enter the hostname of the server \
to run dax on: ', 'is_path': False},
    'root_job_dir': {'msg': 'Please enter where the data should be stored \
on the node: ', 'is_path': True},
    'queue_limit': {'msg': 'Please enter the maximum number of jobs \
that should run at once: ', 'is_path': False},
    'results_dir': {'msg': 'Please enter directory where data will get \
copied to for upload: ', 'is_path': True},
    'max_age': {'msg': 'Please enter max days before re-running dax_build \
on a session: ', 'is_path': False},
    'launcher_type': {'msg': 'Please enter launcher type: ',
                      'is_path': False},
    'skip_lastupdate': {'msg': 'Do you want to skip last update?: ',
                        'is_path': False},
    'api_url': {'msg': 'Please enter your REDCap API URL: ',
                'is_path': False},
    'api_key_dax': {'msg': 'Please enter the key to connect to the \
DAX Manager REDCap database: ', 'is_path': False},
    'spiders_path': {'msg': 'Please enter Folder path where you store \
your spiders: ', 'is_path': True},
    'processors_path': {'msg': 'Please enter Folder path where you store \
your processors: ', 'is_path': True},
    'modules_path': {'msg': 'Please enter Folder path where you store \
your modules: ', 'is_path': True},
}

SGE_TEMPLATE = """#!/bin/bash
#$ -S /bin/sh
#$ -M ${job_email}
#$ -m ${job_email_options}
#$ -l h_rt=${job_walltime}
#$ -l tmem=${job_memory}M
#$ -l h_vmem=${job_memory}M
#$ -o ${job_output_file}
#$ -pe smp ${job_ppn}
#$ -j y
#$ -cwd
#$ -V
uname -a # outputs node info (name, date&time, type, OS, etc)
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=${job_ppn} #set the variable \
to use only the right amount of ppn
export OMP_NUM_THREADS=${job_ppn} #as previous line for openmp code
source ${job_env} #source the specified environement file
SCREEN=$$$$$$$$
SCREEN=${SCREEN:0:8}
echo 'Screen display number for xvfb-run' $SCREEN
xvfb-run --wait=5 \
-a -e /tmp/xvfb_$SCREEN.err -f /tmp/xvfb_$SCREEN.auth \
--server-num=$SCREEN \
--server-args="-screen 0 1920x1200x24 -ac +extension GLX" \
${job_cmds}\n"""

DEFAULT_SGE_DICT = {'cmd_submit': 'qsub',
                    'prefix_jobid': 'Your job ',
                    'suffix_jobid': '("',
                    'cmd_count_nb_jobs': 'expr `qstat -u $USER | wc -l` - 2\n',
                    'queue_status': 'qw',
                    'running_status': 'r',
                    'complete_status': '',
                    'cmd_get_job_memory': "echo ''\n",
                    'cmd_get_job_node': "echo ''\n",
                    'cmd_get_job_status': "qstat -u $USER | grep ${jobid} \
| awk {'print $5'}\n",
                    'cmd_get_job_walltime': "echo ''\n",
                    'job_extension_file': '.pbs',
                    'job_template': SGE_TEMPLATE,
                    'email_opts': 'a'}

SLURM_TEMPLATE = """#!/bin/bash
#SBATCH --mail-user=${job_email}
#SBATCH --mail-type=${job_email_options}
#SBATCH --nodes=1
#SBATCH --ntasks=${job_ppn}
#SBATCH --time=${job_walltime}
#SBATCH --mem=${job_memory}mb
#SBATCH -o ${job_output_file}

uname -a # outputs node info (name, date&time, type, OS, etc)
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=${job_ppn} #set the variable \
to use only the right amount of ppn
export OMP_NUM_THREADS=${job_ppn} #as previous line for openmp code
source ${job_env} #source the specified environement file
SCREEN=$$$$$$$$
SCREEN=${SCREEN:0:8}
echo 'Screen display number for xvfb-run' $SCREEN
xvfb-run --wait=5 \
-a -e /tmp/xvfb_$SCREEN.err -f /tmp/xvfb_$SCREEN.auth \
--server-num=$SCREEN \
--server-args="-screen 0 1920x1200x24 -ac +extension GLX" \
${job_cmds}\n"""

DEFAULT_SLURM_DICT = {'cmd_submit': 'sbatch',
                      'prefix_jobid': 'Submitted batch job ',
                      'suffix_jobid': '\n',
                      'cmd_count_nb_jobs': 'squeue -u masispider,vuiiscci \
--noheader | wc -l\n',
                      'queue_status': 'Q',
                      'running_status': 'R',
                      'complete_status': 'slurm_load_jobs error: Invalid job \
id specified\n',
                      'cmd_get_job_memory': "sacct -j ${jobid}.batch --format \
MaxRss --noheader | awk '{print $1+0}'\n",
                      'cmd_get_job_node': 'sacct -j ${jobid}.batch --format \
NodeList --noheader\n',
                      'cmd_get_job_status': 'slurm_load_jobs error: Invalid \
job id specified\n',
                      'cmd_get_job_walltime': 'sacct -j ${jobid}.batch \
--format CPUTime --noheader\n',
                      'job_extension_file': '.slurm',
                      'job_template': SLURM_TEMPLATE,
                      'email_opts': 'FAIL'}

MOAB_TEMPLATE = """#!/bin/bash
#PBS -M ${job_email}
#PBS -m ${job_email_options}
#PBS -l nodes=1:ppn=${job_ppn}
#PBS -l walltime=${job_walltime}
#PBS -l mem=${job_memory}mb
#PBS -o ${job_output_file}
#PBS -j y

uname -a # outputs node info (name, date&time, type, OS, etc)
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=${job_ppn} #set the variable \
to use only the right amount of ppn
export OMP_NUM_THREADS=${job_ppn} #as previous line for openmp code
source ${job_env} #source the specified environement file
SCREEN=$$$$$$$$
SCREEN=${SCREEN:0:8}
echo 'Screen display number for xvfb-run' $SCREEN
xvfb-run --wait=5 \
-a -e /tmp/xvfb_$SCREEN.err -f /tmp/xvfb_$SCREEN.auth \
--server-num=$SCREEN \
--server-args="-screen 0 1920x1200x24 -ac +extension GLX" \
${job_cmds}\n"""

DEFAULT_MOAB_DICT = {
    'cmd_submit': 'qsub',
    'prefix_jobid': '',
    'suffix_jobid': '.',
    'cmd_count_nb_jobs': 'qstat | grep $USER | wc -l\n',
    'queue_status': 'Q',
    'running_status': 'R',
    'complete_status': 'C',
    'cmd_get_job_memory': "rsh vmpsched 'tracejob -n ${numberofdays} \
${jobid}'2> /dev/null | awk -v FS='(resources_used.mem=|kb)' '{print $2}' \
| sort -u | tail -1\n",
    'cmd_get_job_node': "echo ''\n",
    'cmd_get_job_status': "qstat -f ${jobid} | grep job_state \
| awk {'print $3'}\n",
    'cmd_get_job_walltime': "rsh vmpsched 'tracejob -n ${numberofdays} \
${jobid}' 2> /dev/null | awk -v FS='(resources_used.walltime=|\n)' \
'{print $2}' | sort -u | tail -1\n",
    'job_extension_file': '.pbs',
    'job_template': MOAB_TEMPLATE,
    'email_opts': 'a'}

# Variables for upload
ERR_MSG = 'Error from XnatUtils when uploading: %s'
DAX_SETTINGS = DAX_Settings()
RESULTS_DIR = DAX_SETTINGS.get_results_dir()
JOB_EXTENSION_FILE = DAX_SETTINGS.get_job_extension_file()
DISKQ_DIR = os.path.join(RESULTS_DIR, 'DISKQ')
DISKQ_BATCH_DIR = os.path.join(DISKQ_DIR, 'BATCH')
_COMPLETE_FLAG_FILE = 'READY_TO_COMPLETE.txt'
SMTP_FROM = DAX_SETTINGS.get_smtp_from()
SMTP_HOST = DAX_SETTINGS.get_smtp_host()
SMTP_PASS = DAX_SETTINGS.get_smtp_pass()
_READY_FLAG_FILE = 'READY_TO_UPLOAD.txt'
_FAILED_FLAG_FILE = 'JOB_FAILED.txt'
_EMAILED_FLAG_FILE = 'ALREADY_SEND_EMAIL.txt'
_OUTLOG = 'OUTLOG'
_TRASH = 'TRASH'
_PBS = 'PBS'
_FLAG_FILES = 'FlagFiles'
_UPLOAD_SKIP_LIST = [_OUTLOG, _TRASH, _PBS, _FLAG_FILES]
FLAGFILE_TEMPLATE = os.path.join(RESULTS_DIR, _FLAG_FILES,
                                 'Process_Upload_running')
SNAPSHOTS_ORIGINAL = 'snapshot_original.png'
SNAPSHOTS_PREVIEW = 'snapshot_preview.png'
DEFAULT_HEADER = ['host', 'username', 'password', 'projects']

# Cmd:
GS_CMD = """gs -q -o {original} -sDEVICE=pngalpha -dLastPage=1 {assessor_path}\
/PDF/*.pdf"""
CONVERT_CMD = """convert {original} -resize x200 {preview}"""

# WARNING content for emails
WARNING_START_CONTENT = """
The following assessors already exist and the Spider try to upload files on \
existing files :
"""
WARNING_END_CONTENT = """
You should:
    - remove the assessor if you want to upload the data
    - set the status of the assessor to "uploading"
    - remove the data from the upload folder if you do not want to upload.
"""
WARNING_SUBJECT = 'ERROR/WARNING: dax_upload'

# Variables for testing
DAX_TEST_DIR = os.path.join(os.path.expanduser("~"), '.dax_test')

TD_INFO = """======================================================================
DAX TEST
----------------------------------------------------------------------
Platform  : {platform}
Python v. : {version}
Dax v.    : {dax_version}
XNAT host : {host}
Username  : {user}
======================================================================
Running test for dax files generated by user ...
----------------------------------------------------------------------
"""

TD_END = """
----------------------------------------------------------------------
ran {nb_test} test(s) in {time}s

{state}
"""

SETTINGS_DISPLAY = """  Xnat host: {host}
  Xnat user: {user}
  Projects Priority: {priority}
  Projects Processors: {pp}
  Projects Modules: {pm}
  Root Job Dir: {jobdir}
  Job email: {email}
  Email options: {email_opts}
  Queue limit: {limit}
  Maximum age session: {age}
"""

PROC_DISPLAY = """    *NAME: {name}
      SPIDER:
        Path: {spath}
        version: {version}
      XNAT:
        Host: {host}
        type: {xsitype}
        level: {level}
      CLUSTER:
        memory: {memory}
        walltime: {walltime}
        Number of cores: {ppn}
        Environment file: {env}
      OTHER ARGUMENTS:
{other}
"""
PROC_DEF_ARGS = ['name', 'xnat_host', 'xsitype', 'memreq_mb', 'walltime_str',
                 'ppn', 'env', 'spider_path', 'version']

MOD_DISPLAY = """    *NAME: {name}
      TEMP DIRECTORY: {temp_dir}
      REPORT EMAIL: {email}
      XNAT:
        level: {level}
      OTHER ARGUMENTS:
{other}
"""
MOD_DEF_ARGS = ['name', 'xnat_host', 'directory', 'email']

DEL_DW = "-----------------------------------------------------------------\
-----"
DEL_UP = "=================================================================\
====="


def upload_tasks(logfile, debug, upload_settings=None,
                 host=None, username=None, password=None,
                 projects=None, suffix=None, emailaddress=None,
                 uselocking=True):
    """
    Upload tasks from the queue folder.

    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param upload_settings: settings file (csv, py, json) to define
                            xnat host/project relationship.
    :param host: XNAT host
    :param username: XNAT username
    :param password: XNAT password
    :param suffix: suffix for flagfile
    :param emailaddress: email address for warnings
    :param projects: Project(s) to upload

    """
    bin.set_logger(logfile, debug)

    # Check if folders exist
    check_folders()
    flagfile = "%s%s.txt" % (FLAGFILE_TEMPLATE, suffix)

    # Load the settings for upload
    upload_settings = load_upload_settings(upload_settings, host, username,
                                           password, projects)
    print_upload_settings(upload_settings)
    # create the flag file showing that the spider is running
    if uselocking and is_dax_upload_running(flagfile):
        pass
    else:
        try:
            upload_results(upload_settings, emailaddress)
        finally:
            if uselocking:
                # remove flagfile
                os.remove(flagfile)


def testing(test_file, project, sessions, host=None, username=None, hide=False,
            do_not_remove=False, nb_sess=5):
    """
    Function to run test on some files for dax.

    :param test_file: file to test
    :param project: project ID on XNAT
    :param sessions: list of sessions to run on XNAT
    :param host: XNAT host
    :param username: XNAT username
    :param hide: Hide dax outputs in a logfile in ~/.dax_test/dax_test.log.
    :param do_not_remove: do not remove files generated
    :param nb_sess: number of sessions to process(default 5 maximum)
    """
    # Create test results class object:
    tests = test_results()

    # Load test_file:
    test_obj = load_test(test_file)

    if not test_obj:
        tests.inc_error()
    else:
        _host = host if host is not None else os.environ.get('XNAT_HOST', None)
        _user = username if username is not None else 'user in dax netrc file.'
        if isinstance(test_obj, launcher.Launcher):
            _host = test_obj.xnat_host
            _user = test_obj.xnat_user

        print(TD_INFO.format(platform=platform.system(),
                             version=platform.python_version(),
                             dax_version=__version__,
                             host=_host, user=_user))
        # set test object:
        tests.set_tobj(test_obj)

        # Make the temp dir:
        if not os.path.isdir(DAX_TEST_DIR):
            os.makedirs(DAX_TEST_DIR)

        # Set the log of any dax function to a temp file for user:
        if hide:
            logfile = os.path.join(DAX_TEST_DIR, 'dax_test.log')
        else:
            logfile = None
        log.setup_debug_logger('dax', logfile)

        with XnatUtils.get_interface(host=_host, user=username) as intf:
            tests.set_xnat(intf)
            tests.run_test(project, sessions, nb_sess)

    print(TD_END.format(nb_test=tests.get_number(),
                        time="%.3f" % tests.get_time(),
                        state=tests.get_test_state()))

    if do_not_remove:
        if 'OK' == tests.get_test_state()[:2]:
            shutil.rmtree(DAX_TEST_DIR)


def setup_dax_package():
    """ Setup dax package """
    print('########## DAX_SETUP ##########')
    print('Script to setup the ~/.dax_settings.ini files \
for your dax installation.\n')
    # Set xnat credentials if needed
    set_xnat_netrc()

    # Set the settings for dax
    dsh = DAX_Setup_Handler()

    if dsh.exists():
        print('Settings file ~/.dax_settings.ini found.\n')
        if not xnat_tools_utils.prompt_user_yes_no('Do you want to edit it?'):
            print('########## END ##########')
            sys.exit()

    dsh.config()
    dsh.write()

    print('\n0 error(s) -- dax_setup done.')
    print('########## END ##########')


# Functions for Uploading
def send_email(from_add, password, dests, subject, content, server):
    """
    Send email using the server/from/pws

    :param from_add: address to send the email from
    :param password: password for the email address
    :param dests: list of emails addresses to send to
    :param subject: subject for the email
    :param content: content of the email
    :param server: SMTP server used to send email.
    :return: None
    """
    # Create the container (outer) email message.
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = from_add
    msg['To'] = ','.join(dests)

    # Send the email via our own SMTP server.
    s_obj = smtplib.SMTP(server)
    s_obj.starttls()
    s_obj.login(from_add, password)
    s_obj.sendmail(from_add, dests, msg.as_string())
    s_obj.quit()


def send_warning_emails(warnings, emailaddress):
    """
    Send warning emails about the dax_upload queue

    :param warnings: list of warnings
    :param emailaddress: email address
    :return: None
    """
    if warnings and emailaddress:
        content = WARNING_START_CONTENT
        for warning in warnings:
            content += ' - %s\n' % (warning)
        content += WARNING_END_CONTENT
        if SMTP_FROM and SMTP_PASS and SMTP_HOST:
            send_email(SMTP_FROM, SMTP_PASS, emailaddress.split(','),
                       WARNING_SUBJECT, content, SMTP_HOST)


def check_folders():
    """
    Check that the default folders exist and if not create them

    :return: None
    """
    # make the directories if they don't exist:
    if not os.path.exists(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)
    if not os.path.exists(os.path.join(RESULTS_DIR, _OUTLOG)):
        os.mkdir(os.path.join(RESULTS_DIR, _OUTLOG))
    if not os.path.exists(os.path.join(RESULTS_DIR, _TRASH)):
        os.mkdir(os.path.join(RESULTS_DIR, _TRASH))
    if not os.path.exists(os.path.join(RESULTS_DIR, _PBS)):
        os.mkdir(os.path.join(RESULTS_DIR, _PBS))
    if not os.path.exists(os.path.join(RESULTS_DIR, _FLAG_FILES)):
        os.mkdir(os.path.join(RESULTS_DIR, _FLAG_FILES))


def select_assessor(xnat, assessor_dict):
    """
    Select the assessor pyxnat Eobject from the assessor dictionary information

    :param xnat: pyxnat.interface object
    :param assessor_dict: assessor dictionary
    :return: assessor pyxnat Eobject
    """
    return XnatUtils.select_obj(xnat,
                                assessor_dict['project_id'],
                                assessor_dict['subject_label'],
                                assessor_dict['session_label'],
                                assessor_id=assessor_dict['label'])


def is_dax_upload_running(flagfile):
    """
    Check if dax_upload is not already running on the station

    :return: True if dax_upload already running, False otherwise.
    """
    if os.path.exists(flagfile):
        LOGGER.warn('Upload already running.')
        return True
    else:
        f_obj = open(flagfile, 'w')
        today = datetime.now()
        datestr = "Date: %s%s%s_%s:%s:%s" % (str(today.year),
                                             str(today.month),
                                             str(today.day),
                                             str(today.hour),
                                             str(today.minute),
                                             str(today.second))
        f_obj.write(datestr + '\n')
        f_obj.close()
        LOGGER.debug('Flagfile created: %s with date: %s\n'
                     % (flagfile, datestr))
        return False


def get_assessor_dict(assessor_label, assessor_path):
    """
    Generate the dictionary for an assessor from the folder in the queue

    :param assessor_label: assessor label
    :param assessor_path: assessor path on the station
    :return: None
    """
    assessor_dict = dict()
    keys = ['project_id', 'subject_label', 'session_label', 'label',
            'proctype', 'path']
    labels = assessor_label.split('-x-')
    if len(labels) > 3:
        values = [labels[0], labels[1], labels[2], assessor_label, labels[-1],
                  assessor_path]
        assessor_dict = dict(list(zip(keys, values)))
    return assessor_dict


def get_assessor_list(projects):
    """
    Get the list of assessors labels to upload to XNAT from the queue folder.

    :param projects: list of projects to upload to XNAT
    :return: list of assessor to upload from upload folder
    """
    assessor_label_list = list()

    LOGGER.debug(' - Get Processes names from the upload folder...')
    # check all files/folder in the directory
    dirs = list(filter(os.path.isdir,
                       glob.glob(os.path.join(RESULTS_DIR, '*'))))
    dirs.sort(key=lambda x: os.path.getmtime(x))
    for assessor_label in dirs:
        assessor_label = os.path.basename(assessor_label)
        if assessor_label in _UPLOAD_SKIP_LIST:
            continue
        # If projects set, check that the project is in the list of projects
        # to upload to XNAT
        if projects and assessor_label.split('-x-')[0] not in projects:
            continue

        assessor_path = os.path.join(RESULTS_DIR, assessor_label)
        if not os.path.isdir(assessor_path):
            continue
        if os.path.exists(os.path.join(assessor_path, _EMAILED_FLAG_FILE)):
            continue
        rflag = os.path.join(assessor_path, _READY_FLAG_FILE)
        fflag = os.path.join(assessor_path, _FAILED_FLAG_FILE)
        cflag = os.path.join(assessor_path, _COMPLETE_FLAG_FILE)
        if (os.path.exists(rflag) or os.path.exists(fflag)) and \
           (not is_diskq_assessor(assessor_label) or os.path.exists(cflag)):
            # Passed all checks, so add it to upload list
            assessor_label_list.append(assessor_label)

    return assessor_label_list


def get_pbs_list(projects):
    """
    Get the list of PBS file to upload to XNAT.

    :param projects: list of projects to upload to XNAT
    :return: list of pbs file from the PBS folder
    """
    pbs_list = list()

    LOGGER.debug(' - Get the PBS for the processes...')
    # check all files/folder in the directory
    for pbs_name in os.listdir(os.path.join(RESULTS_DIR, _PBS)):
        # If projects set, check that the project is in the list of
        # projects to upload to XNAT
        if projects and pbs_name.split('-x-')[0] not in projects:
            continue

        pbs_file = os.path.join(RESULTS_DIR, _PBS, pbs_name)
        if os.path.isfile(pbs_file):
            pbs_list.append(pbs_name)

    return pbs_list


def get_version_assessor(assessor_path):
    """
    Get the version of the assessor that we are uploading from text file

    :param assessor_path: path for the assessor
    :return: version of the assessor from the version.txt file
    """
    version = '1.0.0'
    if os.path.exists(os.path.join(assessor_path, 'version.txt')):
        f_obj = open(os.path.join(assessor_path, 'version.txt'), 'r')
        version = f_obj.read().strip()
        f_obj.close()
    return version


def get_dax_docker_version_assessor(assessor_path):
    """
    Get the dax_docker_version of assessor we are uploading from text file

    :param assessor_path: path for the assessor
    :return: version of the assessor from the version.txt file
    """
    dax_docker_version = ''
    fpath = os.path.join(assessor_path, 'dax_docker_version.txt')

    try:
        with open(fpath, 'r') as f_obj:
            dax_docker_version = f_obj.read().strip()

    except IOError as e:
        LOGGER.warn('failed to read dax_docker_version:' + str(e))

    return dax_docker_version


def generate_snapshots(assessor_path):
    """
    Generate Snapshots from the PDF if it exists.

    :param assessor_path: path for the assessor
    :return: None
    """
    snapshot_dir = os.path.join(assessor_path, 'SNAPSHOTS')
    snapshot_original = os.path.join(snapshot_dir, SNAPSHOTS_ORIGINAL)
    snapshot_preview = os.path.join(snapshot_dir, SNAPSHOTS_PREVIEW)
    if not os.path.exists(snapshot_original) and\
       os.path.exists(os.path.join(assessor_path, 'PDF')):
        LOGGER.debug('    +creating original of SNAPSHOTS')
        if not os.path.exists(snapshot_dir):
            os.mkdir(snapshot_dir)
        # Make the snapshots for the assessors with ghostscript
        cmd = GS_CMD.format(original=snapshot_original,
                            assessor_path=assessor_path)
        os.system(cmd)
    # Create the preview snapshot from the original if Snapshots exist :
    if os.path.exists(snapshot_original):
        LOGGER.debug('    +creating preview of SNAPSHOTS')
        # Make the snapshot_thumbnail
        cmd = CONVERT_CMD.format(original=snapshot_original,
                                 preview=snapshot_preview)
        os.system(cmd)


def copy_outlog(assessor_dict, assessor_path):
    """
    Copy the oulog files to the assessor folder if we are uploading.

    :param assessor_dict: dictionary for the assessor
    :return: None
    """
    outlog_path = os.path.join(RESULTS_DIR, _OUTLOG,
                               assessor_dict['label'] + '.output')
    new_outlog_path = os.path.join(assessor_path, _OUTLOG,
                                   assessor_dict['label'] + '.output')
    if os.path.exists(outlog_path):
        os.makedirs(os.path.join(assessor_path, _OUTLOG))
        shutil.move(outlog_path, new_outlog_path)


def get_xsitype(assessor_dict):
    """
    Copy the outlog files to the assessor folder if we are uploading.

    :param assessor_dict: dictionary for the assessor
    :return: xsitype for the assessor_dict
    """
    proctype = assessor_dict['proctype']
    if proctype == 'FS':
        return DEFAULT_FS_DATATYPE
    else:
        return DEFAULT_DATATYPE


def is_complete(assessor_dict, assessor_path, procstatus):
    """
    Copy the oulog files to the assessor folder if we are uploading.

    :param assessor_dict: dictionary for the assessor
    :param procstatus: status to set for the assessor
    :return: True if the assessor is Complete, False otherwise
    """
    if procstatus == READY_TO_COMPLETE or procstatus == COMPLETE:
        eflag = os.path.join(assessor_path, _EMAILED_FLAG_FILE)
        open(eflag, 'w').close()
        LOGGER.warn('  -->Data already present on XNAT.\n')
        return True
    else:
        return False


def create_freesurfer_assessor(assessor_obj):
    """
    Create freesurfer specific assessor using the DEFAULT_FS_DATATYPE from dax

    :param assessor_obj: pyxnat assessor Eobject
    :return: None
    """
    # create the assessor and set the status
    assessor_obj.create(assessors=DEFAULT_FS_DATATYPE,
                        **{DEFAULT_FS_DATATYPE + '/fsversion': '0'})
    now = datetime.now()
    today = '%s-%s-%s-' % (str(now.year), str(now.month), str(now.day))

    assessor_obj.attrs.mset(
        {DEFAULT_FS_DATATYPE + '/validation/status': JOB_PENDING,
         DEFAULT_FS_DATATYPE + '/date': today})


def create_default_assessor(assessor_obj, proctype):
    """
    Create default assessor using the DEFAULT_DATATYPE from dax

    :param assessor_obj: pyxnat assessor Eobject
    :param proctype: proctype for the assessor
    :return: None
    """
    # Create the assessor and set attributes
    now = datetime.now()
    today = '%s-%s-%s-' % (str(now.year), str(now.month), str(now.day))

    assessor_obj.create(assessors=DEFAULT_DATATYPE)
    # Call mset to only make a single HTTP request
    assessor_obj.attrs.mset(
        {DEFAULT_DATATYPE + '/validation/status': JOB_PENDING,
         DEFAULT_DATATYPE + '/proctype': proctype,
         DEFAULT_DATATYPE + '/date': today})


def should_upload_assessor(assessor_obj, assessor_dict, assessor_path, version):
    """
    Check if the assessor is ready to be uploaded to XNAT

    :param assessor_obj: pyxnat assessor Eobject
    :param assessor_dict: assessor dictionary
    :param xsitype: xsitype for the assessor (fsData or proc:GenProcData, ...)
    :param version: version for the assessor
    :return: True if the assessor should be upload, False otherwise
    """
    if not assessor_obj.exists():
        return False
        # if xsitype == DEFAULT_FS_DATATYPE:
        #     create_freesurfer_assessor(assessor_obj)
        # else:
        #     create_default_assessor(assessor_obj, assessor_dict['proctype'])
    else:
        xsitype = assessor_obj.datatype()
        # Check if not already complete assessor
        procstatus = assessor_obj.attrs.get(xsitype + '/procstatus')
        if is_complete(assessor_dict, assessor_path, procstatus):
            return False
    # set the status to UPLOADING
    assessor_obj.attrs.mset({xsitype + '/procstatus': UPLOADING,
                             xsitype + '/procversion': version})
    return True


def upload_assessor(xnat, assessor_dict, assessor_path):
    """
    Upload results to an assessor

    :param xnat: pyxnat.Interface object
    :param assessor_dict: assessor dictionary
    :return: None
    """
    # get spiderpath from version.txt file:
    version = get_version_assessor(assessor_path)
    dax_docker_version = get_dax_docker_version_assessor(assessor_path)
    session_obj = XnatUtils.select_obj(xnat,
                                       assessor_dict['project_id'],
                                       assessor_dict['subject_label'],
                                       assessor_dict['session_label'])
    if not session_obj.exists():
        LOGGER.error('Cannot upload assessor, session does not exist.')
        return True

    # Select assessor
    assessor_dict =\
        assessor_utils.parse_full_assessor_name(os.path.basename(assessor_path))
    assessor_obj = session_obj.assessor(assessor_dict['label'])
    #xsitype = get_xsitype(assessor_dict)
    if should_upload_assessor(assessor_obj,
                              assessor_dict,
                              assessor_path,
                              version):
        xsitype = assessor_obj.datatype()
        # Before Upload
        generate_snapshots(assessor_path)
        copy_outlog(assessor_dict, assessor_path)

        # Upload the XML if FreeSurfer
        if xsitype == DEFAULT_FS_DATATYPE:
            xmlpath = os.path.join(assessor_path, 'XML')
            if os.path.exists(xmlpath):
                LOGGER.debug('    +setting XML for FreeSurfer')
                xml_files_list = os.listdir(xmlpath)
                if len(xml_files_list) != 1:
                    fpath = assessor_path
                    msg = 'cannot upload FreeSurfer assessor, \
unable to find XML file: %s'
                    LOGGER.error(msg % (fpath))
                    return
                xml_path = os.path.join(assessor_path, 'XML',
                                        xml_files_list[0])
                assessor_obj.create(xml=xml_path, allowDataDeletion=False)

        # Upload
        # for each folder=resource in the assessor directory
        for resource in os.listdir(assessor_path):
            resource_path = os.path.join(assessor_path, resource)
            # Need to be in a folder to create the resource :
            if os.path.isdir(resource_path):
                LOGGER.debug('    +uploading %s' % (resource))
                try:
                    upload_resource(assessor_obj, resource, resource_path)
                except Exception as e:
                    _msg = 'failed to upload, skipping assessor:{}:{}'.format(
                        resource_path, str(e))
                    LOGGER.error(_msg)
                    return

        # after Upload
        if is_diskq_assessor(os.path.basename(assessor_path)):
            # was this run using the DISKQ option
            # Read attributes
            ctask = ClusterTask(assessor_dict['label'], RESULTS_DIR, DISKQ_DIR)

            # Set on XNAT
            assessor_obj.attrs.mset({
                xsitype + '/procstatus': ctask.get_status(),
                xsitype + '/validation/status': NEEDS_QA,
                xsitype + '/jobid': ctask.get_jobid(),
                xsitype + '/jobnode': ctask.get_jobnode(),
                xsitype + '/memused': ctask.get_memused(),
                xsitype + '/walltimeused': ctask.get_walltime(),
                xsitype + '/jobstartdate': ctask.get_jobstartdate(),
                xsitype + '/dax_version': __version__,
                xsitype + '/dax_version_hash': __git_revision__,
                xsitype + '/dax_docker_version': dax_docker_version
            })

            # Delete the task from diskq
            ctask.delete()
        elif os.path.exists(os.path.join(assessor_path, _READY_FLAG_FILE)):
            assessor_obj.attrs.set(xsitype + '/procstatus', READY_TO_COMPLETE)
        else:
            assessor_obj.attrs.set(xsitype + '/procstatus', JOB_FAILED)

        # Remove the folder
        shutil.rmtree(assessor_path)

        return True

    return False


def is_diskq_assessor(assr_label):
    # Does a batch file exist for this assessor?
    afile = os.path.join(DISKQ_BATCH_DIR, assr_label + JOB_EXTENSION_FILE)
    return os.path.exists(afile)


def upload_resource(assessor_obj, resource, resource_path):
    """
    Upload a resource folder to an assessor

    :param assessor_obj: pyxnat assessor Eobject
    :param resource: resource to upload
    :param resource_path: resource path on the station
    :return: None
    """
    if resource == 'SNAPSHOTS':
        upload_snapshots(assessor_obj, resource_path)
    else:
        rfiles_list = os.listdir(resource_path)
        if not rfiles_list:
            LOGGER.warn('No files in {}'.format(resource_path))
        elif DAX_SETTINGS.get_use_reference():
            try:
                ref_path = get_reference_path(resource_path)
                XnatUtils.upload_reference(ref_path, assessor_obj, resource)
            except XnatUtilsError as err:
                raise err
        elif len(rfiles_list) > 1 or os.path.isdir(rfiles_list[0]):
            try:
                XnatUtils.upload_folder_to_obj(
                    resource_path, assessor_obj.out_resource(resource),
                    resource, removeall=True)
            except XnatUtilsError as err:
                print(ERR_MSG % err)
        # One or two file, let just upload them:
        else:
            fpath = os.path.join(resource_path, rfiles_list[0])
            try:
                XnatUtils.upload_file_to_obj(
                    fpath, assessor_obj.out_resource(resource), removeall=True)
            except XnatUtilsError as err:
                print(ERR_MSG % err)

def get_reference_path(resource_path):
    return resource_path.replace(
        DAX_SETTINGS.get_results_dir(),
        DAX_SETTINGS.get_reference_dir())

def upload_snapshots(assessor_obj, resource_path):
    """
    Upload snapshots to an assessor

    :param assessor_obj: pyxnat assessor Eobject
    :param resource_path: resource path on the station
    :return: None
    """
    # Remove the previous Snapshots:
    if assessor_obj.out_resource('SNAPSHOTS').exists:
        assessor_obj.out_resource('SNAPSHOTS').delete()
    original = os.path.join(resource_path, SNAPSHOTS_ORIGINAL)
    thumbnail = os.path.join(resource_path, SNAPSHOTS_PREVIEW)
    status = None
    try:
        status = XnatUtils.upload_assessor_snapshots(
            assessor_obj, original, thumbnail)
    except XnatUtilsError as err:
        print(ERR_MSG % err)

    if status:
        os.remove(original)
        os.remove(thumbnail)
    else:
        LOGGER.warn('No snapshots original or preview were uploaded')

    # Upload the rest of the files in snapshots
    if len(os.listdir(resource_path)) > 0:
        try:
            XnatUtils.upload_folder_to_obj(
                resource_path, assessor_obj.out_resource('SNAPSHOTS'),
                'SNAPSHOTS')
        except XnatUtilsError as err:
            print(ERR_MSG % err)

def upload_assessors(xnat, projects):
    """
    Upload all assessors to XNAT

    :param xnat: pyxnat.Interface object
    :param projects: list of projects to upload to XNAT
    :return: None
    """
    # Get the assessor label from the directory :
    assessors_list = get_assessor_list(projects)
    number_of_processes = len(assessors_list)
    warnings = list()

    num_threads = int(DAX_SETTINGS.get_upload_threads())

    print('Starting pool with: ' + str(num_threads) + ' threads')
    sys.stdout.flush()

    pool = Pool(processes=num_threads) 
    for index, assessor_label in enumerate(assessors_list):
        print(index)
        sys.stdout.flush()

        pool.apply_async(upload_thread,[xnat, index, assessor_label, number_of_processes])
    
    print('Waiting for pool to finish...')
    sys.stdout.flush()

    pool.close()
    pool.join()

    print('Pool finished')
    sys.stdout.flush()    

    return warnings

def upload_thread(xnat, index, assessor_label, number_of_processes):
    assessor_path = os.path.join(RESULTS_DIR, assessor_label)
    msg = "    *Process: %s/%s -- label: %s / time: %s"
    LOGGER.info(msg % (str(index + 1), str(number_of_processes),
                       assessor_label, str(datetime.now())))

    #assessor_dict = get_assessor_dict(assessor_label, assessor_path)
    assessor_dict = assessor_utils.parse_full_assessor_name(assessor_label)
    if assessor_dict:
        uploaded = upload_assessor(xnat, assessor_dict, assessor_path)
        if not uploaded:
            mess = """    - Assessor label : {label}\n"""
            warnings.append(mess.format(label=assessor_dict['label']))
    else:
        LOGGER.warn('     --> wrong label')

def upload_pbs(xnat, projects):
    """
    Upload all pbs files to XNAT

    :param xnat: pyxnat.Interface object
    :param projects: list of projects to upload to XNAT
    :return: None
    """
    pbs_list = get_pbs_list(projects)
    number_pbs = len(pbs_list)
    for index, pbsfile in enumerate(pbs_list):
        pbs_fpath = os.path.join(RESULTS_DIR, _PBS, pbsfile)
        mess = """   *Uploading PBS {index}/{max} -- File name: {file}"""
        LOGGER.info(mess.format(index=str(index + 1),
                                max=str(number_pbs),
                                file=pbsfile))
        assessor_label = os.path.splitext(pbsfile)[0]
        #assessor_dict = get_assessor_dict(assessor_label, 'none')
        assessor_dict = assessor_utils.parse_full_assessor_name(assessor_label)
        if not assessor_dict:
            LOGGER.warn('wrong assessor label for %s' % (pbsfile))
            os.rename(pbs_fpath, os.path.join(RESULTS_DIR, _TRASH, pbsfile))
        else:
            assessor_obj = select_assessor(xnat, assessor_dict)
            if not assessor_obj.exists():
                LOGGER.warn('assessor does not exist for %s' % (pbsfile))
                new_location = os.path.join(RESULTS_DIR, _TRASH, pbsfile)
                os.rename(pbs_fpath, new_location)
            else:
                resource_obj = assessor_obj.out_resource(_PBS)
                if resource_obj.exists():
                    label = assessor_dict['label']
                    msg = 'the PBS resource already exists for the assessor %s'
                    LOGGER.warn(msg % (label))
                    adir = os.path.join(RESULTS_DIR, assessor_dict['label'])
                    if os.path.isdir(adir):
                        msg = 'Copying the pbs file in the assessor folder...'
                        LOGGER.warn(msg)
                        pbs_folder = os.path.join(adir, _PBS)
                        if not os.path.exists(pbs_folder):
                            os.mkdir(pbs_folder)
                        os.rename(pbs_fpath, os.path.join(pbs_folder, pbsfile))
                    else:
                        LOGGER.warn('Copying the pbs file in the TRASH ...')
                        trash = os.path.join(RESULTS_DIR, _TRASH, pbsfile)
                        os.rename(pbs_fpath, trash)
                else:
                    # upload the file
                    try:
                        status = XnatUtils.upload_file_to_obj(pbs_fpath,
                                                              resource_obj)
                    except XnatUtilsError as err:
                        print(ERR_MSG % err)
                    if status:
                        os.remove(pbs_fpath)


def upload_outlog(xnat, projects):
    """
    Upload all outlog files to XNAT

    :param xnat: pyxnat.Interface object
    :param projects: list of projects to upload to XNAT
    :return: None
    """
    outlogs_list = os.listdir(os.path.join(RESULTS_DIR, _OUTLOG))
    if projects:
        outlogs_list = [logfile for logfile in outlogs_list
                        if logfile.split('-x-')[0] in projects]

    number_outlog = len(outlogs_list)
    for index, outlogfile in enumerate(outlogs_list):
        outlog_fpath = os.path.join(RESULTS_DIR, _OUTLOG, outlogfile)
        mess = """   *Checking OUTLOG {index}/{max} -- File name: {file}"""
        LOGGER.info(mess.format(index=str(index + 1),
                                max=str(number_outlog),
                                file=outlogfile))
        #assessor_dict = get_assessor_dict(outlogfile[:-7], 'none')
        assessor_label = os.path.splitext(outlogfile)[0]
        assessor_dict = assessor_utils.parse_full_assessor_name(assessor_label)
        if not assessor_dict:
            LOGGER.warn('     wrong outlog file. You should remove it')
        else:
            assessor_obj = select_assessor(xnat, assessor_dict)
            #xtp = get_xsitype(assessor_dict)
            if not assessor_obj.exists():
                msg = '     no assessor on XNAT -- moving file to trash.'
                LOGGER.warn(msg)
                new_location = os.path.join(RESULTS_DIR, _TRASH, outlogfile)
                os.rename(outlog_fpath, new_location)
            else:
                if assessor_obj.attrs.get(assessor_obj.datatype() + '/procstatus') == JOB_FAILED:
                    resource_obj = assessor_obj.out_resource(_OUTLOG)
                    if resource_obj.exists():
                        pass
                    else:
                        LOGGER.info('     uploading file.')
                        try:
                            status = XnatUtils.upload_file_to_obj(outlog_fpath,
                                                                  resource_obj)
                        except XnatUtilsError as err:
                            print(ERR_MSG % err)
                        if status:
                            os.remove(outlog_fpath)


def new_upload_results(upload_settings, emailaddress):

    # get the list of assessors from the results directory
    if len(os.listdir(RESULTS_DIR)) == 0:
        LOGGER.warn('No data to be uploaded.\n')
        sys.exit()

    warnings = list()

    for project in upload_settings:
        try:
            with XnatUtils.get_interface(host=project['host'],
                                         user=project['username'],
                                         pwd=project['password']) as intf:
                LOGGER.info('=' * 60)

                assessors = get_assessor_list(project['projects'])
                x = [assessor_utils.parse_full_assessor_name(a)
                     for a in assessors]

                # create a nested dictionary of assessor result directories by
                # project id then subject label then session label
                z = {}
                for a in x:
                    if not a['project_id'] in z:
                        z[a['project_id']] = dict()
                    zp = z[a['project_id']]

                    if not a['subject_label'] in zp:
                        zp[a['subject_label']] = dict()
                    zs = zp[a['subject_label']]

                    if not a['session_label'] in zs:
                        zs[a['session_label']] = list()
                    ze = zs[a['session_label']]

                    ze.append(a)


                for kp, vp in z.iteritems():
                    for ks, vs in vp.iteritems():
                        for ke, ve in vs.iteritems():
                            # handle all assessors from this session
                            session = intf.select_experiment(kp, ks, ke)
                            if not session.exists():
                                # flag the experiment as missing
                                LOGGER.warning(
                                    "session {}/{}/{} does not exist".format(
                                        kp, ks, ke
                                    )
                                )
                            else:
                                # handle assessors
                                for a in ve:
                                    print(a)
                                    assessor = intf.select_assessor(
                                        kp, ks, ke, a['label'])
                                    if not assessor.exists():
                                        # flag the assessor as missing
                                        LOGGER.warning(
                                            "assessor {}/{}/{}/{} does not exist".format(
                                                kp, ks, ke, a['label']
                                            )
                                        )
                                    else:
                                        # upload this assessor
                                        pass

        except Exception as e:
            LOGGER.error(e.msg)



def upload_results(upload_settings, emailaddress):
    """
    Main function to upload the results / PBS / OUTLOG of assessors
     from the queue folder

    :param upload_settings: dictionary defining the upload information
    :return: None
    """
    if len(os.listdir(RESULTS_DIR)) == 0:
        LOGGER.warn('No data need to be uploaded.\n')
        sys.exit()

    warnings = list()

    for upload_dict in upload_settings:
        try:
            with XnatUtils.get_interface(host=upload_dict['host'],
                                         user=upload_dict['username'],
                                         pwd=upload_dict['password']) as intf:
                LOGGER.info('='*50)
                proj_str = (upload_dict['projects'] if upload_dict['projects']
                            else 'all')
                LOGGER.info('Connecting to XNAT <%s>, upload for projects:%s' % 
                    (upload_dict['host'], proj_str))
                if not XnatUtils.has_dax_datatypes(intf):
                    msg = 'Error: dax datatypes are not installed on xnat <%s>.'
                    raise DaxUploadError(msg % (upload_dict['host']))

                # 1) Upload the assessor data
                # For each assessor label that need to be upload :
                LOGGER.info('Uploading results for assessors')
                if DAX_SETTINGS.get_use_reference():
                    LOGGER.info('using upload by reference, dir is:{}'.format(
                        DAX_SETTINGS.get_reference_dir()))

                warnings.extend(upload_assessors(intf, upload_dict['projects']))

                # 2) Upload the PBS files
                # For each file, upload it to the PBS resource
                LOGGER.info('Uploading PBS files ...')
                upload_pbs(intf, upload_dict['projects'])

                # 3) Upload the OUTLOG files not uploaded with processes
                LOGGER.info('Checking OUTLOG files for JOB_FAILED jobs ...')
                upload_outlog(intf, upload_dict['projects'])
        except DaxNetrcError as e:
            msg = e.msg
            LOGGER.error(e.msg)


    send_warning_emails(warnings, emailaddress)


def load_upload_settings(f_settings, host, username, password, projects):
    """
    Function to parse arguments base on argparse

    :param f_settings: file to define the settings for uploading
    :param host: XNAT host
    :param username: XNAT username
    :param password: XNAT password
    :param projects: XNAT list of projects

    :return: list of dictionaries info_dict
       info_dict for the host [key:value]:
        host : string for XNAT host
        username : string for XNAT username
        password : string for XNAT password
          (can be the environment variable containing the value)
        projects : list of projects to upload for the host
    """
    host_projs = list()
    # If settings file given, load it and use it:
    if f_settings is not None:
        up_file = os.path.abspath(f_settings)
        if not os.path.isfile(up_file):
            raise DaxError('No upload settings file found: %s' % up_file)
        if f_settings.endswith('.json'):
            with open(up_file) as data_file:
                host_projs = json.load(data_file)
        elif f_settings.endswith('.py'):
            settings = imp.load_source('settings', up_file)
            host_projs = settings.host_projects
        elif f_settings.endswith('.csv'):
            with open(up_file, 'rb') as csvfileread:
                csvreader = csv.reader(csvfileread, delimiter=',')
                for index, row in (csvreader):
                    if len(row) < 4:
                        raise DaxError("error: could not read the csv row. \
Missing args. 4 needed, %s found at line %s." % (str(len(row)), str(index)))
                    else:
                        if row != DEFAULT_HEADER:
                            host_projs.append(dict(list(zip(DEFAULT_HEADER,
                                                        row[:4]))))
        elif f_settings.endswith('.yaml'):
            doc = XnatUtils.read_yaml(f_settings)
            host_projs = doc.get('settings')
        else:
            raise DaxError("error: doesn't recognize the file format for the \
settings file. Please use either JSON/PYTHON/CSV format.")
    else:  # if not file, use the environment variables and options
        _host = os.environ['XNAT_HOST']
        username = None
        password = None
        if host:
            _host = host
        if projects:
            projects = projects.split(',')
        else:
            projects = []
        if username:
            username = username
            if not password:
                MSG = "Please provide the password for user <%s> on xnat(%s):"
                password = getpass.getpass(prompt=MSG % (username, _host))
                if not password:
                    raise DaxError('error: the password entered was empty. \
please provide a password')
            elif password in os.environ:
                password = os.environ[password]
            else:
                password = password
        else:
            netrc_obj = DAX_Netrc()
            username, password = netrc_obj.get_login(_host)
        host_projs.append(dict(list(zip(DEFAULT_HEADER, [_host, username,
                                                         password,
                                                         projects]))))
    return host_projs


def print_upload_settings(upload_settings):
    """
    Display Host/Username/Projects that will be used to upload data from
     the queue.

    :return: None
    """
    LOGGER.info('Upload Settings selected by user:')
    for info in upload_settings:
        proj_str = ','.join(info['projects']) if info['projects'] else 'all'
        user_str = info['username'] if info['username'] else ''
        msg = 'XNAT Host: %s -- Xnat Username: %s -- projects: %s'
        LOGGER.info(msg % (info['host'], user_str, proj_str))
    LOGGER.info('Upload Directory: %s ' % (RESULTS_DIR))


# Functions for testings:
class test_results(object):
    '''
    Class to keep tract of test results (number of test, fail, error, time)

    :param tobj: object to be tested by dax_test (processor/module/launcher)
    '''
    def __init__(self, tobj=None):
        # xnat connection:
        self.xnat = None
        # Default variables:
        self.nb_test = 0
        self.error = 0
        self.fail = 0
        self.warning = 0
        self.time = time.time()
        # User variable:
        self.tobj = tobj
        self.should_run = True
        self.launch_obj = None

    def set_tobj(self, tobj):
        """
        Setter for the test object

        :param tobj: test object
        :return: None
        """
        self.tobj = tobj

    def set_xnat(self, xnat):
        """
        Setter for the xnat interface

        :param xnat: pyxnat interface
        :return: None
        """
        self.xnat = xnat

    def run_test(self, project, sessions, nb_sess):
        """
        Run test

        :param project: project ID on XNAT
        :param sessions: list of sessions label on XNAT
        :param nb_sess: number of sessions to test
        :return: None
        """
        # Set the cobj:
        sessions = get_sessions_for_project(self.xnat, project, sessions,
                                            nb_sess)

        # Set the launcher_obj:
        if isinstance(self.tobj, processors.Processor) or \
           isinstance(self.tobj, processors.AutoProcessor):
            proj_proc = {project: [self.tobj]}
            proj_mod = {project: []}
            self.launch_obj = launcher.Launcher(
                proj_proc, proj_mod, priority_project=None,
                xnat_host=self.xnat.host)
        elif isinstance(self.tobj, modules.Module):
            # Set the cobj:
            proj_proc = {project: []}
            proj_mod = {project: [self.tobj]}
            self.launch_obj = launcher.Launcher(
                proj_proc, proj_mod, priority_project=None,
                xnat_host=self.xnat.host)
        elif isinstance(self.tobj, launcher.Launcher):
            self.launch_obj = self.tobj
        else:
            print('[ERROR] Obj can not be identified as a dax objects.')
            self.inc_error()
            self.should_run = False

        if self.should_run:
            if isinstance(self.tobj, processors.Processor) or \
               isinstance(self.tobj, processors.AutoProcessor):
                self.run_test_processor(project, sessions)
            elif isinstance(self.tobj, modules.Module):
                self.run_test_module(project, sessions)
            elif isinstance(self.tobj, launcher.Launcher):
                unique_list = list(set(
                    list(self.tobj.project_process_dict.keys()) +
                    list(self.tobj.project_modules_dict.keys())))
                if self.tobj.priority_project:
                    project_list = self.tobj.get_project_list(unique_list)
                else:
                    project_list = unique_list
                for project in project_list:
                    sessions = randomly_get_sessions(self.xnat, project,
                                                     nb_sess)
                    self.run_test_settings(project, sessions)

    def inc_warning(self):
        """
        Increase warning counter

        :return: None
        """
        self.warning += 1

    def inc_error(self):
        """
        Increase error counter

        :return: None
        """
        self.error += 1

    def inc_fail(self):
        """
        Increase fail counter

        :return: None
        """
        self.fail += 1

    def inc_test(self):
        """
        Increase test counter

        :return: None
        """
        self.nb_test += 1

    def get_time(self):
        """
        Return the time since the object was created

        :return: time in seconds
        """
        end = time.time()
        return end - self.time

    def get_test_state(self):
        """
        Return state of the test

        :return: None
        """
        if self.error > 0 or self.fail > 0:
            return ('FAILED (failures=%s, errors=%s, warnings=%s)'
                    % (str(self.fail), str(self.error), str(self.warning)))
        else:
            state = 'OK'
            tmp = '  (warnings=%s)'
            warning = tmp % str(self.warning) if self.warning != 0 else ''
            return state + warning

    def get_number(self):
        """
        Return Number of tests ran

        :return: int
        """
        return self.nb_test

    def set_proc_cobjs_list(self, proc_obj, project, sessions):
        """
        Method to get the list of Cached Objects for the project/sessions for a
        processor

        :param proc_obj: processor object
        :param project: XNAT project
        :param sessions: XNAT sessions
        :return: None
        """
        co_list = list()
        sess_list = self.xnat.get_sessions(project)
        sess_list = [sess for sess in sess_list if sess['label'] in sessions]

        # Loop through the sessions
        for sess in sess_list:
            csess = XnatUtils.CachedImageSession(self.intf, project,
                                                 sess['subject_label'],
                                                 sess['label'])
            if isinstance(proc_obj, processors.ScanProcessor):
                for cscan in csess.scans():
                    if proc_obj.should_run(cscan.info()):
                        co_list.append(cscan)
            elif isinstance(proc_obj, processors.SessionProcessor):
                co_list.append(csess)
            elif isinstance(proc_obj, processors.AutoProcessor):
                if proc_obj.type == 'session':
                    co_list.append(csess)
                else:
                    for cscan in csess.scans():
                        if proc_obj.should_run(cscan.info()):
                            co_list.append(cscan)

        if len(co_list) == 0:
            print("[WARNING] No scan found for the processor on scans.")
            self.inc_warning()

        return co_list

    def set_mod_cobjs_list(self, mod_obj, project, sessions):
        """
        Method to get the list of Cached Objects for the project/sessions for a
        processor

        :param mod_obj: processor object
        :param project: XNAT project
        :param sessions: XNAT sessions
        :return: None
        """
        co_list = list()
        sess_list = self.xnat.get_sessions(project)
        sess_list = [sess for sess in sess_list if sess['label'] in sessions]

        # Loop through the sessions
        for sess in sess_list:
            csess = XnatUtils.CachedImageSession(self.xnat, project,
                                                 sess['subject_label'],
                                                 sess['label'])
            if isinstance(mod_obj, modules.ScanModule):
                for cscan in csess.scans():
                    if mod_obj.needs_run(cscan, self.xnat):
                        co_list.append(cscan)
            elif isinstance(mod_obj, modules.SessionModule):
                if mod_obj.needs_run(csess, self.xnat):
                    co_list.append(csess)

        if len(co_list) == 0:
            print("[WARNING] No object found for the Module.")
            self.inc_warning()

        return co_list

    def test_has_inputs(self, project, sessions):
        """
        Method to test the has_inputs function

        :param project: XNAT project
        :param sessions: XNAT sessions
        :return: True if SUCCEEDED, False otherwise
        """
        # Test has_inputs for each session
        print_sub_test('test_has_inputs')

        # Loop through the sessions
        for cobj in self.set_proc_cobjs_list(self.tobj, project, sessions):
            cinfo = cobj.info()
            try:
                if isinstance(cobj, XnatUtils.CachedImageScan):
                    msg = "Processor.has_inputs(cobj) running on %s - %s - %s \
..."
                    print(msg % (project, cinfo['session_label'], cinfo['ID']))
                else:
                    msg = "Processor.has_inputs(cobj) running on %s - %s ..."
                    print(msg % (project, cinfo['session_label']))
                state, qcstatus = self.tobj.has_inputs(cobj)
                self.inc_test()
                qcstatus = qcstatus if qcstatus else task.JOB_PENDING
                if state == 0:
                    state = task.NEED_INPUTS
                elif state == 1:
                    state = task.NEED_TO_RUN
                elif state == -1:
                    state = task.NO_DATA
                else:
                    print("[FAIL] State return by Processor.has_inputs() \
unknown (-1/0/1): %s" % state)
                    self.inc_fail()
                    return False
                print("Outputs: state = %s and qcstatus = %s"
                      % (state, qcstatus))
            except Exception:
                print('[ERROR]')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=2, file=sys.stdout)
                self.inc_error()
                return False

        return True

    def test_dax_build(self, project, sessions):
        """
        Method to test a processor through dax

        :param project: XNAT project
        :param sessions: XNAT sessions
        :return: None
        """
        print_sub_test('test_dax_build')
        try:
            self.inc_test()
            print("dax_build on %s - %s ..." % (project, ','.join(sessions)))
            self.launch_obj.build('dax_test', project, ','.join(sessions))
            has_assessors = self.check_sessions(project, sessions)
            if has_assessors:
                print("\nbuild SUCCEEDED")
            else:
                self.inc_fail()
                print("\nbuild FAILED")
        except Exception:
            print('[ERROR]')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            self.inc_error()

    def check_sessions(self, project, sessions):
        """
        Method to test a processor through dax

        :param project: XNAT project
        :param sessions: XNAT sessions
        :return: True if the assessors have been created, False otherwise
        """
        if isinstance(self.tobj, processors.Processor):
            list_proc_obj = [self.tobj]
        elif isinstance(self.tobj, modules.Module):
            return True
        else:
            list_proc_obj = self.tobj.project_process_dict.get(project, list())

        for proc_obj in list_proc_obj:
            for cobj in self.set_proc_cobjs_list(proc_obj, project, sessions):
                cinfo = cobj.info()
                if isinstance(cobj, XnatUtils.CachedImageScan):
                    tmp = "%s-x-%s-x-%s-x-%s-x-%s"
                    assessor_label = tmp % (project,
                                            cinfo['subject_label'],
                                            cinfo['session_label'],
                                            cinfo['ID'],
                                            proc_obj.name)
                else:
                    tmp = "%s-x-%s-x-%s-x-%s"
                    assessor_label = tmp % (project,
                                            cinfo['subject_label'],
                                            cinfo['session_label'],
                                            proc_obj.name)
                assessor_obj = XnatUtils.select_assessor(self.xnat,
                                                         assessor_label)
                if not assessor_obj.exists():
                    print('[FAIL] Assessor %s did not get created on XNAT.'
                          % assessor_label)
                    return False
                else:
                    mget = assessor_obj.attrs.mget([
                        DEFAULT_DATATYPE + '/proctype',
                        DEFAULT_DATATYPE + '/procstatus',
                        DEFAULT_DATATYPE + '/validation/status',
                        DEFAULT_DATATYPE + '/date'])
                    msg = "Assessor %s: \n - proctype: %s\n - procstatus: %s\n\
 - qcstatus: %s\n - date: %s"
                    print(msg % (assessor_label, mget[0], mget[1], mget[2],
                                 mget[3]))
        return True

    def test_dax_launch(self, project, sessions):
        """
        Method to test a processor through dax

        :param project: XNAT project
        :param sessions: XNAT sessions
        :return: None
        """
        print_sub_test('test_dax_launch')
        try:
            self.inc_test()
            print("Launching tasks for %s - %s with writeonly ..."
                  % (project, ','.join(sessions)))
            tasks_list = self.launch_obj.get_tasks(
                self.xnat, self.all_tasks, [project], ','.join(sessions))
            for cur_task in tasks_list:
                cur_task.launch(self.launch_obj.root_job_dir,
                                self.launch_obj.job_email,
                                self.launch_obj.job_email_options,
                                self.launch_obj.xnat_host,
                                True, pbsdir=DAX_TEST_DIR)
            results = self.display_pbs_file(project, sessions)
            if results:
                print("launch SUCCEEDED")
            else:
                print("launch FAILED")
        except Exception:
            print('[ERROR]')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            self.inc_error()

    @staticmethod
    def all_tasks(_):
        """
        Check if a task is launchable

        :param assr_info: dictionary containing procstatus for the assessor
                          (not used)
        :return: True to take all assessor
        """
        return True

    def test_dax(self, project, sessions):
        """
        General Method to test all executables for dax

        :param project: XNAT project
        :param sessions: XNAT sessions
        :return: None
        """
        self.test_dax_build(project, sessions)
        if not isinstance(self.tobj, modules.Module):
            self.test_dax_launch(project, sessions)

    def test_pre_run(self):
        """
        Method to test pre run function for a module through dax

        :param project: XNAT Project
        :param sessions: XNAT Sessions
        :return: None
        """
        print_sub_test('test_pre_run')

        try:
            self.inc_test()
            print("Pre run ...")
            self.tobj.prerun()
            return True
        except Exception:
            print('[ERROR]')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            self.inc_error()
            return False

    def test_run(self, project, sessions):
        """
        Method to test run function for a module

        :param project: XNAT Project
        :param sessions: XNAT Sessions
        :return: None
        """
        print_sub_test('test_run')

        cobj_list = self.set_mod_cobjs_list(self.tobj, project, sessions)
        try:
            self.inc_test()
            print("Run on sessions: %s ..." % ','.join(sessions))
            for cobj in cobj_list:
                cinfo = cobj.info()
                self.tobj.run(cinfo, cobj.full_object())
                if isinstance(self.tobj, modules.SessionModule):
                    result = self.tobj.has_flag_resource(
                        cobj, self.tobj.mod_name)
                    if not result:
                        print("[FAIL] Session Module didn't create the \
flagfile for %s." % (cinfo['label']))

            return True
        except Exception:
            print('[ERROR]')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            self.inc_error()
            return False

    def test_after_run(self, project):
        """
        Method to test after run function for a module

        :param project: XNAT Project
        :return: None
        """
        print_sub_test('test_after_run')

        try:
            self.inc_test()
            print("After run ...")
            self.tobj.afterrun(self.xnat, project)
            return True
        except Exception:
            print('[ERROR]')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            self.inc_error()
            return False

    def run_test_processor(self, project, sessions):
        """
        Method to test a processor through dax

        :param project: XNAT Project
        :param sessions: XNAT Sessions
        :return: None
        """
        # display
        print_new_test(self.tobj.name)

        # Test has_inputs:
        result = self.test_has_inputs(project, sessions)
        if result:
            print("\nhas_inputs SUCCEEDED")
        else:
            print("\nhas_inputs FAILED")

        # Test dax functionalities:
        self.test_dax(project, sessions)

    def run_test_module(self, project, sessions):
        """
        Method to test a module through dax

        :param project: project on XNAT
        :param sessions: list of sessions label on XNAT
        :return: Number of test that ran, fail, error
        """
        # display
        print_new_test(self.tobj.mod_name)

        # Test has_inputs:
        if self.test_pre_run():
            print("prerun() SUCCEEDED")
        else:
            print("prerun() FAILED")

        if self.test_run(project, sessions):
            print("run() SUCCEEDED")
        else:
            print("run() FAILED")

        if self.test_after_run(project):
            print("afterrun() SUCCEEDED")
        else:
            print("afterrun() FAILED")

        # Test dax functionalities:
        self.test_dax(project, sessions)

    def run_test_settings(self, project, sessions):
        """
        Method to test a settings file through dax

        :param project: XNAT Project
        :param sessions: XNAT Sessions
        :return: Number of test that ran, fail, error
        """
        # print info settings:
        self.display_settings()

        # Test dax functionalities:
        self.test_dax(project, sessions)

    def display_pbs_file(self, project, sessions):
        """
        Function to display one of the pbs file created

        :param tests: tests_results object
        :param project: XNAT project
        :param sessions: XNAT sessions
        :return: True if PBS created, False if not.
        """
        pbs_files = list()
        # get a PBS file created:
        for sess in sessions:
            pbs_files.extend(glob.glob(os.path.join(DAX_TEST_DIR,
                             '%s-x-*-x-%s-x-*.pbs' % (project, sess))))

        # if empty raise Error
        if len(pbs_files) == 0:
            print('[ERROR] No PBS file generated in %s by dax_launch'
                  % DAX_TEST_DIR)
            self.inc_error()
            return False
        else:
            print('PBS Example:\n')
            print(open(pbs_files[0], "rb").read())
            return True

    def display_settings(self):
        """
        Function to display from the settings:
            - projects
            - processors and the default values
            - modules and the default values
            - launcher and the default values

        :return: None
        """
        proj_list = list()
        print('Settings arguments:')
        print_settings(self.launch_obj.__dict__)
        proj_mods = self.launch_obj.project_modules_dict
        proj_procs = self.launch_obj.project_process_dict
        proj_list.extend(list(proj_mods.keys()))
        proj_list.extend(list(proj_procs.keys()))
        print('\nList of XNAT projects : %s' % ','.join(list(set(proj_list))))

        for project in list(set(proj_list)):
            print(' - Project %s:' % project)
            print('  + Module(s) arguments:')
            if project in list(proj_mods.keys()) and \
               len(proj_mods[project]) > 0:
                for module in proj_mods[project]:
                    print_module(module)
            else:
                print('    No module set for the project.')
            print('\n  + Processor(s) arguments:')
            if project in list(proj_procs.keys()) and \
               len(proj_procs[project]) > 0:
                for processor in proj_procs[project]:
                    print_processor(processor)
            else:
                print('    No processor set for the project.')


def print_settings(settings_dict):
    """
    Display the settings informations

    :param settings_dict: dictionary containing the variables
      for the dax.launcher.Launcher object
    :return: None
    """
    print(SETTINGS_DISPLAY.format(
        host=settings_dict['xnat_host'],
        user=settings_dict['xnat_user'],
        priority=settings_dict['priority_project'],
        pp=settings_dict['project_process_dict'],
        pm=settings_dict['project_modules_dict'],
        jobdir=settings_dict['root_job_dir'],
        email=settings_dict['job_email'],
        email_opts=settings_dict['job_email_options'],
        limit=settings_dict['queue_limit'],
        age=settings_dict['max_age']))


def print_module(mod_obj):
    """
    Display the module informations

    :param mod_dict: dax.module.Module object
    :return: None
    """
    level = 'Scan' if isinstance(mod_obj, modules.ScanModule) else 'Session'
    mod_dict = mod_obj.__dict__
    other_args = ''
    for key, arg in list(mod_dict.items()):
        if key not in MOD_DEF_ARGS:
            other_args += "       %s: %s\n" % (key, str(arg).strip())
    print(MOD_DISPLAY.format(name=mod_dict['mod_name'],
                             temp_dir=mod_dict['directory'],
                             email=mod_dict['email'],
                             level=level,
                             other=other_args))


def print_processor(proc_obj):
    """
    Display the processor informations

    :param proc_obj: dax.processor.Processor object
    :return: None
    """
    level = 'Session'
    if isinstance(proc_obj, processors.ScanProcessor):
        level = 'Scan'
    elif isinstance(proc_obj, processors.AutoProcessor):
        if proc_obj.type == 'scan':
            level = 'Scan'

    proc_dict = proc_obj.__dict__
    other_args = ''
    if proc_dict.get('xnat_host', None):
        host = proc_dict['xnat_host']
    else:
        host = 'using default XNAT_HOST'

    for key, arg in list(proc_dict.items()):
        if key not in PROC_DEF_ARGS:
            other_args += "       %s: %s\n" % (key, str(arg).strip())

    print(PROC_DISPLAY.format(name=proc_dict['name'],
                              spath=proc_dict['spider_path'],
                              version=proc_dict['version'],
                              host=host,
                              xsitype=proc_dict['xsitype'],
                              level=level,
                              memory=proc_dict['memreq_mb'],
                              walltime=proc_dict['walltime_str'],
                              ppn=proc_dict['ppn'],
                              env=proc_dict['env'],
                              other=other_args))


def randomly_get_sessions(xnat, project, nb_sess=5):
    """
    Retrieve nb_sess sessions label randomly from the test project on XNAT

    :param project: XNAT project
    :return: list of sessions label
    """
    sessions = list()
    list_sess = xnat.get_sessions(project)
    if len(list_sess) < int(nb_sess):
        sessions = [sess['label'] for sess in list_sess]
    else:
        for _ in range(int(nb_sess)):
            session_added = False
            while not session_added:
                random_index = random.randint(0, len(list_sess) - 1)
                if list_sess[random_index]['label'] not in sessions:
                    sessions.append(list_sess[random_index]['label'])
                    session_added = True

    return sessions


def is_python_file(filepath):
    """
    Check if a file is a python file using bash command file

    :param filepath: path to the file to test
    :return: True if it's a python file, False otherwise
    """
    file_call = '''file {fpath}'''.format(fpath=filepath)
    output = sb.check_output(file_call.split())
    if 'python' in output.lower():
        return True

    return False


def load_test(filepath):
    """
    Check if a file exists and if it's a python file

    :param filepath: path to the file to test
    :return: True the file pass the test, False otherwise
    """
    if not os.path.exists(filepath):
        print('[ERROR] %s does not exists.' % filepath)
        return None

    if filepath.endswith('yaml'):
        doc = XnatUtils.read_yaml(filepath)

        if 'projects' in list(doc.keys()):
            try:
                return bin.read_yaml_settings(filepath, LOGGER)
            except AutoProcessorError:
                print('[ERROR]')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=2, file=sys.stdout)
        else:
            # So far only auto processor:
            try:
                return processors.load_from_yaml(XnatUtils, filepath)
            except AutoProcessorError:
                print('[ERROR]')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=2, file=sys.stdout)
    elif filepath.endswith('.py') or is_python_file(filepath):
        test = imp.load_source('test', filepath)
        # Check if processor file
        try:
            return eval('test.{}()'.format(test.__processor_name__))
        except AttributeError:
            pass

        # Check if it's a settings file.py
        try:
            return test.myLauncher
        except AttributeError:
            pass

        # Check if it's a module
        try:
            return eval('test.{}()'.format(os.path.basename(filepath)[:-3]))
        except AttributeError:
            pass

        err = '[ERROR] Module or processor or myLauncher object NOT FOUND in \
the python file {}.'
        print(err.format(filepath))
        return None
    else:
        err = '[ERROR] {} format unknown. Please provide a .py or .yaml file.'
        print(err.format(filepath))
        return None


def print_new_test(name):
    """
    Print separation for new test

    :param name: name for the test
    :return: None
    """
    print('{}\nTest -- {} ...'.format(DEL_UP, name))


def print_sub_test(name):
    """
    Print separation for new test

    :param name: name for the method
    :return: None
    """
    print('\n{}\n + Testing method {} \n'.format(DEL_DW, name))


def get_sessions_for_project(xnat, project, sessions, nb_sess=5):
    """
    Return list of XNAT sessions (between 1-5) to test the object on them

    :param project: XNAT project
    :return: list of sessions label
    """
    # Set Sessions: If No sessions specified, select 5 random sessions for
    # testing:
    if sessions:
        sessions = sessions.split(',')
        if len(sessions) > 5:
            sessions = sessions[:5]
        elif len(sessions) <= 0:
            raise Exception('No sessions set for the test.')
        return sessions
    else:
        if nb_sess > 5:
            nb_sess = 5
        elif nb_sess <= 0:
            raise Exception('--nb_sess set with an interger smaller than 1. \
Please use at least one.')
        return randomly_get_sessions(xnat, project, nb_sess)


# Functions for setting:
class DAX_Setup_Handler(object):
    """DAX_Setup_Handler Class.

    Class to write the dax_settings.ini files required to run any
    dax executables.
    """

    def __init__(self):
        """Entry Point for DAX_Setup_Handler class."""
        # Set the settings_file
        self.settings_file = os.path.join(os.path.expanduser('~'),
                                          '.dax_settings.ini')

        # ConfigParser
        self.config_parser = configparser.SafeConfigParser(allow_no_value=True)

        # Set the configParser from init file or default value
        if os.path.isfile(self.settings_file):
            try:
                self.config_parser.read(self.settings_file)
            except configparser.MissingSectionHeaderError as MSHE:
                self._print_error_and_exit('Missing header bracket detected. \
Please check your ini file.\n', MSHE)
        else:  # set to default
            for section in sorted(DEFAULTS.keys()):
                self.config_parser.add_section(section)
                for option in list(DEFAULTS[section].keys()):
                    self.config_parser.set(section, option,
                                           DEFAULTS[section][option])

    def exists(self):
        """Check if ini file exists.

        :return: True if exists, False otherwise
        """
        return os.path.isfile(self.settings_file)

    def config(self):
        """Config the configParser for each section and ask user for value.

        Caller for all of the _get* methods.
        :return: True if using default settings, False otherwise
        """
        # For each section ask the user if he wants to edit it:
        print('Starting to config the dax_settings.ini file:')
        for section in self.config_parser.sections():
            sys.stdout.write('  - Section: %s\n' % section)
            qst = '    Do you want to set/modify the section [%s] in the \
settings file?' % section
            modify = xnat_tools_utils.prompt_user_yes_no(qst)
            if modify:
                self.config_section(section)

    def config_section(self, section):
        """Configure the section.

        :param section: name of the section
        :return: None
        """
        msg = "Do you want to use specific templates settings from DAX?"
        if section == 'cluster' and xnat_tools_utils.prompt_user_yes_no(msg):
            self._set_cluster_default()
        else:
            for option in self.config_parser.options(section):
                value = self._prompt(section, option)
                self.config_parser.set(section, option, value)

    def write(self):
        """Write config options to the ~/.dax_settings.ini file.

        :return: None
        """
        with open(self.settings_file, 'w+') as ini_f:
            ini_f.write(INI_HEADER)
            self.config_parser.write(ini_f)
        os.chmod(self.settings_file, stat.S_IWUSR | stat.S_IRUSR)

    def _prompt(self, section, option):
        """Method to prompt a user for an input for the option in the template.

        :param option: option name
        :return: String of the input
        """
        if option in list(OPTIONS_DESCRIPTION.keys()):
            if 'confidential' in list(OPTIONS_DESCRIPTION[option].keys()):
                msg = OPTIONS_DESCRIPTION[option]['msg']
                stdin = getpass.getpass(prompt=msg)
            else:
                stdin = input(OPTIONS_DESCRIPTION[option]['msg'])
            if OPTIONS_DESCRIPTION[option]['is_path'] and stdin:
                if stdin.startswith('~/'):
                    stdin = os.path.join(os.path.expanduser('~'), stdin[2:])
                else:
                    stdin = os.path.abspath(stdin)
                if not os.path.exists(stdin):
                    print("Path <%s> does not exists." % stdin)
                    stdin = self._prompt(section, option)
        else:
            stdin = input('Please enter %s: ' % option)
        if not stdin:
            stdin = DEFAULTS[section][option]

        return stdin

    def _set_cluster_default(self, ctype=False):
        """Use the default cluster settings from the cluster type selected.

        :param ctype: True if set to default
        :return: None
        """
        cluster_type = '0'
        while cluster_type not in ['1', '2', '3']:
            cluster_type = input("Which cluster are you using? \
[1.SGE 2.SLURM 3.MOAB] ")
        sys.stdout.write('Warning: You can edit the cluster templates files \
at any time in ~/.dax_templates/\n')

        for option in ['gateway', 'root_job_dir', 'queue_limit', 'results_dir',
                       'max_age', 'launcher_type', 'skip_lastupdate']:
            value = self._prompt('cluster', option)
            self.config_parser.set('cluster', option, value)

        if cluster_type == '1':
            cluster_dict = DEFAULT_SGE_DICT
        elif cluster_type == '2':
            cluster_dict = DEFAULT_SLURM_DICT
        else:
            cluster_dict = DEFAULT_MOAB_DICT

        # Copy the files from the template:
        templates_path = os.path.join(self.config_parser.get('admin',
                                                             'user_home'),
                                      '.dax_templates')
        if not os.path.exists(templates_path):
            os.makedirs(templates_path)
        for option, value in list(cluster_dict.items()):
            if option in OPTIONS_DESCRIPTION and \
               OPTIONS_DESCRIPTION[option]['is_path']:
                file_path = os.path.join(templates_path, option + '.txt')
                with open(file_path, 'w') as fid:
                    fid.writelines(value)
                self.config_parser.set('cluster', option, file_path)
            else:
                self.config_parser.set('cluster', option, value)


def test_connection_xnat(host, user, pwd):
    """
    Method to check connection to XNAT using host, user, pwd.

    :param host: Host for XNAT
    :param user: User for XNAT
    :param pwd: Password for XNAT
    :return: True if succeeded, False otherwise.
    """
    from pyxnat.core.errors import DatabaseError
    from pyxnat import Interface
    xnat = Interface(host, user, pwd)
    try:
        # try deleting SESSION connection
        xnat._exec('/data/JSESSION', method='DELETE')
        print(' --> Good login.\n')
        return True
    except DatabaseError:
        print(' --> error: Wrong login.\n')
        return False


def set_xnat_netrc():
    """Ask User for xnat credentials and store it in xnatnetrc file.

    :return: None
    """
    netrc_obj = DAX_Netrc()
    if netrc_obj.is_empty():
        print('Warning: daxnetrc is empty. Setting XNAT login:')
        connection = False
        while not connection:
            host = input("Please enter your XNAT host: ")
            user = input("Please enter your XNAT username: ")
            pwd = getpass.getpass(prompt='Please enter your XNAT password: ')
            connection = test_connection_xnat(host, user, pwd)
        if connection:
            netrc_obj.add_host(host, user, pwd)
        # add XNAT_HOST to your profile file:
        init_profile(host)


def init_profile(host):
    """Function to init your profile file to call xnat_profile.

    :param host: Host of XNAT to add to your profile
    :return: None
    """
    # link the file in the bashrc or profile
    profile = os.path.join(os.path.expanduser('~'), '.bash_profile')

    if os.path.exists(os.path.join(os.path.expanduser('~'), '.bash_profile')):
        profile = os.path.join(os.path.expanduser('~'), '.bash_profile')
    elif os.path.exists(os.path.join(os.path.expanduser('~'), '.bashrc')):
        profile = os.path.join(os.path.expanduser('~'), '.bashrc')
    elif os.path.exists(os.path.join(os.path.expanduser('~'), '.profile')):
        profile = os.path.join(os.path.expanduser('~'), '.profile')
    else:
        raise DaxSetupError("could not find your profile file.")
    # Add the line to the profile
    line_to_add = 'export XNAT_HOST=%s' % host
    if 'XNAT_HOST' not in open(profile).read():
        with open(profile, "a") as f_profile:
            f_profile.write(BASH_PROFILE_XNAT.format(export_cmd=line_to_add))
