"""dax_settings class to read the INI settings file."""

from future import standard_library
standard_library.install_aliases()

from builtins import object
from collections import OrderedDict
import configparser
from importlib import import_module
import os
import stat
from string import Template
import sys
import netrc

from .errors import DaxNetrcError


__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ["DAX_Netrc", "DAX_Settings", "DEFAULT_DATATYPE",
           "DEFAULT_FS_DATATYPE"]

DEFAULT_TEMPLATE = Template("""echo """)
FILES_OPTIONS = ['cmd_count_nb_jobs', 'cmd_get_job_status',
                 'cmd_get_job_memory', 'cmd_get_job_walltime',
                 'cmd_get_job_node', 'job_template']
# Assessor datatypes
DEFAULT_FS_DATATYPE = 'fs:fsData'
DEFAULT_DATATYPE = 'proc:genProcData'
DAX_MANAGER_DEFAULTS = OrderedDict([
    ('api_url', ''),
    ('api_key_dax', ''),
    ('project', 'dax_project'),
    ('settingsfile', 'dax_settings_full_path'),
    ('masimatlab', 'dax_masimatlab'),
    ('tmp', 'dax_tmp_directory'),
    ('logsdir', 'dax_logs_path'),
    ('user', 'dax_cluster_user'),
    ('gateway', 'dax_gateway'),
    ('email', 'dax_cluster_email'),
    ('queue', 'dax_queue_limit'),
    ('priority', 'dax_proj_order'),
    ('email_opts', 'dax_job_email_options'),
    ('dax_build_start_date', 'dax_build_start_date'),
    ('dax_build_end_date', 'dax_build_end_date'),
    ('dax_build_pid', 'dax_build_pid'),
    ('dax_update_tasks_start_date', 'dax_update_tasks_start_date'),
    ('dax_update_tasks_end_date', 'dax_update_tasks_end_date'),
    ('dax_update_tasks_pid', 'dax_update_tasks_pid'),
    ('dax_launch_start_date', 'dax_launch_start_date'),
    ('dax_launch_end_date', 'dax_launch_end_date'),
    ('dax_launch_pid', 'dax_launch_pid'),
    ('max_age', 'dax_max_age'),
    ('admin_email', 'dax_email_address')])


class DAX_Netrc(object):
    """Class for DAX NETRC file containing the information about XNAT logins.
    """
    def __init__(self):
        self.netrc_file = os.path.join(os.path.expanduser('~'), '.daxnetrc')
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
            msg = 'Wrong permission on %s file. Only you should have read and \
write access.'
            raise DaxNetrcError(msg % self.netrc_file)

    def is_empty(self):
        """ Return True if no host stored."""
        return len(list(self.netrc_obj.hosts.keys())) == 0

    def has_host(self, host):
        """ Return True if host present."""
        return host in list(self.netrc_obj.hosts.keys())

    def add_host(self, host, user, pwd):
        """ Adding host to daxnetrc file."""
        netrc_template = """machine {host}
    login {user}
    password {pwd}
        """
        with open(self.netrc_file, "a") as f_netrc:
            lines = netrc_template.format(host=host, user=user, pwd=pwd)
            f_netrc.writelines(lines)

    def get_hosts(self):
        """ Rerutn list of hosts from netrc file."""
        return list(self.netrc_obj.hosts.keys())

    def get_login(self, host):
        """ Getting login for an host from daxnetrc file."""
        netrc_info = self.netrc_obj.authenticators(host)
        if not netrc_info:
            raise DaxNetrcError('Host <%s> not found in %s file. \
Please run dax_setup or XnatCheckLogin to add host.' % (host, self.netrc_file))
        return netrc_info[0], netrc_info[2]


class DAX_Settings(object):
    """Class for DAX settings based on INI file.

    Note that dax_settings should be in the home directory.
    """

    def __init__(self, ini_settings_file=os.path.join(os.path.expanduser('~'),
                                                      '.dax_settings.ini')):
        """Entry Point for Class Dax_settings."""
        # Variables
        self.ini_settings_file = ini_settings_file
        self.config_parser = configparser.SafeConfigParser(allow_no_value=True)

        if self.exists():
            self.__read__()
        else:
            sys.stdout.write('Warning: No settings.ini file found.')

    def exists(self):
        """Check if ini file exists.

        :return: True if exists, False otherwise
        """
        return os.path.isfile(self.ini_settings_file)

    def __read__(self):
        """Read the configuration file.

        :except: ConfigParser.MissingSectionHeaderError if [ or ] is missing
        :return: None. config_parser is read in place
        """
        try:
            self.config_parser.read(self.ini_settings_file)
        except configparser.MissingSectionHeaderError as MSHE:
            self._print_error_as_warning('Missing header bracket detected. '
                                         'Please check your file.\n', MSHE)

    def is_cluster_valid(self):
        """Check cluster section.

        :return: True if valid settings, False otherwise
        """
        if self.config_parser.has_section('cluster'):
            for option in FILES_OPTIONS:
                file_path = self.config_parser.get('cluster', option)
                if not file_path:
                    sys.stdout.write('Warning: option \
%s not set in settings.\n' % (option))
                    return False
                elif not os.path.isfile(file_path):
                    sys.stdout.write('Warning: %s not found for option \
%s in settings.\n' % (file_path, option))
                    return False
        else:
            return False
        return True

    def load_code_path(self):
        """Check code_path section.

        Try to load all the files in the folder.
        If it fails, print warning (need to fix the spider/processor/module).
        :return: None
        """
        if self.config_parser.has_section('code_path'):
            for option in self.config_parser.options('code_path'):
                dir_path = self.config_parser.get('code_path', option)
                if os.path.isdir(dir_path):
                    li_files = list()
                    for root, _, fnames in os.walk(dir_path):
                        li_files.extend([os.path.join(root, f) for f in fnames
                                         if f.lower().endswith('.py')])
                    for python_file in li_files:
                        self.load_python_file(python_file)

    def load_python_file(self, python_file):
        """Load python file from processors/spiders/modules files."""
        filename = os.path.basename(python_file.lower())
        if 'processor' in filename or\
           'module' in filename or\
           'spider' in filename:
            init_dir = os.getcwd()
            os.chdir(os.path.dirname(python_file))
            try:
                import_module(os.path.basename(python_file)[:-3])
            except Exception as e:
                sys.stdout.write('Warning: Failed to load %s because %s.\n'
                                 % (os.path.basename(python_file), e))
            os.chdir(init_dir)

    def is_dax_manager_valid(self):
        """Check dax_manager section.

        Check that all the options are present.
        Check that the option api_url and api_key_dax are not None.
        :return: True if valid settings, False otherwise
        """
        if self.config_parser.has_section('dax_manager'):
            for option in list(DAX_MANAGER_DEFAULTS.keys()):
                if option not in self.config_parser.options('dax_manager'):
                    sys.stderr.write('Error: %s option missing in \
~/.dax_settings.ini.\n'
                                     % option)
                    return False
            if not self.get('dax_manager', 'api_url') and \
               not self.get('dax_manager', 'api_key_dax'):
                sys.stderr.write('Error: api_url or api_key_dax not set in \
~/.dax_settings.ini.\n')
                return False
        else:
            return False

        return True

    def get(self, header, key):
        """Public getter for any key.

        Checks to see it's defined and gets the value
        :param header: The header section that is associated with the key
        :param key: String which is a key to to a variable in the ini file
        :except: ConfigParser.NoOptionError if the option does not exist
        :except: ConfigParser.NoSectionError if the section does not exist
        :return: The value of the key. If key not found, none

        """
        value = None
        try:
            value = self.config_parser.get(header, key)
        except configparser.NoOptionError as NOE:
            self._print_error_as_warning('No option %s found in header %s'
                                         % (key, header), NOE)
        except configparser.NoSectionError as NSE:
            self._print_error_as_warning('No header %s found in config file %s'
                                         % (header, self.ini_settings_file),
                                         NSE)

        if value == '':
            value = None
        return value

    def iterate_options(self, header, option_list):
        """Iterate through the keys to get the values and get a dict out.

        :param header: String of the name of the header that has the options
                       to get values for
        :param option_list: list of options mapped to the current status of
                            the config_parser
        :return: dict mapping the key/value pairs

        """
        dict_out = dict()
        for option in option_list:
            dict_out[option] = self.get(header, option)

        return dict_out

    def get_cluster_config(self):
        """Method to get all of the key value pairs for the cluster section.

        :return: A dictionary of key value pairs for the cluster section
        """
        opts = self.config_parser.options('cluster')
        return self.iterate_options('cluster', opts)

    def get_admin_config(self):
        """Method to get all of the key value pairs for the admin section.

        :return: A dictionary of key value pairs for the admin section
        """
        opts = self.config_parser.options('admin')
        return self.iterate_options('admin', opts)

    def get_code_path_config(self):
        """Method to get all of the key value pairs for the code_path section.

        :return: A dictionary of key value pairs for the code_path section
        """
        opts = self.config_parser.options('code_path')
        return self.iterate_options('code_path', opts)

    def get_dax_manager_config(self):
        """Method to get all of the key value pairs for the dax_manager section.

        :return: A dictionary of key value pairs for the dax_manager data
         dictionary, None if self.using_dax_manger is False

        """
        opts = self.config_parser.options('dax_manager')
        return self.iterate_options('dax_manager', opts)

    def _print_error_as_warning(self, simple_message, exception):
        """Print an error and exit out of DAX settings.

        Allow the user to print a (hopefully) simpler error message
        followed by the exception.message

        :param simple_message: String of a simple message to print
        :param exception: The Exception object that was raised
        :return: None
        """
        sys.stdout.write('Warning: %s %s\n' % (self.ini_settings_file,
                                               simple_message))
        # sys.stdout.write('Caught exception %s with message:\n %s'
        #                 % (exception.__class__, exception.message))

    # Begin public getters for all values
    #  -- ADMIN section
    def get_user_home(self):
        """Get the user_home value from the admin section.

        If ~, return os.path.expanduser('~')

        :return: String of the user_home, None if empty
        """
        user_home = self.get('admin', 'user_home')
        if user_home == '~':
            return os.path.expanduser('~')
        else:
            return user_home

    def get_admin_email(self):
        """Get the admin_email value from the admin section.

        :return: String of the admin_email, None if emtpy
        """
        return self.get('admin', 'admin_email')

    def get_smtp_host(self):
        """Get the smtp_host value from the admin section.

        :return: String of the smtp_host, None if emtpy
        """
        return self.get('admin', 'smtp_host')

    def get_smtp_from(self):
        """Get the smtp_from value from the admin section.

        :return: String of the smtp_from value, None if emtpy
        """
        return self.get('admin', 'smtp_from')

    def get_smtp_pass(self):
        """Get the smtp_pass value from the admin section.

        :return: String of the smtp_pass value, None if empty
        """
        return self.get('admin', 'smtp_pass')

    def get_xsitype_include(self):
        """Get the xsitype_include value from the admin section.

        :return: List of xsitypes for DAX to check for
        """
        xsitype = self.get('admin', 'xsitype_include')
        if xsitype:
            return xsitype.split(',')
        else:
            return []

    # Begin cluster section
    def get_cmd_submit(self):
        """Get the cmd_submit value from the cluster section.

        :return: String of the cmd_submit value, None if empty
        """
        return self.get('cluster', 'cmd_submit')

    def get_prefix_jobid(self):
        """Get the prefix_jobid value from the cluster section.

        :return: String of the prefix_jobid value, None if empty
        """
        return self.get('cluster', 'prefix_jobid')

    def get_suffix_jobid(self):
        """Get the suffix_jobid value from the cluster section.

        :return: String of the suffix_jobid value, None if empty
        """
        return self.get('cluster', 'suffix_jobid')

    def get_cmd_count_nb_jobs(self):
        """Get the cmd_count_nb_jobs value from the cluster section.

        NOTE: This should be a relative path to a file up a directory
         in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: String of the command
        """
        filepath = self.get('cluster', 'cmd_count_nb_jobs')
        if filepath is None:
            return ''
        if filepath.startswith('~/'):
            filepath = os.path.join(self.get_user_home(), filepath)
        if not os.path.isfile(filepath):
            return ''
        return self.read_file_and_return_string(filepath)

    def get_cmd_get_job_status(self):
        """Get the cmd_get_job_status value from the cluster section.

        NOTE: This should be a relative path to a file up a directory
         in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command

        """
        filepath = self.get('cluster', 'cmd_get_job_status')
        if filepath is None:
            return ''
        if filepath.startswith('~/'):
            filepath = os.path.join(self.get_user_home(), filepath)
        if not os.path.isfile(filepath):
            return ''
        return self.read_file_and_return_template(filepath)

    def get_queue_status(self):
        """Get the queue_status value from the cluster section.

        :return: String of the queue_status value, None if empty
        """
        return self.get('cluster', 'queue_status')

    def get_running_status(self):
        """Get the running_status value from the cluster section.

        :return: String of the running_status value, None if empty
        """
        return self.get('cluster', 'running_status')

    def get_complete_status(self):
        """Get the complete_status value from the cluster section.

        :return: String of the complete_status value, None if empty
        """
        return self.get('cluster', 'complete_status')

    def get_cmd_get_job_memory(self):
        """Get the cmd_get_job_memory value from the cluster section.

        NOTE: This should be a relative path to a file up a directory
         in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command
        """
        filepath = self.get('cluster', 'cmd_get_job_memory')
        if filepath is None:  # no files specify, set to echo
            return DEFAULT_TEMPLATE
        if filepath.startswith('~/'):
            filepath = os.path.join(self.get_user_home(), filepath)
        if not os.path.isfile(filepath):
            return ''
        return self.read_file_and_return_template(filepath)

    def get_cmd_get_job_walltime(self):
        """Get the cmd_get_job_walltime value from the cluster section.

        NOTE: This should be a relative path to a file up a directory
         in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command
        """
        filepath = self.get('cluster', 'cmd_get_job_walltime')
        if filepath is None:  # no files specify, set to echo
            return DEFAULT_TEMPLATE
        if filepath.startswith('~/'):
            filepath = os.path.join(self.get_user_home(), filepath)
        if not os.path.isfile(filepath):
            return ''
        return self.read_file_and_return_template(filepath)

    def get_cmd_get_job_node(self):
        """Get the cmd_get_job_node value from the cluster section.

        NOTE: This should be a relative path to a file up a directory
         in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command
        """
        filepath = self.get('cluster', 'cmd_get_job_node')
        if filepath is None:  # no files specify, set to echo
            return DEFAULT_TEMPLATE
        if filepath.startswith('~/'):
            filepath = os.path.join(self.get_user_home(), filepath)
        if not os.path.isfile(filepath):
            return ''
        return self.read_file_and_return_template(filepath)

    def get_job_extension_file(self):
        """Get the job_extension_file value from the cluster section.

        :return: String of the job_extension_file value, None if empty
        """
        return self.get('cluster', 'job_extension_file')

    def get_job_template(self):
        """Get the job_template value from the cluster section.

        NOTE: This should be a relative path to a file up a directory
         in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command
        """
        filepath = self.get('cluster', 'job_template')
        if filepath is None:
            return ''
        if filepath.startswith('~/'):
            filepath = os.path.join(self.get_user_home(), filepath)
        if not os.path.isfile(filepath):
            return ''
        return self.read_file_and_return_template(filepath)

    def get_email_opts(self):
        """Get the email_opts value from the cluster section.

        :return: String of the email_opts value, None if empty
        """
        return self.get('cluster', 'email_opts')

    def get_gateway(self):
        """Get the gateway value from the cluster section.

        :return: String of the gateway value, None if empty
        """
        return self.get('cluster', 'gateway')

    def get_root_job_dir(self):
        """Get the root_job_dir value from the cluster section.

        :return: String of the root_job_dir value, None if empty
        """
        return self.get('cluster', 'root_job_dir')

    def get_queue_limit(self):
        """Get the queue_limit value from the cluster section.

        :return: int of the queue_limit value, None if empty
        """
        if self.get('cluster', 'queue_limit'):
            return int(self.get('cluster', 'queue_limit'))
        else:
            return 14

    def get_results_dir(self):
        """Get the results_dir value from the cluster section.

        :return: String of the results_dir value, None if empty
        """
        resultsdir = self.get('cluster', 'results_dir')
        if resultsdir is None:
            resultsdir = '/tmp'
        if resultsdir.startswith('~'):
            return os.path.join(os.path.expanduser('~'), resultsdir[2:])
        else:
            return resultsdir

    def get_max_age(self):
        """Get the max_age value from the cluster section.

        :return: int of the max_age value, None if empty
        """
        return int(self.get('cluster', 'max_age'))

    def get_skip_lastupdate(self):
        """Get the skip_lastupdate value from the cluster section.

        :return: skip_lastupdate value
        """
        return self.get('cluster', 'skip_lastupdate')

    def get_launcher_type(self):
        """
        Get the launcher type from the cluster

        :return: String of the launcher type: xnatq-combined, diskq-xnat,
                 diskq-cluster

        """
        return self.get('cluster', 'launcher_type')

    def get_api_url(self):
        """Get the api_url value from the dax_manager section.

        :return: String of the api_url value, None if empty
        """
        return self.get('dax_manager', 'api_url')

    def get_api_key_dax(self):
        """Get the api_key_dax value from the dax_manager section.

        :return: String of the api_key_dax value, None if empty
        """
        return self.get('dax_manager', 'api_key_dax')

    @staticmethod
    def read_file_and_return_template(filepath):
        """Reads a a file and returns the string as a string Template.

        :param filepath: the file to read, already checked for existance
        :raise: OSError if the file is emtpy
        :return: Template for the command in the file
        """
        with open(filepath, 'r') as f:
            data = f.read()
        if data is None or data == '':
            return ''
        return Template(data)

    @staticmethod
    def read_file_and_return_string(filepath):
        """Reads a a file and returns the string in it.

        :param filepath: the file to read, already checked for existance
        :raise: OSError if the file is emtpy
        :return: String of data in text file
        """
        with open(filepath, 'r') as f:
            data = f.read()
        if data is None or data == '':
            return ''
        return data
