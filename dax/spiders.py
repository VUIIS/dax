"""
    Title: spiders.py
    Author: Benjamin Yvernault
    contact: b.yvernault@ucl.ac.uk
    Purpose:
        Spider base class and class for Scan and Session spider
        Spider name must be: Spider_[name]_v[version].py
        Utils for spiders
"""

__author__ = 'Benjamin Yvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Spider base class, Scan and Session spider class, and Utils for spiders."
__version__ = '1.0.0'
__modifications__ = '26 August 2015 - Original write'

import os
import re
import sys
import time
import getpass
import collections
from dax import XnatUtils
from datetime import datetime

class Spider(object):
    """
        Base class for spider

        :param spider_path: spider file path
        :param jobdir: directory for temporary files
        :param xnat_project: project ID on XNAT
        :param xnat_subject: subject label on XNAT
        :param xnat_session: experiment label on XNAT
        :param xnat_host: host for XNAT if not set in environment variables
        :param xnat_user: user for XNAT if not set in environment variables
        :param xnat_pass: password for XNAT if not set in environment variables
        :param suffix: suffix to the assessor creation
    """
    def __init__(self, spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix=""):
        # Spider path:
        self.spider_path = spider_path
        # directory for temporary files + create it
        self.jobdir = XnatUtils.makedir(os.path.abspath(jobdir))
        # to copy results at the end
        self.spider_handler = None
        # Xnat info:
        self.xnat_project = xnat_project
        self.xnat_subject = xnat_subject
        self.xnat_session = xnat_session
        # Xnat connection settings:
        self.host = self.get_default_value("host", "XNAT_HOST", xnat_host)
        self.user = self.get_default_value("user", "XNAT_USER", xnat_user)
        self.pwd = self.get_pwd(xnat_pass, xnat_user)
        # Suffix
        if not suffix:
            self.suffix = ""
        else:
            # Set the suffix_proc remove any special characters and replace by '_'
            self.suffix = re.sub('[^a-zA-Z0-9]', '_', suffix)
            # Replace multiple underscores by one
            self.suffix = re.sub('_+', '_', self.suffix)
            # Remove underscore if at the end of suffix
            if self.suffix[-1] == '_': self.suffix = self.suffix[:-1]
            # Add an underscore at the beginning if not present
            if self.suffix[0] != '_': self.suffix = '_'+self.suffix
        # print time writer:
        self.time_writer = TimedWriter()
        # Export the variable:
        os.environ['XNAT_HOST'] = self.host
        os.environ['XNAT_USER'] = self.user
        os.environ['XNAT_PASS'] = self.pwd

    def get_default_value(self, variable, env_name, value):
        """
            Return the default value for the variable:
                if arg not NULL
                else env variables define by arguments

            :param variable: variable name
            :param env_name: name of the environment variable
            :param value:    value given by the user
            :return: default value
        """
        if value:
            return value
        else:
            if env_name in os.environ and os.environ[env_name]!="":
                return os.environ[env_name]
            else:
                err = "%s not set by user." % (env_name)
                err += "\nTo set it choose one of this solution:"
                err += "\n\tSet the option --%s in the spider class" % (variable)
                err += "\n\tSet the environment variable %s" % (env_name)
                raise ValueError(err)

    def get_pwd(self, pwd, user):
        """
            Return the password from env or ask user if the user was set

            :param pwd: password
            :param user: user
            :return: default value
        """
        if pwd:
            return pwd
        else:
            if user:
                msg = "Enter the password for user '%s' on your XNAT -- %s :" % (user, self.host)
                return getpass.getpass(prompt=msg)
            else:
                if "XNAT_PASS" in os.environ and os.environ["XNAT_PASS"]!="":
                    return os.environ["XNAT_PASS"]
                else:
                    err = "XNAT_PASS not set by user."
                    err += "\n\t   Set the environment variable XNAT_PASS"
                    raise ValueError(err)

    def select_obj(self, intf, obj_label, resource):
        """
            Select scan or assessor resource

            :param obj_label: xnat object label (scan ID or assessor label)
            :param resource: folder name under the xnat object
            return pyxnat object
        """
        tmp_dict = collections.OrderedDict([('project', self.xnat_project),
                                            ('subject', self.xnat_subject),
                                            ('experiment', self.xnat_session)])
        #try on scan
        tmp_dict_scan = tmp_dict
        tmp_dict_scan['scan'] = obj_label
        tmp_dict_scan['resource'] = resource
        xnat_obj = intf.select(self.select_str(tmp_dict_scan))
        if xnat_obj:
            return xnat_obj
        else:
            #else try assessor
            tmp_dict_assessor = tmp_dict
            tmp_dict_assessor['assessor'] = obj_label
            tmp_dict_assessor['out/resource'] = resource
            xnat_obj = intf.select(self.select_str(tmp_dict_assessor))
            if xnat_obj:
                return xnat_obj
            else:
                err = "No XNAT Object found with the following values: "
                err += str(tmp_dict)
                err += "\n scan or assessor: %s / resource: %s " % (obj_label,
                                                                    resource)
                raise ValueError(err)

    def download(self, obj_label, resource, folder):
        """
            Return a python list of the files downloaded for the resource on the scan
                example:
                  download(scan_id, "DICOM", "/Users/test")
                 or
                  download(assessor_label, "DATA", "/Users/test")

            :param obj_label: xnat object label (scan ID or assessor label)
            :param resource: folder name under the xnat object
            :param folder: download directory
            :return: python list of files downloaded
        """
        # Open connection to XNAT
        xnat = XnatUtils.get_interface(host=self.host, user=self.user, pwd=self.pwd)
        resource_obj = self.select_obj(intf=xnat,
                                       obj_label=obj_label,
                                       resource=resource)
        # close connection
        xnat.disconnect()
        return XnatUtils.download_files_from_obj(directory=folder,
                                                 resource_obj=resource_obj)

    def define_spider_process_handler(self):
        """
            Define the SpiderProcessHandler for the end of any spider
        """
        raise NotImplementedError()

    def has_spider_handler(self):
        """
            Init Spider Handler if it was not already created.
        """
        if not self.spider_handler:
            self.define_spider_process_handler()

    def upload(self, fpath, resource):
        """
            upload files to the queue on the cluster to be upload to XNAT by DAX pkg
            E.g:
                spider.upload("/Users/DATA/", "DATA")
                spider.upload("/Users/stats_dir/statistical_measures.txt", "STATS")

            :param fpath: path to the folder/file to be uploaded
            :param resource: folder name to upload to on the assessor
        """
        self.has_spider_handler()
        if os.path.isfile(fpath):
            if resource == 'PDF':
                self.spider_handler.add_pdf(fpath)
            else:
                self.spider_handler.add_file(fpath, resource)
        elif os.path.isdir(fpath):
            self.spider_handler.add_folder(fpath, resource)
        else:
            err = "upload(): file path does not exist: %s" % (fpath)
            raise ValueError(err)

    def upload_dict(self, files_dict):
        """
            upload files to the queue on the cluster to be upload to XNAT by DAX pkg
            following the files python dictionary: {resource_name : fpath}
            E.g:
                fdict = {"DATA" : "/Users/DATA/", "PDF": "/Users/PDF/report.pdf"}
                spider.upload_dict(fdict)

            :param files_dict: python dictionary containing the pair resource/fpath
        """
        self.has_spider_handler()
        for resource, fpath in files_dict.items():
            if isinstance(fpath, str):
                self.upload(fpath, resource)
            elif isinstance(fpath, list):
                for ffpath in fpath:
                    self.upload(ffpath, resource)
            else:
                err = "upload_dict(): variable not recognize in dictionary for resource %s : %s" % (resource, type(fpath))
                raise ValueError(err)

    def end(self):
        """
            Finish the script by sending the end of script flag and cleaning the folder

            :param jobdir: directory for the spider
        """
        self.has_spider_handler()
        self.spider_handler.done()
        self.spider_handler.clean(self.jobdir)
        self.print_end()

    def run(self):
        """
            Method to execute the process
        """
        raise NotImplementedError()

    def finish(self):
        """
            Method to copy the results in the Spider Results folder dax.RESULTS_DIR
        """
        raise NotImplementedError()

    def print_init(self, argument_parse, author, email):
        """
            Print a message to display information on the init parameters, author,
            email, and arguments using time writer

            :param argument_parse: argument parser
            :param author: author of the spider
            :param email: email of the author
        """
        self.print_info(author, email)
        self.time_writer('-------- Spider starts --------')
        self.time_writer('Date and Time at the beginning of the Spider: '+ str(datetime.now()))
        self.time_writer('INFO: Arguments')
        self.print_args(argument_parse)

    def print_msg(self, message):
        """
            Print message using time writer

            :param message: string displayed for the user
        """
        self.time_writer(message)

    def print_err(self, err_message):
        """
            Print error message using time writer

            :param err_message: error message displayed for the user
        """
        self.time_writer.print_stderr_message(err_message)

    def print_info(self, author, email):
        """
            Print information on the spider using time writer

            :param author: author of the spider
            :param email: email of the author
        """
        self.print_msg("Running spider : %s" %(self.spider_path))
        self.print_msg("Spider Author: %s" % (author))
        self.print_msg("Author Email:  %s" % (email))

    def print_args(self, argument_parse):
        """
            print arguments given to the Spider

            :param argument_parse: argument parser
        """
        self.time_writer("-- Arguments given to the spider --")
        for info, value in vars(argument_parse).items():
            self.time_writer("""{info} : {value}""".format(info=info, value=value))
        self.time_writer("-----------------------------------")

    def print_end(self):
        """
            Last print statement to give the time and date at the end of the spider
        """
        self.time_writer('Time at the end of the Spider: '+ str(datetime.now()))

    @staticmethod
    def run_system_cmd(cmd):
        """
            Run system command line via os.system()

            :param cmd: command to run
        """
        os.system(cmd)

    @staticmethod
    def select_str(xnat_dict):
        """
            Return string for pyxnat to select object from python dict

            :param tmp_dict: python dictionary with xnat information
                keys = ["project", "subject", "experiement", "scan", "resource"]
                  or
                keys = ["project", "subject", "experiement", "assessor", "out/resource"]
            :return string: string path to select pyxnat object
        """
        select_str = ''
        for key, value in xnat_dict.items():
            if value:
                select_str += '''/{key}/{label}'''.format(key=key, label=value)
        return select_str


class ScanSpider(Spider):
    """
        class for scan-spider

        :param super --> see base class
        :param xnat_scan: scan ID on XNAT (if running on a specific scan)
    """
    def __init__(self, spider_path, jobdir, xnat_project, xnat_subject, xnat_session, xnat_scan,
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix=""):
        super(ScanSpider, self).__init__(spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                                         xnat_host, xnat_user, xnat_pass, suffix)
        self.xnat_scan = xnat_scan

    def define_spider_process_handler(self):
        """
            Define the SpiderProcessHandler for the end of session spider
        """
        # Create the SpiderProcessHandler if first time upload
        self.spider_handler = XnatUtils.SpiderProcessHandler(self.spider_path,
                                                             self.suffix,
                                                             self.xnat_project,
                                                             self.xnat_subject,
                                                             self.xnat_session,
                                                             self.xnat_scan,
                                                             time_writer=self.time_writer)

    def pre_run(self):
        """
            Method to download the inputs
        """
        raise NotImplementedError()

    def run(self):
        """
            Method to execute the process
        """
        raise NotImplementedError()

    def finish(self):
        """
            Method to copy the results in the Spider Results folder dax.RESULTS_DIR
        """
        raise NotImplementedError()

class SessionSpider(Spider):
    """
        class for session-spider

        :param super --> see base class
    """
    def __init__(self, spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix=""):
        super(SessionSpider, self).__init__(spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                                            xnat_host, xnat_user, xnat_pass, suffix)

    def define_spider_process_handler(self):
        """
            Define the SpiderProcessHandler for the end of session spider
        """
        # Create the SpiderProcessHandler if first time upload
        self.spider_handler = XnatUtils.SpiderProcessHandler(self.spider_path,
                                                             self.suffix,
                                                             self.xnat_project,
                                                             self.xnat_subject,
                                                             self.xnat_session,
                                                             time_writer=self.time_writer)

    def run(self):
        """
            Method to execute the process
        """
        raise NotImplementedError()

    def finish(self):
        """
            Method to copy the results in the Spider Results folder dax.RESULTS_DIR
        """
        raise NotImplementedError()

#### CLASSES ####
# class to display time
class TimedWriter(object):
    '''
        Class to automatically write timed output message

        Args:
            name - Names to write with output (default=None)

        Examples:
            >>>a = Time_Writer()
            >>>a("this is a test")
            [00d 00h 00m 00s] this is a test
            >>>sleep(60)
            >>>a("this is a test")
            [00d 00h 01m 00s] this is a test

        Written by Andrew Plassard (Vanderbilt)
    '''
    def __init__(self, name=None):
        self.start_time = time.localtime()
        self.name = name

    def print_stderr_message(self, text):
        '''Prints a timed message to stderr'''
        self.print_timed_message(text, pipe=sys.stderr)

    def print_timed_message(self, text, pipe=sys.stdout):
        '''Prints a timed message
        Args:
            text - text to display
            pipe - pipe to write to (default: sys.stdout)
        '''
        msg = ""
        if self.name:
            msg = "[%s]" % self.name
        time_now = time.localtime()
        time_diff = time.mktime(time_now)-time.mktime(self.start_time)
        (days, res) = divmod(time_diff, 86400)
        (hours, res) = divmod(res, 3600)
        (mins, secs) = divmod(res, 60)
        msg = "%s[%dd %02dh %02dm %02ds] %s" % (msg, days, hours, mins, secs, text)
        print >> pipe, msg

    def __call__(self, text, pipe=sys.stdout):
        '''Prints a timed message
        Inputs:
            text - text to display
            pipe - pipe to write to (default: sys.stdout)
        '''
        self.print_timed_message(text, pipe=pipe)

#### Functions ####
def get_default_argparser(name, description):
    """
    Return default argparser arguments for all Spider

    :return: argparser obj
    """
    from argparse import ArgumentParser
    ap = ArgumentParser(prog=name, description=description)
    ap.add_argument('-p', dest='proj_label', help='Project Label', required=True)
    ap.add_argument('-s', dest='subj_label', help='Subject Label', required=True)
    ap.add_argument('-e', dest='sess_label', help='Session Label', required=True)
    ap.add_argument('-d', dest='temp_dir', help='Temporary Directory', required=True)
    ap.add_argument('--suffix', dest='suffix', help='assessor suffix. default: None', default=None)
    ap.add_argument('--host', dest='host', help='Set XNAT Host. Default: using env variable XNAT_HOST', default=None)
    ap.add_argument('--user', dest='user', help='Set XNAT User. Default: using env variable XNAT_USER', default=None)
    return ap

def get_session_argparser(name, description):
    """
    Return session argparser arguments for session Spider

    :return: argparser obj
    """
    ap = get_default_argparser(name, description)
    return ap

def get_scan_argparser(name, description):
    """
    Return scan argparser arguments for scan Spider

    :return: argparser obj
    """
    ap = get_default_argparser(name, description)
    ap.add_argument('-c', dest='scan_label', help='Scan label', required=True)
    return ap

def is_good_version(version):
    """
    Check the format of the version and return true if it's a proper format.
    Format: X.Y.Z
            see http://semver.org

    :param version: version given by the user
    """
    vers = version.split('.')
    if len(vers) != 3:
        return False
    else:
        if not vers[0].isdigit() or \
           not vers[1].isdigit() or \
           not vers[2].isdigit():
            return False
    return True
