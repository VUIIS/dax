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
from dax_settings import DEFAULT_EMAIL_OPTS, JOB_TEMPLATE, CMD_SUBMIT, CMD_COUNT_NB_JOBS, CMD_GET_JOB_STATUS, CMD_GET_JOB_WALLTIME, CMD_GET_JOB_MEMORY, CMD_GET_JOB_NODE, RUNNING_STATUS, QUEUE_STATUS, COMPLETE_STATUS, PREFIX_JOBID, SUFFIX_JOBID

MAX_TRACE_DAYS = 30

#Logger to print logs
LOGGER = logging.getLogger('dax')

def c_output(output):
    """ function to check if the output is a number """
    try:
        int(output)
        error = False
    except (CalledProcessError, ValueError) as err:
        error = True
        LOGGER.error(err)
    return error

def count_jobs():
    """ count the number of jobs in the queue """
    cmd = CMD_COUNT_NB_JOBS
    output = subprocess.check_output(cmd, shell=True)
    error = c_output(output)
    while error:
        LOGGER.info('     try again to access number of jobs in 2 seconds.')
        time.sleep(2)
        output = subprocess.check_output(cmd, shell=True)
        error = c_output(output)
    return int(output)

def job_status(jobid):
    """ return the job status on the cluster """
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
    """ check if the job is traceable """
    try:
        trace_date = datetime.strptime(jobdate, "%Y-%m-%d")
        diff_days = (datetime.today() - trace_date).days
        return diff_days <= MAX_TRACE_DAYS
    except ValueError:
        return False

def tracejob_info(jobid, jobdate):
    """ function to trace the job information """
    time_s = datetime.strptime(jobdate, "%Y-%m-%d")
    diff_days = (datetime.today()-time_s).days+1
    jobinfo = dict()
    jobinfo['mem_used'] = get_job_mem_used(jobid, diff_days)
    jobinfo['walltime_used'] = get_job_walltime_used(jobid, diff_days)
    jobinfo['jobnode'] = get_job_node(jobid, diff_days)

    return jobinfo

def get_job_mem_used(jobid, diff_days):
    """ return memory used for the task from cluster """
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
    """ return walltime used for the task from cluster """
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
    """ return job node for the task from cluster """
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
    """ function to extract a specific length out of a string """
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
                 ppn=1, email=None, email_options=DEFAULT_EMAIL_OPTS):
        """ init function """
        self.filename = filename
        self.outfile = outfile
        self.cmds = cmds
        self.walltime_str = walltime_str
        self.mem_mb = mem_mb
        self.email = email
        self.email_options = email_options
        self.ppn = ppn

    def write(self):
        """ write the file """
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
                    'job_cmds':'\n'.join(self.cmds)}
        with open(self.filename, 'w') as f_obj:
            f_obj.write(JOB_TEMPLATE.safe_substitute(job_data))

    def submit(self):
        """ submit the file to the cluster """
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
