#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" cluster.py

Cluster functionality
"""
__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

import subprocess
from subprocess import CalledProcessError
import os
from datetime import datetime

MAX_TRACE_DAYS=30

def count_jobs():
    cmd = "qstat | grep $USER | wc -l"
    
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return int(output)
    except (CalledProcessError,ValueError):
        return -1
    
def job_status(jobid):
    cmd = "qstat -f "+str(jobid)+" | grep job_state | awk {'print $3'}"
    # TODO: handle invalid jobid, error message will look like this:
    # "qstat: Unknown Job Id Error jobid"
    
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        output = output.strip()
        return output
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
    jobinfo = {'mem_used' : '', 'walltime_used' : ''}
    
    cmd = 'rsh vmpsched "tracejob -n '+str(diff_days)+' '+jobid+'"'
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)        
        if 'Exit_status' in output:
            #get the walltime used
            tmpstr = output.split('resources_used.walltime=')
            if len(tmpstr) > 1:
                jobinfo['walltime_used'] = tmpstr[1].split('\n')[0]
       
            #get the mem used
            tmpstr = output.split('resources_used.mem=')
            if len(tmpstr) > 1:
                jobinfo['mem_used'] = tmpstr[1].split('kb')[0]+'kb'
                
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
        pbs_dir = os.path.dirname(self.filename)
        if not os.path.exists(pbs_dir):
            os.makedirs(pbs_dir)
        
        f = open(self.filename,'w')
        f.write('#!/bin/bash\n')
        if self.email != None:
            f.write('#PBS -M ' + self.email+'\n')
            f.write('#PBS -m '+self.email_options+'\n')
        f.write('#PBS -l nodes=1:ppn='+str(self.ppn)+'\n')
        f.write('#PBS -l walltime='+str(self.walltime_str)+'\n')
        f.write('#PBS -l mem=' + str(self.mem_mb) + 'mb\n')
        f.write('#PBS -o ' + self.outfile+'\n')
        f.write('#PBS -j oe '+ '\n')
        f.write('\n')
        f.write('export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS='+str(self.ppn)+'\n')     
        f.write('uname -a') # outputs node info (name, date&time, type, OS, etc)
        f.write('\n')
        
        # Write the shell commands
        for line in self.cmds:
            f.write(line+'\n')

        f.close()

    def submit(self):
        try:
            cmd = 'qsub ' + self.filename
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            jobid = output.split('.')[0]
        except CalledProcessError:
            jobid = '0'
        
        return jobid
    
