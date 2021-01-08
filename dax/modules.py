""" Module classes for Scan and Sessions """

from datetime import datetime
import logging
import os
import shutil

from . import XnatUtils
from .dax_settings import DAX_Settings
from . import utilities


__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ['Module', 'ScanModule', 'SessionModule']
DAX_SETTINGS = DAX_Settings()
# Logger for logs
LOGGER = logging.getLogger('dax')


class Module(object):
    """ Object Module to create a module for DAX
        Module runs directly during a build on a session or scan
        to generate inputs data for scans/sessions
    """
    def __init__(self, mod_name, directory, email, text_report, smtp_host=None):
        """
        Entry point of the Base Module Class.

        :param mod_name: Name of the module
        :param directory: Temp directory to store data
        :param email: email address to send report
        :param text_report: string to write for report email
        :return: None
        """
        self.mod_name = mod_name
        self.directory = directory
        self.email = XnatUtils.get_input_list(input_val=email,
                                              default_val=None)
        self.text_report = text_report
        self.send_an_email = 0
        self.smtp_host = smtp_host

    def needs_run(self):
        """
        Check if the module needs to run
        Implemented in derived classes.

        :return: True if it does, False otherwise
        """
        raise NotImplementedError()

    def prerun(self):
        """
        Method to run before looping on a project
        Implemented in derived classes.

        :return: None
        """
        raise NotImplementedError()

    def afterrun(self):
        """
        Method to run after looping on a project
        Implemented in derived classes.

        :return: None
        """
        raise NotImplementedError()

    def report(self, string):
        """
        Add report to an email and send it at the end of the module

        :param string: string to add to the email
        :return: None
        """
        self.text_report += """  -{content}\n""".format(content=string)
        self.send_an_email = 1

    def get_report(self):
        """
        Get the report text

        :return: text_report variable
        """
        return self.text_report

    def make_dir(self, suffix=''):
        """
        Create the tmp directory for the modules

        :param suffix: suffix to add to the directory name
        :return: None
        """
        # add the suffix if one to the directory:
        if suffix:
            if suffix not in self.directory:
                self.directory = '%s_%s' % (self.directory.rstrip('/'), suffix)

        # Check if the directory exists
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        else:
            if suffix:
                self.clean_directory()
            else:
                today = datetime.now()
                dir_format = "%s_tmp_%s_%s_%s_%s_%s_%s"""
                fname = dir_format % (self.mod_name,
                                      str(today.year),
                                      str(today.month),
                                      str(today.day),
                                      str(today.hour),
                                      str(today.minute),
                                      str(today.second))
                self.directory = os.path.join(self.directory, fname)

                if not os.path.exists(self.directory):
                    os.makedirs(self.directory)
                else:
                    self.clean_directory()

    def getname(self):
        """ get the name of the module """
        return self.mod_name

    def clean_directory(self):
        """ Clean the tmp directory """
        for fname in os.listdir(self.directory):
            fpath = os.path.join(self.directory, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)
            else:
                shutil.rmtree(fpath)

    def send_report(self, subject=None):
        """
        Email the report

        :param subject: subject to set for the email.
                        Default: **ERROR/WARNING for modname**
        :return: None
        """
        if self.smtp_host and self.email:
            if not subject:
                subject = "** ERROR/WARNING for {} **".format(self.mod_name)

            utilities.send_email_netrc(
                self.smtp_host, self.email, subject, self.text_report)


class ScanModule(Module):
    """ Module running on a scan """
    def __init__(self, mod_name, directory, email, text_report):
        """
        Entry point of the derived Module Class for Scan level.

        :param mod_name: Name of the module
        :param directory: Temp directory to store data
        :param email: email address to send report
        :param text_report: string to write for report email
        :return: None
        """
        super(ScanModule, self).__init__(mod_name, directory, email,
                                         text_report)

    def run(self):
        """
        Method to run on one scan
        Implemented in classes.

        :return: None
        """
        raise NotImplementedError()

    def log_warning_error(self, message, scan_info, error=False):
        """
        Print warning or error for a project/subject/session/scan

        :param message: message to print
        :param scan_info: dictionary e.g. <XnatUtils.CachedImageScan>.info()
        :param error: True if the message is an error and not a warning
        :return: None
        """
        error_format = 'ERROR: %s for %s/%s/%s/%s'
        warn_format = 'WARNING: %s for %s/%s/%s/%s'
        if error:
            self.report(error_format % (message,
                                        scan_info['project_id'],
                                        scan_info['subject_label'],
                                        scan_info['session_label'],
                                        scan_info['scan_id']))
        else:
            self.report(warn_format % (message,
                                       scan_info['project_id'],
                                       scan_info['subject_label'],
                                       scan_info['session_label'],
                                       scan_info['scan_id']))


class SessionModule(Module):
    """ Module running on a session """
    def __init__(self, mod_name, directory, email, text_report):
        """
        Entry point of the derived Module Class for Session level.

        :param mod_name: Name of the module
        :param directory: Temp directory to store data
        :param email: email address to send report
        :param text_report: string to write for the report email
        :return: None
        """
        super(SessionModule, self).__init__(mod_name, directory, email,
                                            text_report)

    def run(self):
        """
        Method to run on one session.
        Implemented in classes.

        :return: None
        """
        raise NotImplementedError()

    @staticmethod
    def has_flag_resource(csess, flag_resource):
        """
        Check if the session has the flag_resource

        :param csess: CachedImageSession object (see Xnatutils)
        :param flag_resource: resource to verify its existence on XNAT
        :return: True if the resource exists, False otherwise.
        """
        sess_res_list = csess.get_resources()
        flagres_list = [res for res in sess_res_list
                        if res['label'] == flag_resource]
        if len(flagres_list) > 0:
            LOGGER.debug('Already run')
            return False

        return True

    def log_warning_error(self, message, sess_info, error=False):
        """
        Print warning or error for a project/subject/session

        :param message: message to print
        :param sess_info: dictionary e.g. <XnatUtils.CachedImageSession>.info()
        :param error: True if the message is an error and not a warning
        :return: None
        """
        error_format = 'ERROR: %s for %s/%s/%s'
        warn_format = 'WARNING: %s for %s/%s/%s'
        if error:
            self.report(error_format.format(message,
                                            sess_info['project_id'],
                                            sess_info['subject_label'],
                                            sess_info['session_label']))
        else:
            self.report(warn_format.format(message,
                                           sess_info['project_id'],
                                           sess_info['subject_label'],
                                           sess_info['session_label']))


def modules_by_type(mod_list):
    """
    Method to separate scan modules from session modules

    :param mod_list: list of scan/session modules classes.
    :return: list of session modules, list of scan modules
    """
    sess_mod_list = list()
    scan_mod_list = list()

    # Build list of processors by type
    if mod_list is not None:
        for mod in mod_list:
            if issubclass(mod.__class__, ScanModule):
                scan_mod_list.append(mod)
            elif issubclass(mod.__class__, SessionModule):
                sess_mod_list.append(mod)
            else:
                LOGGER.warn('unknown module type: %s' % mod)

    return sess_mod_list, scan_mod_list
