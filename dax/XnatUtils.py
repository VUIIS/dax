""" XnatUtils contains useful function to interface with XNAT using Pyxnat module
The functions are divided into 4 categories:
1) Class Specific to XNAT and Spiders:
InterfaceTemp to create an interface with XNAT using a tempfolder
AssessorHandler to handle assessor label string and access object
SpiderProcessHandler to handle results at the end of any spider

2) Methods to query XNAT database and get XNAT object :

3) Methods to access/check objects on XNAT

4) Methods to Download / Upload data to XNAT

5) Other Methods

6) Cached Class for DAX

7) Old download functions still used in some spiders
"""

import re
import os
import sys
import glob
import gzip
import shutil
import tempfile
import random
import subprocess
import collections
from lxml import etree
from pyxnat import Interface
from datetime import datetime

import task
from dax_settings import RESULTS_DIR, XSITYPE_INCLUDE

import xml.etree.cElementTree as ET

NS = {'xnat' : 'http://nrg.wustl.edu/xnat',
      'proc' : 'http://nrg.wustl.edu/proc',
      'fs'   : 'http://nrg.wustl.edu/fs',
      'xsi'  : 'http://www.w3.org/2001/XMLSchema-instance'}

### VARIABLE ###
# Assessor datatypes
DEFAULT_FS_DATATYPE = 'fs:fsData'
DEFAULT_DATATYPE = 'proc:genProcData'

# URI
PROJECTS_URI     = '/REST/projects'
PROJECT_URI      = '/REST/projects/{project}'
P_RESOURCES_URI  = '/REST/projects/{project}/resources'
P_RESOURCE_URI   = '/REST/projects/{project}/resources/{resource}'
ALL_SUBJ_URI     = '/REST/subjects'
SUBJECTS_URI     = '/REST/projects/{project}/subjects'
SUBJECT_URI      = '/REST/projects/{project}/subjects/{subject}'
SU_RESOURCES_URI = '/REST/projects/{project}/subjects/{subject}/resources'
SU_RESOURCE_URI  = '/REST/projects/{project}/subjects/{subject}/resources/{resource}'
SE_ARCHIVE_URI   = '/REST/archive/experiments'
ALL_SESS_URI     = '/REST/experiments'
ALL_SESS_PROJ_URI= '/REST/projects/{project}/experiments'
SESSIONS_URI     = '/REST/projects/{project}/subjects/{subject}/experiments'
SESSION_URI      = '/REST/projects/{project}/subjects/{subject}/experiments/{session}'
SE_RESOURCES_URI = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/resources'
SE_RESOURCE_URI  = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/resources/{resource}'
SCANS_URI        = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/scans'
SCAN_URI         = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/scans/{scan}'
SC_RESOURCES_URI = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/scans/{scan}/resources'
SC_RESOURCE_URI  = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/scans/{scan}/resources/{resource}'
ASSESSORS_URI    = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/assessors'
ASSESSOR_URI     = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/assessors/{assessor}'
A_RESOURCES_URI  = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/assessors/{assessor}/out/resources'
A_RESOURCE_URI   = '/REST/projects/{project}/subjects/{subject}/experiments/{session}/assessors/{assessor}/out/resources/{resource}'

# List post URI variables:
SUBJECT_POST_URI = '''?columns=ID,project,label,URI,last_modified,src,handedness,gender,yob'''
SESSION_POST_URI = '''?xsiType={stype}&columns=ID,URI,subject_label,subject_ID,modality,project,date,xsiType,{stype}/age,label,{stype}/meta/last_modified,{stype}/original'''
SCAN_POST_URI = '''?columns=ID,URI,label,subject_label,project,xnat:imagesessiondata/scans/scan/id,xnat:imagesessiondata/scans/scan/type,xnat:imagesessiondata/scans/scan/quality,xnat:imagesessiondata/scans/scan/note,xnat:imagesessiondata/scans/scan/frames,xnat:imagesessiondata/scans/scan/series_description,xnat:imagesessiondata/subject_id'''
SCAN_PROJ_POST_URI = '''?project={project}&xsiType=xnat:imageSessionData&columns=ID,URI,label,subject_label,project,xnat:imagesessiondata/subject_id,xnat:imagescandata/id,xnat:imagescandata/type,xnat:imagescandata/quality,xnat:imagescandata/note,xnat:imagescandata/frames,xnat:imagescandata/series_description,xnat:imagescandata/file/label'''
SCAN_PROJ_INCLUDED_POST_URI = '''?xnat:imagesessiondata/sharing/share/project={project}&xsiType=xnat:imageSessionData&columns=ID,URI,label,subject_label,project,xnat:imagesessiondata/subject_id,xnat:imagescandata/id,xnat:imagescandata/type,xnat:imagescandata/quality,xnat:imagescandata/note,xnat:imagescandata/frames,xnat:imagescandata/series_description,xnat:imagescandata/file/label'''
ASSESSOR_FS_POST_URI = '''?columns=ID,label,URI,xsiType,project,xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,xnat:imagesessiondata/label,URI,{fstype}/procstatus,{fstype}/validation/status&xsiType={fstype}'''
ASSESSOR_PR_POST_URI = '''?columns=ID,label,URI,xsiType,project,xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,xnat:imagesessiondata/label,{pstype}/procstatus,{pstype}/proctype,{pstype}/validation/status&xsiType={pstype}'''
ASSESSOR_FS_PROJ_POST_URI = '''?project={project}&xsiType={fstype}&columns=ID,label,URI,xsiType,project,xnat:imagesessiondata/subject_id,subject_label,xnat:imagesessiondata/id,xnat:imagesessiondata/label,URI,{fstype}/procstatus,{fstype}/validation/status,{fstype}/procversion,{fstype}/jobstartdate,{fstype}/memused,{fstype}/walltimeused,{fstype}/jobid,{fstype}/jobnode,{fstype}/out/file/label'''
ASSESSOR_PR_PROJ_POST_URI = '''?project={project}&xsiType={pstype}&columns=ID,label,URI,xsiType,project,xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,xnat:imagesessiondata/label,{pstype}/procstatus,{pstype}/proctype,{pstype}/validation/status,{pstype}/procversion,{pstype}/jobstartdate,{pstype}/memused,{pstype}/walltimeused,{pstype}/jobid,{pstype}/jobnode,{pstype}/out/file/label'''

####################################################################################
#                                    1) CLASS                                      #
####################################################################################
class InterfaceTemp(Interface):
    """
    Extends the pyxnat.Interface class to make a temporary directory, write the
     cache to it and then blow it away on the Interface.disconnect call()
     NOTE: This is deprecated in pyxnat 1.0.0.0
    """
    def __init__(self, xnat_host, xnat_user, xnat_pass, temp_dir=None):
        """
        Entry point for the InterfaceTemp class

        :param xnat_host: XNAT Host url
        :param xnat_user: XNAT User ID
        :param xnat_pass: XNAT Password
        :param temp_dir: Directory to write the Cache to
        :return: None

        """
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        self.temp_dir = temp_dir
        super(InterfaceTemp, self).__init__(server=xnat_host, user=xnat_user, password=xnat_pass, cachedir=temp_dir)

    def disconnect(self):
        """
        Disconnect the JSESSION and blow away the cache

        :return: None
        """
        self._exec('/data/JSESSION', method='DELETE')
        shutil.rmtree(self.temp_dir)

class AssessorHandler:
    """
    Class to intelligently deal with the Assessor labels and to hopefully make the splitting of the strings easier.
    """
    def __init__(self, label):
        """
        The purpose of this method is to split an assessor label and parse out its associated pieces

        :param label: An assessor label of the form
         ProjectID-x-Subject_label-x-SessionLabel-x-ScanId-x-proctype or
         ProjectID-x-Subject_label-x-SessionLabel-x-proctype
        :return: None

        """
        self.assessor_label = label
        self.is_session_assessor = False
        self.is_scan_assessor=False
        if len(re.findall('-x-', label)) == 3:
            self.project_id, self.subject_label, self.session_label, self.proctype = label.split('-x-')
            self.scan_id = None
            self.is_session_assessor = True
        elif len(re.findall('-x-', label)) == 4:
            self.project_id, self.subject_label, self.session_label, self.scan_id, self.proctype = label.split('-x-')
            self.is_scan_assessor = True
        else:
            self.assessor_label = None

    def is_valid(self):
        """
        Check to see if we have a valid assessor label (aka not None)

        :return: True if valid, False if not valid
        """
        return self.assessor_label != None

    def get_project_id(self):
        """
        Get the project ID from the assessor label

        :return: The XNAT project label

        """
        return self.project_id

    def get_subject_label(self):
        """
        Get the subject label from the assessor label

        :return: The XNAT subject label

        """
        return self.subject_label

    def get_session_label(self):
        """
        Get the session label from the assessor label

        :return: The XNAT session label

        """
        return self.session_label

    def get_scan_id(self):
        """
        Get the scan ID from teh assessor label

        :return: The scan id for the assessor label

        """
        return self.scan_id

    def get_proctype(self):
        """
        Get the proctype from the assessor label

        :return: The proctype for the assessor

        """
        return self.proctype

    def select_assessor(self, intf):
        """
        Run Interface.select() on the assessor label

        :param intf: pyxnat.Interface object
        :return: The pyxnat EObject of the assessor

        """
        string_obj = '''/project/{project}/subject/{subject}/experiment/{session}/assessor/{label}'''.format(project=self.project_id, subject=self.subject_label, session=self.session_label, label=self.assessor_label)
        return intf.select(string_obj)

class SpiderProcessHandler:
    """
    Class to handle the uploading of results from a spider to the upload directory
    """
    def __init__(self, script_name, suffix, project, subject, experiment, scan=None, time_writer=None):
        """
        Entry point to the SpiderProcessHandler Class

        :param script_name: Basename of the Spider (full path works as well, it will be removed)
        :param suffix: Processor suffix
        :param project: Project on XNAT
        :param subject: Subject on XNAT
        :param experiment: Session on XNAT
        :param scan: Scan (if needed) On Xnat
        :param time_writer: TimedWriter object if wanted
        :return: None

        """
        #Variables:
        self.error = 0
        self.has_pdf = 0
        self.time_writer = time_writer
        # Get the process name and the version
        if len(script_name.split('/')) > 1:
            script_name = os.path.basename(script_name)
        if script_name.endswith('.py'):
            script_name = script_name[:-3]
        if 'Spider' in script_name:
            script_name = script_name[7:]

        # get the processname from spider
        if len(re.split("/*_v[0-9]/*", script_name)) > 1:
            self.version = script_name.split('_v')[-1].replace('_','.')
            proctype = re.split("/*_v[0-9]/*", script_name)[0]+'_v'+self.version.split('.')[0]
        else:
            self.version = '1.0.0'
            proctype = script_name

        if suffix:
            if suffix[0] !='_':
                suffix = '_'+suffix

            suffix = re.sub('[^a-zA-Z0-9]', '_', suffix)
            if suffix[-1] == '_':
                suffix = suffix[:-1]
            proctype = proctype + suffix

        #Create the assessor handler
        if not scan:
            assessor_label = project+'-x-'+subject+'-x-'+experiment+'-x-'+proctype
        else:
            assessor_label = project+'-x-'+subject+'-x-'+experiment+'-x-'+scan+'-x-'+proctype
        self.assr_handler = AssessorHandler(assessor_label)

        #Create the upload directory
        self.directory = os.path.join(RESULTS_DIR, assessor_label)
        #if the folder already exists : remove it
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        else:
            #Remove files in directories
            clean_directory(self.directory)

        self.print_msg("INFO: Handling results ...")
        self.print_msg('''-Creating folder {folder} for {label}'''.format(folder=self.directory,
                                                                          label=assessor_label))

    def print_msg(self, msg):
        """
        Prints a message using TimedWriter object if defined otherwise default print

        :param msg: Message to print
        :return: None

        """
        if self.time_writer:
            self.time_writer(msg)
        else:
            print msg

    def print_err(self, msg):
        """
        Print error message using time writer if set, print otherwise

        :param msg: Message to print
        :return: None

        """
        if self.time_writer:
            self.time_writer.print_stderr_message(msg)
        else:
            print "Error: "+msg

    def set_error(self):
        """
        Set the flag for the error to 1

        :return: None

        """
        self.error = 1

    def file_exists(self, fpath):
        """
        Check to see if a file exists

        :param fpath: full path to a file to assert it exists
        :return: True if it exists, False if it doesn't

        """
        if not os.path.isfile(fpath.strip()):
            self.error = 1
            self.print_err('''file {file} does not exists.'''.format(file=fpath))
            return False
        else:
            return True

    def folder_exists(self, fpath):
        """
        Check to see if a folder exists

        :param fpath: Full path to a folder to assert it exists
        :return: True if it exists, False if it doesn't

        """
        if not os.path.isdir(fpath.strip()):
            self.error = 1
            self.print_err('''folder {folder} does not exists.'''.format(folder=fpath))
            return False
        else:
            return True

    def print_copying_statement(self, label, src, dest):
        """
        Print a line that data is being copied to the upload directory

        :param label: The XNAT resource label
        :param src: Source directory or file
        :param dest: Destination directory or file
        :return: None

        """
        self.print_msg('''  -Copying {label}: {src} to {dest}'''.format(label=label, src=src, dest=dest))

    def add_pdf(self, filepath):
        """
        Add the PDF and run ps2pdf on the file if it ends with .ps

        :param filepath: Full path to the PDF/PS file
        :return: None

        """
        if self.file_exists(filepath):
            #Check if it's a ps:
            if filepath.lower().endswith('.ps'):
                pdf_path = os.path.splitext(filepath)[0]+'.pdf'
                ps2pdf_cmd = '''ps2pdf {ps} {pdf}'''.format(ps=filepath, pdf=pdf_path)
                self.print_msg('''  -Convertion {cmd} ...'''.format(cmd=ps2pdf_cmd))
                os.system(ps2pdf_cmd)
            else:
                pdf_path = filepath
            self.add_file(pdf_path, 'PDF')
            self.has_pdf = 1

    def add_snapshot(self, snapshot):
        """
        Add in the snapshots (for quick viewing on XNAT)

        :param snapshot: Full path to the snapshot file
        :return: None

        """
        self.add_file(snapshot, 'SNAPSHOTS')

    def add_file(self, filepath, resource):
        """
        Add a file in the assessor in the upload directory based on the
         resource name as will be seen on XNAT

        :param filepath: Full path to a file to upload
        :param resource: The resource name it should appear under in XNAT
        :return: None

        """
        if self.file_exists(filepath):
            #make the resource folder
            respath = os.path.join(self.directory, resource)
            if not os.path.exists(respath):
                os.mkdir(respath)
            #mv the file
            self.print_copying_statement(resource, filepath, respath)
            shutil.copy(filepath, respath)
            #if it's a nii or a rec file, gzip it:
            if filepath.lower().endswith('.nii') or filepath.lower().endswith('.rec'):
                os.system('gzip '+os.path.join(respath, os.path.basename(filepath)))

    def add_folder(self, folderpath, resource_name=None):
        """
        Add a folder to the assessor in the upload directory.

        :param folderpath: Full path to the folder to upoad
        :param resource_name: Resource name desired (if different than basename)
        :except shutil.Error: Directories are the same
        :except OSError: The directory doesn't exist
        :return: None

        """
        if self.folder_exists(folderpath):
            if not resource_name:
                res = os.path.basename(os.path.abspath(folderpath))
            else:
                res = resource_name
            dest = os.path.join(self.directory, res)

            try:
                shutil.copytree(folderpath, dest)
                self.print_copying_statement(res, folderpath, dest)
            # Directories are the same
            except shutil.Error as excep:
                self.print_err('Directory not copied. Error: %s' % excep)
            # Any error saying that the directory doesn't exist
            except OSError as excep:
                self.print_err('Directory not copied. Error: %s' % excep)

    def set_assessor_status(self, status):
        """
        Set the status of the assessor based on passed value

        :param status: Value to set the procstatus to
        :except: All catchable errors.
        :return: None
        """
        # Connection to Xnat
        try:
            xnat = get_interface()
            assessor = self.assr_handler.select_assessor(xnat)
            if self.assr_handler.get_proctype() == 'FS':
                former_status = assessor.attrs.get(DEFAULT_FS_DATATYPE+'/procstatus')
            else:
                former_status = assessor.attrs.get(DEFAULT_DATATYPE+'/procstatus')
            if assessor.exists() and former_status == task.JOB_RUNNING :
                if self.assr_handler.get_proctype() == 'FS':
                    assessor.attrs.set(DEFAULT_FS_DATATYPE+'/procstatus', status)
                    self.print_msg('  -status set for FreeSurfer to '+str(status))
                else:
                    assessor.attrs.set(DEFAULT_DATATYPE+'/procstatus', status)
                    self.print_msg('  -status set for assessor to '+str(status))
        except:
            # fail to access XNAT -- let dax_upload set the status
            pass
        finally:
            if 'xnat' in locals() or xnat != None: xnat.disconnect()

    def done(self):
        """
        Create a flag file that the assessor is ready to be uploaded and set
         the status as READY_TO_UPLOAD

        :return: None

        """
        #creating the version file to give the spider version:
        f_obj = open(os.path.join(self.directory, 'version.txt'), 'w')
        f_obj.write(self.version)
        f_obj.close()
        #Finish the folder
        if not self.error and self.has_pdf:
            self.print_msg('INFO: Job ready to be upload, error: '+ str(self.error))
            #make the flag folder
            open(os.path.join(self.directory, task.READY_TO_UPLOAD+'.txt'), 'w').close()
            #set status to ReadyToUpload
            self.set_assessor_status(task.READY_TO_UPLOAD)
        else:
            self.print_msg('INFO: Job failed, check the outlogs, error: '+ str(self.error))
            #make the flag folder
            open(os.path.join(self.directory, task.JOB_FAILED+'.txt'), 'w').close()
            #set status to JOB_FAILED
            self.set_assessor_status(task.JOB_FAILED)

    def clean(self, directory):
        """
        Clean directory if no error and pdf created

        :param directory: directory to be cleaned
        """
        if self.has_pdf and not self.error:
            #Remove the data
            shutil.rmtree(directory)

####################################################################################
#                     2) Query XNAT and Access XNAT obj                            #
####################################################################################
def get_interface(host=None, user=None, pwd=None):
    """
    Opens a connection to XNAT using XNAT_USER, XNAT_PASS, and XNAT_HOST from
     env if host/user/pwd are None.

    :param host: URL to connect to XNAT
    :param user: XNAT username
    :param pwd: XNAT password
    :return: InterfaceTemp object which extends functionaly of pyxnat.Interface

    """
    if user == None:
        user = os.environ['XNAT_USER']
    if pwd == None:
        pwd = os.environ['XNAT_PASS']
    if host == None:
        host = os.environ['XNAT_HOST']
    # Don't sys.exit, let callers catch KeyErrors
    return InterfaceTemp(host, user, pwd)

def list_projects(intf):
    """
    Gets a list of all of the projects that you have access to

    :param intf: pyxnat.Interface object
    :return: list of dictionaries of projects you have access to

    """
    projects_list = intf._get_json(PROJECTS_URI)
    return projects_list

def list_project_resources(intf, projectid):
    """
    Gets a list of all of the project resources for the project ID you want.

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :return: list of resources for the specificed project
    """
    post_uri = P_RESOURCES_URI.format(project=projectid)
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_subjects(intf, projectid=None):
    """
    List all the subjects that you have access to. Or, alternatively, list
     the subjects in a single project based on passed project ID

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :return: list of dictionaries of subjects in the project or projects.

    """
    if projectid:
        post_uri = SUBJECTS_URI.format(project=projectid)
    else:
        post_uri = ALL_SUBJ_URI

    post_uri += SUBJECT_POST_URI

    subject_list = intf._get_json(post_uri)

    for subj in subject_list:
        if projectid:
            # Override the project returned to be the one we queried
            subj['project'] = projectid

        subj['project_id'] = subj['project']
        subj['project_label'] = subj['project']
        subj['subject_id'] = subj['ID']
        subj['subject_label'] = subj['label']
        subj['last_updated'] = subj['src']

    return sorted(subject_list, key=lambda k: k['subject_label'])

def list_subject_resources(intf, projectid, subjectid):
    """
    Gets a list of all of the resources for a subject for a project
     requested by the user

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject to get resources for
    :return: List of resources for the subject

    """
    post_uri = SU_RESOURCES_URI.format(project=projectid, subject=subjectid)
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_sessions(intf, projectid=None, subjectid=None):
    """
    List all the sessions that you have access to. Or, alternatively, list the session
     in a single project (and single subject) based on passed project ID (/subject ID)

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :return: List of sessions
    """
    type_list = []
    full_sess_list = []

    if projectid and subjectid:
        post_uri = SESSIONS_URI.format(project=projectid, subject=subjectid)
    elif projectid == None and subjectid == None:
        post_uri = ALL_SESS_URI
    elif projectid and subjectid == None:
        post_uri = ALL_SESS_PROJ_URI.format(project=projectid)
    else:
        return None

    # First get a list of all experiment types
    post_uri_types = post_uri+'?columns=xsiType'
    sess_list = intf._get_json(post_uri_types)
    for sess in sess_list:
        sess_type = sess['xsiType'].lower()
        if sess_type not in type_list:
            type_list.append(sess_type)

    #Get the subjects list to get the subject ID:
    subj_list = list_subjects(intf, projectid)
    subj_id2lab = dict((subj['ID'], [subj['handedness'], subj['gender'], subj['yob']]) for subj in subj_list)

    # Get list of sessions for each type since we have to specific about last_modified field
    for sess_type in type_list:
        post_uri_type = post_uri + SESSION_POST_URI.format(stype=sess_type)
        sess_list = intf._get_json(post_uri_type)

        for sess in sess_list:
            # Override the project returned to be the one we queried
            if projectid:
                sess['project'] = projectid

            sess['project_id'] = sess['project']
            sess['project_label'] = sess['project']
            sess['subject_id'] = sess['subject_ID']
            sess['session_id'] = sess['ID']
            sess['session_label'] = sess['label']
            sess['session_type'] = sess_type.split('xnat:')[1].split('session')[0].upper()
            sess['type'] = sess_type.split('xnat:')[1].split('session')[0].upper()
            sess['last_modified'] = sess[sess_type+'/meta/last_modified']
            sess['last_updated'] = sess[sess_type+'/original']
            sess['age'] = sess[sess_type+'/age']
            sess['handedness'] = subj_id2lab[sess['subject_ID']][0]
            sess['gender'] = subj_id2lab[sess['subject_ID']][1]
            sess['yob'] = subj_id2lab[sess['subject_ID']][2]

        # Add sessions of this type to full list
        full_sess_list.extend(sess_list)

    # Return list sorted by label
    return sorted(full_sess_list, key=lambda k: k['session_label'])

def list_session_resources(intf, projectid, subjectid, sessionid):
    """
    Gets a list of all of the resources for a session associated to a subject/project
     requested by the user

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :param sessionid: ID/label of a session to get resources for
    :return: List of resources for the session

    """
    post_uri = SE_RESOURCES_URI.format(project=projectid, subject=subjectid, session=sessionid)
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_scans(intf, projectid, subjectid, sessionid):
    """
    List all the scans that you have access to based on passed session/subject/project.

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :param sessionid: ID/label of a session
    :return: List of all the scans
    """
    post_uri = SESSIONS_URI.format(project=projectid, subject=subjectid)
    post_uri += SCAN_POST_URI
    scan_list = intf._get_json(post_uri)
    new_list = []

    for scan in scan_list:
        if scan['ID'] == sessionid or scan['label'] == sessionid:
            snew = {}
            snew['scan_id'] = scan['xnat:imagesessiondata/scans/scan/id']
            snew['scan_label'] = scan['xnat:imagesessiondata/scans/scan/id']
            snew['scan_quality'] = scan['xnat:imagesessiondata/scans/scan/quality']
            snew['scan_note'] = scan['xnat:imagesessiondata/scans/scan/note']
            snew['scan_frames'] = scan['xnat:imagesessiondata/scans/scan/frames']
            snew['scan_description'] = scan['xnat:imagesessiondata/scans/scan/series_description']
            snew['scan_type'] = scan['xnat:imagesessiondata/scans/scan/type']
            snew['ID'] = scan['xnat:imagesessiondata/scans/scan/id']
            snew['label'] = scan['xnat:imagesessiondata/scans/scan/id']
            snew['quality'] = scan['xnat:imagesessiondata/scans/scan/quality']
            snew['note'] = scan['xnat:imagesessiondata/scans/scan/note']
            snew['frames'] = scan['xnat:imagesessiondata/scans/scan/frames']
            snew['series_description'] = scan['xnat:imagesessiondata/scans/scan/series_description']
            snew['type'] = scan['xnat:imagesessiondata/scans/scan/type']
            snew['project_id'] = projectid
            snew['project_label'] = projectid
            snew['subject_id'] = scan['xnat:imagesessiondata/subject_id']
            snew['subject_label'] = scan['subject_label']
            snew['session_id'] = scan['ID']
            snew['session_label'] = scan['label']
            snew['session_uri'] = scan['URI']
            new_list.append(snew)

    return sorted(new_list, key=lambda k: k['label'])

def list_project_scans(intf, projectid, include_shared=True):
    """
    List all the scans that you have access to based on passed project.

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param include_shared: include the shared data in this project
    :return: List of all the scans for the project
    """
    scans_dict = dict()

    #Get the sessions list to get the modality:
    session_list = list_sessions(intf, projectid)
    sess_id2mod = dict((sess['session_id'], [sess['handedness'], sess['gender'], sess['yob'], sess['age'], sess['last_modified'], sess['last_updated']]) for sess in session_list)

    post_uri = SE_ARCHIVE_URI
    post_uri += SCAN_PROJ_POST_URI.format(project=projectid)
    scan_list = intf._get_json(post_uri)

    for scan in scan_list:
        key = scan['ID']+'-x-'+scan['xnat:imagescandata/id']
        if scans_dict.get(key):
            scans_dict[key]['resources'].append(scan['xnat:imagescandata/file/label'])
        else:
            snew = {}
            snew['scan_id'] = scan['xnat:imagescandata/id']
            snew['scan_label'] = scan['xnat:imagescandata/id']
            snew['scan_quality'] = scan['xnat:imagescandata/quality']
            snew['scan_note'] = scan['xnat:imagescandata/note']
            snew['scan_frames'] = scan['xnat:imagescandata/frames']
            snew['scan_description'] = scan['xnat:imagescandata/series_description']
            snew['scan_type'] = scan['xnat:imagescandata/type']
            snew['ID'] = scan['xnat:imagescandata/id']
            snew['label'] = scan['xnat:imagescandata/id']
            snew['quality'] = scan['xnat:imagescandata/quality']
            snew['note'] = scan['xnat:imagescandata/note']
            snew['frames'] = scan['xnat:imagescandata/frames']
            snew['series_description'] = scan['xnat:imagescandata/series_description']
            snew['type'] = scan['xnat:imagescandata/type']
            snew['project_id'] = projectid
            snew['project_label'] = projectid
            snew['subject_id'] = scan['xnat:imagesessiondata/subject_id']
            snew['subject_label'] = scan['subject_label']
            snew['session_type'] = scan['xsiType'].split('xnat:')[1].split('Session')[0].upper()
            snew['session_id'] = scan['ID']
            snew['session_label'] = scan['label']
            snew['session_uri'] = scan['URI']
            snew['handedness'] = sess_id2mod[scan['ID']][0]
            snew['gender'] = sess_id2mod[scan['ID']][1]
            snew['yob'] = sess_id2mod[scan['ID']][2]
            snew['age'] = sess_id2mod[scan['ID']][3]
            snew['last_modified'] = sess_id2mod[scan['ID']][4]
            snew['last_updated'] = sess_id2mod[scan['ID']][5]
            snew['resources'] = [scan['xnat:imagescandata/file/label']]
            # make a dictionary of dictionaries
            scans_dict[key] = (snew)

    if include_shared:
        post_uri = SE_ARCHIVE_URI
        post_uri += SCAN_PROJ_INCLUDED_POST_URI.format(project=projectid)
        scan_list = intf._get_json(post_uri)

        for scan in scan_list:
            key = scan['ID']+'-x-'+scan['xnat:imagescandata/id']
            if scans_dict.get(key):
                scans_dict[key]['resources'].append(scan['xnat:imagescandata/file/label'])
            else:
                snew = {}
                snew['scan_id'] = scan['xnat:imagescandata/id']
                snew['scan_label'] = scan['xnat:imagescandata/id']
                snew['scan_quality'] = scan['xnat:imagescandata/quality']
                snew['scan_note'] = scan['xnat:imagescandata/note']
                snew['scan_frames'] = scan['xnat:imagescandata/frames']
                snew['scan_description'] = scan['xnat:imagescandata/series_description']
                snew['scan_type'] = scan['xnat:imagescandata/type']
                snew['ID'] = scan['xnat:imagescandata/id']
                snew['label'] = scan['xnat:imagescandata/id']
                snew['quality'] = scan['xnat:imagescandata/quality']
                snew['note'] = scan['xnat:imagescandata/note']
                snew['frames'] = scan['xnat:imagescandata/frames']
                snew['series_description'] = scan['xnat:imagescandata/series_description']
                snew['type'] = scan['xnat:imagescandata/type']
                snew['project_id'] = projectid
                snew['project_label'] = projectid
                snew['subject_id'] = scan['xnat:imagesessiondata/subject_id']
                snew['subject_label'] = scan['subject_label']
                snew['session_type'] = scan['xsiType'].split('xnat:')[1].split('Session')[0].upper()
                snew['session_id'] = scan['ID']
                snew['session_label'] = scan['label']
                snew['session_uri'] = scan['URI']
                snew['handedness'] = sess_id2mod[scan['ID']][0]
                snew['gender'] = sess_id2mod[scan['ID']][1]
                snew['yob'] = sess_id2mod[scan['ID']][2]
                snew['age'] = sess_id2mod[scan['ID']][3]
                snew['last_modified'] = sess_id2mod[scan['ID']][4]
                snew['last_updated'] = sess_id2mod[scan['ID']][5]
                snew['resources'] = [scan['xnat:imagescandata/file/label']]
                # make a dictionary of dictionaries
                scans_dict[key] = (snew)

    return sorted(scans_dict.values(), key=lambda k: k['scan_label'])

def list_scan_resources(intf, projectid, subjectid, sessionid, scanid):
    """
    Gets a list of all of the resources for a scan associated to a session/subject/project
     requested by the user

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :param sessionid: ID/label of a session
    :param scanid: ID of a scan to get resources for
    :return: List of resources for the scan
    """
    post_uri = SC_RESOURCES_URI.format(project=projectid,
                                       subject=subjectid,
                                       session=sessionid,
                                       scan=scanid)
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_assessors(intf, projectid, subjectid, sessionid):
    """
    List all the assessors that you have access to based on passed session/subject/project.

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :param sessionid: ID/label of a session
    :return: List of all the assessors

    """
    new_list = list()

    #Check that the assessors types are present on XNAT
    if not has_dax_datatypes(intf):
        print '** WARNING: datatypes for processors not found on XNAT. **'
        return new_list

    if has_fs_datatypes:
        # First get FreeSurfer
        post_uri = ASSESSORS_URI.format(project=projectid,
                                        subject=subjectid,
                                        session=sessionid)
        post_uri += ASSESSOR_FS_POST_URI.format(fstype=DEFAULT_FS_DATATYPE)
        assessor_list = intf._get_json(post_uri)

        for asse in assessor_list:
            anew = {}
            anew['ID'] = asse['ID']
            anew['label'] = asse['label']
            anew['uri'] = asse['URI']
            anew['assessor_id'] = asse['ID']
            anew['assessor_label'] = asse['label']
            anew['assessor_uri'] = asse['URI']
            anew['project_id'] = projectid
            anew['project_label'] = projectid
            anew['subject_id'] = asse['xnat:imagesessiondata/subject_id']
            anew['session_id'] = asse['session_ID']
            anew['session_label'] = asse['session_label']
            anew['procstatus'] = asse['fs:fsdata/procstatus']
            anew['qcstatus'] = asse['fs:fsdata/validation/status']
            anew['proctype'] = 'FreeSurfer'
            anew['xsiType'] = asse['xsiType']
            new_list.append(anew)

    if has_genproc_datatypes:
        # Then add genProcData
        post_uri = ASSESSORS_URI.format(project=projectid,
                                        subject=subjectid,
                                        session=sessionid)
        post_uri += ASSESSOR_PR_POST_URI.format(pstype=DEFAULT_DATATYPE)
        assessor_list = intf._get_json(post_uri)

        for asse in assessor_list:
            anew = {}
            anew['ID'] = asse['ID']
            anew['label'] = asse['label']
            anew['uri'] = asse['URI']
            anew['assessor_id'] = asse['ID']
            anew['assessor_label'] = asse['label']
            anew['assessor_uri'] = asse['URI']
            anew['project_id'] = projectid
            anew['project_label'] = projectid
            anew['subject_id'] = asse['xnat:imagesessiondata/subject_id']
            anew['session_id'] = asse['session_ID']
            anew['session_label'] = asse['session_label']
            anew['procstatus'] = asse['proc:genprocdata/procstatus']
            anew['proctype'] = asse['proc:genprocdata/proctype']
            anew['qcstatus'] = asse['proc:genprocdata/validation/status']
            anew['xsiType'] = asse['xsiType']
            new_list.append(anew)

    return sorted(new_list, key=lambda k: k['label'])

def list_project_assessors(intf, projectid):
    """
    List all the assessors that you have access to based on passed project.

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :return: List of all the assessors for the project
    """
    assessors_dict = dict()

    #Check that the assessors types are present on XNAT
    if not has_dax_datatypes(intf):
        print '** WARNING: datatypes for processors not found on XNAT. **'
        return list()

    #Get the sessions list to get the different variables needed:
    session_list = list_sessions(intf, projectid)
    sess_id2mod = dict((sess['session_id'], [sess['subject_label'],
                        sess['type'], sess['handedness'], sess['gender'],
                        sess['yob'], sess['age'], sess['last_modified'],
                        sess['last_updated']]) for sess in session_list)

    if has_fs_datatypes:
        # First get FreeSurfer
        post_uri = SE_ARCHIVE_URI
        post_uri += ASSESSOR_FS_PROJ_POST_URI.format(project=projectid,
                                                     fstype=DEFAULT_FS_DATATYPE)
        assessor_list = intf._get_json(post_uri)

        for asse in assessor_list:
            if asse['label']:
                key = asse['label']
                if assessors_dict.get(key):
                    assessors_dict[key]['resources'].append(asse['fs:fsdata/out/file/label'])
                else:
                    anew = {}
                    anew['ID'] = asse['ID']
                    anew['label'] = asse['label']
                    anew['uri'] = asse['URI']
                    anew['assessor_id'] = asse['ID']
                    anew['assessor_label'] = asse['label']
                    anew['assessor_uri'] = asse['URI']
                    anew['project_id'] = projectid
                    anew['project_label'] = projectid
                    anew['subject_id'] = asse['xnat:imagesessiondata/subject_id']
                    anew['subject_label'] = asse['subject_label']
                    anew['session_type'] = sess_id2mod[asse['session_ID']][1]
                    anew['session_id'] = asse['session_ID']
                    anew['session_label'] = asse['session_label']
                    anew['procstatus'] = asse['fs:fsdata/procstatus']
                    anew['qcstatus'] = asse['fs:fsdata/validation/status']
                    anew['proctype'] = 'FreeSurfer'

                    if len(asse['label'].rsplit('-x-FS')) > 1:
                        anew['proctype'] = anew['proctype']+asse['label'].rsplit('-x-FS')[1]

                    anew['version'] = asse.get('fs:fsdata/procversion')
                    anew['xsiType'] = asse['xsiType']
                    anew['jobid'] = asse.get('fs:fsdata/jobid')
                    anew['jobstartdate'] = asse.get('fs:fsdata/jobstartdate')
                    anew['memused'] = asse.get('fs:fsdata/memused')
                    anew['walltimeused'] = asse.get('fs:fsdata/walltimeused')
                    anew['jobnode'] = asse.get('fs:fsdata/jobnode')
                    anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                    anew['gender'] = sess_id2mod[asse['session_ID']][3]
                    anew['yob'] = sess_id2mod[asse['session_ID']][4]
                    anew['age'] = sess_id2mod[asse['session_ID']][5]
                    anew['last_modified'] = sess_id2mod[asse['session_ID']][6]
                    anew['last_updated'] = sess_id2mod[asse['session_ID']][7]
                    anew['resources'] = [asse['fs:fsdata/out/file/label']]
                    assessors_dict[key] = anew

    if has_genproc_datatypes:
        # Then add genProcData
        post_uri = SE_ARCHIVE_URI
        post_uri += ASSESSOR_PR_PROJ_POST_URI.format(project=projectid,
                                                     pstype=DEFAULT_DATATYPE)
        assessor_list = intf._get_json(post_uri)

        for asse in assessor_list:
            if asse['label']:
                key = asse['label']
                if assessors_dict.get(key):
                    assessors_dict[key]['resources'].append(asse['proc:genprocdata/out/file/label'])
                else:
                    anew = {}
                    anew['ID'] = asse['ID']
                    anew['label'] = asse['label']
                    anew['uri'] = asse['URI']
                    anew['assessor_id'] = asse['ID']
                    anew['assessor_label'] = asse['label']
                    anew['assessor_uri'] = asse['URI']
                    anew['project_id'] = projectid
                    anew['project_label'] = projectid
                    anew['subject_id'] = asse['xnat:imagesessiondata/subject_id']
                    anew['subject_label'] = sess_id2mod[asse['session_ID']][0]
                    anew['session_type'] = sess_id2mod[asse['session_ID']][1]
                    anew['session_id'] = asse['session_ID']
                    anew['session_label'] = asse['session_label']
                    anew['procstatus'] = asse['proc:genprocdata/procstatus']
                    anew['proctype'] = asse['proc:genprocdata/proctype']
                    anew['qcstatus'] = asse['proc:genprocdata/validation/status']
                    anew['version'] = asse['proc:genprocdata/procversion']
                    anew['xsiType'] = asse['xsiType']
                    anew['jobid'] = asse.get('proc:genprocdata/jobid')
                    anew['jobnode'] = asse.get('proc:genprocdata/jobnode')
                    anew['jobstartdate'] = asse.get('proc:genprocdata/jobstartdate')
                    anew['memused'] = asse.get('proc:genprocdata/memused')
                    anew['walltimeused'] = asse.get('proc:genprocdata/walltimeused')
                    anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                    anew['gender'] = sess_id2mod[asse['session_ID']][3]
                    anew['yob'] = sess_id2mod[asse['session_ID']][4]
                    anew['age'] = sess_id2mod[asse['session_ID']][5]
                    anew['last_modified'] = sess_id2mod[asse['session_ID']][6]
                    anew['last_updated'] = sess_id2mod[asse['session_ID']][7]
                    anew['resources'] = [asse['proc:genprocdata/out/file/label']]
                    assessors_dict[key] = anew

    return sorted(assessors_dict.values(), key=lambda k: k['label'])

def list_assessor_out_resources(intf, projectid, subjectid, sessionid, assessorid):
    """
    Gets a list of all of the resources for an assessor associated to a session/subject/project
     requested by the user

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :param sessionid: ID/label of a session
    :param assessorid: ID/label of an assessor to get resources for
    :return: List of resources for the assessor
    """
    #Check that the assessors types are present on XNAT
    if not has_dax_datatypes(intf):
        print 'WARNING: datatypes fs:fsData or proc:genProcData not found on XNAT.'
        return list()

    post_uri = A_RESOURCES_URI.format(project=projectid,
                                      subject=subjectid,
                                      session=sessionid,
                                      assessor=assessorid)
    resource_list = intf._get_json(post_uri)
    return resource_list

def get_resource_lastdate_modified(intf, resource_obj):
    """
    Get the last modified data for a resource on XNAT (NOT WORKING: bug on XNAT side)

    :param intf: pyxnat.Interface object
    :param resource: resource pyxnat Eobject
    :return: date of last modified data with the format %Y%m%d%H%M%S
    """
    # xpaths for times in resource xml
    created_dicom_xpath = "/cat:DCMCatalog/cat:entries/cat:entry/@createdTime"
    modified_dicom_xpath = "/cat:DCMCatalog/cat:entries/cat:entry/@modifiedTime"
    created_xpath = "/cat:Catalog/cat:entries/cat:entry/@createdTime"
    modified_xpath = "/cat:Catalog/cat:entries/cat:entry/@modifiedTime"
    # Get the resource object and its uri
    res_xml_uri = '%s?format=xml' % (resource_obj._uri)
    # Get the XML for resource
    xmlstr = intf._exec(res_xml_uri, 'GET')
    # Parse out the times
    root = etree.fromstring(xmlstr)
    create_times = root.xpath(created_xpath, namespaces=root.nsmap)
    if not create_times:
        create_times = root.xpath(created_dicom_xpath, namespaces=root.nsmap)
    mod_times = root.xpath(modified_xpath, namespaces=root.nsmap)
    if not mod_times:
        mod_times = root.xpath(modified_dicom_xpath, namespaces=root.nsmap)
    # Find the most recent time
    all_times = create_times + mod_times
    if all_times:
        max_time = max(all_times)
        date = max_time.split('.')[0]
        res_date = date.split('T')[0].replace('-', '')+date.split('T')[1].replace(':', '')
    else:
        res_date = ('{:%Y%m%d%H%M%S}'.format(datetime.now()))
    return res_date

def select_assessor(intf, assessor_label):
    """
    Select assessor from his label

    :param assessor_label: label for the assessor requested
    :return: pyxnat EObject for the assessor selected
    """
    labels = assessor_label.split('-x-')
    return intf.select('/project/'+labels[0]+'/subject/'+labels[1]+'/experiment/'+labels[2]+'/assessor/'+assessor_label)

def get_full_object(intf, obj_dict):
    """
    Method to run Interface.select() on a dictionary of scan, assessor,
     experiment, subject or project data

    :param intf: pyxnat.Interface Object
    :param obj_dict: A dictionary of information from XnatUtils.list_assessors,
     XnatUtils.list_scans, XnatUtils.list_sessions, or XnatUtils.list_subjects
    :return: The pyxnat EObject selected (but not checked for existance)

    """
    if 'scan_id' in obj_dict:
        proj = obj_dict['project_id']
        subj = obj_dict['subject_id']
        sess = obj_dict['session_id']
        scan = obj_dict['scan_id']
        return intf.select('/project/'+proj+'/subject/'+subj+'/experiment/'+sess+'/scan/'+scan)
    elif 'xsiType' in obj_dict and (obj_dict['xsiType'] == 'fs:fsData' or obj_dict['xsiType'] == 'proc:genProcData'):
        proj = obj_dict['project_id']
        subj = obj_dict['subject_id']
        sess = obj_dict['session_id']
        assr = obj_dict['assessor_id']
        return intf.select('/project/'+proj+'/subject/'+subj+'/experiment/'+sess+'/assessor/'+assr)
    elif 'experiments' in obj_dict['URI']:
        proj = obj_dict['project']
        subj = obj_dict['subject_ID']
        sess = obj_dict['ID']
        return intf.select('/project/'+proj+'/subject/'+subj+'/experiment/'+sess)
    elif 'subjects' in obj_dict['URI']:
        proj = obj_dict['project']
        subj = obj_dict['ID']
        return intf.select('/project/'+proj+'/subject/'+subj)
    elif 'projects' in obj_dict['URI']:
        proj = obj_dict['project']
        return intf.select('/project/'+proj)
    else:
        return intf.select('/project/')  #Return non existing object: obj.exists() -> False

def get_assessor(xnat, projid, subjid, sessid, assrid):
    """
    Run Interface.select down to the assessor level

    :param xnat: pyxnat.Interface Object
    :param projid: XNAT Project ID
    :param subjid: XNAT Subject ID
    :param sessid: XNAT Session ID
    :param assrid: XNAT Assesor label
    :return: pyxnat EObject of the assessor

    """
    assessor = xnat.select('/projects/'+projid+'/subjects/'+subjid+'/experiments/'+sessid+'/assessors/'+assrid)
    return assessor

def select_obj(intf, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None):
    """
    Based on inputs, run Interface.select() down the URI tree

    :param intf: pyxnat.Interface Object
    :param project_id: XNAT Project ID
    :param subject_id: XNAT Subject ID/label
    :param session_id: XNAT Session ID/label
    :param scan_id: XNAT Scan ID/label
    :param assessor_id: XNAT Assesor ID/label
    :return: pyxnat EObject based on user inputs

    """
    select_str = ''
    if not project_id:
        print "ERROR: select_obj in XnatUtils: can not select if no project_id given."
        return intf.select('/project/')  #Return non existing object: obj.exists() -> False
    if scan_id and assessor_id:
        print "ERROR: select_obj in XnatUtils: can not select scan_id and assessor_id at the same time."
        return intf.select('/project/')  #Return non existing object: obj.exists() -> False
    tmp_dict = collections.OrderedDict([('project', project_id), ('subject', subject_id), ('experiment', session_id), ('scan', scan_id), ('assessor', assessor_id)])
    if assessor_id:
        tmp_dict['out/resource'] = resource
    else:
        tmp_dict['resource'] = resource

    for key, value in tmp_dict.items():
        if value:
            select_str += '''/{key}/{label}'''.format(key=key, label=value)
    return intf.select(select_str)

def generate_assessor_handler(project, subject, session, proctype, scan=None):
    """
    Generate an assessorHandler object corresponding to the labels in the parameters

    :param project: project label on XNAT
    :param subject: subject label on XNAT
    :param session: session label on XNAT
    :param proctype: proctype for the assessor
    :param scan: scan label on XNAT if apply
    :return: assessorHandler object
    """
    if scan:
        assessor_label = '-x-'.join([project, subject, session, scan, proctype])
    else:
        assessor_label = '-x-'.join([project, subject, session, proctype])
    return AssessorHandler(assessor_label)

def has_dax_datatypes(intf):
    """
    Check if Xnat instance has the datatypes for DAX

    :param intf: pyxnat.Interface object
    :return: True if it does, False otherwise
    """
    xnat_datatypes = intf.inspect.datatypes()
    for dax_datatype in XSITYPE_INCLUDE:
        if dax_datatype not in xnat_datatypes:
            return False
    return True

def has_fs_datatypes(intf):
    """
    Check if Xnat instance has the fs:fsData types installed

    :param intf: pyxnat.Interface object
    :return: True if it does, False otherwise
    """
    if DEFAULT_FS_DATATYPE not in intf.inspect.datatypes():
        return False
    return True

def has_genproc_datatypes(intf):
    """
    Check if Xnat instance has the fs:fsData types installed

    :param intf: pyxnat.Interface object
    :return: True if it does, False otherwise
    """
    if DEFAULT_DATATYPE not in intf.inspect.datatypes():
        return False
    return True

####################################################################################
#                     Functions to access/check object                             #
####################################################################################
def is_cscan_unusable(cscan):
    """
    Check to see if a CachedImageScan is unusable

    :param cscan: XnatUtils.CachedImageScan object
    :return: True if unusable, False otherwise

    """
    return cscan.info()['quality'] == "unusable"

def is_cscan_usable(cscan):
    """
    Check to see if a CachedImageScan is usable

    :param cscan: XnatUtils.CachedImageScan object
    :return: True if usable, False otherwise

    """
    return cscan.info()['quality'] == "usable"

def is_cscan_good_type(cscan, types_list):
    """
    Check to see if the CachedImageScan type is of type(s) specificed by user.

    :param cassr: CachedImageScan object from XnatUtils
    :param types_list: List of scan types
    :return: True if type is in the list, False if not.

    """
    return cscan.info()['type'] in types_list

def is_scan_unusable(scan_obj):
    """
    Check to see if a scan is usable

    :param scan_obj: Scan EObject from Interface.select()
    :return: True if usable, False otherwise

    """
    return scan_obj.attrs.get('xnat:imageScanData/quality') == "unusable"

def is_scan_good_type(scan_obj, types_list):
    """
    Check to see if a scan is of good type.

    :param scan_obj: Scan EObject from Interface.select()
    :param types_list: List of scan types
    :return: True if scan is in type list, False if not.

    """
    return scan_obj.attrs.get('xnat:imageScanData/type') in types_list

def has_resource(cobj, resource_label):
    """
    Check to see if a CachedImageObject has a specified resource

    :param cobj: CachedImageObject object from XnatUtils
    :param resource_label: label of the resource to check
    :return: True if cobj has the resource and there is at least one file, False if not.

    """
    res_list = [res for res in cobj.get_resources() if res['label'] == resource_label]
    if len(res_list) > 0 and res_list[0]['file_count'] > 0:
        return True
    return False

def is_assessor_same_scan_unusable(cscan, proctype):
    """
    Check to see if the assessor matching the user passed scan and proctype has
     passed QC.

    :param cscan: CachedImageScan object from XnatUtils
    :param proctype: Process type of the assessor
    :return: 0 if the assessor is not ready or doesn't exist. -1 if it failed,
     or 1 if OK

    """
    scan_info = cscan.info()
    assr_label = '-x-'.join([scan_info['project_id'], scan_info['subject_label'], scan_info['session_label'], scan_info['ID'], proctype])
    assr_list = [cassr.info() for cassr in cscan.parent().assessors() if cassr.info()['label'] == assr_label]
    if not assr_list:
        return 0
    else:
        return is_bad_qa(assr_list[0]['qcstatus'])

def is_cassessor_good_type(cassr, types_list):
    """
    Check to see if the CachedImageAssessor proctype is of type(s) specificed by user.

    :param cassr: CachedImageAssessor object from XnatUtils
    :param types_list: List of proctypes
    :return: True if proctype is in the list, False if not.

    """
    assr_info = cassr.info()
    return assr_info['proctype'] in types_list

def is_cassessor_usable(cassr):
    """
    Check to see if the CachedImageAssessor is usable

    :param cassr: CachedImageAssessor object from XnatUtils
    :return: 0 if the assessor is not ready or doesn't exist, -1 if failed,
     1 if OK.

    """
    assr_info = cassr.info()
    return is_bad_qa(assr_info['qcstatus'])

def is_assessor_good_type(assessor_obj, types_list):
    """
    Check to see if an assessor is of good type.

    :param assessor_obj: Assessor EObject from Interface.select()
    :param types_list: List of proctypes
    :return: True if assessor is in proctypes list, False if not.

    """
    atype = assessor_obj.attrs.get('xsiType')
    proctype = assessor_obj.attrs.get(atype+'/proctype')
    return proctype in types_list

def is_assessor_usable(assessor_obj):
    """
    Check to see if the assessor is usable

    :param cassr: Assessor EObject object from Interface.select()
    :return: 0 if the assessor is not ready or doesn't exist, -1 if failed,
     1 if OK.

    """
    atype = assessor_obj.attrs.get('xsiType')
    qcstatus = assessor_obj.attrs.get(atype+'/validation/status')
    return is_bad_qa(qcstatus)

def is_bad_qa(qcstatus):
    """
    Check to see if the QA status of an assessor is bad (aka unusable)

    :param qcstatus: String of the QC status of the assessor
    :return: True if bad, False if not bad

    """
    if qcstatus in [task.JOB_PENDING, task.NEEDS_QA, task.REPROC]:
        return 0
    for qc in task.BAD_QA_STATUS:
        if qc in qcstatus.split(' ')[0].lower():
            return -1
    return 1

def get_good_cscans(csess, scantypes):
    """
    Given a CachedImageSession, get the list of all of the usable
     CachedImageScan objects in the session

    :param csess: CachedImageSession object from XnatUtils
    :param scantypes: List of scantypes to filter for
    :return: List of CachedImageScan objects that fit the scantypes and that
     are usable

    """
    cscans_list = list()
    for cscan in csess.scans():
        if is_cscan_good_type(cscan, scantypes) and not is_cscan_unusable(cscan):
            cscans_list.append(cscan)
    return cscans_list

def get_good_scans(session_obj, scantypes):
    """
    Get usable scans from a session.

    :param session_obj: Pyxnat session EObject
    :param scantypes: List of scanttypes to filter for
    :return: List of python scan EObjects that fit the scantypes and that are
     usable

    """
    scans = list()
    for scan_obj in session_obj.scans().fetchall('obj'):
        if is_scan_good_type(scan_obj, scantypes) and not is_scan_unusable(scan_obj):
            scans.append(scan_obj)
    return scans

def get_good_cassr(csess, proctypes):
    """
    Get all the assessors in the session and filter out the ones that are
     usable and that have the proctype(s) specified

    :param csess: CachedImageSession object from XnatUtils
    :param proctypes: List of proctypes to filter for
    :return: List of CachedImageAssessor objects that are usable and have
     one of the proctype(s) specified.

    """
    cassr_list = list()
    for cassr in csess.assessors():
        usable_status = is_cassessor_usable(cassr)
        if is_cassessor_good_type(cassr, proctypes) and usable_status == 1:
            cassr_list.append(cassr)
    return cassr_list

def get_good_assr(session_obj, proctypes):
    """
    Get all the assessors in the session and filter out the ones
     that are usable and that have the proctype(s) specified

    :param session_obj: Session EObject from Pyxnat
    :param proctypes: List of proctype(s) to filter for
    :return: List of Assessor EObjects that are usable and have one of the
     proctype(s) specified.

    """
    assessors = list()
    for assessor_obj in session_obj.assessors().fetchall('obj'):
        usable_status = is_assessor_usable(assessor_obj)
        if is_assessor_good_type(assessor_obj, proctypes) and usable_status == 1 :
            assessors.append(assessor_obj)
    return assessors

####################################################################################
#                     Download/Upload resources from XNAT                          #
####################################################################################
def check_dl_inputs(directory, xnat_obj, function_name):
    """
    Method to check and see if the directory for download exists and that the
     selected pyxnat EObject exists

    :param directory: Full path to the download directory
    :param xnat_obj: Pyxnat EObject to download from
    :param function_name: Function name of the download method in XnatUtils
    :return: True if object and directory exist, False otherwise.

    """
    if not os.path.exists(directory):
        print '''ERROR: {fct} in XnatUtils: Folder {path} does not exist.'''.format(fct=function_name, path=directory)
        return False
    if not xnat_obj.exists():
        print '''ERROR: {fct} in XnatUtils: xnat object for parent <{label}> does not exist on XNAT.'''.format(fct=function_name, label=xnat_obj.parent().label())
        return False
    return True

def islist(argument, argname):
    """
    Check to see if the input argument is a list. If it's a string, convert it
     to a list, if it's not a list or string, print an error

    :param argument: Input datatype to check to see if it is a list or a string
    :param argname: Name of the argument?
    :return: List of the string or an empty list (if argument is not of type list or str)

    """
    if isinstance(argument, list):
        pass
    elif isinstance(argument, str):
        argument = [argument]
    else:
        print """ERROR: download_scantypes in XnatUtils: wrong format for {name}.""".format(name=argname)
        argument = list()
    return argument

def download_file_from_obj(directory, resource_obj, fname=None):
    """
    Downloads a file from a Pyxnat EObject

    :param directory: Full path to the download directory
    :param resource_obj: Pyxnat EObject to download a file from
    :param fname: Name of the file that you want to download
    :return: File path to the file downloaded. Or None if the file doesn't exist

    """
    if not check_dl_inputs(directory, resource_obj, 'download_file_from_obj'):
        return None

    if fname:
        if resource_obj.file(fname).exists():
            fpath = os.path.join(directory, os.path.basename(fname))
            resource_obj.file(fname).get(fpath)
            return fpath
        else:
            print '''ERROR: download_resource in XnatUtils: file {name} does not exist for resource {label}.'''.format(name=fname, label=resource_obj.label())
            return None
    else:
        return download_biggest_file_from_obj(directory, resource_obj)

def download_file(directory, resource, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, fname=None):
    """
    Download a file from an arbitrarily defined pyxnat EObject at any
     hierarchy of the URI tree

    :param directory: Full path to the download directory
    :param resource: XNAT resource to download from
    :param project_id: XNAT project ID to download from
    :param subject_id: Subject ID/label to download from
    :param session_id: Session ID/label to download from
    :param scan_id:  Scan ID to download from
    :param assessor_id: Assessor ID/label to download from
    :param fname: File name that you want to download from the selected EObject
    :return: Path to the file downloaded.

    """
    xnat = get_interface()
    resource_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id, resource)
    fpath = download_file_from_obj(directory, resource_obj, fname)
    xnat.disconnect()
    return fpath

def download_files_from_obj(directory, resource_obj):
    """
    Download ALL of the files from a Pyxnat EObject

    :param directory: Full path to the download directory
    :param resource_obj: Pyxnat EObject to download all the files from
    :return: List of all the files downloaded, or empty list if no files
     downloaded

    """
    fpaths = list()
    if not check_dl_inputs(directory, resource_obj, 'download_files_from_obj'):
        return fpaths #return empty list without anything being download

    resource_obj.get(directory, extract=True)
    resource_dir = os.path.join(directory, resource_obj.label())
    for root, _, filenames in os.walk(resource_dir):
        fpaths.extend([os.path.join(root, filename) for filename in filenames])

    return fpaths

def download_files(directory, resource, project_id=None, subject_id=None,
                   session_id=None, scan_id=None, assessor_id=None):
    """
    Download a file from an arbitrarily defined pyxnat EObject at any
     hierarcy of the URI tree

    :param directory: Full path to the download directory
    :param resource: XNAT resource to download from
    :param project_id: XNAT project ID to download from
    :param subject_id: Subject ID/label to download from
    :param session_id: Session ID/label to download from
    :param scan_id:  Scan ID to download from
    :param assessor_id: Assessor ID/label to download from
    :return: List of all the files downloaded

    """
    xnat = get_interface()
    resource_obj = select_obj(xnat, project_id, subject_id, session_id,
                              scan_id, assessor_id, resource)
    fpaths = download_files_from_obj(directory, resource_obj)
    xnat.disconnect()
    return fpaths

def download_biggest_file_from_obj(directory, resource_obj):
    """
    Downloads the largest file (based on file size in bytes) from a Pyxnat EObject

    :param directory: Full path to the download directory
    :param resource_obj: Pyxnat EObject to download from
    :return: None if the file was not downloaded. None if the file size is <=0,
     and None if XnatUtils.check_dl_inputs fails. Otherwise, the file path is
     returned for the file downloaded

    """
    file_index = 0
    biggest_size = 0
    fpath = None
    if not check_dl_inputs(directory, resource_obj, 'download_biggest_file_from_obj'):
        return None

    for index, file_obj in enumerate(resource_obj.files()):
        fsize = int(file_obj.size())
        if biggest_size < fsize:
            biggest_size = fsize
            file_index = index
            fpath = file_obj._urn
    if biggest_size > 0 and fpath:
        resource_fname = resource_obj.files().get()[file_index]
        if not os.path.isdir(directory):
            os.makedirs(directory)
        resource_obj.file(fpath).get(os.path.join(directory, resource_fname))
        return os.path.join(directory, resource_fname)
    else:
        return None

def download_biggest_file(directory, resource, project_id=None,
                          subject_id=None, session_id=None,
                          scan_id=None, assessor_id=None):
    """
    Download the larged file (based on file size in bytes) from an arbitrarily
     defined URI based on project/subject/session etc.

    :param directory: Full path to the download directory
    :param resource: XNAT resource label to download from
    :param project_id: XNAT project ID to download from
    :param subject_id: XNAT subject ID/label to download from
    :param session_id: XNAT session ID/label to download from
    :param scan_id: XNAT scan ID to download from
    :param assessor_id: XNAT assessor label/ID to download from
    :return: File path of the file downloaded

    """
    xnat = get_interface()
    resource_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id, resource)
    fpath = download_biggest_file_from_obj(directory, resource_obj)
    xnat.disconnect()
    return fpath

def download_from_obj(directory, xnat_obj, resources, all_files=False):
    """
    Download files from resource(s) on XNAT.

    :param directory: Full path to the download directory
    :param xnat_obj: pyxnat EObject to download files from
    :param resources: Resource labels (note, 1 level down from xnat_obj) to
     download from
    :param all_files: If True download all of the files, if False, download
     the biggest
    :return: List of filepaths downloaded

    """
    """ Download resources from an object from XNAT (project/subject/session/scan(or)assessor)
        Inputs:
            directory: directory where the data will be downloaded
            xnat_obj: selected object from XNAT that can have a resource (project or subject or session or scan or assessor)
            resources: list of resources name on XNAT
            all_files: download all the files from the resources. If False, download the biggest file.
        Return:
            list of files path downloaded on your local computer
    """
    fpaths = list()
    if not check_dl_inputs(directory, xnat_obj, 'download_from_obj'):
        return fpaths

    resources = islist(resources, 'resources')
    if not resources:
        return fpaths

    for resource in resources:
        if xnat_obj.datatype() in ['proc:genProcData', 'fs:fsData']:
            resource_obj = xnat_obj.out_resource(resource)
        else:
            resource_obj = xnat_obj.resource(resource)
        if all_files:
            fpath = download_files_from_obj(directory, resource_obj)
            fpaths.append(fpath)
        else:
            fpath = download_biggest_file_from_obj(directory, resource_obj)
            fpaths.append(fpath)
    return fpaths

def download(directory, resources, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, all_files=False):
    """
    General downloader from arbitrary URI based on inputs.

    :param directory: Full path to the download directory
    :param resources: List of resource labels to download from
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param scan_id: XNAT scan ID
    :param assessor_id: XNAT assessor ID/label
    :param all_files: If True, download all of the files, if False, download
     the biggest file
    :return: List of filepaths for the downloaded files

    """
    xnat = get_interface()
    xnat_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id)
    fpaths = download_from_obj(directory, xnat_obj, resources, all_files)
    xnat.disconnect()
    return fpaths

def download_scan_types(directory, project_id, subject_id, session_id, scantypes, resources, all_files=False):
    """
    Downloads resources from a scan given a scan type, rather than a scan ID

    :param directory: Directory to download the data to
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param scantypes: List of scan types to download resources from.
    :param resources: List of resources to download data from.
    :param all_files: If 1, download from all resources for the scan object, otherwise use the list.
    :return: list of filepaths for the files downloaded

    """
    fpaths = list()
    scantypes = islist(scantypes, 'scantypes')
    if not scantypes:
        return fpaths
    xnat = get_interface()
    for scan in list_scans(xnat, project_id, subject_id, session_id):
        if scan['type'] in scantypes:
            scan_obj = select_obj(xnat, project_id, subject_id, session_id, scan['ID'])
            fpaths.extend(download_from_obj(directory, scan_obj, resources, all_files))
    xnat.disconnect()
    return fpaths

def download_scan_seriesdescriptions(directory, project_id, subject_id, session_id, seriesdescriptions, resources, all_files=False):
    """
    Downloads resources from a scan given a series type, rather than a scan ID

    :param directory: Directory to download the data to
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param seriesdescriptions: List of scan series descriptions to download
     resources from.
    :param resources: List of resources to download data from.
    :param all_files: If 1, download from all resources for the scan object,
     otherwise use the list.
    :return: list of filepaths for the files downloaded

    """
    fpaths = list()
    seriesdescriptions = islist(seriesdescriptions, 'seriesdescription')
    if not seriesdescriptions:
        return fpaths
    xnat = get_interface()
    for scan in list_scans(xnat, project_id, subject_id, session_id):
        if scan['series_description'] in seriesdescriptions:
            scan_obj = select_obj(xnat, project_id, subject_id, session_id, scan['ID'])
            fpaths.extend(download_from_obj(directory, scan_obj, resources, all_files))
    xnat.disconnect()
    return fpaths

def download_assessor_proctypes(directory, project_id, subject_id, session_id, proctypes, resources, all_files=False):
    """
    Download resources from an assessor based on a list of proctypes

    :param directory: Directory to download the data to
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param proctypes: list of proctypes to download from
    :param resources: list of resources to download from
    :param all_files: True if download all the files, False if download the biggest file
    :return: List of filepaths for the files downloaded

    """
    fpaths = list()
    proctypes = islist(proctypes, 'proctypes')
    if not proctypes:
        return fpaths
    proctypes = set([proctype.replace('FreeSurfer', 'FS') for proctype in proctypes])
    xnat = get_interface()
    for assessor in list_assessors(xnat, project_id, subject_id, session_id):
        if assessor['proctype'] in proctypes:
            assessor_obj = select_obj(xnat, project_id, subject_id, session_id, assessor_id=assessor['label'])
            fpaths.extend(download_from_obj(directory, assessor_obj, resources, all_files))
    xnat.disconnect()
    return fpaths

def upload_file_to_obj(filepath, resource_obj, remove=False, removeall=False, fname=None):
    """
    Upload a file to a pyxnat EObject

    :param filepath: Full path to the file to upload
    :param resource_obj: pyxnat EObject to upload the file to. Note this should be a resource
    :param remove: Remove the file if it exists
    :param removeall: Remove all of the files
    :param fname: save the file on disk with this value as file name
    :return: True if upload was OK, False otherwise

    """
    if os.path.isfile(filepath): #Check existence of the file
        if removeall and resource_obj.exists: #Remove previous resource to upload the new one
            resource_obj.delete()
        filepath = check_image_format(filepath)
        if fname:
            filename = fname
            if filepath.endswith('.gz') and not fname.endswith('.gz'):
                filename += '.gz'
        else:
            filename = os.path.basename(filepath)
        if resource_obj.file(str(filename)).exists():
            if remove:
                resource_obj.file(str(filename)).delete()
            else:
                print """WARNING: upload_file_to_obj in XnatUtils: resource {filename} already exists.""".format(filename=filename)
                return False
        resource_obj.file(str(filename)).put(str(filepath), overwrite=True)
        return True
    else:
        print """ERROR: upload_file_to_obj in XnatUtils: file {file} doesn't exist.""".format(file=filepath)
        return False

def upload_file(filepath, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None, remove=False, removeall=False, fname=None):
    """
    Upload a file to an arbitrary URI on XNAT

    :param filepath: Full path of the file to upload
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param scan_id: XNAT scan ID
    :param assessor_id: XNAT assessor ID/label
    :param resource: Resource label to upload to
    :param remove: remove the file if it exists in the resource if True
    :param removeall: remove all of the files that exist for the resource if True
    :param fname: save the file on disk with this value as file name
    :return: True if upload was OK, False otherwise
    """
    status = False
    if not resource:
        print "ERROR: upload_file in XnatUtils: resource argument not provided."
    else:
        xnat = get_interface()
        resource_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id, resource)
        status = upload_file_to_obj(filepath, resource_obj, remove, removeall, fname)
        xnat.disconnect()
    return status

def upload_files_to_obj(filepaths, resource_obj, remove=False, removeall=False):
    """
    Upload a list of files to a resource on XNAT

    :param filepaths: list of files to upload
    :param resource_obj: pyxnat EObject to upload all of the files to
    :param remove: remove files that already exist for the resource.
    :param removeall: remove all previous files on the resource.
    :return: True if upload was OK, False otherwise

    """
    if removeall and resource_obj.exists: #Remove previous resource to upload the new one
        resource_obj.delete()
    status = list()
    for filepath in filepaths:
        status.append(upload_file_to_obj(filepath, resource_obj, remove=remove, removeall=False))
    return status

def upload_files(filepaths, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None, remove=False, removeall=False):
    """
    Upload files to an arbitrary URI in XNAT

    :param filepaths: list of files to upload to XNAT
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param scan_id: XNAT scan ID
    :param assessor_id: XNAT assessor ID/label
    :param resource: Label of a resource to upload to on XNAT
    :param remove: Remove files that already exists on the resource.
    :param removeall: Remove all previous files on the resource.
    :return: list of True/False for each file uploaded. True if OK, False if
     upload failed.

    """
    status = [False]*len(filepaths)
    if not resource:
        print "ERROR: upload_files in XnatUtils: resource argument not provided."
    else:
        xnat = get_interface()
        resource_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id, resource)
        status = upload_files_to_obj(filepaths, resource_obj, remove, removeall)
        xnat.disconnect()
    return status

def upload_folder_to_obj(directory, resource_obj, resource_label, remove=False, removeall=False):
    """
    Upload all of the files in a folder based on the pyxnat EObject passed

    :param directory: Full path of the directory to upload
    :param resource_obj: pyxnat EObject to upload the data to
    :param resource_label: label of where you want the contents of the
     directory to be stored under on XNAT. Note this is a level down
     from resource_obj
    :param remove: Remove the file if it exists if True
    :param removeall: Remove all of the files if they exist if True
    :return: True if upload was OK, False otherwise

    """
    if not os.path.exists(directory):
        print """ERROR: upload_folder in XnatUtils: directory {directory} does not exist.""".format(directory=directory)
        return False

    if resource_obj.exists:
        if removeall:
            resource_obj.delete()
        if not remove: #check if any files already exists on XNAT, if yes return FALSE
            for fpath in get_files_in_folder(directory):
                if resource_obj.file(fpath).exists():
                    print """ERROR: upload_folder_to_obj in XnatUtils: file {file} already found on XNAT. No upload. Use remove/removeall.""".format(file=fpath)
                    return False

    fzip = resource_label+'.zip'
    initdir = os.getcwd()
    #Zip all the files in the directory
    os.chdir(directory)
    os.system('zip -r '+fzip+' * > /dev/null')
    #upload
    resource_obj.put_zip(os.path.join(directory, fzip), overwrite=True, extract=True)
    #return to the initial directory:
    os.chdir(initdir)
    return True

def upload_folder(directory, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None, remove=False, removeall=False):
    """
    Upload a folder to some URI in XNAT based on the inputs

    :param directory: Full path to directory to upload
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param scan_id: XNAT scan ID
    :param assessor_id: XNAT assessor ID
    :param resource: resource label of where to upload the data to
    :param remove: Remove the file if it already exists (if True). Otherwise don't upload if exists
    :param removeall: Remove all of the files that exist, and upload what is in the local directory.
    :return: True if upload was OK, False otherwise

    """
    status = False
    if not resource:
        print "ERROR: upload_folder in XnatUtils: no resource argument provided."
    else:
        xnat = get_interface()
        resource_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id, resource)
        status = upload_folder_to_obj(directory, resource_obj, resource, remove, removeall)
        xnat.disconnect()
    return status

def copy_resource_from_obj(directory, xnat_obj, old_res, new_res):
    """
    Copy a resource from an old location to a new location,

    :param directory: Temporary directory to download the old resource to
    :param xnat_obj: pyxnat EObject of the parent of the old_res
    :param old_res: pyxnat EObject of resource to copy
    :param new_res: pyxnat EObject of where to copy the old_res to
    :return: True if upload was OK, false otherwise.

    """
    #resources objects:
    if xnat_obj.datatype() in ['proc:genProcData', 'fs:fsData']:
        old_resource_obj = xnat_obj.out_resource(old_res)
        new_resource_obj = xnat_obj.out_resource(new_res)
    else:
        old_resource_obj = xnat_obj.resource(old_res)
        new_resource_obj = xnat_obj.resource(new_res)
    #Copy
    fpaths = download_files_from_obj(directory, old_resource_obj)
    if not fpaths:
        return False
    status = upload_folder_to_obj(os.path.join(directory, old_resource_obj.label()), new_resource_obj, new_res)
    #clean director
    clean_directory(directory)
    return status

def copy_resource(directory, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, old_res=None, new_res=None):
    """
    Copy a resource from an old location to a new location,

    :param directory: Temporary directory to download the old resource to
    :param project_id: XNAT Project ID
    :param subject_id: XNAT Subject ID/label
    :param session_id: XNAT session ID/label
    :param scan_id:  XNAT scan ID
    :param assessor_id: XNAT assessor ID/label
    :param old_res: pyxnat EObject of resource to copy
    :param new_res: pyxnat EObject of where to copy the old_res to
    :return: True if upload was OK, false otherwise.

    """
    status = False
    if not old_res or not new_res:
        print "ERROR: copy_resource in XnatUtils: resource argument (old_res or new_res) not provided."
    else:
        xnat = get_interface()
        xnat_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id)
        status = copy_resource_from_obj(directory, xnat_obj, old_res, new_res)
        xnat.disconnect()
    return status

def upload_assessor_snapshots(assessor_obj, original, thumbnail):
    """
    Upload the snapshots of the assessor PDF (both the original and the thumbnail)

    :param assessor_obj: pyxnat EObject of the assessor to upload the snapshots to
    :param original: The original file (full size)
    :param thumbnail: The thumbnail of the original file
    :return: True if it uploaded OK, False if it failed.

    """
    if not os.path.isfile(original) or not os.path.isfile(thumbnail):
        print "ERROR: upload_assessor_snapshots in XnatUtils: original or thumbnail snapshots don't exist."
        return False

    assessor_obj.out_resource('SNAPSHOTS').file(os.path.basename(thumbnail)).put(thumbnail, thumbnail.split('.')[1].upper(), 'THUMBNAIL', overwrite=True)
    assessor_obj.out_resource('SNAPSHOTS').file(os.path.basename(original)).put(original, original.split('.')[1].upper(), 'ORIGINAL', overwrite=True)
    return True

def clean_directory(directory):
    """
    Remove a directory tree or file

    :param directory: The directory (with sub directories if desired that you
     want to delete). Also works with a file.
    :return: None

    """
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isdir(fpath):
            shutil.rmtree(fpath)
        else:
            os.remove(fpath)

def gzip_nii(directory):
    """
    Gzip all the NIfTI files in a directory via system call.

    :param directory: The directory to filter for *.nii files
    :return: None

    """
    for fpath in glob.glob(os.path.join(directory, '*.nii')):
        os.system('gzip '+fpath)

def ungzip_nii(directory):
    """
    Gunzip all of the NIfTI files in a directory via system call.

    :param directory: The directory to filter for *.nii.gz files
    :return: None

    """
    for fpath in glob.glob(os.path.join(directory, '*.nii.gz')):
        os.system('gzip -d '+fpath)

def run_matlab(matlab_script, verbose=False):
    """
    Call MATLAB with -nodesktop -nosplash and -singlecompthread.

    :param matlab_script: Full path to the .m file to run
    :param verbose: True to print all MATLAB output to terminal, False to
     suppress.
    :return: None

    """
    print """Matlab script: {script} running ...""".format(script=matlab_script)
    # with xvfb-run: xvfb-run  -e {err} -f {auth} -a --server-args="-screen 0 1600x1280x24 -ac -extension GLX"
    cmd = """matlab -singleCompThread -nodesktop -nosplash < {script}""".format(script=matlab_script)
    if not verbose:
        matlabdir = os.path.dirname(matlab_script)
        prefix = os.path.basename(matlab_script).split('.')[0]
        cmd = cmd+' > '+os.path.join(matlabdir, prefix+'_outlog.log')
    os.system(cmd)
    print """Matlab script: {script} done""".format(script=matlab_script)

def run_subprocess(args):
    """
    Runs a subprocess call

    :param args: Args for the call
    :return: STDOUT, and STDERR

    """
    process = subprocess.Popen(args,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr

def makedir(directory, prefix='TempDir'):
    """
    Makes a directory if it doesn't exist and if it does, makes a sub directory
     with the format prefix_date in the directory specified.

    :param directory: The directory to create
    :param prefix: prefix for the base directory, default: TempDir
    :return: Full path of the directory created.

    """
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        today = datetime.now()
        directory = os.path.join(directory, prefix+'_'+str(today.year)+'_'+str(today.month)+'_'+str(today.day))
        if not os.path.exists(directory):
            os.mkdir(directory)
        else:
            clean_directory(directory)
    return directory

def print_args(options):
    """
    Given a dictionary of arguments for the spider, print the key/value pairs.

    :param options: Dictionary of key value pairs
    :return: None

    """
    print "--Arguments given to the spider--"
    for info, value in vars(options).items():
        if value:
            print """{info}: {value}""".format(info=info, value=value)
        else:
            print info, ": Not set. The process might fail without this argument."
    print "---------------------------------"

def get_files_in_folder(folder, label=''):
    """
    Recursively list all of the files in a folder

    :param folder: Full path of the folder to search
    :param label: Prefix to prepend to the file path (not sure why you would do
     this)
    :return: List of files in a folder

    """
    f_list = list()
    for fpath in os.listdir(folder):
        ffpath = os.path.join(folder, fpath)
        if os.path.isfile(ffpath):
            fpath = check_image_format(fpath)
            if label:
                filename = os.path.join(label, fpath)
            else:
                filename = fpath
            f_list.append(filename)
        else:
            label = os.path.join(label, fpath)
            f_list.extend(get_files_in_folder(ffpath, label))
    return f_list

def check_image_format(fpath):
    """
    Check to see if a NIfTI file or REC file are uncompress and runs gzip via
     system command if not compressed

    :param fpath: Filepath of a NIfTI or REC file
    :return: the new file path of the gzipped file.

    """
    if fpath.endswith('.nii') or fpath.endswith('.rec'):
        os.system('gzip '+fpath)
        fpath = fpath+'.gz'
    return fpath

def upload_list_records_redcap(redcap_project, data):
    """
    Uploads a dictionary of information to REDCap via PyCap.

    :param redcap_project: PyCap Project object
    :param data: The data to upload
    :except: All catchable errors.
    :return: None

    """
    upload_data = True
    if isinstance(data, dict):
        data = [data]
    elif isinstance(data, list):
        pass
    else:
        upload_data = False
    if upload_data:
        try:
            response = redcap_project.import_records(data)
            assert 'count' in response
        except AssertionError as err:
            print 'ERROR: upload_list_records_redcap in XnatUtils: Creation of record failed. The error is the following: '
            print '      ', err
            print response
        except:
            print 'ERROR: upload_list_records_redcap in XnatUtils: connection to REDCap interupted.'

def get_input_list(input_val, default_val):
    """
    Method to get a list from a comma separated string.

    :param input_val: Input string or list
    :param default_val: Default value (generally used for a spider)
    :return: listified string or default value if input is not a list or string.

    """
    if isinstance(input_val, list):
        return input_val
    elif isinstance(input_val, str):
        return input_val.split(',')
    else:
        return default_val

def get_input_str(input_val, default_val):
    """
    Get the first element of a list.

    :param input_val: Input list
    :param default_val: Default value string
    :return: If input_val is a list, return first element, if input is a
     string, return that string, otherwise return the default value.

    """
    if isinstance(input_val, list):
        return input_val[0]
    elif isinstance(input_val, str):
        return input_val
    else:
        return default_val

def get_random_sessions(xnat, project_id, num_sessions):
    """
    Get a random list of session labels from an XNAT project

    :param xnat: pyxnat Interface object
    :param project_id: XNAT Project ID
    :param num_sessions: Number of sessions if <1 and >0, it is assumed to be a percent.
    :return: List of session labels for the project

    """
    sessions = list_experiments(xnat, project_id)
    session_labels = [x['label'] for x in sessions]
    if num_sessions >0 and num_sessions <1:
        num_sessions = int(num_sessions*len(session_labels))
    return ','.join(random.sample(session_labels, num_sessions))

####################################################################################
#                                5) Cached Class                                   #
####################################################################################
class CachedImageSession():
    """
    Class to cache the XML information for a session on XNAT
    """
    def __init__(self, xnat, proj, subj, sess):
        """
        Entry point for the CachedImageSession class

        :param xnat: pyxnat Interface object
        :param proj: XNAT project ID
        :param subj: XNAT subject ID/label
        :param sess: XNAT session ID/label
        :return: None

        """
        #self.sess_element = ET.fromstring(xnat.session_xml(proj,sess))
        xml_str = xnat.select('/project/'+proj+'/subject/'+subj+'/experiment/'+sess).get()
        self.sess_element = ET.fromstring(xml_str)
        self.project = proj
        self.subject = subj

    def label(self):
        """
        Get the label of the session

        :return: String of the session label

        """
        return self.sess_element.get('label')

    def get(self, name):
        """
        Get the value of a variable name in the session

        :param name: The variable name that you want to get the value of
        :return: The value of the variable or '' if not found.

        """
        value = self.sess_element.get(name)
        if value != None:
            return value

        element = self.sess_element.find(name, NS)
        if element != None:
            return element.text

        split_array = name.rsplit('/', 1)
        if len(split_array) == 2:
            tag, attr = split_array
            element = self.sess_element.find(tag, NS)
            if element != None:
                value = element.get(attr)
                if value != None:
                    return value

        return ''

    def scans(self):
        """
        Get a list of CachedImageScan objects for the XNAT session

        :return: List of CachedImageScan objects for the session.

        """
        scan_list = []
        scan_elements = self.sess_element.find('xnat:scans', NS)
        if scan_elements:
            for scan in scan_elements:
                scan_list.append(CachedImageScan(scan, self))

        return scan_list

    def assessors(self):
        """
        Get a list of CachedImageAssessor objects for the XNAT session

        :return: List of CachedImageAssessor objects for the session.

        """
        assr_list = []

        assr_elements = self.sess_element.find('xnat:assessors', NS)
        if assr_elements:
            for assr in assr_elements:
                assr_list.append(CachedImageAssessor(assr, self))

        return assr_list

    def info(self):
        """
        Get a dictionary of lots of variables that correspond to the session

        :return: Dictionary of variables

        """
        sess_info = {}

        sess_info['ID'] = self.get('ID')
        sess_info['label'] = self.get('label')
        sess_info['note'] = self.get('xnat:note')
        sess_info['session_type'] = self.get('session_type')
        sess_info['project_id'] = self.project
        sess_info['original'] = self.get('original')
        sess_info['modality'] = self.get('modality')
        sess_info['UID'] = self.get('UID')
        sess_info['subject_id'] = self.get('xnat:subject_ID')
        sess_info['subject_label'] = self.subject
        sess_info['project_label'] = sess_info['project_id']
        sess_info['project'] = sess_info['project_id']
        sess_info['subject_ID'] = self.get('xnat:subject_ID')
        sess_info['URI'] = '/data/experiments/'+sess_info['ID']
        sess_info['session_label'] = sess_info['label']
        sess_info['last_updated'] = sess_info['original']
        sess_info['type'] = sess_info['modality']

        return sess_info

    def resources(self):
        """
        Get a list of CachedResource objects for the session

        :return: List of CachedResource objects for the session
        """
        res_list = []

        file_elements = self.sess_element.findall('xnat:resources/xnat:resource', NS)
        if file_elements:
            for file_element in file_elements:
                xsi_type = file_element.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                if xsi_type == 'xnat:resourceCatalog':
                    res_list.append(CachedResource(file_element, self))

        return res_list

    def get_resources(self):
        """
        Return a list of dictionaries that correspond to the information for each
         resource

        :return: List of dictionaries that correspond to the information for each
         resource

        """
        return [res.info() for res in self.resources()]

class CachedImageScan():
    """
    Class to cache the XML information for a scan on XNAT
    """
    def __init__(self, scan_element, parent):
        """
        Entry point for the CachedImageScan class

        :param scan_element: XML string corresponding to a scan
        :param parent: Parent XML string of the session
        :return: None

        """
        self.scan_parent = parent
        self.scan_element = scan_element

    def parent(self):
        """
        Get the parent of the scan

        :return: XML String of the scan parent

        """
        return self.scan_parent

    def label(self):
        """
        Get the ID of the scan

        :return: String of the scan ID

        """
        return self.scan_element.get('ID')

    def get(self, name):
        """
        Get the value of a variable associated with a scan.

        :param name: Name of the variable to get the value of
        :return: Value of the variable if it exists, or '' otherwise.

        """
        value = self.scan_element.get(name)
        if value != None:
            return value

        element = self.scan_element.find(name, NS)
        if element != None:
            return element.text

        if ':' in name:
            tag, attr = name.rsplit(':', 1)
            element = self.scan_element.find(tag, NS)
            if element != None:
                value = element.get(attr)
                if value != None:
                    return value

        return ''

    def info(self):
        """
        Get lots of variables assocaited with this scan.

        :return: Dictionary of infomation about the scan.

        """
        scan_info = {}

        scan_info['ID'] = self.get('ID')
        scan_info['label'] = self.get('ID')
        scan_info['quality'] = self.get('xnat:quality')
        scan_info['frames'] = self.get('xnat:frames')
        scan_info['note'] = self.get('xnat:note')
        scan_info['type'] = self.get('type')
        scan_info['series_description'] = self.get('xnat:series_description')
        scan_info['project_id'] = self.parent().project
        scan_info['subject_id'] = self.parent().get('xnat:subject_ID')
        scan_info['subject_label'] = self.parent().subject

        scan_info['scan_id'] = scan_info['ID']
        scan_info['scan_label'] = scan_info['label']
        scan_info['scan_quality'] = scan_info['quality']
        scan_info['scan_note'] = scan_info['note']
        scan_info['scan_type'] = scan_info['type']
        scan_info['scan_frames'] = scan_info['frames']
        scan_info['scan_description'] = scan_info['series_description']

        scan_info['session_id'] = self.parent().get('ID')
        scan_info['session_label'] = self.parent().get('label')
        scan_info['project_label'] = scan_info['project_id']

        return scan_info

    def resources(self):
        """
        Get a list of the CachedResource (s) associated with this scan.

        :return: List of the CachedResource (s) associated with this scan.
        """
        res_list = []

        file_elements = self.scan_element.findall('xnat:file', NS)
        if file_elements:
            for file_element in file_elements:
                xsi_type = file_element.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                if xsi_type == 'xnat:resourceCatalog':
                    res_list.append(CachedResource(file_element, self))

        return res_list

    def get_resources(self):
        """
        Get a list of dictionaries of info for each CachedResource.

        :return: List of dictionaries of infor for each CachedResource.
        """
        return [res.info() for res in self.resources()]

class CachedImageAssessor():
    """
    Class to cache the XML information for an assessor on XNAT
    """
    def __init__(self, assr_element, parent):
        """
        Entry point for the CachedImageAssessor class on XNAT

        :param assr_element: the assessor XML string on XNAT
        :param parent: the parent element of the assessor
        :return: None

        """
        self.assr_parent = parent
        self.assr_element = assr_element

    def parent(self):
        """
        Get the parent element of the assessor (session)

        :return: The session element XML string

        """
        return self.assr_parent

    def label(self):
        """
        Get the label of the assessor

        :return: String of the assessor label

        """
        return self.assr_element.get('label')

    def get(self, name):
        """
        Get the value of a variable associated with the assessor

        :param name: Variable name to get the value of
        :return: Value of the variable, otherwise ''.

        """
        value = self.assr_element.get(name)
        if value != None:
            return value

        element = self.assr_element.find(name, NS)
        if element != None:
            return element.text

        #tag, attr = name.rsplit('/', 1)
        #element = self.assr_element.find(tag, NS)
        #if element != None:
        #    value = element.get(attr)
        #    if value != None:
        #        return value

        split_array = name.rsplit('/', 1)
        if len(split_array) == 2:
            tag, attr = split_array
            element = self.assr_element.find(tag, NS)
            if element != None:
                value = element.get(attr)
                if value != None:
                    return value

        return ''

    def info(self):
        """
        Get a dictionary of information associated with the assessor

        :return: None

        """
        assr_info = {}

        assr_info['ID'] = self.get('ID')
        assr_info['label'] = self.get('label')
        assr_info['assessor_id'] = assr_info['ID']
        assr_info['assessor_label'] = assr_info['label']
        assr_info['project_id'] = self.get('project')
        assr_info['project_label'] = assr_info['project_id']
        assr_info['subject_id'] = self.parent().get('xnat:subject_ID')
        assr_info['subject_label'] = self.parent().subject
        assr_info['session_id'] = self.parent().get('ID')
        assr_info['session_label'] = self.parent().get('label')
        assr_info['xsiType'] = self.get('{http://www.w3.org/2001/XMLSchema-instance}type').lower()

        if assr_info['xsiType'] == 'fs:fsdata':
            # FreeSurfer
            assr_info['procstatus'] = self.get('fs:procstatus')
            assr_info['qcstatus'] = self.get('xnat:validation/status')
            assr_info['version'] = self.get('fs:procversion')
            assr_info['jobid'] = self.get('fs:jobid')
            assr_info['jobstartdate'] = self.get('fs:jobstartdate')
            assr_info['memused'] = self.get('fs:memused')
            assr_info['walltimeused'] = self.get('fs:walltimeused')
            assr_info['jobnode'] = self.get('fs:jobnode')
            assr_info['proctype'] = 'FreeSurfer'

        elif assr_info['xsiType'] == 'proc:genprocdata':
            # genProcData
            assr_info['procstatus'] = self.get('proc:procstatus')
            assr_info['proctype'] = self.get('proc:proctype')
            assr_info['qcstatus'] = self.get('xnat:validation/status')
            assr_info['version'] = self.get('proc:procversion')
            assr_info['jobid'] = self.get('proc:jobid')
            assr_info['jobstartdate'] = self.get('proc:jobstartdate')
            assr_info['memused'] = self.get('proc:memused')
            assr_info['walltimeused'] = self.get('proc:walltimeused')
            assr_info['jobnode'] = self.get('proc:jobnode')
        else:
            print 'WARN:unknown xsiType for assessor:'+assr_info['xsiType']

        return assr_info

    def in_resources(self):
        """
        Get a list of CachedResource objects for "in" type

        :return: List of CachedResource objects for "in" type

        """
        res_list = []

        file_elements = self.assr_element.findall('xnat:in/xnat:file', NS)
        if file_elements:
            for file_element in file_elements:
                res_list.append(CachedResource(file_element, self))

        return res_list

    def out_resources(self):
        """
        Get a list of CachedResource objects for "out" type

        :return: List of CachedResource objects for "out" type

        """
        res_list = []

        file_elements = self.assr_element.findall('xnat:out/xnat:file', NS)
        if file_elements:
            for file_element in file_elements:
                res_list.append(CachedResource(file_element, self))

        return res_list

    def get_in_resources(self):
        """
        Get a list of dictionaries of info for the CachedResource objects
         for "in" type

        :return: List of dictionaries of info for the CachedResource objects
         for "in" type

        """
        return [res.info() for res in self.in_resources()]

    def get_out_resources(self):
        """
        Get a list of dictionaries of info for the CachedResource objects
         for "out" type

        :return: List of dictionaries of info for the CachedResource objects
         for "out" type

        """
        return [res.info() for res in self.out_resources()]

    def get_resources(self):
        """
        Makes a call to get_out_resources.

        :return: List of dictionaries of info for the CachedResource objects
         for "out" type

        """
        return self.get_out_resources()

class CachedResource():
    """
    Class to cache resource XML info on XNAT
    """
    def __init__(self, element, parent):
        """
        Entry point for the CachgedResource class

        :param element: The XML string of the resource
        :param parent: Parent XML string from the resource
        :return:
        """
        self.res_parent = parent
        self.res_element = element

    def parent(self):
        """
        Get the resource parent XML string

        :return: The resource parent XML string

        """
        return self.res_parent

    def label(self):
        """
        Get the label of the resource

        :return: String of the label of the resource

        """
        return self.res_element.get('label')

    def get(self, name):
        """
        Get the value of a variable associated with the resource

        :param name: Variable name to get the value of
        :return: The value of the variable, '' otherwise.

        """
        value = self.res_element.get(name)
        if value != None:
            return value

        element = self.res_element.find(name, NS)
        if element != None:
            return element.text

        split_array = name.rsplit('/', 1)
        if len(split_array) == 2:
            tag, attr = split_array
            element = self.res_element.find(tag, NS)
            if element != None:
                value = element.get(attr)
                if value != None:
                    return value

        return ''

    def info(self):
        """
        Get a dictionary of information relating to the resource

        :returns: dictionary of information about the resource.
        """
        res_info = {}

        res_info['URI'] = self.get('URI')
        res_info['label'] = self.get('label')
        res_info['file_size'] = self.get('file_size')
        res_info['file_count'] = self.get('file_count')
        res_info['format'] = self.get('format')
        res_info['content'] = self.get('content')

        return res_info
####################### File Utils ######################################################
def gzip_file(file_not_zipped):
    """
    Method to gzip a file using the gzip python package

    :param file_not_zipped: Full path to a file to gzip
    :return: Full path to the gzipped file

    """
    file_out = list()
    content = open(file_not_zipped, 'rb')
    content = content.read()
    fout = gzip.open(file_not_zipped + '.gz', 'wb')
    fout.write(content)
    fout.close()
    file_out.append(file_not_zipped + '.gz')
    os.remove(file_not_zipped)
    return file_out

def gunzip_file(file_zipped):
    """
    Gunzips a file using the gzip python package

    :param file_zipped: Full path to the gzipped file
    :return: None

    """
    gzfile = gzip.GzipFile(file_zipped)
    gzdata = gzfile.read()
    gzfile.close()
    open(file_zipped[:-3],'w').write(gzdata)


####################### DEPRECATED Methods still in used in different Spiders ##########################
# It will need to be removed when the spiders are updated
def list_experiments(intf, projectid=None, subjectid=None):
    """
    Deprecated method to list all the experiments that you have access to. Or, alternatively, list
     the experiments in a single project (and single subject) based on passed project ID (/subject ID)

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :return: List of experiments
    """
    if projectid and subjectid:
        post_uri = SESSIONS_URI.format(project=projectid, subject=subjectid)
    elif projectid == None and subjectid == None:
        post_uri = ALL_SESS_URI
    elif projectid and subjectid == None:
        post_uri = ALL_SESS_PROJ_URI.format(project=projectid)
    else:
        return None

    post_uri += '?columns=ID,URI,subject_label,subject_ID,modality,project,date,xsiType,label,xnat:subjectdata/meta/last_modified'
    experiment_list = intf._get_json(post_uri)

    for exp in experiment_list:
        if projectid:
            # Override the project returned to be the one we queried and add others for convenience
            exp['project'] = projectid

        exp['subject_id'] = exp['subject_ID']
        exp['session_id'] = exp['ID']
        exp['session_label'] = exp['label']
        exp['project_id'] = exp['project']
        exp['project_label'] = exp['project']

    return sorted(experiment_list, key=lambda k: k['session_label'])

def list_experiment_resources(intf, projectid, subjectid, experimentid):
    """
    Deprecated method to get a list of all of the resources for an experiment
     associated to a subject and a project requested by the user

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :param subjectid: ID/label of a session to get resources for
    :return: List of resources for the session
    """
    post_uri = SE_RESOURCES_URI.format(project=projectid, subject=subjectid, session=experimentid)
    resource_list = intf._get_json(post_uri)
    return resource_list

def download_Scan(Outputdirectory,projectName,subject,experiment,scan,resource_list,all_resources=0):
    """
    Deprecated method to download resources from a scan given a scan ID

    :param Outputdirectory: Directory to download the data to
    :param projectName: XNAT project ID
    :param subject: XNAT subject ID/label
    :param experiment: XNAT session ID/label
    :param scan: Scan ID to download from
    :param resource_list: List of resources to download data from.
    :param all_resources: If 1, download from all resources for the scan object, otherwise use the list.
    :return: None

    """
    print'Download resources from '+ projectName + '/' + subject+ '/'+ experiment + '/'+ scan

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_Scan function. Not a list.\n"
        sys.exit()

    try:
        xnat = get_interface()
        SCAN=xnat.select('/project/'+projectName+'/subjects/'+subject+'/experiments/'+experiment+'/scans/'+scan)
        if SCAN.exists():
            if SCAN.attrs.get('quality')!='unusable':
                dl_good_resources_scan(SCAN,resource_list,Outputdirectory,all_resources)
            else:
                print 'DOWNLOAD WARNING: Scan unusable!'
        else:
            print 'DOWNLOAD ERROR: '+ projectName + '/' + subject+ '/'+ experiment + '/'+scan+' does not correspond to a Project/Subject/experiment/scan on Xnat.'

    finally:
        xnat.disconnect()
    print '===================================================================\n'

## from a list of scantype given, Download the resources
def download_ScanType(Outputdirectory,projectName,subject,experiment,List_scantype,resource_list,all_resources=0):
    """
    Deprecated method to download resources from a scan given a series description, rather than a scan ID

    :param Outputdirectory: Directory to download the data to
    :param projectName: XNAT project ID
    :param subject: XNAT subject ID/label
    :param experiment: XNAT session ID/label
    :param List_scantype: List of scan types to download resources from.
    :param resource_list: List of resources to download data from.
    :param all_resources: If 1, download from all resources for the scan object, otherwise use the list.
    :return: None

    """

    print'Download resources from '+ projectName + '/' + subject+ '/'+ experiment + ' and the scan types like ',
    print List_scantype

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_ScanType function. Not a list.\n"
        sys.exit()

    #check list of SD:
    if isinstance(List_scantype, list):
        pass
    elif isinstance(List_scantype, str):
        List_scantype=[List_scantype]
    else:
        print "INPUTS ERROR: Check the format of the list of series_description in the download_ScanType function. Not a list.\n"
        sys.exit()

    try:
        xnat = get_interface()

        for scan in list_scans(xnat, projectName, subject, experiment):
            if scan['type'] in List_scantype:
                if scan['quality']!='unusable':
                    SCAN=xnat.select('/project/'+projectName+'/subjects/'+subject+'/experiments/'+experiment+'/scans/'+scan['ID'])
                    dl_good_resources_scan(SCAN,resource_list,Outputdirectory,all_resources)
                else:
                    print 'DOWNLOAD WARNING: Scan unusable!'

    finally:
        xnat.disconnect()
    print '===================================================================\n'

def download_ScanSeriesDescription(Outputdirectory,projectName,subject,experiment,List_scanSD,resource_list,all_resources=0):
    """
    Deprecated method to download resources from a scan given a series description, rather than a scan ID

    :param Outputdirectory: Directory to download the data to
    :param projectName: XNAT project ID
    :param subject: XNAT subject ID/label
    :param experiment: XNAT session ID/label
    :param List_scanSD: List of series descriptions to download resources from.
    :param resource_list: List of resources to download data from.
    :param all_resources: If 1, download from all resources for the scan object, otherwise use the list.
    :return: None

    """

    print'Download resources from '+ projectName + '/' + subject+ '/'+ experiment + ' and the list of series description ',
    print List_scanSD

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_ScanSeriesDescription function. Not a list.\n"
        sys.exit()

    #check list of SD:
    if isinstance(List_scanSD, list):
        pass
    elif isinstance(List_scanSD, str):
        List_scanSD=[List_scanSD]
    else:
        print "INPUTS ERROR: Check the format of the list of series_description in the download_ScanSeriesDescription function. Not a list.\n"
        sys.exit()

    try:
        xnat = get_interface()

        for scan in list_scans(xnat, projectName, subject, experiment):
            SCAN=xnat.select('/project/'+projectName+'/subjects/'+subject+'/experiments/'+experiment+'/scans/'+scan['ID'])

            if SCAN.attrs.get('series_description') in List_scanSD:
                if scan['quality']!='unusable':
                    dl_good_resources_scan(SCAN,resource_list,Outputdirectory,all_resources)
                else:
                    print 'DOWNLOAD WARNING: Scan unusable!'

    finally:
        xnat.disconnect()
    print '===================================================================\n'

def download_Assessor(Outputdirectory,assessor_label,resource_list,all_resources=0):
    """
    Deprecated method to download resources from a specific assessor.

    :param Outputdirectory: Directory to download data to
    :param assessor_label: The label of the assessor to download from
    :param resource_list: The list of resource(s) that you want to download data from
    :param all_resources: if 1, download all of the resources.
    :return: None

    """

    print'Download resources from process '+ assessor_label

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_Assessor function. Not a list.\n"
        sys.exit()

    try:
        xnat = get_interface()
        labels=assessor_label.split('-x-')
        ASSESSOR=xnat.select('/project/'+labels[0]+'/subjects/'+labels[1]+'/experiments/'+labels[2]+'/assessors/'+assessor_label)
        dl_good_resources_assessor(ASSESSOR,resource_list,Outputdirectory,all_resources)

    finally:
        xnat.disconnect()
    print '===================================================================\n'

## from an assessor type, download the resources :
def download_AssessorType(Outputdirectory,projectName,subject,experiment,List_process_type,resource_list,all_resources=0):
    """
    Deprecated method to download an assessor by the proctype.
     Can download a resource, or all resources

    :param Outputdirectory: Directory to download data to
    :param projectName: XNAT project ID
    :param subject: XNAT project subject ID/label
    :param experiment: XNAT project session ID/label
    :param List_process_type: List of process type(s) (proctypes) to download from
    :param resource_list: List of resources to download from each proctype
    :param all_resources: if 1, download from all resources, otherwise use resource_list
    :return: None

    """

    print'Download resources from '+ projectName + '/' + subject+ '/'+ experiment + ' and the process ',
    print List_process_type

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_AssessorType function. Not a list.\n"
        sys.exit()

    #Check input for subjects_exps_list :
    if isinstance(List_process_type, list):
        pass
    elif isinstance(List_process_type, str):
        List_process_type=[List_process_type]
    else:
        print "INPUTS ERROR: Check the format of the list of process type in the download_AssessorType function. Not a list.\n"
        sys.exit()

    #if FreeSurfer in the list, change it to FS
    List_process_type = [process_type.replace('FreeSurfer', 'FS') for process_type in List_process_type]

    try:
        xnat = get_interface()

        for assessor in list_assessors(xnat, projectName, subject, experiment):
            for proc_type in List_process_type:
                if proc_type==assessor['label'].split('-x-')[-1]:
                    ASSESSOR=xnat.select('/project/'+projectName+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor['label'])
                    dl_good_resources_assessor(ASSESSOR,resource_list,Outputdirectory,all_resources)

    finally:
        xnat.disconnect()
    print '===================================================================\n'


def dl_good_resources_scan(Scan,resource_list,Outputdirectory,all_resources):
    """
    Deprecated method to download "good" resources from a scan

    :param Scan: pyxnat EObject of the scan
    :param resource_list: List of resource names to download from for the scan
    :param Outputdirectory: Directory to download all of the data from
    :param all_resources: Override the list and download all the files from
     all the resources if true, otherwise use the list
    :return: None

    """
    for Resource in resource_list:
        resourceOK=0
        if Scan.resource(Resource).exists():
            resourceOK=1
        elif Scan.resource(Resource.upper()).exists():
            Resource=Resource.upper()
            resourceOK=1
        elif Scan.resource(Resource.lower()).exists():
            Resource=Resource.lower()
            resourceOK=1

        if resourceOK and all_resources:
            download_all_resources(Scan.resource(Resource),Outputdirectory)
        elif resourceOK and not all_resources:
            dl,_=download_biggest_resources(Scan.resource(Resource),Outputdirectory)
            if not dl:
                print 'ERROR: Download failed, the size of file for the resource is zero.'

def dl_good_resources_assessor(Assessor,resource_list,Outputdirectory,all_resources):
    """
    Deprecated method to download all "good" resources from an assessor

    :param Assessor: pyxnat EObject of the assessor
    :param resource_list: List of resources labels to download resources from
    :param Outputdirectory: Download directory for the files from the selected resources
    :param all_resources: If true, download from all resources, otherwise only the specified ones.
    :return: None

    """
    for Resource in resource_list:
        resourceOK=0
        if Assessor.out_resource(Resource).exists():
            resourceOK=1
        elif Assessor.out_resource(Resource.upper()).exists():
            Resource=Resource.upper()
            resourceOK=1
        elif Assessor.out_resource(Resource.lower()).exists():
            Resource=Resource.lower()
            resourceOK=1

        if resourceOK and all_resources:
            download_all_resources(Assessor.out_resource(Resource),Outputdirectory)
        elif resourceOK and not all_resources:
            dl,_=download_biggest_resources(Assessor.out_resource(Resource),Outputdirectory)
            if not dl:
                print 'ERROR: Download failed, the size of file for the resource is zero.'

def download_biggest_resources(Resource,directory,filename='0'):
    """
    Deprecated method to download the biggest file from a resource

    :param Resource: pyxnat EObject to download the biggest file from
    :param directory: Download directory
    :param filename: Filename to override the current name of. If changed,
     the value of filename will be the filename as downlaoded.
    :return: 1 if download worked and then the full path to the file, 0 and nan otherwise.

    """
    if os.path.exists(directory):
        number=0
        Bigger_file_size=0
        for index,fname in enumerate(Resource.files().get()[:]):
            size=int(Resource.file(fname).size())
            if Bigger_file_size<size:
                Bigger_file_size=size
                number=index

        if Bigger_file_size==0:
            return 0,'nan'
        else:
            Input_res_label_fname = Resource.files().get()[number]
            if filename=='0':
                DLFileName = os.path.join(directory,Input_res_label_fname)
            else:
                DLFileName = os.path.join(directory,filename)
            Resource.file(Input_res_label_fname).get(DLFileName)
            return 1,str(DLFileName)
    else:
        print'ERROR download_biggest_resources in XnatUtils: Folder '+directory+' does not exist.'

def download_all_resources(Resource,directory):
    """
    Deprecated method from a pyxnat EObject, download all of the files in it

    :param Resource: pyxnat EObject to download resources from
    :param directory: Directory to download all of the files to
    :return: None

    """
    if os.path.exists(directory):
        #if more than one file:
        if len(Resource.files().get())>1:
            #create a dir with the resourcename:
            Outputdir=os.path.join(directory,Resource.label())
            if not os.path.exists(Outputdir):
                os.mkdir(Outputdir)
            print '   ->Downloading all resources for '+Resource.label()+' as a zip'
            Resource.get(Outputdir,extract=False) #not sure the extract True is working
            print '   ->Unzipping ...'
            os.system('unzip -d '+Outputdir+' '+os.path.join(Outputdir,Resource.label()+'.zip')+' > /dev/null')
        #if only one, if using download all resources, download it and unzip it if it's a zip
        else:
            print '   ->Downloading resource for '+Resource.label()
            Input_res_label_fname = Resource.files().get()[0]
            Resource.file(Input_res_label_fname).get(os.path.join(directory,Input_res_label_fname))
            if os.path.join(directory,Input_res_label_fname)[-3:]=='zip':
                print '   -> Unzipping ...'
                os.system('unzip -d '+directory+' '+os.path.join(directory,Input_res_label_fname)+' > /dev/null')
    else:
        print'ERROR download_all_resources in XnatUtils: Folder '+directory+' does not exist.'

def upload_all_resources(Resource,directory):
    """
    Deprecated method to upload all of the files in a directory to a resource on XNAT

    :param Resource: pyxnat EObject of the resource to put the files
    :param directory: Directory to scrape for files to upload to the resource
    :return: None

    """
    if os.path.exists(directory):
        if not Resource.exists():
            Resource.create()
        #for each files in this folderl, Upload files in the resource :
        Resource_files_list=os.listdir(directory)
        #for each folder=resource in the assessor directory, more than 2 files, use the zip from XNAT
        if len(Resource_files_list)>2:
            upload_zip(directory,Resource)
        #One or two file, let just upload them:
        else:
            for filename in Resource_files_list:
                #if it's a folder, zip it and upload it
                if os.path.isdir(filename):
                    upload_zip(filename, directory+'/'+filename)
                elif filename.lower().endswith('.zip'):
                    Resource.put_zip(directory+'/'+filename, overwrite=True, extract=True)
                else:
                    #upload the file
                    Resource.file(filename).put(directory+'/'+filename, overwrite=True)
    else:
        print'ERROR upload_all_resources in XnatUtils: Folder '+directory+' does not exist.'

def upload_zip(Resource, directory):
    """
    Deprecated method to upload a folder to XNAT as a zip file and then unzips when put. The
     label of the resource will be the folder name

    :param Resource: pyxnat EObject of the resource to upload to
    :param directory: Full path to the directory to upload
    :return: None

    """
    filenameZip=Resource.label()+'.zip'
    initDir=os.getcwd()
    #Zip all the files in the directory
    os.chdir(directory)
    os.system('zip -r '+filenameZip+' *')
    #upload
    Resource.put_zip(directory+'/'+filenameZip, overwrite=True, extract=True)
    #return to the initial directory:
    os.chdir(initDir)

def download_resource_assessor(directory,xnat,project,subject,experiment,assessor_label,resources_list,quiet):
    """
    Deprecated method to download resource(s) from an assessor.

    :param directory: The directory to download data to
    :param xnat: pyxnat Interface object
    :param project: Project ID on XNAT
    :param subject: Subject ID/label on XNAT
    :param experiment: Session ID/label on XNAT
    :param assessor_label: Assessor ID/label on XNAT
    :param resources_list: list of resource(s) to download from the assessor
    :param quiet: Suppress print statements
    :return: None

    """

    if not quiet:
        print '    +Process: '+assessor_label

    assessor=xnat.select('/project/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor_label)
    if not assessor.exists():
        print '      !!WARNING: No assessor with the ID selected.'
        return

    if 'fMRIQA' in assessor_label:
        labels=assessor_label.split('-x-')
        SCAN=xnat.select('/project/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/scans/'+labels[3])
        SD=SCAN.attrs.get('series_description')
        SD=SD.replace('/','_')
        SD=SD.replace(" ", "")

        if SD!='':
            directory=directory+'-x-'+SD

    if not os.path.exists(directory):
        os.mkdir(directory)

    #all resources
    if resources_list[0]=='all':
        post_uri_resource = A_RESOURCES_URI.format(project=project, subject=subject, session=experiment, assessor=assessor_label)
        resources_list = xnat._get_json(post_uri_resource)
        for resource in resources_list:
            Resource=xnat.select('/project/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor_label+'/out/resources/'+resource['label'])
            if Resource.exists():
                if not quiet:
                    print '      *download resource '+resource['label']

                assessor_real_type=assessor_label.split('-x-')[-1]
                if 'FS' in assessor_real_type:
                    #make a directory for each of the resource
                    Res_path=directory+'/'+resource['label']
                    if not os.path.exists(Res_path):
                        os.mkdir(Res_path)
                    Resource.get(Res_path, extract=False)
                else:
                    if len(Resource.files().get()) > 0:
                        #make a directory for each of the resource
                        Res_path=directory+'/'+resource['label']
                        if not os.path.exists(Res_path):
                            os.mkdir(Res_path)

                        for fname in Resource.files().get()[:]:
                            Resfile = Resource.file(fname)
                            local_fname = os.path.join(Res_path, fname)
                            Resfile.get(local_fname)
                    else:
                        print "\t    *ERROR : The size of the resource is 0."

    #resources in the options
    else:
        for resource in resources_list:
            Resource=xnat.select('/project/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor_label+'/out/resources/'+resource)
            if Resource.exists():
                if not quiet:
                    print '      *download resource '+resource

                assessor_real_type=assessor_label.split('-x-')[-1]
                if 'FS' in assessor_real_type:
                    #make a directory for each of the resource
                    Res_path=directory+'/'+resource
                    if not os.path.exists(Res_path):
                        os.mkdir(Res_path)

                    Resource.get(Res_path, extract=False)
                else:
                    if len(Resource.files().get()) > 0:
                        #make a directory for each of the resource
                        Res_path=directory+'/'+resource
                        if not os.path.exists(Res_path):
                            os.mkdir(Res_path)

                        for fname in Resource.files().get()[:]:
                            Resfile = Resource.file(fname)
                            local_fname = os.path.join(Res_path, fname)
                            Resfile.get(local_fname)
                    else:
                        print "      !!ERROR : The size of the resource is 0."
            else:
                print '      !!WARNING : no resource '+resource+' for this assessor.'
    print'\n'


def Upload_folder_to_resource(resourceObj,directory):
    """
    Deprecated method to upload a folder to XNAT as a zip file and then unzips when put. The
     label of the resource will be the folder name

    :param resourceObj: pyxnat EObject of the resource to upload to
    :param directory: Full path to the directory to upload
    :return: None

    """
    filenameZip=resourceObj.label()+'.zip'
    initDir=os.getcwd()
    #Zip all the files in the directory
    os.chdir(directory)
    os.system('zip -r '+filenameZip+' *')
    #upload
    resourceObj.put_zip(directory+'/'+filenameZip, overwrite=True, extract=True)
    #return to the initial directory:
    os.chdir(initDir)

def Download_resource_to_folder(Resource,directory):
    """
    Deprecated method to download all of the files in an XNAT resource to a directory named
     with basename == resource label

    :param Resource: pyxnat EObject of the resource to download files from
    :param directory: The directory to download the data to.
     The resource label name is appeneded as basename
    :return: None

    """
    Res_path=os.path.join(directory,Resource.label())
    if os.path.exists(Res_path):
        os.remove(Res_path)
    Resource.get(directory,extract=True)
