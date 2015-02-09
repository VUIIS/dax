#Example for SUN GRID ENGINE pbs:

import os
from string import Template 
from stat import S_IXUSR, ST_MODE
from os.path import expanduser

USER_HOME = expanduser("~")

""" This file can be edited by users to match their cluster commands.
    
    1) PBS:
You can customize the command for PBS.
One command is to count the number of jobs from the cluster running under the USER.

CMD_SUBMIT_PBS        --> command to submit jobs (default: qsub)
PREFIX_JOBID          --> string before the job ID in the output of the CMD_SUBMIT_PBS
SUFFIX_JOBID          --> string after the job ID in the output of the CMD_SUBMIT_PBS

CMD_COUNT_NB_JOBS     --> command to return the number of jobs 

CMD_GET_JOB_STATUS    --> command to return the status of a job given it jobid
RUNNING_STATUS        --> string return for RUNNING Job (e.g: 'r')
QUEUE_STATUS          --> string return for IN QUEUE Job (e.g: 'qw')

CMD_GET_JOB_DONE_INFO --> command to submit jobs (default: qsub)
PREFIX_WALLTIME       --> string before the Walltime used in the output of the CMD_GET_JOB_DONE_INFO
SUFFIX_WALLTIME       --> string after the Walltime used in the output of the CMD_GET_JOB_DONE_INFO
PREFIX_MEMORY         --> string before the Memory used in the output of the CMD_GET_JOB_DONE_INFO
SUFFIX_MEMORY         --> string after the Memory used in the output of the CMD_GET_JOB_DONE_INFO
EXIT_STATUS           --> string to check in the output to be sure the value for walltime and memory are there

    2) PATH / default value for cluster
    
RESULTS_DIR  --> where results from jobs are stored to be upload to xnat later.
ROOT_JOB_DIR --> Directory used for temp job folder for intermediate results
QUEUE_LIMIT  --> Number max of jobs authorized in the queue.

"""

#Function for PBS cluster jobs:
#Command to submit job to the cluster:
CMD_SUBMIT_PBS='qsub'
PREFIX_JOBID="Your job "
SUFFIX_JOBID='("'
#Command to count the number of jobs running for a user
CMD_COUNT_NB_JOBS="qstat -u $USER | wc -l"
#Command to get the status of a job giving it jobid. Shoudl return R/Q/C for running/queue or others that will mean clear
CMD_GET_JOB_STATUS=Template("""qstat -u $USER | grep ${jobid} | awk {'print $5'}""")
RUNNING_STATUS='r'
QUEUE_STATUS='qw'
#Command to get the walltime and memory used by the jobs at the end of the job
#Command to get the walltime and memory used by the jobs at the end of the job: each command need to return the value as a string.
CMD_GET_JOB_MEMORY=Template("""qstat""") #not define
CMD_GET_JOB_WALLTIME=Template("""qstat""") #not define
#Template for your PBS
JOB_EXTENSION_FILE='.pbs' 
PBS_TEMPLATE = Template("""#!/bin/bash
#$ -q clusterjob
#$ -l mem_free=${pbs_memory}M
#$ -l mem_token=${pbs_memory}M
#$ -l h_vmem=${pbs_memory}M
#$ -o ${pbs_output_file}
#$ -j y
#$ -V

export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=${pbs_ppn} #set the variable to use only good amount of ppn
uname -a # outputs node info (name, date&time, type, OS, etc)
${pbs_cmds}
""")
#Default EMAIL options:
DEFAULT_EMAIL_OPTS='bae'

#Path for results from job by default.
#Root directory for jobs
DEFAULT_ROOT_JOB_DIR = '/tmp'
#Number maximun of job in the queue:
DEFAULT_QUEUE_LIMIT = 200
#Result dir
DEFAULT_RESULTS_DIR=os.path.join(USER_HOME,'RESULTS_XNAT_SPIDER')

if 'UPLOAD_SPIDER_DIR' not in os.environ:
    RESULTS_DIR=DEFAULT_RESULTS_DIR
    if not os.path.exists(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)
else:
    RESULTS_DIR=os.environ['UPLOAD_SPIDER_DIR'] 
    
