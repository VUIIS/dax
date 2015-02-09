# Example for MOAB PBS:

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
CMD_GET_JOB_MEMORY    --> command to get job memory used 
CMD_GET_JOB_WALLTIME  --> command to get job walltime used
JOB_EXTENSION_FILE    --> extension for job script (default: .pbs)
DEFAULT_EMAIL_OPTS    --> EMAIL options (default: bae)

    2) PATH / default value for cluster
    
DEFAULT_GATEWAY --> Name of the computer you are working on (define by HOSTNAME), default value if HOSTNAME not in env
RESULTS_DIR     --> where results from jobs are stored to be upload to xnat later.
ROOT_JOB_DIR    --> Directory used for temp job folder for intermediate results
QUEUE_LIMIT     --> Number max of jobs authorized in the queue.

    3) Email information to send email (optional)
    
SMTP_FROM --> address from where you will send the email.
SMTP_PASS --> password for the email address.
SMTP_HOST --> server HOST ID (e.g: google --> stmp.gmail.com)

    4) REDCap for dax_manager (optional)
    
API_URL      --> api url for redcap database
API_KEY_DAX  --> api key for redcap project holding the information for the settings
API_KEY_XNAT --> api key for redcap project holding the jobID submit to the cluster
REDCAP_VAR   --> dictionary to set up the general variables for the project
PS: In this file, all variable default are read if the .bashrc or your configuration file doesn't have the environment variable
set.
"""

#### Default value set by users ####
#Function for PBS cluster jobs:
#Command to submit job to the cluster:
CMD_SUBMIT_PBS='qsub'
PREFIX_JOBID=None
SUFFIX_JOBID='.'
#Command to count the number of jobs running for a user
CMD_COUNT_NB_JOBS="qstat | grep $USER | wc -l"
#Command to get the status of a job giving it jobid. Shoudl return R/Q/C for running/queue or others that will mean clear
CMD_GET_JOB_STATUS=Template("""qstat -f ${jobid} | grep job_state | awk {'print $3'}""")
RUNNING_STATUS='R'
QUEUE_STATUS='Q'
#Command to get the walltime and memory used by the jobs at the end of the job: each command need to return the value as a string.
CMD_GET_JOB_MEMORY=Template("""rsh vmpsched "tracejob -n ${numberofdays} ${jobid}" 2> /dev/null | awk -v FS="(resources_used.mem=|kb)" '{print $2}' | sort -u | tail -1""")
CMD_GET_JOB_WALLTIME=Template("""rsh vmpsched "tracejob -n ${numberofdays} ${jobid}" 2> /dev/null | awk -v FS="(resources_used.walltime=|\n)" '{print $2}' | sort -u | tail -1""")
#Template for your PBS
JOB_EXTENSION_FILE='.pbs' 
PBS_TEMPLATE = Template("""#!/bin/bash
#PBS -M ${pbs_email}
#PBS -m ${pbs_email_options}
#PBS -l nodes=1:ppn=${pbs_ppn}
#PBS -l walltime=${pbs_walltime}
#PBS -l mem=${pbs_memory}mb
#PBS -o ${pbs_output_file}
#PBS -j ${pbs_output_file_options}
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=${pbs_ppn} #set the variable to use only good amount of ppn
uname -a # outputs node info (name, date&time, type, OS, etc)
${pbs_cmds}
""")
#Default EMAIL options:
DEFAULT_EMAIL_OPTS='bae'

#Path for results from job by default.
#Gateway of the computer you are running on for default if HOSTNAME is not an env:
DEFAULT_GATEWAY = None
#Root directory for jobs
DEFAULT_ROOT_JOB_DIR = '/tmp'
#Number maximun of job in the queue:
DEFAULT_QUEUE_LIMIT = 600
#Result dir
DEFAULT_RESULTS_DIR=os.path.join(USER_HOME,'RESULTS_XNAT_SPIDER')
#Email
DEFAULT_SMTP_HOST='stmp.gmail.com'  #google
DEFAULT_SMTP_FROM=None
DEFAULT_SMTP_PASS=None
#REDCap
DEFAULT_API_URL='https://redcap.vanderbilt.edu/api/'
DEFAULT_API_KEY_DAX=None
DEFAULT_API_KEY_XNAT=None
#Dictionary with variable name on REDCap:                   Variable for:
REDCAP_VAR={'project':'dax_project',                        #record_id (project on XNAT)
            'settingsfile':'dax_settings_full_path',        #path on your computer to the settings file
            'masimatlab':'dax_masimatlab',                  #path to masimatlab
            'tmp':'dax_tmp_directory',                      #tmp folder to hold data for modules
            'logsdir':'dax_logs_path',                      #folder to hold logs for updates
            'user':'dax_cluster_user',                      #user that will run the project (USER env variable)
            'gateway':'dax_gateway',                        #name of your computer set in this settings or from gateway if cluster
            'email':'dax_email_address',                    #email address for report
            'queue':'dax_queue_limit',                      #queue limit that you allow for the project
            'priority':'dax_proj_order',                    #project order number: 1 will be first and then ...
            'email_opts':'dax_job_email_options',           #job options for job on cluster (bae)
            'update_start_date':'dax_update_start_date',    #date for dax_update, the last one starting
            'update_end_date':'dax_update_end_date',        #date for dax_update, the last one ending
            'open_start_date':'dax_update_open_start_date', #date for dax_update_open_tasks, the last one starting
            'open_end_date':'dax_update_open_end_date',     #date for dax_update_open_tasks, the last one ending
            'update_pid':'dax_update_pid',                  #pid for update
            'update_open_pid':'dax_update_open_pid'}        #pid for update_open

#### Getting value from the environ variable if set or default value (do not touch) ####
#Upload directory
if 'UPLOAD_SPIDER_DIR' not in os.environ:
    RESULTS_DIR=DEFAULT_RESULTS_DIR
    if not os.path.exists(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)
else:
    RESULTS_DIR=os.environ['UPLOAD_SPIDER_DIR'] 
#Settings to send email (optional):
#STMP_FROM:
if 'SMTP_FROM' not in os.environ:
    SMTP_FROM=DEFAULT_SMTP_FROM
else:
    SMTP_FROM=os.environ['SMTP_FROM'] 
#API_URL:
if 'SMTP_PASS' not in os.environ:
    SMTP_PASS=DEFAULT_SMTP_PASS
else:
    SMTP_PASS=os.environ['SMTP_PASS'] 
#API_URL:
if 'SMTP_HOST' not in os.environ:
    SMTP_HOST=DEFAULT_SMTP_HOST
else:
    SMTP_HOST=os.environ['SMTP_HOST'] 
#Management using REDCap (optional):
#Variables for REDCap:
#API_URL:
if 'API_URL' not in os.environ:
    API_URL=DEFAULT_API_URL
else:
    API_URL=os.environ['API_URL'] 
#API_KEY for dax project (save here or in .bashrc and name the env variable API_KEY_DAX):
if 'API_KEY_DAX' not in os.environ:
    API_KEY_DAX=DEFAULT_API_KEY_DAX
else:
    API_KEY_DAX=os.environ['API_KEY_DAX']
#API_KEY for XNAT project where each jobs will correspond to a job submit to cluster (save here or in .bashrc and name the env variable API_KEY_XNAT):
if 'API_KEY_XNAT' not in os.environ:
    API_KEY_XNAT=DEFAULT_API_KEY_XNAT
else:
    API_KEY_XNAT=os.environ['API_KEY_XNAT'] 

