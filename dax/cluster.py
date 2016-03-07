""" cluster.py

Cluster functionality
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

import os
import time
import logging
import subprocess
from datetime import datetime
from subprocess import CalledProcessError
from dax_settings import DAX_Settings
DAX_SETTINGS = DAX_Settings()
DEFAULT_EMAIL_OPTS = DAX_SETTINGS.get_email_opts()
JOB_TEMPLATE = DAX_SETTINGS.get_job_template()
CMD_SUBMIT = DAX_SETTINGS.get_cmd_submit()
CMD_COUNT_NB_JOBS = DAX_SETTINGS.get_cmd_count_nb_jobs()
CMD_GET_JOB_STATUS = DAX_SETTINGS.get_cmd_get_job_status()
CMD_GET_JOB_WALLTIME = DAX_SETTINGS.get_cmd_get_job_walltime()
CMD_GET_JOB_MEMORY = DAX_SETTINGS.get_cmd_get_job_memory()
CMD_GET_JOB_NODE = DAX_SETTINGS.get_cmd_get_job_node()
RUNNING_STATUS = DAX_SETTINGS.get_running_status()
QUEUE_STATUS = DAX_SETTINGS.get_queue_status()
COMPLETE_STATUS = DAX_SETTINGS.get_complete_status()
PREFIX_JOBID = DAX_SETTINGS.get_prefix_jobid()
SUFFIX_JOBID = DAX_SETTINGS.get_suffix_jobid()
MAX_TRACE_DAYS = 30

#Logger to print logs
LOGGER = logging.getLogger('dax')

def c_output(output):
    """
    Check if the output value is an integer

    :param output: variable to check
    :return: True if output is not an integer, False otherwise.
    """
    try:
        int(output)
        error = False
    except (CalledProcessError, ValueError) as err:
        error = True
        LOGGER.error(err)
    return error

def count_jobs():
    """
    Count the number of jobs in the queue on the cluster

    :return: number of jobs in the queue
    """
    cmd = CMD_COUNT_NB_JOBS
    output = subprocess.check_output(cmd, shell=True)
    error = c_output(output)
    while error:
        LOGGER.info('     try again to access number of jobs in 2 seconds.')
        time.sleep(2)
        output = subprocess.check_output(cmd, shell=True)
        error = c_output(output)
    if int(output) < 0:
        return 0
    else:
        return int(output)

def job_status(jobid):
    """
    Get the status for a job on the cluster

    :param jobid: job id to check
    :return: job status

    """
    cmd = CMD_GET_JOB_STATUS.safe_substitute({'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        output = output.strip()
        if output == RUNNING_STATUS:
            return 'R'
        elif output == QUEUE_STATUS:
            return 'Q'
        elif output == COMPLETE_STATUS:
            return 'C'
        else:
            return None
    except CalledProcessError:
        return None

def is_traceable_date(jobdate):
    """
    Check if the job is traceable on the cluster

    :param jobdate: launching date of the job
    :return: True if traceable, False otherwise.
    """
    try:
        trace_date = datetime.strptime(jobdate, "%Y-%m-%d")
        diff_days = (datetime.today() - trace_date).days
        return diff_days <= MAX_TRACE_DAYS
    except ValueError:
        return False

def tracejob_info(jobid, jobdate):
    """
    Trace the job information from the cluster

    :param jobid: job id to check
    :param jobdate: launching date of the job
    :return: dictionary object with 'mem_used', 'walltime_used', 'jobnode'
    """
    time_s = datetime.strptime(jobdate, "%Y-%m-%d")
    diff_days = (datetime.today()-time_s).days+1
    jobinfo = dict()
    jobinfo['mem_used'] = get_job_mem_used(jobid, diff_days)
    jobinfo['walltime_used'] = get_job_walltime_used(jobid, diff_days)
    jobinfo['jobnode'] = get_job_node(jobid, diff_days)

    return jobinfo

def get_job_mem_used(jobid, diff_days):
    """
    Get the memory used for the task from cluster

    :param jobid: job id to check
    :param diff_days: difference of days between starting date and now
    :return: string with the memory usage, empty string if error
    """
    mem = ''
    # Check for blank jobid
    if not jobid:
        return mem

    cmd = CMD_GET_JOB_MEMORY.safe_substitute({'numberofdays':diff_days, 'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        if output:
            mem = output.strip()

    except CalledProcessError:
        pass

    return mem

def get_job_walltime_used(jobid, diff_days):
    """
    Get the walltime used for the task from cluster

    :param jobid: job id to check
    :param diff_days: difference of days between starting date and now
    :return: string with the walltime used, empty string if error
    """
    walltime = ''
    # Check for blank jobid
    if not jobid:
        return walltime

    cmd = CMD_GET_JOB_WALLTIME.safe_substitute({'numberofdays':diff_days, 'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        if output:
            walltime = output.strip()

    except CalledProcessError:
        pass

    if not walltime and diff_days > 3:
        walltime = 'NotFound'

    return walltime

def get_job_node(jobid, diff_days):
    """
    Get the node where the job was running on the cluster

    :param jobid: job id to check
    :param diff_days: difference of days between starting date and now
    :return: string with the node, empty string if error
    """
    jobnode = ''
    # Check for blank jobid
    if not jobid:
        return jobnode

    cmd = CMD_GET_JOB_NODE.safe_substitute({'numberofdays':diff_days, 'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        if output:
            jobnode = output.strip()

    except CalledProcessError:
        pass

    return jobnode

def get_specific_str(big_str, prefix, suffix):
    """
    Extract a specific length out of a string

    :param big_str: string to reduce
    :param prefix: prefix to remove
    :param suffix: suffix to remove
    :return: string reduced, return empty string if prefix and suffix not present
    """
    specific_str = big_str
    if prefix and len(specific_str.split(prefix)) > 1:
        specific_str = specific_str.split(prefix)[1]
    if suffix and len(specific_str.split(suffix)) > 1:
        specific_str = specific_str.split(suffix)[0]
    if specific_str != big_str:
        return specific_str
    else:
        return ''

class PBS:   #The script file generator class
    """ PBS class to generate/submit the cluster file to run a task """
    def __init__(self, filename, outfile, cmds, walltime_str, mem_mb=2048,
                 ppn=1, email=None, email_options=DEFAULT_EMAIL_OPTS, xnat_host=os.environ['XNAT_HOST']):
        """
        Entry point for the PBS class

        :param filename: filename for the script
        :param outfile: filepath for the outlogs
        :param cmds: commands to run in the script
        :param walltime_str: walltime to set for the script
        :param mem_mb: memory in mb to set for the script
        :param ppn: number of processor to set for the script
        :param email: email address to set for the script
        :param email_options: email options to set for the script
        :return: None
        """
        self.filename = filename
        self.outfile = outfile
        self.cmds = cmds
        self.walltime_str = walltime_str
        self.mem_mb = mem_mb
        self.email = email
        self.email_options = email_options
        self.ppn = ppn
        self.xnat_host = xnat_host

    def write(self):
        """
        Write the file

        :return: None
        """
        #pbs_dir
        job_dir = os.path.dirname(self.filename)
        if not os.path.exists(job_dir):
            os.makedirs(job_dir)
        # Write the Bedpost script (default value)
        job_data = {'job_email':self.email,
                    'job_email_options':self.email_options,
                    'job_ppn':str(self.ppn),
                    'job_walltime':str(self.walltime_str),
                    'job_memory':str(self.mem_mb),
                    'job_output_file':self.outfile,
                    'job_output_file_options':'oe',
                    'job_cmds':'\n'.join(self.cmds),
                    'xnat_host':self.xnat_host}
        with open(self.filename, 'w') as f_obj:
            f_obj.write(JOB_TEMPLATE.safe_substitute(job_data))

    def submit(self):
        """
        Submit the file to the cluster

        :return: None
        """
        try:
            cmd = CMD_SUBMIT +' '+ self.filename
            proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = proc.communicate()
            if output:
                LOGGER.info('    '+output)
            if error:
                LOGGER.error(error)
            #output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            jobid = get_specific_str(output, PREFIX_JOBID, SUFFIX_JOBID)
        except CalledProcessError as err:
            LOGGER.error(err)
            jobid = '0'

        return jobid.strip()

class ClusterLaunchException(Exception):
    """Custom exception raised when launch on the grid failed"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to launch job on the grid.')

class ClusterCountJobsException(Exception):
    """Custom exception raised when attempting to get the number of
    jobs fails"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to fetch number of '
                                 'jobs from the grid.')

class ClusterJobIDException(Exception):
    """Custom exception raised when attempting to get the job id failed"""
    def __init__(self):
        Exception.__init__(self, 'ERROR: Failed to get job id.')
