#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" cluster.py

Cluster functionality
"""

import os
import time
import logging
import subprocess as sb
from datetime import datetime

from .dax_settings import DAX_Settings
from .errors import ClusterError


__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
DAX_SETTINGS = DAX_Settings()
MAX_TRACE_DAYS = 30
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
    except ValueError as err:
        error = True
        LOGGER.error(err)
    return error


def cj_subcmd(cmd):
    output = sb.check_output(cmd, shell=True)
    error = c_output(output)
    while error:
        LOGGER.info('    try again to access number of jobs in 2 seconds.')
        time.sleep(2)
        output = sb.check_output(cmd, shell=True)
        error = c_output(output)
    if int(output) < 0:
        return 0
    else:
        return int(output)


def count_jobs(resdir,force_no_qsub=False):
    """
    Count the number of jobs in the queue on the cluster

    :return: number of jobs in the queue. tuple of
             (launched, pending, pendinguploads)
    """
    if force_no_qsub:
        LOGGER.info(' Running locally. No queue with jobs.')
        return (0, 0, 0)
    elif command_found(cmd=DAX_SETTINGS.get_cmd_submit()):
        launched = cj_subcmd(DAX_SETTINGS.get_cmd_count_jobs_launched())
        pending = cj_subcmd(DAX_SETTINGS.get_cmd_count_jobs_pending())
        cmd = DAX_SETTINGS.get_cmd_count_pendinguploads()
        cmd = cmd.safe_substitute({'resdir': resdir})
        pendinguploads = cj_subcmd(cmd)
        return (launched, pending, pendinguploads)
    else:
        LOGGER.error('ERROR: failed to find cluster commands')
        raise ClusterLaunchException


def job_status(jobid):
    """
    Get the status for a job on the cluster

    :param jobid: job id to check
    :return: job status

    """
    cmd = DAX_SETTINGS.get_cmd_get_job_status()\
                      .safe_substitute({'jobid': jobid})

    LOGGER.debug(str(cmd).strip())

    try:
        output = sb.check_output(cmd, stderr=sb.STDOUT, shell=True)
        LOGGER.debug('output='+str(output))
        output = output.decode().strip()
        if output == DAX_SETTINGS.get_running_status():
            return 'R'
        elif output == DAX_SETTINGS.get_queue_status():
            return 'Q'
        elif output == DAX_SETTINGS.get_complete_status() or len(output) == 0:
            return 'C'
        else:
            return None
    except sb.CalledProcessError as e:
        LOGGER.debug(str(e))
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
    diff_days = (datetime.today() - time_s).days + 1
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

    cmd = DAX_SETTINGS.get_cmd_get_job_memory()\
                      .safe_substitute({'numberofdays': diff_days,
                                        'jobid': jobid})
    try:
        output = sb.check_output(cmd, stderr=sb.STDOUT, shell=True)
        if output.startswith(b'sacct: error'):
            raise ClusterError(output)
        if output:
            mem = output.strip()
            mem = mem.decode()

    except (sb.CalledProcessError, ClusterError):
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

    cmd = DAX_SETTINGS.get_cmd_get_job_walltime()\
                      .safe_substitute({'numberofdays': diff_days,
                                        'jobid': jobid})

    try:
        output = sb.check_output(cmd, stderr=sb.STDOUT, shell=True)
        if output:
            walltime = output.strip()
            walltime = walltime.decode()

    except sb.CalledProcessError:
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

    if jobid == 'no_qsub':
        cmd = 'uname -a'
        output = sb.check_output(cmd, stderr=sb.STDOUT, shell=True)
        if output and len(output.strip().split(' ')) > 1:
            jobnode = output.strip().split(' ')[1]
        return jobnode

    cmd = DAX_SETTINGS.get_cmd_get_job_node()\
                      .safe_substitute({'numberofdays': diff_days,
                                        'jobid': jobid})

    try:
        output = sb.check_output(cmd, stderr=sb.STDOUT, shell=True)
        if output:
            jobnode = output.strip()
            jobnode = jobnode.decode()
    except sb.CalledProcessError:
        pass

    return jobnode


def get_specific_str(big_str, prefix, suffix):
    """
    Extract a specific length out of a string

    :param big_str: string to reduce
    :param prefix: prefix to remove
    :param suffix: suffix to remove
    :return: string reduced, return empty string if prefix/suffix not present
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


def command_found(cmd='qsub'):
    """ Return True if the command was found."""
    if True in [os.path.isfile(os.path.join(path, cmd)) and
                os.access(os.path.join(path, cmd), os.X_OK)
                for path in os.environ["PATH"].split(os.pathsep)]:
        return True
    return False


class PBS(object):   # The script file generator class
    """ PBS class to generate/submit the cluster file to run a task """
    def __init__(self, filename, outfile, cmds, walltime_str, mem_mb=2048,
                 ppn=1, env=None, email=None,
                 email_options=DAX_SETTINGS.get_email_opts(), rungroup=None,
                 xnat_host=None, job_template=None):
        """
        Entry point for the PBS class

        :param filename: filename for the script
        :param outfile: filepath for the outlogs
        :param cmds: commands to run in the script
        :param walltime_str: walltime to set for the script
        :param mem_mb: memory in mb to set for the script
        :param ppn: number of processor to set for the script
        :param env: Environment file to source  for the script
        :param email: email address to set for the script
        :param email_options: email options to set for the script
        :param rungroup: group to run job under on the cluster
        :param xnat_host: set the XNAT_HOST for the job (export)
        :return: None
        """
        self.filename = filename
        self.outfile = outfile
        self.cmds = cmds
        self.walltime_str = walltime_str
        self.mem_mb = mem_mb
        self.email = email
        self.email_options = email_options
        self.rungroup = rungroup
        self.ppn = ppn
        self.job_template = job_template
        if env:
            self.env = env
        else:
            self.env = os.path.join(os.environ['HOME'], '.bashrc')
        if xnat_host:
            self.xnat_host = xnat_host
        else:
            self.xnat_host = os.environ['XNAT_HOST']

    def write(self):
        """
        Write the file

        :return: None
        """
        # pbs_dir
        job_dir = os.path.dirname(self.filename)
        if not os.path.exists(job_dir):
            os.makedirs(job_dir)
        # Write the Bedpost script (default value)
        job_data = {'job_email': self.email,
                    'job_email_options': self.email_options,
                    'job_rungroup': self.rungroup,
                    'job_ppn': str(self.ppn),
                    'job_env': str(self.env),
                    'job_walltime': str(self.walltime_str),
                    'job_memory': str(self.mem_mb),
                    'job_output_file': self.outfile,
                    'job_output_file_options': 'oe',
                    'job_cmds': '\n'.join(self.cmds),
                    'xnat_host': self.xnat_host}

        with open(self.filename, 'w') as f_obj:
            _tmp = DAX_SETTINGS.get_job_template(self.job_template)
            _str = _tmp.safe_substitute(job_data)
            f_obj.write(_str)

    def submit(self, outlog=None, force_no_qsub=False):
        """
        Submit the file to the cluster

        :return: None
        """
        return submit_job(self.filename, outlog=outlog,
                          force_no_qsub=force_no_qsub)


def submit_job(filename, outlog=None, force_no_qsub=False):
    """
    Submit the file to the cluster
    :return: jobid and error if the job failed when running locally
    """
    failed = False
    submit_cmd = DAX_SETTINGS.get_cmd_submit()
    if command_found(cmd=submit_cmd) and not force_no_qsub:
        try:
            cmd = '%s %s' % (submit_cmd, filename)
            proc = sb.Popen(cmd.split(), stdout=sb.PIPE, stderr=sb.PIPE)
            output, error = proc.communicate()
            if output:
                LOGGER.info(output.decode())
            if error:
                LOGGER.error(error.decode())
            jobid = get_specific_str(
                output.decode(), DAX_SETTINGS.get_prefix_jobid(),
                DAX_SETTINGS.get_suffix_jobid())
        except sb.CalledProcessError as err:
            LOGGER.error(err)
            jobid = '0'

    else:
        cmd = 'sh %s' % (filename)
        proc = sb.Popen(cmd.split(), stdout=sb.PIPE, stderr=sb.PIPE)
        output, error = proc.communicate()
        if outlog:
            with open(outlog, 'w') as log_obj:
                for line in output:
                    log_obj.write(line)
                for line in error:
                    log_obj.write(line)

        if error:
            # Set the status to JOB_FAILED
            failed = True
        jobid = 'no_qsub'

    return jobid.strip(), failed
