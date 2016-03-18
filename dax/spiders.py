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
from stat import S_IXUSR, ST_MODE
from shutil import copyfile
from shutil import copytree
from string import Template

class Spider(object):
    """ Base class for spider """
    def __init__(self, spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix="", skip_finish=False):
        """
        Entry point for the Base class for spider

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
        # run the finish or not
        self.skip_finish = skip_finish

    def get_default_value(self, variable, env_name, value):
        """
        Return the default value for the variable if arg not NULL else
         env variables defined by the args

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
        list_files = XnatUtils.download_files_from_obj(directory=folder,
                                                       resource_obj=resource_obj)
        # close connection
        xnat.disconnect()
        return list_files

    def define_spider_process_handler(self):
        """
        Define the SpiderProcessHandler so the file(s) and PDF are checked for
         existence and uploaded to the upload_dir accordingly.
        Implemented in derived classes.

        :raises: NotImplementedError() if not overridden.
        :return: None
        """
        raise NotImplementedError()

    def has_spider_handler(self):
        """
        Check to see that the SpiderProcessHandler is defined. If it is not,
         call define_spider_process_handler

        :return: None

        """
        if not self.spider_handler:
            self.define_spider_process_handler()

    def upload(self, fpath, resource):
        """
        Upload files to the queue on the cluster to be upload to XNAT by DAX pkg
        E.g: spider.upload("/Users/DATA/", "DATA")
         spider.upload("/Users/stats_dir/statistical_measures.txt", "STATS")

        :param fpath: path to the folder/file to be uploaded
        :param resource: folder name to upload to on the assessor
        :raises: ValueError if the file to upload does not exist
        :return: None

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
        E.g: fdict = {"DATA" : "/Users/DATA/", "PDF": "/Users/PDF/report.pdf"}
         spider.upload_dict(fdict)

        :param files_dict: python dictionary containing the pair resource/fpath
        :raises: ValueError if the filepath is not a string or a list
        :return: None

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
        :return: None

        """
        self.has_spider_handler()
        self.spider_handler.done()
        self.spider_handler.clean(self.jobdir)
        self.print_end()

    
    def pre_run(self):
        """
        Pre-Run method to download and organise inputs for the pipeline
        Implemented in derived class objects.
        
        :raises: NotImplementedError if not overridden.
        :return: None
        """
        raise NotImplementedError()

    def run(self):
        """
        Runs the "core" or "image processing process" of the pipeline
        Implemented in derived class objects.
        
        :raises: NotImplementedError if not overridden.
        :return: None
        """
        raise NotImplementedError()

    def finish(self):
        """
        Method to copy the results in the Spider Results folder dax.RESULTS_DIR
        Implemented in derived class objects.

        :raises: NotImplementedError if not overriden by user
        :return: None
        """
        raise NotImplementedError()

    def print_init(self, argument_parse, author, email):
        """
        Print a message to display information on the init parameters, author,
        email, and arguments using time writer

        :param argument_parse: argument parser
        :param author: author of the spider
        :param email: email of the author
        :return: None
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
        :return: None
        """
        self.time_writer(message)

    def print_err(self, err_message):
        """
        Print error message using time writer

        :param err_message: error message displayed for the user
        :return: None
        """
        self.time_writer.print_stderr_message(err_message)

    def print_info(self, author, email):
        """
        Print information on the spider using time writer

        :param author: author of the spider
        :param email: email of the author
        :return: None
        """
        self.print_msg("Running spider : %s" %(self.spider_path))
        self.print_msg("Spider Author: %s" % (author))
        self.print_msg("Author Email:  %s" % (email))

    def print_args(self, argument_parse):
        """
        print arguments given to the Spider

        :param argument_parse: argument parser
        :return: None
        """
        self.time_writer("-- Arguments given to the spider --")
        for info, value in vars(argument_parse).items():
            self.time_writer("""{info} : {value}""".format(info=info, value=value))
        self.time_writer("-----------------------------------")

    def print_end(self):
        """
        Last print statement to give the time and date at the end of the spider

        :return: None
        """
        self.time_writer('Time at the end of the Spider: '+ str(datetime.now()))

    @staticmethod
    def run_system_cmd(cmd):
        """
        Run system command line via os.system()

        :param cmd: command to run
        :return: None
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
    """ Derived class for scan-spider """
    def __init__(self, spider_path, jobdir, xnat_project, xnat_subject, xnat_session, xnat_scan,
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix=""):
        """
        Entry point for Derived class for Spider on Scan level
        
        :param super --> see base class
        :param xnat_scan: scan ID on XNAT (if running on a specific scan)
        """
        super(ScanSpider, self).__init__(spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                                         xnat_host, xnat_user, xnat_pass, suffix)
        self.xnat_scan = xnat_scan

    def define_spider_process_handler(self):
        """
        Define the SpiderProcessHandler for the end of scan spider
         using the init attributes about XNAT

        :return: None
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
        Pre-Run method to download and organise inputs for the pipeline
        Implemented in derived class objects.
        
        :raises: NotImplementedError if not overridden.
        :return: None
        """
        raise NotImplementedError()

    def run(self):
        """
        Runs the "core" or "image processing process" of the pipeline
        Implemented in derived class objects.
        
        :raises: NotImplementedError if not overridden.
        :return: None
        """
        raise NotImplementedError()

    def finish(self):
        """
        Method to copy the results in the Spider Results folder dax.RESULTS_DIR
        Implemented in derived class objects.

        :raises: NotImplementedError if not overriden by user
        :return: None
        """
        raise NotImplementedError()

class SessionSpider(Spider):
    """ Derived class for session-spider """
    def __init__(self, spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix=""):
        """
        Entry point for Derived class for Spider on Session level
        
        :param super --> see base class
        """
        super(SessionSpider, self).__init__(spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                                            xnat_host, xnat_user, xnat_pass, suffix)

    def define_spider_process_handler(self):
        """
        Define the SpiderProcessHandler for the end of session spider
         using the init attributes about XNAT

        :return: None
        """
        # Create the SpiderProcessHandler if first time upload
        self.spider_handler = XnatUtils.SpiderProcessHandler(self.spider_path,
                                                             self.suffix,
                                                             self.xnat_project,
                                                             self.xnat_subject,
                                                             self.xnat_session,
                                                             time_writer=self.time_writer)

    def pre_run(self):
        """
        Pre-Run method to download and organise inputs for the pipeline
        Implemented in derived class objects.
        
        :raises: NotImplementedError if not overridden.
        :return: None
        """
        raise NotImplementedError()

    def run(self):
        """
        Runs the "core" or "image processing process" of the pipeline
        Implemented in derived class objects.
        
        :raises: NotImplementedError if not overridden.
        :return: None
        """
        raise NotImplementedError()

    def finish(self):
        """
        Method to copy the results in the Spider Results folder dax.RESULTS_DIR
        Implemented in derived class objects.

        :raises: NotImplementedError if not overriden by user
        :return: None
        """
        raise NotImplementedError()

class AutoSpider(Spider):
    def __init__(self, name, params, outputs, template, datatype='session'):
        self.name = name
        self.params = params
        self.outputs = outputs
        self.template = template
        self.datatype = datatype
        self.copy_list = []

        # Make the parser
        parser = self.get_argparser()

        # Now parse commandline arguments
        args = parser.parse_args()
        print(args)

        # Initialize spider with the args
        super(AutoSpider, self).__init__(name,
            args.temp_dir, args.proj_label, args.subj_label, args.sess_label,
            xnat_host=args.host, xnat_user=args.user, xnat_pass=None,
            suffix=args.suffix, skip_finish=args.skipfinish)

        if datatype == 'scan':
            self.xnat_scan = args.scan_label

        # Make a list of parameters that need to be copied to our input directory
        for p in params:
            if p[1] == 'FILE' or p[1] == 'DIR':
                self.copy_list.append(p[0])

        self.src_inputs = vars(args)
        self.input_dir = os.path.join(self.jobdir, 'INPUT')
        self.script_dir = os.path.join(self.jobdir, 'SCRIPT')
        self.run_inputs = {}

    def get_argparser(self):
        if self.datatype == 'scan':
            parser = get_scan_argparser(self.name, 'Run '+self.name)
        else:
            parser = get_session_argparser(self.name, 'Run '+self.name)

        # Add input params to arguments
        for p in self.params:
            parser.add_argument('--'+p[0], dest=p[0], help=p[2], required=True)

        return parser

    def define_spider_process_handler(self):
        """
        Define the SpiderProcessHandler for the end of spider
         using the init attributes about XNAT
        :return: None
        """
        # Create the SpiderProcessHandler if first time upload
        if self.datatype == 'scan':
            self.spider_handler = XnatUtils.SpiderProcessHandler(
                self.spider_path,
                self.suffix,
                self.xnat_project,
                self.xnat_subject,
                self.xnat_session,
                self.xnat_scan,
                time_writer=self.time_writer
            )

        else:
            self.spider_handler = XnatUtils.SpiderProcessHandler(
                self.spider_path,
                self.suffix,
                self.xnat_project,
                self.xnat_subject,
                self.xnat_session,
                time_writer=self.time_writer
            )

    def copy_inputs(self):
        self.run_inputs = self.src_inputs

        os.mkdir(self.input_dir)

        for _input in self.copy_list:
            # Split the list and handle each copy each individual file/dir
            src_list = self.src_inputs[_input].split(',')
            dst_list = []
            for i, src in enumerate(src_list):
                input_name = _input+'_'+str(i)
                dst = self.copy_input(src, input_name)
                if not dst:
                    print('ERROR:copying inputs')
                    return None
                else:
                    dst_list.append(dst)

            # Build new comma-separated list with local paths
            self.run_inputs[_input] = ','.join(dst_list)

        return self.run_inputs

    def go(self):

        self.pre_run()

        self.run()

        if not self.skip_finish:
            self.finish()

    def pre_run(self):
        '''Pre-Run method to download and organise inputs for the pipeline
        Implemented in derived class objects.'''
        print('DEBUG:pre_run()')
        self.copy_inputs()

    def run(self):
        print('DEBUG:run()')
        os.mkdir(self.script_dir)

        if self.template.startswith('#PYTHON'):
            self.run_python(self.template, 'example.py')
        elif self.template.startswith('%MATLAB'):
            self.run_matlab(self.template, 'example.m')

    def finish(self):
        print('DEBUG:finish()')

        self.has_spider_handler()

        # Add each output
        if self.outputs:
            for _output in self.outputs:
                _path = os.path.join(self.jobdir, _output[0])
                _type = _output[1]
                _res = _output[2]

                if _type == 'FILE':
                    if _res == 'PDF':
                        self.spider_handler.add_pdf(_path)
                    else:
                        self.spider_handler.add_file(_path, _res)
                elif _type == 'DIR':
                    self.spider_handler.add_folder(_path, _res)
                else:
                    print('ERROR:unknown type:'+_type)
        else:
            for _output in os.listdir(self.jobdir):
                _path = os.path.join(self.jobdir, _output)
                _res = os.path.basename(_output)
                self.spider_handler.add_folder(_path, _res)

        self.end()

    def run_matlab(self, mat_template, filename):
        filepath = os.path.join(self.script_dir, filename)
        template = Template(mat_template)

        # Write the script
        with open(filepath, 'w') as f:
            f.write(template.substitute(self.run_inputs))

        # Run the script
        XnatUtils.run_matlab(filepath, verbose=True)

    def run_shell(self, sh_template, filename):
        filepath = os.path.join(self.script_dir, filename)
        template = Template(sh_template)

        # Write the script
        with open(filepath, 'w') as f:
            f.write(template.substitute(self.run_inputs))

        # Run it
        os.chmod(filepath, os.stat(filepath)[ST_MODE] | S_IXUSR)
        os.system(filepath)

    def run_python(self, py_template, filename):
        filepath = os.path.join(self.script_dir, filename)
        template = Template(py_template)

        # Write the script
        with open(filepath, 'w') as f:
            f.write(template.substitute(self.run_inputs))

        # Run it
        os.chmod(filepath, os.stat(filepath)[ST_MODE] | S_IXUSR)
        os.system('python '+filepath)

    def copy_input(self, src, input_name):

        if self.is_xnat_uri(src):
            print('DEBUG:copying xnat input:'+src)
            src = self.parse_xnat_uri(src)
            dst = self.copy_xnat_input(src, input_name)
        else:
            print('DEBUG:copying local input:'+src)
            dst = self.copy_local_input(src, input_name)

        return dst

    def copy_xnat_input(self, src, input_name):
        dst_dir = os.path.join(self.input_dir, input_name)
        os.makedirs(dst_dir)

        if '/files/' in src:
            # Handle file
            _res, _file = src.split('/files/')
            dst = os.path.join(dst_dir, _file)

            print('DEBUG:downloading from XNAT:'+src+' to '+dst)
            result =  self.download_xnat_file(src, dst)
            return result

        elif '/resources/' in src:
            # Handle resource
            print('DEBUG:downloading from XNAT:'+src+' to '+dst_dir)
            result = self.download_xnat_resource(src, dst_dir)
            return result
        else:
            print('ERROR:invalid xnat path')
            return None

    def copy_local_input(self, src, input_name):
        dst_dir = os.path.join(self.input_dir, input_name)
        os.makedirs(dst_dir)

        if os.path.isdir(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            copytree(src, dst)
        elif os.path.isfile(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            copyfile(src, dst)
        else:
            print('ERROR:input does not exist:'+src)
            dst = None

        return dst

    def download_xnat_file(self, src, dst):
        result = None

        try:
            xnat = XnatUtils.get_interface(self.host, self.user, self.pwd)

            try:
                _res, _file = src.split('/files/')
                res = xnat.select(_res)
                result = res.file(_file).get(dst)
            except:
                print('ERROR:downloading from XNAT')
        except:
            print('ERROR:FAILED to get XNAT connection')
        finally:
            xnat.disconnect()

        return result

    def download_xnat_resource(self, src, dst):
        result = None

        try:
            xnat = XnatUtils.get_interface(self.host, self.user, self.pwd)
            try:
                res = xnat.select(src)
                res.get(dst, extract=True)
                result = dst
            except:
                print('ERROR:downloading from XNAT')
        except:
            print('ERROR:FAILED to get XNAT connection')
        finally:
            xnat.disconnect()

        return result

    def is_xnat_uri(self, uri):
        return uri.startswith('xnat:/')

    def parse_xnat_uri(self, src):
        src = src[len('xnat:/'):]
        src = src.replace('{session}', '/projects/'+self.xnat_project+'/subjects/'+self.xnat_subject+'/experiments/'+self.xnat_session)
        return src

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
        """
        Entry point of TimedWriter class

        :param name: Name to give the TimedWriter
        :return: None

        """
        self.start_time = time.localtime()
        self.name = name

    def print_stderr_message(self, text):
        """
        Prints a timed message to stderr

        :param text: The text to print
        :return: None

        """
        self.print_timed_message(text, pipe=sys.stderr)

    def print_timed_message(self, text, pipe=sys.stdout):
        """
        Prints a timed message

        :param text: text to print
        :param pipe: pipe to write to. defaults to sys.stdout
        :return: None

        """
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
        """
        Prints a timed message calling print_timed_message

        :param text: text to print
        :param pipe: pipe to write to. defaults to sys.stdout
        :return: None

        """
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
    ap.add_argument('--skipfinish', help='Skip the finish step, so do not move files to upload queue', action='store_true')
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
     Format: X.Y.Z see http://semver.org

    :param version: version given by the user
    :return: False if the version does not follow semantic
     versioning, true if it does.

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

def load_inputs(inputs_file):
    import csv

    with open(inputs_file, 'Ur') as f:
        data = list(tuple(rec) for rec in csv.reader(f, delimiter=','))

    return data

def load_outputs(outputs_file):
    import csv

    with open(outputs_file, 'Ur') as f:
       data = list(tuple(rec) for rec in csv.reader(f, delimiter=','))

    return data

def load_template(template_file):
    with open (template_file, "r") as f:
        data = f.read()

    return data
