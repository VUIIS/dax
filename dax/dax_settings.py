import os
import stat
import netrc
from string import Template
from urllib.parse import urlparse

from .errors import DaxNetrcError

# Assessor datatypes
DEFAULT_FS_DATATYPE = 'fs:fsData'
DEFAULT_DATATYPE = 'proc:genProcData'

SLURM_JOBMEM = "sacct -j ${jobid}.batch --format MaxRss --noheader | awk '{print $1+0}'"

SLURM_JOBTIME = "sacct -j ${jobid}.batch --format CPUTime --noheader"

SLURM_COUNTJOBS = 'squeue --me --noheader | wc -l'

SLURM_COUNTJOBS_LAUNCHED = 'squeue --me --noheader | wc -l'

SLURM_COUNTJOBS_PENDING = 'squeue --me -t PENDING --noheader | wc -l'

SLURM_COUNT_PENDINGUPLOADS = 'ls -d ${resdir}/*-x-* |wc -l'

SLURM_JOBNODE = "sacct -j ${jobid}.batch --format NodeList --noheader"

SLURM_JOBSTATUS = "squeue -j ${jobid} --noheader | awk {'print $5'}"

SLURM_EXT = '.slurm'

SLURM_SUBMIT = 'sbatch'

SLURM_COMPLETE = 'slurm_load_jobs error: Invalid job id specified'

SLURM_RUNNING = 'R'

SLURM_QUEUED = 'Q'


class DAX_Netrc(object):
    """Class for DAX NETRC file containing information about XNAT logins """
    def __init__(self):
        self.netrc_file = os.path.expanduser('~/.netrc')
        if not os.path.exists(self.netrc_file):
            open(self.netrc_file, 'a').close()
            # Setting mode for the file:
            os.chmod(self.netrc_file, stat.S_IWUSR | stat.S_IRUSR)
        self.is_secured()
        self.netrc_obj = netrc.netrc(self.netrc_file)

    def is_secured(self):
        """ Check if file is secure."""
        st = os.stat(self.netrc_file)
        grp_access = bool(st.st_mode & stat.S_IRWXG)
        other_access = bool(st.st_mode & stat.S_IRWXO)
        if grp_access or other_access:
            msg = 'Wrong permissions on %s. Only user should have access.'
            raise DaxNetrcError(msg % self.netrc_file)

    def is_empty(self):
        """ Return True if no host stored."""
        return len(list(self.netrc_obj.hosts.keys())) == 0

    def has_host(self, host):
        """ Return True if host present."""
        return host in list(self.netrc_obj.hosts.keys())

    def add_host(self, host, user, pwd):
        """ Adding host to daxnetrc file."""
        netrc_template = \
"""machine {host}
login {user}
password {pwd}
"""
        parsed_host = urlparse(host).hostname

        with open(self.netrc_file, "a") as f_netrc:
            lines = netrc_template.format(host=parsed_host, user=user, pwd=pwd)
            f_netrc.writelines(lines)

    def get_hosts(self):
        """ Rerutn list of hosts from netrc file."""
        return list(self.netrc_obj.hosts.keys())

    def get_login(self, host):
        """ Getting login for a host from .netrc file."""
        parsed_host = urlparse(host).hostname

        netrc_info = self.netrc_obj.authenticators(parsed_host)
        if not netrc_info:
            msg = 'Host {} not found in netrc file.'.format(host)
            raise DaxNetrcError(msg)

        return netrc_info[0], netrc_info[2]


class DAX_Settings(object):
    def __init__(self):
        pass

    def get_user_home(self):
        return os.path.expanduser('~')

    def get_xsitype_include(self):
        return ['proc:genProcData']

    def get_cmd_submit(self):
        return SLURM_SUBMIT

    def get_prefix_jobid(self):
        return 'Submitted batch job'

    def get_suffix_jobid(self):
        return ''

    def get_cmd_count_nb_jobs(self):
        return SLURM_COUNTJOBS

    def get_cmd_count_jobs_launched(self):
        return SLURM_COUNTJOBS_LAUNCHED

    def get_cmd_count_jobs_pending(self):
        return SLURM_COUNTJOBS_PENDING

    def get_cmd_count_pendinguploads(self):
        return Template(SLURM_COUNT_PENDINGUPLOADS)

    def get_cmd_get_job_status(self):
        return Template(SLURM_JOBSTATUS)

    def get_queue_status(self):
        return SLURM_QUEUED

    def get_running_status(self):
        return SLURM_RUNNING

    def get_complete_status(self):
        return SLURM_COMPLETE

    def get_cmd_get_job_memory(self):
        return Template(SLURM_JOBMEM)

    def get_cmd_get_job_walltime(self):
        return Template(SLURM_JOBTIME)

    def get_cmd_get_job_node(self):
        return Template(SLURM_JOBNODE)

    def get_job_extension_file(self):
        return SLURM_EXT

    def get_root_job_dir(self):
        return '/tmp'

    def get_launcher_type(self):
        return 'diskq-combined'

    def get_use_reference(self):
        return False

    def get_email_opts(self):
        return 'FAIL'

    def get_job_template(self, filepath):
        filepath = os.path.expanduser(filepath)

        with open(filepath, 'r') as f:
            data = f.read()

        return Template(data)
