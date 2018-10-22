"""
    Title: spiders.py
    Author: Benjamin Yvernault
    contact: b.yvernault@ucl.ac.uk
    Purpose:
        Spider base class and class for Scan and Session spider
        Spider name must be: Spider_[name]_v[version].py
        Utils for spiders
"""

from __future__ import print_function
from __future__ import division

from builtins import str
from builtins import range
from builtins import object
from past.builtins import basestring
from past.utils import old_div

import collections
import csv
from datetime import datetime
import glob
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import os
import re
from scipy.misc import imresize
from shutil import copyfile, copytree
from stat import S_IXUSR, ST_MODE
from string import Template
import subprocess as sb
import sys
import time

from . import XnatUtils
from .errors import SpiderError, AutoSpiderError


try:
    basestring
except NameError:
    basestring = str

__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ["Spider", "ScanSpider", "SessionSpider", "AutoSpider",
           "TimedWriter"]
UNICODE_SPIDER = """
Spider information:
  -- General --
    type:    {type}
    path:    {path}
    jobdir:  {jobdir}
    suffix:  {suffix}
  -- XNAT --
    host:    {host}
    user:    {user}
    project: {project}
    subject: {subject}
    session: {session}{scan}
{extra}
"""

FSLSWAP_VAL = {0: 'x',
               1: 'y',
               2: 'z'}


class Spider(object):
    """ Base class for spider """
    def __init__(self, spider_path, jobdir,
                 xnat_project, xnat_subject, xnat_session,
                 xnat_host=None, xnat_user=None, xnat_pass=None,
                 suffix="", subdir=True, skip_finish=False):
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
        :param subdir: create a subdir Temp in the jobdir if the directory
                       isn't empty.
        :param skip_finish: skip the finish function
        """
        # Spider path:
        self.spider_path = spider_path
        # directory for temporary files + create it
        self.jobdir = XnatUtils.makedir(os.path.abspath(jobdir), subdir=subdir)
        # to copy results at the end
        self.spider_handler = None
        # Xnat info:
        self.xnat_project = xnat_project
        self.xnat_subject = xnat_subject
        self.xnat_session = xnat_session
        self.xnat_scan = None
        # Xnat connection settings:
        self.host = xnat_host
        self.user = xnat_user
        self.pwd = xnat_pass
        # Suffix
        if not suffix:
            self.suffix = ""
        else:
            # Set the suffix_proc remove any special characters, replace by '_'
            self.suffix = re.sub('[^a-zA-Z0-9]', '_', suffix)
            # Replace multiple underscores by one
            self.suffix = re.sub('_+', '_', self.suffix)
            # Remove underscore if at the end of suffix
            if self.suffix[-1] == '_':
                self.suffix = self.suffix[:-1]
            # Add an underscore at the beginning if not present
            if self.suffix[0] != '_':
                self.suffix = '_%s' % self.suffix
        # print time writer:
        self.time_writer = TimedWriter(use_date=True)
        # run the finish or not
        self.skip_finish = skip_finish
        # Inputs:
        self.inputs = None
        # data:
        self.data = dict()
        # cmd arguments:
        self.cmd_args = list()

    def __unicode__(self):
        """ Unicode for spiders."""
        extra = '  -- Extra --\n'
        # if inputs
        if self.inputs:
            unicode_inputs = '    Inputs:\n'
            for in_dict in self.inputs:
                v = ("type: %s - label: %s - res: %s"
                     % (in_dict.get('type'), in_dict.get('label'),
                        in_dict.get('resource')))
                unicode_inputs = '%s        %s\n' % (unicode_inputs, v)
            extra += unicode_inputs
        # if data downloaded
        if self.data:
            unicode_data = '    Data:\n'
            for label, li_inputs in list(self.data.items()):
                v = "label: %s\n" % label
                for res_name, files in list(li_inputs.items()):
                    v = ("%s\t  - resource: %s - files: %s\n"
                         % (v, res_name, files))
                unicode_data = '%s        %s\n' % (unicode_data, v)
            extra += unicode_data
        scan_str = '\n    scan:%s' % self.xnat_scan if self.xnat_scan else ''
        return UNICODE_SPIDER.format(
            type='Scan' if self.xnat_scan else 'Session',
            path=self.spider_path,
            jobdir=self.jobdir,
            suffix=self.suffix,
            host=self.host,
            user=self.user,
            project=self.xnat_project,
            subject=self.xnat_subject,
            session=self.xnat_session,
            scan=scan_str,
            extra=extra,
        )

    def __str__(self):
        return str(self).encode('utf-8')

    @staticmethod
    def get_data_dict(otype, label, resource, directory, scan=None):
        """Create a data_dict for self.inputs from user need."""
        return {'type': otype,
                'label': label,
                'resource': resource,
                'dir': directory,
                'scan': scan}

    def select_obj(self, intf, obj_label, resource):
        """
        Select scan or assessor resource

        :param obj_label: xnat object label (scan ID or assessor label)
        :param resource: folder name under the xnat object
        return pyxnat object

        """
        tmp_dict = collections.OrderedDict([
            ('project', self.xnat_project),
            ('subject', self.xnat_subject),
            ('experiment', self.xnat_session)
        ])
        # try on scan
        tmp_dict_scan = tmp_dict.copy()
        tmp_dict_scan['scan'] = obj_label
        tmp_dict_scan['resource'] = resource
        xnat_obj = intf.select(self.select_str(tmp_dict_scan))
        if xnat_obj.exists():
            return xnat_obj
        else:
            # else try assessor
            tmp_dict_assessor = tmp_dict.copy()
            tmp_dict_assessor['assessor'] = obj_label
            tmp_dict_assessor['out/resource'] = resource
            xnat_obj = intf.select(self.select_str(tmp_dict_assessor))
            if xnat_obj.exists():
                return xnat_obj
            else:
                # Error: not on XNAT
                err = "No XNAT Object found with the following values: "
                err += str(tmp_dict)
                err += "\n scan or assessor: %s / resource: %s " % (obj_label,
                                                                    resource)
                raise ValueError(err)

    def download_inputs(self):
        """
        Download inputs data from XNAT define in self.inputs.

        self.inputs = list of data dictionary with keys define below
        keys:
            'type': 'scan' or 'assessor' or 'subject' or 'project' or 'session'
            'label': label on XNAT (not needed for session/subject/project)
            'resource': name of resource to download or list of resources
            'dir': directory to download files into (optional)
          - for assessor only if not giving the label but just proctype
            'scan': id of the scan for the assessor (if None, sessionAssessor)

        self.data = list of dictionary with keys define below:
            'label': label on XNAT
            'files': list of files downloaded

        set self.data, a python list of the data downloaded.
        """
        self.time_writer('-------- download_inputs --------')
        if not self.inputs:
            raise SpiderError('download_inputs(): self.inputs not define in \
your spider.')
        if not isinstance(self.inputs, list):
            raise SpiderError('self.inputs is not a list: %s' % self.inputs)
        # Inputs folder: jobdir/inputs
        input_dir = os.path.join(self.jobdir, 'inputs')
        with XnatUtils.get_interface(host=self.host, user=self.user,
                                     pwd=self.pwd) as intf:
            for data_dict in self.inputs:
                if not isinstance(data_dict, dict):
                    raise SpiderError('data in self.inputs is not a dict: %s'
                                      % data_dict)
                if isinstance(data_dict['resource'], list):
                    resources = data_dict['resource']
                else:
                    resources = [data_dict['resource']]
                list_inputs = dict()
                for res in resources:
                    if 'dir' in list(data_dict.keys()):
                        data_folder = os.path.join(input_dir,
                                                   data_dict['dir'])
                    else:
                        data_folder = os.path.join(input_dir,
                                                   data_dict['label'])
                    self.time_writer(' downloading %s for %s into %s'
                                     % (res, data_dict['label'], data_folder))
                    if not os.path.isdir(data_folder):
                        os.makedirs(data_folder)
                    xnat_dict = self.get_xnat_dict(data_dict, res)
                    res_str = self.select_str(xnat_dict)
                    resource_obj = intf.select(res_str)
                    resource_obj.get(data_folder, extract=True)
                    resource_dir = os.path.join(data_folder,
                                                resource_obj.label())
                    list_files = list()
                    for root, _, filenames in os.walk(resource_dir):
                        list_files.extend([os.path.join(root, filename)
                                           for filename in filenames])
                    list_inputs[res] = list_files
                if data_dict['label'] in list(self.data.keys()):
                    self.data[data_dict['label']].update(list_inputs)
                else:
                    self.data[data_dict['label']] = list_inputs
        self.time_writer('-----------------------------------')

    def get_xnat_dict(self, data_dict, resource):
        """Return a OrderedDict dictionary with XNAT information.

        keys:
            project
            subject
            experiment
            scan
            resource
            assessor
            out/resource  (for assessor)
        """
        xdict = collections.OrderedDict([('project', self.xnat_project)])
        itype = data_dict.get('type', None)
        if not itype:
            print("Warning: 'type' not specified in inputs %s" % data_dict)
            return None
        label = data_dict.get('label', None)
        if itype == 'subject':
            xdict['subject'] = self.xnat_subject
        elif itype == 'session':
            xdict['subject'] = self.xnat_subject
            xdict['experiment'] = self.xnat_session
        elif itype == 'scan':
            xdict['subject'] = self.xnat_subject
            xdict['experiment'] = self.xnat_session
            if not label:
                print("Warning: 'label' not specified in inputs %s"
                      % data_dict)
                return None
            else:
                xdict['scan'] = data_dict.get('label', None)
        elif itype == 'assessor':
            xdict['subject'] = self.xnat_subject
            xdict['experiment'] = self.xnat_session
            if not label:
                print("Warning: 'label' not specified in inputs %s"
                      % data_dict)
                return None
            else:
                scan_id = data_dict.get('scan', None)
                xdict['assessor'] = self.get_assessor_label(label, scan_id)

        if data_dict == 'assessor':
            xdict['out/resource'] = resource
        else:
            xdict['resource'] = resource
        return xdict

    def get_assessor_label(self, label, scan):
        tmp_list = [self.xnat_project,
                    self.xnat_subject,
                    self.xnat_session]
        if '-x-' not in label:
            if not scan:
                tmp_list.append(label)
            else:
                tmp_list.append(scan)
                tmp_list.append(label)
            return '-x-'.join(tmp_list)
        else:
            return label

    def download(self, obj_label, resource, folder):
        """
        Return a python list of the files downloaded for the scan's resource
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
        with XnatUtils.get_interface(host=self.host, user=self.user,
                                     pwd=self.pwd) as intf:
            resource_obj = self.select_obj(intf=intf,
                                           obj_label=obj_label,
                                           resource=resource)
            list_files = XnatUtils.download_files_from_obj(
                directory=folder, resource_obj=resource_obj)
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
        Upload files to the queue on the cluster to be upload to XNAT by DAX
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
            raise SpiderError(err)

    def upload_dict(self, files_dict):
        """
        upload files to the queue on the cluster to be upload to XNAT by DAX
         following the files python dictionary: {resource_name : fpath}
        E.g: fdict = {"DATA" : "/Users/DATA/", "PDF": "/Users/PDF/report.pdf"}
         spider.upload_dict(fdict)

        :param files_dict: python dictionary containing the pair resource/fpath
        :raises: ValueError if the filepath is not a string or a list
        :return: None

        """
        self.has_spider_handler()
        for resource, fpath in list(files_dict.items()):
            if isinstance(fpath, basestring):
                self.upload(fpath, resource)
            elif isinstance(fpath, list):
                for ffpath in fpath:
                    self.upload(ffpath, resource)
            else:
                err = "upload_dict(): variable not recognize in dictionary \
for resource %s : %s"
                raise SpiderError(err % (resource, type(fpath)))

    def end(self):
        """
        Finish the script by sending the end of script flag and cleaning folder

        :param jobdir: directory for the spider
        :return: None

        """
        self.has_spider_handler()
        self.spider_handler.done()
        self.spider_handler.clean(self.jobdir)
        self.print_end()

    def check_executable(self, executable, name, version_opt='--version'):
        """Method to check the executable.

        :param executable: executable path
        :param name: name of Executable
        :return: Complete path to the executable
        """
        if executable == name:
            if not XnatUtils.executable_exists(executable):
                raise SpiderError("Executable '%s' not found on your computer."
                                  % name)
        else:
            executable = os.path.abspath(executable)
            if not executable.endswith(name):
                if os.path.isdir(executable):
                    executable = os.path.join(executable, name)
                else:
                    msg = "Error for executable path '%s': Wrong name."
                    raise SpiderError(msg % executable)
            if not os.path.isfile(executable):
                msg = "Executable '%s' not found"
                raise SpiderError(msg % executable)

        self.get_exe_version(executable, version_opt)
        return executable

    def get_exe_version(self, executable, version_opt='--version'):
        """Method to check the executable.

        :param executable: executable to run
        :param version_opt: options to get the version of the executable
        :return: version
        """
        pversion = sb.Popen([executable, version_opt],
                            stdout=sb.PIPE,
                            stderr=sb.PIPE)
        nve_version, _ = pversion.communicate()
        self.time_writer('Executable <%s> version: %s' %
                         (executable, nve_version.strip()))
        return nve_version

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
        self.time_writer('Date and Time at the beginning of the Spider: %s'
                         % str(datetime.now()))
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
        self.print_msg("Running spider : %s" % (self.spider_path))
        self.print_msg("Spider Author: %s" % (author))
        self.print_msg("Author Email:  %s" % (email))

    def print_args(self, argument_parse):
        """
        print arguments given to the Spider

        :param argument_parse: argument parser
        :return: None
        """
        self.time_writer("-- Arguments given to the spider --")
        for info, value in sorted(vars(argument_parse).items()):
            self.time_writer("%s : %s" % (info, value))
        self.time_writer("-----------------------------------")

    def print_end(self):
        """
        Last print statement to give the time and date at the end of the spider

        :return: None
        """
        self.time_writer('Time at the end of the Spider: %s'
                         % str(datetime.now()))

    def plot_images_page(self, pdf_path, page_index, nii_images, title,
                         image_labels, slices=None, cmap='gray',
                         vmins=None, vmaxs=None, volume_ind=None, orient='ax'):
        """Plot list of images (3D-4D) on a figure (PDF page).

        See function at the end of the file.
        """
        return plot_images(
            pdf_path=pdf_path, page_index=page_index, nii_images=nii_images,
            title=title, image_labels=image_labels, slices=slices, cmap=cmap,
            vmins=vmins, vmaxs=vmaxs, volume_ind=volume_ind, orient=orient,
            time_writer=self.time_writer)

    def plot_stats_page(self, pdf_path, page_index, stats_dict, title,
                        tables_number=3, columns_header=['Header', 'Value'],
                        limit_size_text_column1=30,
                        limit_size_text_column2=10):
        """Generate pdf report of stats information from a csv/txt.

        See function at the end of the file.
        """
        return plot_stats(
            pdf_path=pdf_path, page_index=page_index, stats_dict=stats_dict,
            title=title, tables_number=tables_number,
            columns_header=columns_header,
            limit_size_text_column1=limit_size_text_column1,
            limit_size_text_column2=limit_size_text_column2,
            time_writer=self.time_writer)

    def merge_pdf_pages(self, pdf_pages, pdf_final):
        """Concatenate all pdf pages in the list into a final pdf.

        See function at the end of the file.
        """
        return merge_pdfs(pdf_pages, pdf_final, self.time_writer)

    def run_cmd_args(self):
        """
        Run a command line via os.system() with arguments set in self.cmd_args

        cmd_args is a dictionary:
            exe: executable to use (matlab, python, sh)
            template: string defining the command line with argument
            args: dictionary with:
                    key = argument
                    value = value to set
            filename: name for the file if written into a file (optional)
        :return: True if succeeded, False otherwise
        """
        self.time_writer('-------- run_cmd_args --------')
        # Check cmd_args set by user:
        cmd_keys = list(self.cmd_args.keys())
        if not self.cmd_args:
            raise SpiderError("self.cmd_args not defined.")
        if 'exe' not in cmd_keys:
            raise SpiderError("self.cmd_args doesn't have a key 'exe'.")
        elif not XnatUtils.executable_exists(self.cmd_args['exe']):
            msg = "Executable not found: %s."
            raise SpiderError(msg % self.cmd_args['exe'])
        if 'template' not in cmd_keys:
            msg = "self.cmd_args doesn't have a key 'template'."
            raise SpiderError(msg)
        if 'args' not in cmd_keys:
            raise SpiderError("self.cmd_args doesn't have a key 'args'.")

        # Add options to matlab if it's not present in the exe
        cmd = ''
        template = Template(self.cmd_args['template'])
        exe = self.cmd_args['exe']
        if exe.lower() == 'matlab':
            exe = 'matlab -singleCompThread -nodesktop -nosplash < '
            # add file to run the matlab command if not set
            if 'filename' not in cmd_keys:
                self.cmd_args['filename'] = os.path.join(
                    self.jobdir, 'run_%s_matlab.m' % self.xnat_session)

        # Write the template in file and call the executable on the file
        if 'filename' in cmd_keys:
            if not os.path.exists(os.path.dirname(self.cmd_args['filename'])):
                raise SpiderError("Folder for %s does not exist."
                                  % os.path.dirname(self.cmd_args['filename']))
            with open(self.cmd_args['filename'], 'w') as f:
                f.write(template.substitute(self.cmd_args['args']))
            cmd = '%s %s' % (exe, self.cmd_args['filename'])
        else:
            # Run the template directly with the exe:
            #  check if exe not already present in template
            if not self.cmd_args['template'].startswith(exe):
                cmd = exe
            cmd = '%s %s' % (cmd, template.substitute(self.cmd_args['args']))

        self.time_writer("Running command: %s" % cmd)
        succeeded = execute_cmd(cmd, time_writer=self.time_writer)
        self.time_writer('-----------------------------------')
        return succeeded

    def run_system_cmd(self, cmd):
        """
        Run system command line via os.system()

        :param cmd: command to run
        :return: True if succeeded, False otherwise
        """
        return execute_cmd(cmd, time_writer=self.time_writer)

    @staticmethod
    def select_str(xnat_dict):
        """
        Return string for pyxnat to select object from python dict

        :param tmp_dict: python dictionary with xnat information
            keys = ["project", "subject", "experiement", "scan", "resource"]
              or
            keys = ["project", "subject", "experiement", "assessor",
                    "out/resource"]
        :return string: string path to select pyxnat object
        """
        select_str = ''
        for key, value in list(xnat_dict.items()):
            if value:
                select_str += '''/{key}/{label}'''.format(key=key, label=value)
        return select_str


class ScanSpider(Spider):
    """ Derived class for scan-spider """
    def __init__(self, spider_path, jobdir,
                 xnat_project, xnat_subject, xnat_session, xnat_scan,
                 xnat_host=None, xnat_user=None, xnat_pass=None,
                 suffix="", subdir=True, skip_finish=False):
        """
        Entry point for Derived class for Spider on Scan level

        :param super --> see base class
        :param xnat_scan: scan ID on XNAT (if running on a specific scan)
        """
        super(ScanSpider, self).__init__(
            spider_path, jobdir,
            xnat_project, xnat_subject, xnat_session,
            xnat_host, xnat_user, xnat_pass,
            suffix, subdir, skip_finish)
        self.xnat_scan = xnat_scan

    def define_spider_process_handler(self):
        """
        Define the SpiderProcessHandler for the end of scan spider
         using the init attributes about XNAT

        :return: None
        """
        # Create the SpiderProcessHandler if first time upload
        self.spider_handler = XnatUtils.SpiderProcessHandler(
            self.spider_path,
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
    def __init__(self, spider_path, jobdir,
                 xnat_project, xnat_subject, xnat_session,
                 xnat_host=None, xnat_user=None, xnat_pass=None,
                 suffix="", subdir=True, skip_finish=False):
        """
        Entry point for Derived class for Spider on Session level

        :param super --> see base class
        """
        super(SessionSpider, self).__init__(
            spider_path, jobdir,
            xnat_project, xnat_subject, xnat_session,
            xnat_host, xnat_user, xnat_pass, suffix, subdir, skip_finish)

    def define_spider_process_handler(self):
        """
        Define the SpiderProcessHandler for the end of session spider
         using the init attributes about XNAT

        :return: None
        """
        # Create the SpiderProcessHandler if first time upload
        self.spider_handler = XnatUtils.SpiderProcessHandler(
            self.spider_path,
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


SCRIPT_NAME = {
    'python': '.py',
    'matlab': '.m',
    'ruby': '.rb',
    'bash': '.sh'
}
UNICODE_AUTOSPIDER = """AutoSpider information:
  -- General --
    Name:    {name}
    jobdir:  {jobdir}
    suffix:  {suffix}
  -- XNAT --
    host:    {host}
    user:    {user}
    assessor: {assessor}
  -- Inputs --
{inputs}
"""


# AutoSpider should not be used by the USER. Use InitAutoSpider &
# GenerateAutoSpider to generate the files needed for a new spider
class AutoSpider(object):
    """ Class for Autospider """
    def __init__(self, name, params, outputs, template, version=None,
                 exe_lang=None):
        """
        Entry point for Autospider class

        :param name: spider name
        :param params: inputs parameters
        :param outputs: outputs to save
        :param template: template to run
        :param version: spider version
        :param exe_lang: executable language (python, matlab, bash, ruby)
        """
        self.name = name
        self.params = params
        self.outputs = list()
        self.template = template
        self.exe_lang = exe_lang
        self.copy_list = []

        # Make the parser
        parser = self.get_argparser()

        # Now parse commandline arguments
        args = parser.parse_args()

        # Spider path:
        self.spider_name = name
        if version:
            self.spider_name += '_v%s' % version

        # directory for temporary files + create it
        self.jobdir = XnatUtils.makedir(os.path.abspath(args.temp_dir),
                                        subdir=args.subdir)
        # Xnat connection settings:
        self.host = args.host
        self.user = args.user
        self.pwd = None
        # Suffix
        if not args.suffix:
            self.suffix = ""
        else:
            # Set the suffix_proc remove any special characters, replace by '_'
            self.suffix = re.sub('[^a-zA-Z0-9]', '_', args.suffix)
            # Replace multiple underscores by one
            self.suffix = re.sub('_+', '_', self.suffix)
            # Remove underscore if at the end of suffix
            if self.suffix[-1] == '_':
                self.suffix = self.suffix[:-1]
            # Add an underscore at the beginning if not present
            if self.suffix[0] != '_':
                self.suffix = '_%s' % self.suffix

        # print time writer:
        self.time_writer = TimedWriter(use_date=True)
        # run the finish or not
        self.skip_finish = args.skipfinish

        # Set matlab_bin from args or default to just matlab
        self.matlab_bin = getattr(args, 'matlab_bin', 'matlab')

        # Get commandline inputs
        self.src_inputs = vars(args)

        # Make a list of params that need to be copied to input directory
        for p in params:
            # Check input type
            if p[1] not in ['FILE', 'DIR']:
                continue

            # Check for optional arguments that are not set
            if len(p) >= 4 and \
               p[3].lower().startswith('f') and \
               not self.src_inputs[p[0]]:
                continue

            self.copy_list.append(p[0])

        self.src_inputs['temp_dir'] = self.jobdir
        self.input_dir = os.path.join(self.jobdir, 'INPUT')
        self.script_dir = os.path.join(self.jobdir, 'SCRIPT')
        self.run_inputs = {}

        # Outputs
        self._populate_from_inputs(outputs)

        # Assessor:
        self.ahandler = XnatUtils.AssessorHandler(args.assessor_label)

    def __unicode__(self):
        """ Unicode for AutoSpiders."""
        unicode_inputs = list()
        for key, value in list(self.src_inputs.items()):
            if key not in ['assessor_label', 'temp_dir', 'suffix', 'host',
                           'user']:
                unicode_inputs.append("    %s: %s" % (key, value))
        return UNICODE_AUTOSPIDER.format(
            name=self.spider_name,
            jobdir=self.jobdir,
            suffix='None' if not self.suffix else self.suffix,
            host=self.host,
            user=self.user,
            assessor=self.ahandler.assessor_label,
            inputs='\n'.join(unicode_inputs),
        )

    def __str__(self):
        """ Unicode for AutoSpiders."""
        return str(self).encode('utf-8')

    def get_argparser(self):
        """Get argparser for the AutoSpider."""
        parser = get_auto_argparser(self.name, 'Run %s' % self.name)
        # Add input params to arguments
        for p in self.params:
            _required = True
            if len(p) >= 4 and p[3].lower().startswith('f'):
                _required = False
            parser.add_argument('--' + p[0], dest=p[0], help=p[2],
                                required=_required)
        return parser

    def copy_inputs(self):
        """ Copy the inputs data for AutoSpider."""
        self.run_inputs = self.src_inputs

        if not os.path.exists(self.input_dir):
            os.mkdir(self.input_dir)

        for _input in self.copy_list:
            # Split the list and handle each copy each individual file/dir
            src_list = self.src_inputs[_input].split(',')
            dst_list = []
            for i, src in enumerate(src_list):
                input_name = '%s_%s' % (_input, str(i))
                dst = self.copy_input(src, input_name)
                if not dst:
                    self.time_writer('ERROR: copying inputs')
                    return None
                else:
                    dst_list.append(dst)

            # Build new comma-separated list with local paths
            self.run_inputs[_input] = ','.join(dst_list)

        return self.run_inputs

    def _populate_from_inputs(self, outputs):
        """ Populate the outputs with the inputs if set"""
        for output in outputs:
            # If a argument in the string from input
            if '${' in output[0]:
                name = output[0].partition('{')[-1].rpartition('}')[0]
                if name in list(self.src_inputs.keys()):
                    for val in self.src_inputs.get(name).split(','):
                        out1 = output[0].replace('${%s}' % name, val)
                        out2 = output[1]
                        out3 = output[2].replace('${%s}' % name, val)
                        self.outputs.append((out1, out2, out3))
                else:
                    err = '${ found in the output but the format is unknown. \
The format {} can not be read by the spider because {} is not an input.'
                    raise AutoSpiderError(err.format(output[0], name))
            else:
                self.outputs.append(output)

    def go(self):
        """Main method for AutoSpider."""
        for line in self.__unicode__().split('\n'):
            self.time_writer(line)

        self.pre_run()

        self.run()

        if not self.skip_finish:
            self.finish()

    def pre_run(self):
        """Pre-Run method to download and organise inputs for the pipeline
        Implemented in derived class objects."""
        self.time_writer('AutoSpider pre_run(): Download/copy inputs...')
        self.copy_inputs()

    def run(self):
        """Run method to execute the template for AutoSpider."""
        self.time_writer('AutoSpider run(): Running command from template...')

        if not os.path.exists(self.script_dir):
            os.mkdir(self.script_dir)

        # Get filepath and template
        filename = 'script%s' % SCRIPT_NAME[self.exe_lang]
        filepath = os.path.join(self.script_dir, filename)
        template = Template(self.template)

        # Write the script
        with open(filepath, 'w') as f:
            f.write(template.substitute(self.run_inputs))

        if not self.exe_lang:
            if self.template.startswith('#PYTHON'):
                self.exe_lang = 'python'
            elif self.template.startswith('%MATLAB'):
                self.exe_lang = 'matlab'
            elif self.template.startswith('#RUBY'):
                self.exe_lang = 'ruby'
            elif self.template.startswith('#BASH'):
                self.exe_lang = 'bash'
            else:
                raise AutoSpiderError('Template Unknown. Please add #BASH/\
#PYTHON/#RUBY/#MATLAB at the beginning of the call file and rerun \
GeneratorAutoSpider.')

        self.succeeded = run_cmd(self.exe_lang, filepath,
                                 time_writer=self.time_writer,
                                 matlab_bin=self.matlab_bin)

    def finish(self):
        """finish method to copy the results."""
        if not self.succeeded:
            self.time_writer('AutoSpider finish(): run() failed. Exit.')
            return

        # to copy results at the end
        self.spider_handler = XnatUtils.SpiderProcessHandler(
            self.spider_name, self.suffix,
            assessor_handler=self.ahandler,
            time_writer=self.time_writer,
            host=self.src_inputs.get('host', os.environ['XNAT_HOST']))

        self.time_writer('AutoSpider finish(): Copying outputs...')

        # Add each output
        if self.outputs:
            for _output in self.outputs:
                # _path = os.path.join(self.jobdir, _output[0])
                _type = _output[1]
                _res = _output[2]
                _path_list = glob.glob(os.path.join(self.jobdir, _output[0]))

                required = True
                if len(_output) >= 4 and _output[3].lower().startswith('f'):
                    required = False

                if len(_path_list) == 0 and required:
                    err = "outputs not found for %s of type <'%s'>: %s"
                    raise AutoSpiderError(err % (_res, _type, _output[0]))

                if _res == 'PDF':
                    if _type != 'FILE':
                        raise AutoSpider('ERROR: illegal type for PDF: %s'
                                         % _type)
                    elif len(_path_list) > 1:
                        raise AutoSpider('ERROR: multiple PDFs found')
                    elif len(_path_list) == 0:
                        raise AutoSpider('ERROR: no PDF found')
                    else:
                        self.spider_handler.add_pdf(_path_list[0])
                elif _type == 'FILE':
                    for _path in _path_list:
                        self.spider_handler.add_file(_path, _res)
                elif _type == 'DIR':
                    for _path in _path_list:
                        self.spider_handler.add_folder(_path, _res)
                else:
                    raise AutoSpider('ERROR: unknown type: %s' % _type)
        else:
            # Output not specified so upload everything in the job dir
            for _output in os.listdir(self.jobdir):
                _path = os.path.join(self.jobdir, _output)
                _res = os.path.basename(_output)
                self.spider_handler.add_folder(_path, _res)

        self.end()

    def end(self):
        """
        Finish the script by sending the end of script flag and cleaning folder
        :return: None
        """
        self.spider_handler.done()
        self.spider_handler.clean(self.jobdir)
        self.print_end()

    def print_end(self):
        """
        Last print statement

        :return: None
        """
        self.time_writer('End of Spider: %s' % self.spider_name)

    def copy_input(self, src, input_name):
        """Copy inputs or download from XNAT."""
        if self.is_xnat_uri(src):
            if src.startswith('xnat://'):
                src = src[len('xnat:/'):]
            else:
                src = src[len('xnat:'):]

            self.time_writer(' - copying xnat input: %s' % src)
            dst = self.copy_xnat_input(src, input_name)
        else:
            self.time_writer(' - copying local input: %s' % src)
            dst = self.copy_local_input(src, input_name)

        return dst

    def copy_xnat_input(self, src, input_name):
        """Copy xnat inputs."""
        dst_dir = os.path.join(self.input_dir, input_name)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        if '/files/' in src:
            # Handle file
            _res, _file = src.split('/files/')
            _file = os.path.basename(_file)
            dst = os.path.join(dst_dir, _file)

            self.time_writer(' - downloading from XNAT: %s to %s' % (src, dst))
            result = self.download_xnat_file(src, dst)
            if result:
                return dst
            else:
                return None

        elif '/file/' in src:
            err = 'invalid xnat path: %s. "file" found instead of "files".'
            raise AutoSpiderError(err % src)

        elif '/resources/' in src or '/resource/' in src:
            # Handle resource
            self.time_writer(' - downloading from XNAT: %s to %s'
                             % (src, dst_dir))
            result = self.download_xnat_resource(src, dst_dir)
            return result

        else:
            err = 'invalid xnat path: %s. Missing "/resource(s)/" or \
"/files/" in path.'
            raise AutoSpiderError(err % src)

    def copy_local_input(self, src, input_name):
        """Copy local inputs."""
        dst_dir = os.path.join(self.input_dir, input_name)
        os.makedirs(dst_dir)

        if os.path.isdir(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            copytree(src, dst)
        elif os.path.isfile(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            copyfile(src, dst)
        else:
            raise AutoSpiderError('input does not exist: %s' % src)

        return dst

    def download_xnat_file(self, src, dst):
        """Download XNAT specific file."""
        results = None
        with XnatUtils.get_interface(host=self.host, user=self.user,
                                     pwd=self.pwd) as intf:
            try:
                _res, _file = src.split('/files/')
                res = intf.select(_res)
                if not res.exists():
                    msg = 'resources specified by %s not found on XNAT.'
                    raise AutoSpiderError(msg % src)
            except Exception:
                msg = 'resources can not be checked because the path given is \
wrong for XNAT. Please check https://wiki.xnat.org/display/XNAT16/\
XNAT+REST+API+Directory for the path.'
                raise AutoSpiderError(msg % src)
            try:
                results = res.file(_file).get(dst)
            except Exception:
                raise AutoSpiderError('downloading files from XNAT failed.')

        return results

    def download_xnat_resource(self, src, dst):
        """Download XNAT complete resource."""
        results = None
        with XnatUtils.get_interface(host=self.host, user=self.user,
                                     pwd=self.pwd) as intf:
            try:
                res = intf.select(src)
                if not res.exists():
                    msg = 'resources specified by %s not found on XNAT.'
                    raise AutoSpiderError(msg % src)
            except Exception:
                msg = 'resources can not be checked because the path given is \
wrong for XNAT: %s. Please check https://wiki.xnat.org/display/XNAT16/\
XNAT+REST+API+Directory for the path.'
                raise AutoSpiderError(msg % src)

            try:
                # res.get(dst, extract=True)
                results = XnatUtils.download_files_from_obj(dst, res)
                if len(results) == 1:
                    return results[0]
                else:
                    return results
            except Exception as err:
                print(err)
                raise AutoSpiderError('downloading resource from XNAT failed.')

        return results

    def is_xnat_uri(self, uri):
        """Check if uri is xnat or local."""
        return uri.startswith('xnat:/')

    def print_args(self, argument_parse):
        """
        print arguments given to the Spider

        :param argument_parse: argument parser
        :return: None
        """
        self.time_writer("-- Arguments given to the AutoSpider --")
        self.time_writer("Argument : Value ")
        self.time_writer("-----------------------------------")
        for info, value in sorted(vars(argument_parse).items()):
            self.time_writer("%s : %s" % (info, value))
        self.time_writer("-----------------------------------")


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
    def __init__(self, name=None, use_date=False):
        """
        Entry point of TimedWriter class

        :param name: Name to give the TimedWriter
        :return: None

        """
        self.start_time = time.localtime()
        self.name = name
        self.use_date = use_date

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
        if self.use_date:
            now = datetime.now()
            msg = "%s[%s] %s" % (msg, now.strftime("%Y-%m-%d %H:%M:%S"), text)
        else:
            time_now = time.localtime()
            time_diff = time.mktime(time_now) - time.mktime(self.start_time)
            (days, res) = divmod(time_diff, 86400)
            (hours, res) = divmod(res, 3600)
            (mins, secs) = divmod(res, 60)
            msg = ("%s[%dd %02dh %02dm %02ds] %s"
                   % (msg, days, hours, mins, secs, text))
        print(msg, file=pipe)

    def __call__(self, text, pipe=sys.stdout):
        """
        Prints a timed message calling print_timed_message

        :param text: text to print
        :param pipe: pipe to write to. defaults to sys.stdout
        :return: None

        """
        self.print_timed_message(text, pipe=pipe)


# Functions
def get_default_argparser(name, description):
    """
    Return default argparser arguments for all Spider

    :return: argparser obj

    """
    from argparse import ArgumentParser
    ap = ArgumentParser(prog=name, description=description)
    ap.add_argument('-p', dest='proj_label', help='Project Label',
                    required=True)
    ap.add_argument('-s', dest='subj_label', help='Subject Label',
                    required=True)
    ap.add_argument('-e', dest='sess_label', help='Session Label',
                    required=True)
    ap.add_argument('-d', dest='temp_dir', help='Temporary Directory',
                    required=True)
    ap.add_argument('--suffix', dest='suffix', default=None,
                    help='assessor suffix. default: None')
    ap.add_argument(
        '--host', dest='host', default=None,
        help='Set XNAT Host. Default: using env variable XNAT_HOST')
    ap.add_argument(
        '--user', dest='user', default=None,
        help='Set XNAT User.')
    ap.add_argument(
        '--no_subdir', action='store_false', dest='subdir',
        help="Do not create a subdir Temp in the jobdir if the directory \
isn't empty.")
    ap.add_argument(
        '--skipfinish', action='store_true', dest='skipfinish',
        help='Skip the finish step, so do not move files to upload queue')
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


def get_auto_argparser(name, description):
    """
    Return default argparser arguments for AutoSpider

    :return: argparser obj

    """
    from argparse import ArgumentParser
    ap = ArgumentParser(prog=name, description=description)
    ap.add_argument('-d', dest='temp_dir', help='Temporary Directory',
                    required=True)
    ap.add_argument('-a', '--assessor', dest='assessor_label', required=True,
                    help='XNAT Assessor label.')
    ap.add_argument('--suffix', dest='suffix', default=None,
                    help='assessor suffix. default: None')
    ap.add_argument(
        '--host', dest='host', default=None,
        help='Set XNAT Host. Default: using env variable XNAT_HOST')
    ap.add_argument(
        '--user', dest='user', default=None,
        help='Set XNAT User.')
    ap.add_argument(
        '--no_subdir', action='store_false', dest='subdir',
        help="Do not create a subdir Temp in the jobdir if the directory \
isn't empty.")
    ap.add_argument(
        '--skipfinish', action='store_true', dest='skipfinish',
        help='Skip the finish step, so do not move files to upload queue')
    return ap


def smaller_str(str_option, size=10, end=False):
    """Method to shorten a string into a smaller size.

    :param str_option: string to shorten
    :param size: size of the string to keep (default: 10 characters)
    :param end: keep the end of the string visible (default beginning)
    :return: shortened string
    """
    if len(str_option) > size:
        if end:
            return '...%s' % (str_option[-size:])
        else:
            return '%s...' % (str_option[:size])
    else:
        return str_option


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
    """Load Inputs for AutoSpider."""
    with open(inputs_file, 'Ur') as f:
        data = list(tuple(rec) for rec in csv.reader(f, delimiter=','))
    return data


def load_outputs(outputs_file):
    """Load Outputs for AutoSpider."""
    with open(outputs_file, 'Ur') as f:
        data = list(tuple(rec) for rec in csv.reader(f, delimiter=','))
    return data


def load_template(template_file):
    """Load template for AutoSpider."""
    with open(template_file, "r") as f:
        data = f.read()
    return data


def use_time_writer(time_writer, msg):
    """Print using the time_writer or just print if not define."""
    if not time_writer:
        print(msg)
    else:
        time_writer(msg)


def run_cmd(exe_lang, fpath, time_writer=None, matlab_bin='matlab'):
    """
    Run the file fpath using the exe_lang specified.

    :param exe_lang: executable language (bash, python, ruby, matlab)
    :param fpath: file to run
    :param time_writer: time writer to display time for each line print
    :return: None
    """
    use_time_writer(time_writer, '-------- Run Command --------')

    if exe_lang == 'matlab':
        exe = '%s -singleCompThread -nodesktop -nosplash <' % matlab_bin
    else:
        os.chmod(fpath, os.stat(fpath)[ST_MODE] | S_IXUSR)
        exe = exe_lang
    cmd = '%s "%s"' % (exe, fpath)

    use_time_writer(time_writer, "Running command: %s" % cmd)
    result = execute_cmd(cmd, time_writer=time_writer)
    use_time_writer(time_writer, '-----------------------------------')
    return result


def execute_cmd(cmd, time_writer=None):
    """
    Execute a command and print in time the output using subprocess

    :param cmd: command to run
    :return: True if succeeded, False otherwise
    """
    process = sb.Popen(cmd, shell=True, stdout=sb.PIPE, stderr=sb.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline().rstrip()
        if nextline == '' and process.poll() is not None:
            break
        use_time_writer(time_writer, nextline)

    output, error = process.communicate()

    if process.returncode:
        return False
    return True


# PDF Generator for spiders:
# Display images:
def plot_images(pdf_path, page_index, nii_images, title,
                image_labels, slices=None, cmap='gray',
                vmins=None, vmaxs=None, volume_ind=None,
                orient='ax', time_writer=None):
    """Plot list of images (3D-4D) on a figure (PDF page).

    plot_images_figure will create one pdf page with only images.
    Each image corresponds to one line with by default axial/sag/cor view
    of the mid slice. If you use slices, it will show different slices of
    the axial plan view. You can specify the cmap and the vmins/vmaxs if
    needed by using a dictionary with the index of each line (0, 1, ...).

    :param pdf_path: path to the pdf to save this figure to
    :param page_index: page index for PDF
    :param nii_images: python list of nifty images
    :param title: Title for the report page
    :param image_labels: list of titles for each images
        one per image in nii_images
    :param slices: dictionary of list of slices to display
        if None, display axial, coronal, sagital
    :param cmap: cmap to use to display images or dict
        of cmaps for each images with the indices as key
    :param vmins: define vmin for display (dict)
    :param vmaxs: define vmax for display (dict)
    :param volume_ind: if slices specified and 4D image given,
                       select volume
    :param orient: 'ax' or 'cor' or 'sag', default: 'sag'
    :param time_writer: function to print with time (default using print)
    :return: pdf path created

    E.g for two images:
    images = [imag1, image2]
    slices = {'0':[50, 80, 100, 130],
              '1':[150, 180, 200, 220]}
    labels = {'0': 'Label 1',
              '1': 'Label 2'}
    cmaps = {'0':'hot',
             '1': 'gray'}
    vmins = {'0':10,
             '1':20}
    vmaxs = {'0':100,
             '1':150}
    """
    plt.ioff()
    use_time_writer(time_writer, 'INFO: generating pdf page %d with images.'
                                 % page_index)
    fig = plt.figure(page_index, figsize=(7.5, 10))
    # Titles:
    if not isinstance(cmap, dict):
        default_cmap = cmap
        cmap = {}
    else:
        default_cmap = 'gray'
    if not isinstance(vmins, dict):
        use_time_writer(time_writer, "Warning: vmins wasn't a dictionary. \
Using default.")
        vmins = {}
    if not isinstance(vmaxs, dict):
        use_time_writer(time_writer, "Warning: vmaxs wasnt' a dictionary. \
Using default.")
        vmaxs = {}
    if isinstance(nii_images, basestring):
        nii_images = [nii_images]
    number_im = len(nii_images)

    if slices:
        use_time_writer(time_writer, 'INFO: showing different slices.')
    else:
        use_time_writer(time_writer, 'INFO: display different plan view \
(ax/sag/cor) of the mid slice.')
    for index, image in enumerate(nii_images):
        # Open niftis with nibabel
        f_img_ori = nib.load(image)
        # Reorient for display with python if fslswapdim exists:
        if True in [os.path.isfile(os.path.join(path, 'fslswapdim')) and
                    os.access(os.path.join(path, 'fslswapdim'), os.X_OK)
                    for path in os.environ["PATH"].split(os.pathsep)]:
            if image.endswith('.nii.gz'):
                ext = '.nii.gz'
            else:
                ext = '.nii'
            image_name = ('%s_reorient%s'
                          % (os.path.basename(image).split('.')[0], ext))
            image_reorient = os.path.join(os.path.dirname(image),
                                          image_name)
            qform = f_img_ori.header.get_qform()
            v = np.argmax(np.absolute(qform[0:3, 0:3]), axis=0)
            neg = {0: '', 1: '', 2: ''}
            if qform[v[0]][0] < 0:
                neg[0] = '-'
            if qform[v[1]][1] < 0:
                neg[1] = '-'
            if qform[v[2]][2] < 0:
                neg[2] = '-'
            args = '%s%s %s%s %s%s' % (neg[np.where(v == 0)[0][0]],
                                       FSLSWAP_VAL[np.where(v == 0)[0][0]],
                                       neg[np.where(v == 1)[0][0]],
                                       FSLSWAP_VAL[np.where(v == 1)[0][0]],
                                       neg[np.where(v == 2)[0][0]],
                                       FSLSWAP_VAL[np.where(v == 2)[0][0]])
            cmd = 'fslswapdim %s %s %s' % (image, args, image_reorient)
            use_time_writer(time_writer, 'INFO: command: %s' % cmd)
            os.system(cmd)

            if not os.path.exists(image_reorient) and \
               image_reorient.endswith('.nii'):
                image_reorient = '%s.gz' % image_reorient
            data = nib.load(image_reorient).get_data()
        else:
            data = f_img_ori.get_data()
        if len(data.shape) > 3:
            if isinstance(volume_ind, int):
                data = data[:, :, :, volume_ind]
            else:
                data = data[:, :, :, old_div(data.shape[3], 2)]
        default_slices = [old_div(data.shape[2], 4), old_div(data.shape[2], 2),
                          3 * old_div(data.shape[2], 4)]
        default_label = 'Line %s' % index
        if slices:
            if not isinstance(slices, dict):
                use_time_writer(time_writer, "Warning: slices wasn't a \
dictionary. Using default.")
                slices = {}
            li_slices = slices.get(str(index), default_slices)
            slices_number = len(li_slices)
            for slice_ind, slice_value in enumerate(li_slices):
                ind = slices_number * index + slice_ind + 1
                ax = fig.add_subplot(number_im, slices_number, ind)
                if orient == 'cor':
                    dslice = data[:, slice_value, :]
                elif orient == 'ax':
                    dslice = data[:, :, slice_value]
                else:
                    dslice = data[slice_value, :, :]
                ax.imshow(np.rot90(np.transpose(dslice), 2),
                          cmap=cmap.get(str(index), default_cmap),
                          vmin=vmins.get(str(index), None),
                          vmax=vmaxs.get(str(index), None))
                ax.set_title('Slice %d' % slice_value, fontsize=7)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_axis_off()
                if slice_ind == 0:
                    ax.set_ylabel(image_labels.get(str(index),
                                  default_label), fontsize=9)
        else:
            # Fix Orientation:
            dslice = []
            dslice_z = data[:, :, old_div(data.shape[2], 2)]
            if dslice_z.shape[0] != dslice_z.shape[1]:
                dslice_z = imresize(dslice_z, (max(dslice_z.shape),
                                               max(dslice_z.shape)))
            dslice_y = data[:, old_div(data.shape[1], 2), :]
            if dslice_y.shape[0] != dslice_y.shape[1]:
                dslice_y = imresize(dslice_y, (max(dslice_y.shape),
                                               max(dslice_y.shape)))
            dslice_x = data[old_div(data.shape[0], 2), :, :]
            if dslice_x.shape[0] != dslice_x.shape[1]:
                dslice_x = imresize(dslice_x, (max(dslice_x.shape),
                                               max(dslice_x.shape)))

            dslice = [dslice_z, dslice_y, dslice_x]
            ax = fig.add_subplot(number_im, 3, 3 * index + 1)
            ax.imshow(np.rot90(np.transpose(dslice[0]), 2),
                      cmap=cmap.get(str(index), default_cmap),
                      vmin=vmins.get(str(index), None),
                      vmax=vmaxs.get(str(index), None))
            ax.set_title('Axial', fontsize=7)
            ax.set_ylabel(image_labels.get(str(index), default_label),
                          fontsize=9)
            ax.set_xticks([])
            ax.set_yticks([])
            ax = fig.add_subplot(number_im, 3, 3 * index + 2)
            ax.imshow(np.rot90(np.transpose(dslice[1]), 2),
                      cmap=cmap.get(str(index), default_cmap),
                      vmin=vmins.get(str(index), None),
                      vmax=vmaxs.get(str(index), None))
            ax.set_title('Coronal', fontsize=7)
            ax.set_axis_off()
            ax = fig.add_subplot(number_im, 3, 3 * index + 3)
            ax.imshow(np.rot90(np.transpose(dslice[2]), 2),
                      cmap=cmap.get(str(index), default_cmap),
                      vmin=vmins.get(str(index), None),
                      vmax=vmaxs.get(str(index), None))
            ax.set_title('Sagittal', fontsize=7)
            ax.set_axis_off()

    fig.tight_layout()
    date = datetime.now()
    # Titles page
    plt.figtext(0.5, 0.985, '-- %s PDF report --' % title,
                horizontalalignment='center', fontsize=12)
    plt.figtext(0.5, 0.02, 'Date: %s -- page %d' % (str(date), page_index),
                horizontalalignment='center', fontsize=8)
    fig.savefig(pdf_path, transparent=True, orientation='portrait',
                dpi=100)
    plt.close(fig)
    return pdf_path


# Plot statistics in a table
def plot_stats(pdf_path, page_index, stats_dict, title,
               tables_number=3, columns_header=['Header', 'Value'],
               limit_size_text_column1=30, limit_size_text_column2=10,
               time_writer=None):
    """Generate pdf report of stats information from a csv/txt.

    plot_stats_page generate a pdf page displaying a dictionary
    of stats given to the function. Column 1 represents the key
    or header and the column 2 represents the value associated.
    You can rename the two column by using the args column1/2.
    There are three columns than can have 50 values max.

    :param pdf_path: path to the pdf to save this figure to
    :param page_index: page index for PDF
    :param stats_dict: python dictionary of key=value to display
    :param title: Title for the report page
    :param tables_number: number of columns to display (def:3)
    :param columns_header: list of header for the column
        default: header, value
    :param limit_size_text_column1: limit of text display in column 1
    :param limit_size_text_column2: limit of text display in column 2
    :param time_writer: function to print with time (default using print)
    :return: pdf path created
    """
    plt.ioff()
    use_time_writer(time_writer,
                    'INFO: generating pdf page %d with stats.' % page_index)

    cell_text = list()
    for key, value in list(stats_dict.items()):
        txt = smaller_str(key.strip().replace('"', ''),
                          size=limit_size_text_column1)
        val = smaller_str(str(value),
                          size=limit_size_text_column2)
        cell_text.append([txt, "%s" % val])

    # Make the table
    fig = plt.figure(page_index, figsize=(7.5, 10))
    nb_stats = len(list(stats_dict.keys()))
    for i in range(tables_number):
        ax = fig.add_subplot(1, tables_number, i + 1)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.axis('off')
        csize = old_div(nb_stats, 3)
        the_table = ax.table(
            cellText=cell_text[csize * i:csize * (i + 1)],
            colColours=[(0.8, 0.4, 0.4), (1.0, 1.0, 0.4)],
            colLabels=columns_header,
            colWidths=[0.8, 0.32],
            loc='center',
            rowLoc='left',
            colLoc='left',
            cellLoc='left')

        the_table.auto_set_font_size(False)
        the_table.set_fontsize(6)

    # Set footer and title
    date = datetime.now()
    plt.figtext(0.5, 0.985, '-- %s PDF report --' % title,
                horizontalalignment='center', fontsize=12)
    plt.figtext(0.5, 0.02, 'Date: %s -- page %d' % (str(date), page_index),
                horizontalalignment='center', fontsize=8)
    fig.savefig(pdf_path, transparent=True, orientation='portrait',
                dpi=300)
    plt.close(fig)
    return pdf_path


# Merge PDF pages together using ghostscript 'gs'
def merge_pdfs(pdf_pages, pdf_final, time_writer=None):
    """Concatenate all pdf pages in the list into a final pdf.

    You can provide a list of pdf path or give a dictionary
    with each page specify by a number:
      pdf_pages = {'1': pdf_page1, '2': pdf_page2}

    :param pdf_pages: python list or dictionary of pdf page path
    :param pdf_final: final PDF path
    :param time_writer: function to print with time (default using print)
    :return: pdf path created
    """
    use_time_writer(time_writer, 'INFO: Concatenate all pdfs pages.')
    pages = ''
    if isinstance(pdf_pages, dict):
        for key in sorted(pdf_pages.keys()):
            pages = '%s %s ' % (pages, pdf_pages[key])
    elif isinstance(pdf_pages, list):
        pages = ' '.join(pdf_pages)
    else:
        raise TypeError('Wrong type for pdf_pages (list or dict).')
    args = '-q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite \
-dPDFSETTINGS=/prepress'
    cmd = 'gs %s -sOutputFile=%s %s' % (args, pdf_final, pages)
    use_time_writer(time_writer, 'INFO:saving final PDF: %s ' % cmd)
    os.system(cmd)
    return pdf_final
