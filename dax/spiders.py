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
    """ Base class for spider """
    def __init__(self, spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix="", subdir=True):
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
        :param subdir: create a subdir Temp in the jobdir if the directory isn't empty

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
        
    def check_executable(self, executable, name):
        """Method to check the executable.

        :param executable: executable path
        :param name: name of Executable
        :return: Complete path to the executable
        """
        if executable == name:
            # Check the output of which:
            pwhich = sb.Popen(['which', executable],
                              stdout=sb.PIPE,
                              stderr=sb.PIPE)
            results, _ = pwhich.communicate()
            if not results or results.startswith('/usr/bin/which: no'):
                raise Exception("Executable '%s' not found on your computer."
                                % (name))
        else:
            executable = os.path.abspath(executable)
            if executable.endswith(name):
                pass
            elif os.path.isdir(executable):
                executable = os.path.join(executable, name)
            if not os.path.exists(executable):
                raise Exception("Executable '%s' not found" % (executable))

        pversion = sb.Popen([executable, '--version'],
                            stdout=sb.PIPE,
                            stderr=sb.PIPE)
        nve_version, _ = pversion.communicate()
        self.time_writer('%s version: %s' %
                         (name, nve_version.strip()))
        return executable


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

    def plot_images_figure(self, pdf_path, page_index, nii_images, title,
                           image_labels, slices=None, cmap='gray',
                           vmins=None, vmaxs=None):
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
        self.time_writer('INFO: generating pdf page %d with images.'
                         % page_index)
        fig = plt.figure(page_index, figsize=(7.5, 10))
        # Titles:
        if not isinstance(cmap, dict):
            default_cmap = cmap
            cmap = {}
        else:
            default_cmap = 'gray'
        if not isinstance(vmins, dict):
            self.time_writer("Warning: vmins wasn't a dictionary. \
Using default.")
            vmins = {}
        if not isinstance(vmins, dict):
            self.time_writer("Warning: vmaxs wasnt' a dictionary. \
Using default.")
            vmaxs = {}
        if isinstance(nii_images, str):
            nii_images = [nii_images]
        number_im = len(nii_images)
        for index, image in enumerate(nii_images):
            # Open niftis with nibabel
            f_img = nib.load(image)
            data = f_img.get_data()
            if len(data.shape) == 4:
                data = data[:, :, :, data.shape[3]/2]
            default_slices = [data.shape[2]/4, data.shape[2]/2,
                              3*data.shape[2]/4]
            default_label = 'Line %s' % index

            if slices:
                if not isinstance(slices, dict):
                    self.time_writer("Warning: slices wasn't a dictionary. \
Using default.")
                    slices = {}
                self.time_writer('INFO: showing different slices.')
                li_slices = slices.get(str(index), default_slices)
                slices_number = len(li_slices)
                for slice_ind, slice_value in enumerate(li_slices):
                    ind = slices_number*index+slice_ind+1
                    ax = fig.add_subplot(number_im, slices_number, ind)
                    data_z_rot = np.rot90(data[:, :, slice_value])
                    ax.imshow(data_z_rot,
                              cmap=cmap.get(str(index), default_cmap),
                              vmin=vmins.get(str(index), None),
                              vmax=vmaxs.get(str(index), None))
                    ax.set_title('Slice %d' % slice_value, fontsize=7)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    if slice_ind == 0:
                        ax.set_ylabel(image_labels.get(str(index),
                                      default_label), fontsize=9)
            else:
                self.time_writer('INFO: display different plan view \
(ax/sag/cor) of the mid slice.')
                ax = fig.add_subplot(number_im, 3, 3*index+1)
                data_z_rot = np.rot90(data[:, :, data.shape[2]/2])
                ax.imshow(data_z_rot, cmap=cmap.get(str(index), default_cmap),
                          vmin=vmins.get(str(index), None),
                          vmax=vmaxs.get(str(index), None))
                ax.set_title('Axial', fontsize=7)
                ax.set_ylabel(image_labels.get(str(index), default_label),
                              fontsize=9)
                ax.set_xticks([])
                ax.set_yticks([])
                ax = fig.add_subplot(number_im, 3, 3*index+2)
                data_y_rot = np.rot90(data[:, data.shape[1]/2, :])
                ax.imshow(data_y_rot, cmap=cmap.get(str(index), default_cmap),
                          vmin=vmins.get(str(index), None),
                          vmax=vmaxs.get(str(index), None))
                ax.set_title('Coronal', fontsize=7)
                ax.set_axis_off()
                ax = fig.add_subplot(number_im, 3, 3*index+3)
                data_x_rot = np.rot90(data[data.shape[0]/2, :, :])
                ax.imshow(data_x_rot, cmap=cmap.get(str(index), default_cmap),
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
        plt.show()
        fig.savefig(pdf_path, transparent=True, orientation='portrait',
                    dpi=100)
        plt.close(fig)

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
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix="", subdir=True):
        """
        Entry point for Derived class for Spider on Scan level

        :param super --> see base class
        :param xnat_scan: scan ID on XNAT (if running on a specific scan)
        """
        super(ScanSpider, self).__init__(spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                                         xnat_host, xnat_user, xnat_pass, suffix, subdir)
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
                 xnat_host=None, xnat_user=None, xnat_pass=None, suffix="", subdir=True):
        """
        Entry point for Derived class for Spider on Session level

        :param super --> see base class
        """
        super(SessionSpider, self).__init__(spider_path, jobdir, xnat_project, xnat_subject, xnat_session,
                                            xnat_host, xnat_user, xnat_pass, suffix, subdir)

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
