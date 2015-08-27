""" This file can be edited by users to match their cluster commands.

    1) Submission System (by default SLURM) and script file:
You can customize the command for your Submission System.

ADMIN_EMAIL           --> admin for dax_manager
CMD_SUBMIT            --> command to submit jobs (default: sbatch)
PREFIX_JOBID          --> string before the job ID in the output of the CMD_SUBMIT
SUFFIX_JOBID          --> string after the job ID in the output of the CMD_SUBMIT
CMD_COUNT_NB_JOBS     --> command to return the number of jobs
CMD_GET_JOB_STATUS    --> command to return the status of a job given it jobid
RUNNING_STATUS        --> string return for RUNNING Job (e.g: 'r')
QUEUE_STATUS          --> string return for IN QUEUE Job (e.g: 'qw')
COMPLETE_STATUS       --> string return for complete job 
JOB_EXTENSION_FILE    --> extension for script file (default: .slurm)
CMD_GET_JOB_MEMORY    --> command to get job memory used
CMD_GET_JOB_WALLTIME  --> command to get job walltime used
CMD_GET_JOB_NODE      --> command to get job node used
JOB_EXTENSION_FILE    --> extension for job script (default: .slurm)
DEFAULT_EMAIL_OPTS    --> EMAIL options (default: ALL)

    2) PATH / default value for cluster

DEFAULT_GATEWAY --> Name of the computer you are working on (define by HOSTNAME),
                    default value if HOSTNAME not in env
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

    5) others

MAX_AGE --> maximun age for a session to get reset

PS: In this file, all variable default are read if the .bashrc or
    your configuration file doesn't have the environment variable set.
"""

import os
from string import Template
from os.path import expanduser

USER_HOME = expanduser("~")

#### Admin email for dax_manager ####
ADMIN_EMAIL = []

#### Default value set by users ####
#Function for PBS cluster jobs:
#Command to submit job to the cluster:
CMD_SUBMIT = 'sbatch'
PREFIX_JOBID = 'Submitted batch job '
SUFFIX_JOBID = '\n'
#Command to count the number of jobs running for a user
CMD_COUNT_NB_JOBS = "squeue -u $USER --noheader | wc -l"
#Command to get the status of a job giving it jobid.
#Shoudl return R/Q/C for running/queue or others that will mean clear
CMD_GET_JOB_STATUS = Template("""squeue -j ${jobid} --noheader | awk {'print $5'}""")
RUNNING_STATUS = 'R'
QUEUE_STATUS = 'Q'
COMPLETE_STATUS = 'slurm_load_jobs error: Invalid job id specified'
#Command to get the walltime and memory used by the jobs at the end of the job
TEMPLATE = """sacct -j ${jobid}.batch --format MaxRss --noheader | awk '{print $1+0}'"""
CMD_GET_JOB_MEMORY = Template(TEMPLATE)
CMD_GET_JOB_WALLTIME = Template("""sacct -j ${jobid}.batch --format CPUTime --noheader""")
CMD_GET_JOB_NODE = Template("""sacct -j ${jobid}.batch --format NodeList --noheader""")
#Template for your script file to submit a job
JOB_EXTENSION_FILE = '.slurm'
JOB_TEMPLATE = Template("""#!/bin/bash
#SBATCH --mail-user=${job_email}
#SBATCH --mail-type=${job_email_options}
#SBATCH --nodes=1
#SBATCH --ntasks=${job_ppn}
#SBATCH --time=${job_walltime}
#SBATCH --mem=${job_memory}mb
#SBATCH -o ${job_output_file}

uname -a # outputs node info (name, date&time, type, OS, etc)
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=${job_ppn} #set the variable to use only good amount of ppn
SCREEN=$$$$$$$$
echo 'Screen display number for xvfb-run' $SCREEN
xvfb-run --wait=5 \
-a -e /tmp/xvfb_$SCREEN.err -f /tmp/xvfb_$SCREEN.auth \
--server-num=$SCREEN \
--server-args="-screen 0 1920x1200x24 -ac +extension GLX" \
${job_cmds}
""")
#Default EMAIL options:
DEFAULT_EMAIL_OPTS = 'FAIL'

#Path for results from job by default.
#Gateway of the computer you are running on for default if HOSTNAME is not an env:
DEFAULT_GATEWAY = None
#Root directory for jobs
DEFAULT_ROOT_JOB_DIR = '/tmp'
#Number maximun of job in the queue:
DEFAULT_QUEUE_LIMIT = 600
#Result dir
DEFAULT_RESULTS_DIR = os.path.join(USER_HOME, 'RESULTS_XNAT_SPIDER')
#Email
DEFAULT_SMTP_HOST = 'stmp.gmail.com'  #google
DEFAULT_SMTP_FROM = None
DEFAULT_SMTP_PASS = None
#REDCap
DEFAULT_API_URL = 'https://redcap.vanderbilt.edu/api/'
DEFAULT_API_KEY_DAX = None
DEFAULT_API_KEY_XNAT = None
#Dictionary with variable name on REDCap in order:
#Variable for:
#record_id (project on XNAT)
#path on your computer to the settings file
#path to masimatlab
#tmp folder to hold data for modules
#folder to hold logs for updates
#user that will run the project (USER env variable)
#name of your computer set in this settings or from gateway if cluster
#email address for report
#queue limit that you allow for the project
#project order number: 1 will be first and then ...
#job options for job on cluster (bae)
#date for dax_build, the last one starting
#date for dax_build, the last one ending
#pid for dax_build
#date for dax_update_taks, the last one starting
#date for dax_update_tasks, the last one ending
#pid for dax_update_tasks
#date for dax_launch, the last one starting
#date for dax_launch, the last one ending
#pid for dax_launc
REDCAP_VAR = {'project':'dax_project',
              'settingsfile':'dax_settings_full_path',
              'masimatlab':'dax_masimatlab',
              'tmp':'dax_tmp_directory',
              'logsdir':'dax_logs_path',
              'user':'dax_cluster_user',
              'gateway':'dax_gateway',
              'email':'dax_cluster_email',
              'queue':'dax_queue_limit',
              'priority':'dax_proj_order',
              'email_opts':'dax_job_email_options',
              'dax_build_start_date':'dax_build_start_date',
              'dax_build_end_date':'dax_build_end_date',
              'dax_build_pid':'dax_build_pid',
              'dax_update_tasks_start_date':'dax_update_tasks_start_date',
              'dax_update_tasks_end_date':'dax_update_tasks_end_date',
              'dax_update_tasks_pid':'dax_update_tasks_pid',
              'dax_launch_start_date':'dax_launch_start_date',
              'dax_launch_end_date':'dax_launch_end_date',
              'dax_launch_pid':'dax_launch_pid',
              'max_age':'dax_max_age',
              'admin_email':'dax_email_address'}

#### Getting value from the environ variable if set or default value (do not touch) ####
#Upload directory
if 'UPLOAD_SPIDER_DIR' not in os.environ:
    RESULTS_DIR = DEFAULT_RESULTS_DIR
    if not os.path.exists(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)
else:
    RESULTS_DIR = os.environ['UPLOAD_SPIDER_DIR']
#Settings to send email (optional):
#STMP_FROM:
if 'SMTP_FROM' not in os.environ:
    SMTP_FROM = DEFAULT_SMTP_FROM
else:
    SMTP_FROM = os.environ['SMTP_FROM']
#API_URL:
if 'SMTP_PASS' not in os.environ:
    SMTP_PASS = DEFAULT_SMTP_PASS
else:
    SMTP_PASS = os.environ['SMTP_PASS']
#API_URL:
if 'SMTP_HOST' not in os.environ:
    SMTP_HOST = DEFAULT_SMTP_HOST
else:
    SMTP_HOST = os.environ['SMTP_HOST']
#Management using REDCap (optional):
#Variables for REDCap:
#API_URL:
if 'API_URL' not in os.environ:
    API_URL = DEFAULT_API_URL
else:
    API_URL = os.environ['API_URL']
#API_KEY for dax project (save here or in .bashrc and name the env variable API_KEY_DAX):
if 'API_KEY_DAX' not in os.environ:
    API_KEY_DAX = DEFAULT_API_KEY_DAX
else:
    API_KEY_DAX = os.environ['API_KEY_DAX']


# MAX AGE for a session:
DEFAULT_MAX_AGE = 7 # number of days
