__author__ = 'damons'

import os
import sys
import ConfigParser
from string import Template

class DAX_Settings(object):
    """
    Class for DAX settings based on INI file.
    Note that dax_settings should be in the home directory.
    """

    def __init__(self, ini_settings_file=os.path.join(os.path.expanduser('~'), '.dax_settings.ini')):
        if not os.path.isfile(ini_settings_file):
            sys.stderr.write('ERROR: file %s not found\n' % ini_settings_file)
            raise OSError

        self.ini_settings_file = ini_settings_file
        self.config_parser = ConfigParser.ConfigParser(allow_no_value=True)
        # Flag for REDCap DAX manager usage.
        self.using_dax_manager = False
        self.__read__()
        self.__isvalid__()

    def __read__(self):
        """
        Read the configuration file

        :except: ConfigParser.MissingSectionHeaderError if [ or ] is missing
        :return: None. config_parser is read in place

        """
        try:
            self.config_parser.read(self.ini_settings_file)
        except ConfigParser.MissingSectionHeaderError as MSHE:
            self._print_error_and_exit('Missing header bracket detected. '
                                       'Please check your file.\n', MSHE)

    def __isvalid__(self):
        """
        Check the ini file to make sure that it has the 3 required sections
        (admin, cluster and redcap)

        :except: ConfigParser.NoSectionError if any of the 3 required sections
         is missing
        :return: None

        """
        try:
            self.config_parser.options('cluster')
        except ConfigParser.NoSectionError as ClusterNSE:
            self._print_error_and_exit('ERROR: missing section "cluster"', ClusterNSE)
        try:
            self.config_parser.options('admin')
        except ConfigParser.NoSectionError as ClusterNSE:
            self._print_error_and_exit('ERROR: missing section "admin"', ClusterNSE)
        try:
            self.config_parser.options('redcap')
        except ConfigParser.NoSectionError as ClusterNSE:
            self._print_error_and_exit('ERROR: missing section "redcap"', ClusterNSE)
        try:
            self.config_parser.options('dax_manager')
            self.using_dax_manager = True
        except ConfigParser.NoSectionError:
            pass

    def get(self, header, key):
        """
        Public getter for any key. Checks to see it's defined and gets the value

        :param header: The header section that is associated with the key
        :param key: String which is a key to to a variable in the ini file
        :except: ConfigParser.NoOptionError if the option does not exist
        :except: ConfigParser.NoSectionError if the section does not exist
        :return: The value of the key. If key not found, none

        """
        value = None
        try:
            value = self.config_parser.get(header, key)
        except ConfigParser.NoOptionError as NOE:
            self._print_error_and_exit('No option %s found in header %s'
                                       % (key, header), NOE)
        except ConfigParser.NoSectionError as NSE:
            self._print_error_and_exit('No header %s found in config file %s'
                                       % (header, self.ini_settings_file), NSE)

        if value == '':
            value = None
        return value

    def iterate_options(self, header, option_list):
        """
        Iterate through the keys to get the values and get a dict out

        :param header: String of the name of the header that has the options to get values for
        :param option_list: list of options mapped to the current status of the config_parser
        :return: dict mapping the key/value pairs

        """
        dict_out = dict()
        for option in option_list:
            dict_out[option] = self.get(header, option)

        return dict_out

    def get_cluster_config(self):
        """
        Method to get all of the key value pairs JUST for the cluster section

        :return: A dictionary of key value pairs for the cluster section

        """

        opts = self.config_parser.options('cluster')
        return self.iterate_options('cluster', opts)

    def get_admin_config(self):
        """
        Method to get all of the key value pairs JUST for the admin section

        :return: A dictionary of key value pairs for the admin section

        """
        opts = self.config_parser.options('admin')
        return self.iterate_options('admin', opts)

    def get_redcap_config(self):
        """
        Method to get all of the key value pairs JUST for the redcap section

        :return: A dictionary of key value pairs for the redcap section

        """
        opts = self.config_parser.options('redcap')
        return self.iterate_options('redcap', opts)

    def get_dax_manager_data_dictionary(self):
        """
        Method to retrieve the dax_manager data dictionary from the ini file

        :return: A dictionary of key value pairs for the dax_manager data
         dictionary, None if self.using_dax_manger is False

        """
        if self.using_dax_manager:
            opts = self.config_parser.options('dax_manager')
            return self.iterate_options('dax_manager', opts)
        else:
            return None

    def _print_error_and_exit(self, simple_message, exception):
        """
        Print an error and exit out of DAX settings. Allow the user to print a
         (hopefully) simpler error message followed by the exception.message

        :param simple_message: String of a simple message to print
        :param exception: The Exception object that was raised
        :return: None

        """
        sys.stderr.write('ERROR: %s %s\n' % (self.ini_settings_file,
                                             simple_message))
        sys.stderr.write('Caught exception %s with message:\n %s' % (exception.__class__,
                                                                     exception.message))
        sys.exit(1)

    # Begin public getters for all values
    #  -- ADMIN section
    def get_user_home(self):
        """
        Get the user_home value from the admin section. If ~,
         return os.path.expanduser('~')

        :return: String of the user_home, None if empty

        """
        user_home = self.get('admin', 'user_home')
        if user_home == '~':
            return os.path.expanduser('~')
        else:
            return user_home

    def get_admin_email(self):
        """
        Get the admin_email value from the admin section

        :return: String of the admin_email, None if emtpy

        """
        return self.get('admin', 'admin_email')

    def get_smtp_host(self):
        """
        Get the smtp_host value from the admin section

        :return: String of the smtp_host, None if emtpy

        """
        return self.get('admin', 'smtp_host')

    def get_smtp_from(self):
        """
        Get the smtp_from value from the admin section

        :return: String of the smtp_from value, None if emtpy

        """
        return self.get('admin', 'smtp_from')

    def get_smtp_pass(self):
        """
        Get the smtp_pass value from the admin section

        :return: String of the smtp_pass value, None if empty

        """
        return self.get('admin', 'smtp_pass')

    # Begin cluster section
    def get_cmd_submit(self):
        """
        Get the cmd_submit value from the cluster section

        :return: String of the cmd_submit value, None if empty

        """
        return self.get('cluster', 'cmd_submit')

    def get_prefix_jobid(self):
        """
        Get the prefix_jobid value from the cluster section

        :return: String of the prefix_jobid value, None if empty

        """
        return self.get('cluster', 'prefix_jobid')

    def get_suffix_jobid(self):
        """
        Get the suffix_jobid value from the cluster section

        :return: String of the suffix_jobid value, None if empty

        """
        return self.get('cluster', 'suffix_jobid')

    def get_cmd_count_nb_jobs(self):
        """
        Get the cmd_count_nb_jobs value from the cluster section.
         NOTE: This should be a relative path to a file up a
         directory in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: String of the command

        """
        filepath = self.get('cluster', 'cmd_count_nb_jobs')
        if filepath is None:
            raise OSError(2, 'cmd_count_nb_jobs is None. Must specify')
        if not os.path.isfile(filepath):
            raise OSError(2, 'cmd_count_bj_jobs file does not exist', filepath)
        return self.read_file_and_return_string(filepath)

    def get_cmd_get_job_status(self):
        """
        Get the cmd_get_job_status value from the cluster section
         NOTE: This should be a relative path to a file up a
         directory in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command

        """
        filepath = self.get('cluster', 'cmd_get_job_status')
        if filepath is None:
            raise OSError(2, 'cmd_get_job_status is None. Must specify')
        if not os.path.isfile(filepath):
            raise OSError(2, 'cmd_get_job_status file does not exist', filepath)
        return self.read_file_and_return_template(filepath)

    def get_queue_status(self):
        """
        Get the queue_status value from the cluster section

        :return: String of the queue_status value, None if empty

        """
        return self.get('cluster', 'queue_status')

    def get_running_status(self):
        """
        Get the running_status value from the cluster section

        :return: String of the running_status value, None if empty

        """
        return self.get('cluster', 'running_status')

    def get_complete_status(self):
        """
        Get the complete_status value from the cluster section

        :return: String of the complete_status value, None if empty

        """
        return self.get('cluster', 'complete_status')

    def get_cmd_get_job_memory(self):
        """
        Get the cmd_get_job_memory value from the cluster section
         NOTE: This should be a relative path to a file up a
         directory in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command

        """
        filepath = self.get('cluster', 'cmd_get_job_memory')
        if filepath is None:
            raise OSError(2, 'cmd_get_job_memory is None. Must specify')
        if not os.path.isfile(filepath):
            raise OSError(2, 'cmd_get_job_memory file does not exist', filepath)
        return self.read_file_and_return_template(filepath)

    def get_cmd_get_job_walltime(self):
        """
        Get the cmd_get_job_walltime value from the cluster section
         NOTE: This should be a relative path to a file up a
         directory in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command

        """
        filepath = self.get('cluster', 'cmd_get_job_walltime')
        if filepath is None:
            raise OSError(2, 'cmd_get_job_walltime is None. Must specify')
        if not os.path.isfile(filepath):
            raise OSError(2, 'cmd_get_job_walltime file does not exist', filepath)
        return self.read_file_and_return_template(filepath)

    def get_cmd_get_job_node(self):
        """
        Get the cmd_get_job_node value from the cluster section
         NOTE: This should be a relative path to a file up a
         directory in templates

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command

        """
        filepath = self.get('cluster', 'cmd_get_job_node')
        if filepath is None:
            raise OSError(2, 'cmd_get_job_node is None. Must specify')
        if not os.path.isfile(filepath):
            raise OSError(2, 'cmd_get_job_node file does not exist', filepath)
        return self.read_file_and_return_template(filepath)

    def get_job_extension_file(self):
        """
        Get the job_extension_file value from the cluster section

        :return: String of the job_extension_file value, None if empty

        """
        return self.get('cluster', 'job_extension_file')

    def get_job_template(self):
        """
        Get the job_template value from the cluster section

        :raise: OSError if the field is empty or if the file doesn't exist
        :return: Template class of the file containing the command

        """
        filepath = self.get('cluster', 'job_template')
        if filepath is None:
            raise OSError(2, 'job_template is None. Must specify')
        if not os.path.isfile(filepath):
            raise OSError(2, 'job_template file does not exist', filepath)
        return self.read_file_and_return_template(filepath)

    def get_email_opts(self):
        """
        Get the email_opts value from the cluster section

        :return: String of the email_opts value, None if empty

        """
        return self.get('cluster', 'email_opts')

    def get_gateway(self):
        """
        Get the gateway value from the cluster section

        :return: String of the gateway value, None if empty

        """
        return self.get('cluster', 'gateway')

    def get_root_job_dir(self):
        """
        Get the root_job_dir value from the cluster section

        :return: String of the root_job_dir value, None if empty

        """
        return self.get('cluster', 'root_job_dir')

    def get_queue_limit(self):
        """
        Get the queue_limit value from the cluster section

        :return: int of the queue_limit value, None if empty

        """
        return int(self.get('cluster', 'queue_limit'))

    def get_results_dir(self):
        """
        Get the results_dir value from the cluster section

        :return: String of the results_dir value, None if empty

        """
        return self.get('cluster', 'results_dir')

    def get_max_age(self):
        """
        Get the max_age value from the cluster section

        :return: int of the max_age value, None if empty

        """
        return int(self.get('cluster', 'max_age'))

    # redcap section
    def get_api_url(self):
        """
        Get the api_url value from the cluster section

        :return: String of the api_url value, None if empty

        """
        return self.get('redcap', 'api_url')

    def get_api_key_dax(self):
        """
        Get the api_key_dax value from the cluster section

        :return: String of the api_key_dax value, None if empty

        """
        return self.get('redcap', 'api_key_dax')

    def get_api_key_xnat(self):
        """
        Get the api_key_xnat value from the cluster section

        :return: String of the api_key_xnat value, None if empty

        """
        return self.get('redcap', 'api_key_xnat')

    @staticmethod
    def read_file_and_return_template(filepath):
        """
        Reads a a file and returns the string as a string Template

        :param filepath: the file to read, already checked for existance
        :raise: OSError if the file is emtpy
        :return: Template for the command in the file

        """
        with open(filepath, 'r') as f:
            data = f.read()
        if data is None or data == '':
            raise OSError(2, 'No data in file', filepath)
        return Template(data)

    @staticmethod
    def read_file_and_return_string(filepath):
        """
        Reads a a file and returns the string in it

        :param filepath: the file to read, already checked for existance
        :raise: OSError if the file is emtpy
        :return: String of data in text file

        """
        with open(filepath, 'r') as f:
            data = f.read()
        if data is None or data == '':
            raise OSError(2, 'No data in file', filepath)
        return data

