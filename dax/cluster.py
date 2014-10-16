#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" cluster.py

Cluster functionality
"""
__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

import subprocess,os
from subprocess import CalledProcessError
from datetime import datetime
from dax_settings import PBS_TEMPLATE,CMD_SUBMIT_PBS,CMD_COUNT_NB_JOBS,CMD_GET_JOB_STATUS,CMD_GET_JOB_DONE_INFO,PREFIX_WALLTIME,SUFFIX_WALLTIME,PREFIX_MEMORY,SUFFIX_MEMORY,EXIT_STATUS,RUNNING_STATUS,QUEUE_STATUS,PREFIX_JOBID,SUFFIX_JOBID

MAX_TRACE_DAYS=30

def count_jobs():
    cmd = CMD_COUNT_NB_JOBS
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return int(output)
    except (CalledProcessError,ValueError):
        return -1
    
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
    
def tracejob_info(jobid, jobdate):
    d = datetime.strptime(jobdate, "%Y-%m-%d")
    diff_days = (datetime.today() - d).days + 1
    jobinfo = {'mem_used' : '', 'walltime_used' : ''}
    
    cmd = CMD_GET_JOB_DONE_INFO.safe_substitute(**{'numberofdays':diff_days,'jobid':jobid})
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)        
        if EXIT_STATUS and EXIT_STATUS in output:
            #get the walltime used
            jobinfo['walltime_used'] = get_specific_str(output,PREFIX_WALLTIME,SUFFIX_WALLTIME)
            #get the mem used
            jobinfo['mem_used'] = get_specific_str(output,PREFIX_MEMORY,SUFFIX_MEMORY)
                
    except CalledProcessError:
        pass
    
    if jobinfo['walltime_used'] == '' and diff_days > 3: 
        jobinfo['walltime_used'] = 'NotFound'

    return jobinfo
  
class PBS:  
    #constructor
    def __init__(self,filename,outfile,cmds,walltime_str,mem_mb=2048,ppn=1,email=None,email_options='bae'):
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
        pbs_dir = os.path.dirname(self.filename)
        if not os.path.exists(pbs_dir):
            os.makedirs(pbs_dir)
        # Write the Bedpost script (default value)
        PBS_data = {'pbs_email': self.email,
                    'pbs_email_options': self.email_options,
                    'pbs_ppn': str(self.ppn),
                    'pbs_walltime': str(self.walltime_str),
                    'pbs_memory': str(self.mem_mb),
                    'pbs_output_file': self.outfile,
                    'pbs_output_file_options': 'oe',
                    'pbs_cmds':'\n'.join(self.cmds)}
        with open(self.filename, 'w') as f:
            f.write(PBS_TEMPLATE.safe_substitute(**PBS_data))

    def submit(self):
        try:
            cmd = CMD_SUBMIT_PBS +' '+ self.filename
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            jobid = get_specific_str(output,PREFIX_JOBID,SUFFIX_JOBID)
        except CalledProcessError:
            jobid = '0'
        
        return jobid.strip()

    
