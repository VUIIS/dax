""" Module classes for Scan and Sessions """
import os
import shutil
import smtplib
import logging
import XnatUtils
from datetime import datetime
from email.mime.text import MIMEText
from .dax_settings import SMTP_HOST, SMTP_FROM, SMTP_PASS

#Logger for logs
LOGGER = logging.getLogger('dax')

class Module(object):
    """ Object Module to create a module for DAX
        Module runs directly during a build on a session or scan
        to generate inputs data for scans/sessions
    """
    def __init__(self, mod_name, directory, email, text_report):
        """ Init function """
        self.mod_name = mod_name
        self.directory = directory
        self.email = XnatUtils.get_input_list(input_val=email, default_val=None)
        self.text_report = text_report
        self.send_an_email = 0

    def needs_run(self):
        """ return true if the module needs to run on a scan/session """
        raise NotImplementedError()

    def prerun(self):
        """ code to run before looping on a project """
        raise NotImplementedError()

    def afterrun(self):
        """ code to run after looping on a project """
        raise NotImplementedError()

    def report(self, string):
        """ add report to the text to email at the end of the module """
        self.text_report += """  -{content}\n""".format(content=string)
        self.send_an_email = 1

    def get_report(self):
        """ get the report text """
        return self.text_report

    def make_dir(self, suffix=''):
        """ create the tmp directory for the modules """
        #add the suffix if one to the directory:
        if suffix:
            if not suffix in self.directory:
                self.directory = self.directory.rstrip('/')+'_'+suffix

        #Check if the directory exists
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        else:
            if suffix:
                self.clean_directory()
            else:
                today = datetime.now()
                dir_format = """{modname}_tmp_{year}_{month}_{day}_{hour}_{minute}_{second}"""
                fname = dir_format.format(modname=self.mod_name,
                                          year=str(today.year),
                                          month=str(today.month),
                                          day=str(today.day),
                                          hour=str(today.hour),
                                          minute=str(today.minute),
                                          second=str(today.second))
                self.directory = os.path.join(self.directory, fname)

                if not os.path.exists(self.directory):
                    os.mkdir(self.directory)
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
        """ email the report """
        if SMTP_HOST and SMTP_FROM and SMTP_PASS and self.email:
            # Create the container (outer) email message.
            msg = MIMEText(self.text_report)
            if not subject:
                subject = """**ERROR/WARNING for {modname}**""".format(modname=self.mod_name)
            msg['Subject'] = subject
            # me == the sender's email address
            # family = the list of all recipients' email addresses
            msg['From'] = SMTP_FROM
            msg['To'] = ",".join(self.email)
            # Send the email via our own SMTP server.
            smtp = smtplib.SMTP(SMTP_HOST)
            smtp.starttls()
            smtp.login(SMTP_FROM, SMTP_PASS)
            smtp.sendmail(SMTP_FROM, self.email, msg.as_string())
            smtp.quit()

class ScanModule(Module):
    """ Module running on a scan """
    def __init__(self, mod_name, directory, email, text_report):
        """ Overridden Module init function """
        super(ScanModule, self).__init__(mod_name, directory, email, text_report)

    def run(self):
        """ code to run on one scan"""
        raise NotImplementedError()

    def log_warning_error(self, message, scan_info, error=False):
        """ print warning or error for a project/subject/session/scan"""
        error_format = '''ERROR: {message} for {project}/{subject}/{session}/{scan}'''
        warn_format = '''WARNING: {message} for {project}/{subject}/{session}/{scan}'''
        if error:
            self.report(error_format.format(message=message,
                                            project=scan_info['project_id'],
                                            subject=scan_info['subject_label'],
                                            session=scan_info['session_label'],
                                            scan=scan_info['scan_id']))
        else:
            self.report(warn_format.format(message=message,
                                           project=scan_info['project_id'],
                                           subject=scan_info['subject_label'],
                                           session=scan_info['session_label'],
                                           scan=scan_info['scan_id']))

class SessionModule(Module):
    """ Module running on a session """
    def __init__(self, mod_name, directory, email, text_report):
        """ Overridden Module init function """
        super(SessionModule, self).__init__(mod_name, directory, email, text_report)

    def run(self):
        """ code to run on one session"""
        raise NotImplementedError()

    @staticmethod
    def has_flag_resource(csess, flag_resource):
        """ check if the session has the flag_resource """
        sess_res_list = csess.get_resources()
        flagres_list = [res for res in sess_res_list if res['label'] == flag_resource]
        if len(flagres_list) > 0:
            LOGGER.debug('Already run')
            return False

        return True

    def log_warning_error(self, message, sess_info, error=False):
        """ print warning or error for a project/subject/session"""
        error_format = '''ERROR: {message} for {project}/{subject}/{session}'''
        warn_format = '''WARNING: {message} for {project}/{subject}/{session}'''
        if error:
            self.report(error_format.format(message=message,
                                            project=sess_info['project_id'],
                                            subject=sess_info['subject_label'],
                                            session=sess_info['session_label']))
        else:
            self.report(warn_format.format(message=message,
                                           project=sess_info['project_id'],
                                           subject=sess_info['subject_label'],
                                           session=sess_info['session_label']))

def modules_by_type(mod_list):
    exp_mod_list = list()
    scan_mod_list = list()

    # Build list of processors by type
    for mod in mod_list:
        if issubclass(mod.__class__, ScanModule):
            scan_mod_list.append(mod)
        elif issubclass(mod.__class__, SessionModule):
            exp_mod_list.append(mod)
        else:
            LOGGER.warn('unknown module type:'+mod)

    return exp_mod_list, scan_mod_list
