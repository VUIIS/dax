#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" cluster.py

Cluster functionality
"""
__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

import subprocess,os,logging,time
from subprocess import CalledProcessError
from datetime import datetime
from dax_settings import DEFAULT_EMAIL_OPTS,JOB_TEMPLATE,CMD_SUBMIT,CMD_COUNT_NB_JOBS,CMD_GET_JOB_STATUS,CMD_GET_JOB_WALLTIME,CMD_GET_JOB_MEMORY,CMD_GET_JOB_NODE,RUNNING_STATUS,QUEUE_STATUS,PREFIX_JOBID,SUFFIX_JOBID

MAX_TRACE_DAYS=30

#Logger to print logs
logger = logging.getLogger('dax')

def c_output(output):
    try:
        int(output)
        error=False
    except (CalledProcessError,ValueError) as e:
        error=True
        logger.error(e)
    return error

def count_jobs():
    cmd = CMD_COUNT_NB_JOBS
    output=subprocess.check_output(cmd, shell=True)
    error=c_output(output)
    while error:
        logger.info('     try again to access number of jobs in 2 seconds.')
        time.sleep(2)
        output = subprocess.check_output(cmd,shell=True)
        error=c_output(output)
    return int(output)
    """try:
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        if error:
            logger.error(error)
        return int(output)
    except (CalledProcessError,ValueError) as e:
        logger.error(e)
        return -1"""
    
def job_status(jobid):
    cmd=CMD_GET_JOB_STATUS.safe_substitute(**{'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        output = output.strip()
        if output==RUNNING_STATUS:
            return 'R'
        elif output==QUEUE_STATUS:
            return 'Q'
        else:
            return 'C'
    except CalledProcessError:
        return ''    
  
def is_traceable_date(jobdate):
    try:
        trace_date = datetime.strptime(jobdate,"%Y-%m-%d")
        diff_days = (datetime.today() - trace_date).days
        return (diff_days <= MAX_TRACE_DAYS)
    except ValueError:
        return False

def tracejob_info(jobid, jobdate):
    d = datetime.strptime(jobdate, "%Y-%m-%d")
    diff_days = (datetime.today() - d).days + 1
    jobinfo = dict()
    jobinfo['mem_used']=get_job_mem_used(jobid,diff_days)
    jobinfo['walltime_used']=get_job_walltime_used(jobid,diff_days)
    jobinfo['jobnode']=get_job_node(jobid,diff_days)
    
    return jobinfo
    
def get_job_mem_used(jobid,diff_days):
    mem=''
    # Check for blank jobid
    if not jobid:
        return mem
        
    cmd = CMD_GET_JOB_MEMORY.safe_substitute(**{'numberofdays':diff_days,'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)        
        if output:
            mem=output.strip()
                
    except CalledProcessError:
        pass
    
    return mem

def get_job_walltime_used(jobid,diff_days):
    walltime=''
    # Check for blank jobid
    if not jobid:
        return walltime
        
    cmd = CMD_GET_JOB_WALLTIME.safe_substitute(**{'numberofdays':diff_days,'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)        
        if output:
            walltime=output.strip()
                
    except CalledProcessError:
        pass
    
    if not walltime and diff_days > 3: 
        walltime = 'NotFound'

    return walltime
    
def get_job_node(jobid,diff_days):
    jobnode=''
    # Check for blank jobid
    if not jobid:
        return jobnode
        
    cmd = CMD_GET_JOB_NODE.safe_substitute(**{'numberofdays':diff_days,'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)        
        if output:
            jobnode=output.strip()
                
    except CalledProcessError:
        pass
    
    return jobnode
    
def get_specific_str(big_str,prefix,suffix):
    specific_str = big_str
    if prefix and len(specific_str.split(prefix))>1:
        specific_str = specific_str.split(prefix)[1]
    if suffix and len(specific_str.split(suffix))>1:
        specific_str = specific_str.split(suffix)[0]
    if specific_str!=big_str:
        return specific_str
    else:
        return ''
  
class PBS:   #The script file generator class
    #constructor
    def __init__(self,filename,outfile,cmds,walltime_str,mem_mb=2048,ppn=1,email=None,email_options=DEFAULT_EMAIL_OPTS):
        self.filename=filename
        self.outfile=outfile
        self.cmds=cmds
        self.walltime_str=walltime_str
        self.mem_mb=mem_mb
        self.email=email
        self.email_options=email_options
        self.ppn=ppn

    def write(self):
        #pbs_dir
        job_dir = os.path.dirname(self.filename)
        if not os.path.exists(job_dir):
            os.makedirs(job_dir)
        # Write the Bedpost script (default value)
        JOB_data = {'job_email': self.email,
                    'job_email_options': self.email_options,
                    'job_ppn': str(self.ppn),
                    'job_walltime': str(self.walltime_str),
                    'job_memory': str(self.mem_mb),
                    'job_output_file': self.outfile,
                    'job_output_file_options': 'oe',
                    'job_cmds':'\n'.join(self.cmds)}
        with open(self.filename, 'w') as f:
            f.write(JOB_TEMPLATE.safe_substitute(**JOB_data))

    def submit(self):
        try:
            cmd = CMD_SUBMIT +' '+ self.filename
            p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = p.communicate()
            if output:
                logger.info('    '+output)
            if error:
                logger.error(error)
            #output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            jobid = get_specific_str(output,PREFIX_JOBID,SUFFIX_JOBID)
        except CalledProcessError as e:
            logger.error(e)
            jobid = '0'
        
        return jobid.strip()

    
