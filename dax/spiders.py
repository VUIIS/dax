"""
    Title: spiders.py
    Author: Benjamin Yvernault
    contact: b.yvernault@ucl.ac.uk
    Purpose:
        Spider base class and class for Scan and Session spider
        Spider name must be: Spider_[name]_v[version].py
"""

__author__ = 'Benjamin Yvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Spider base class and class for Scan and Session spider."
__version__ = '1.0.0'
__modifications__ = '26 August 2015 - Original write'

import os
import re
import getpass
import collections
import SpiderUtils
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
        :param manual: if using the spider manually (not on the cluster) (boolean)
                       ask user if the HOST/USER/PASS are not set for XNAT
    """
    def __init__(self, spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix="", manual=False):
        # Spider path:
        self.spider_path = spider_path
        # directory for temporary files + create it
        self.jobdir = jobdir
        XnatUtils.makedir(os.path.abspath(self.jobdir))
        # to copy results at the end
        self.spider_handler = None
        # Xnat info:
        self.xnat_project = xnat_project
        self.xnat_subject = xnat_subject
        self.xnat_session = xnat_session
        # Xnat connection settings:
        self.host = self.get_default_value("xnat_host", "XNAT_HOST", xnat_host)
        self.user = self.get_default_value("xnat_host", "XNAT_USER", xnat_user)
        self.pwd = self.get_default_value("xnat_host", "XNAT_PASS", xnat_pass)
        # Suffix
        if suffix[0] != '_': self.suffix = '_'+suffix
        else: self.suffix = suffix
        # Set the suffix_proc remove any special characters and replace by '_'
        self.suffix = re.sub('[^a-zA-Z0-9]', '_', self.suffix)
        self.manual = manual
        # print time writer:
        self.time_writer = SpiderUtils.TimedWriter()

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
            if env_name in os.environ:
                return os.environ[env_name]
            else:
                if not self.manual:
                    err = "%s not set by user." % (env_name)
                    err += "\nTo set it choose one of this solution:"
                    err += "\n\tSet arguments '%s' in the spider class" % (variable)
                    err += "\n\tSet the environment variable %s" % (env_name)
                    raise ValueError(err)
                else:
                    msg = """Enter <{var}>:""".format(var=variable)
                    if env_name == 'XNAT_PASS':
                        return getpass.getpass(prompt=msg)
                    else:
                        return raw_input(msg)

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
            spider.upload_dict("/Users/DATA/", "DATA")

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
        self.time_writer('Date and Time at the beginning of the Spider: ', str(datetime.now()))
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
        self.time_writer('\nTime at the end of the Spider: ', str(datetime.now()))

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
        return string to select pyxnat object
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
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix="", manual=False):
        super(ScanSpider, self).__init__(spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                                         xnat_host, xnat_user, xnat_pass, suffix, manual)
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
                                                             self.xnat_scan)

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
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix="", manual=False):
        super(SessionSpider, self).__init__(spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                                            xnat_host, xnat_user, xnat_pass, suffix, manual)

    def define_spider_process_handler(self):
        """
        Define the SpiderProcessHandler for the end of session spider
        """
        # Create the SpiderProcessHandler if first time upload
        self.spider_handler = XnatUtils.SpiderProcessHandler(self.spider_path,
                                                             self.suffix,
                                                             self.xnat_project,
                                                             self.xnat_subject,
                                                             self.xnat_session)

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
