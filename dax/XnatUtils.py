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
import glob
import shutil
import tempfile
import collections
from datetime import datetime
import gzip
from pyxnat import Interface
from lxml import etree

from dax_settings import RESULTS_DIR

import xml.etree.cElementTree as ET

NS = {'xnat' : 'http://nrg.wustl.edu/xnat',
      'proc' : 'http://nrg.wustl.edu/proc',
      'fs'   : 'http://nrg.wustl.edu/fs',
      'xsi'  : 'http://www.w3.org/2001/XMLSchema-instance'}

### VARIABLE ###
# Status:
JOB_PENDING = 'Job Pending' # job is still running, not ready for QA yet
NEEDS_QA = 'Needs QA' # For FS, the complete status
JOB_RUNNING = 'JOB_RUNNING' # the job has been submitted on the cluster and is running right now.
JOB_FAILED = 'JOB_FAILED' # the job failed on the cluster.
READY_TO_UPLOAD = 'READY_TO_UPLOAD' # Job done, waiting for the Spider to upload the results
REPROC = 'Reproc' # will cause spider to zip the current results and put in OLD, and then processing
BAD_QA_STATUS = ['bad', 'fail']

####################################################################################
#                                    1) CLASS                                      #
####################################################################################
class InterfaceTemp(Interface):
    '''Extends the functionality of Interface
    to have a temporary cache that is removed
    when .disconnect() is called.
    '''
    def __init__(self, xnat_host, xnat_user, xnat_pass, temp_dir=None):
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        self.temp_dir = temp_dir
        super(InterfaceTemp, self).__init__(server=xnat_host, user=xnat_user, password=xnat_pass, cachedir=temp_dir)

    def disconnect(self):
        self._exec('/data/JSESSION', method='DELETE')
        shutil.rmtree(self.temp_dir)

class AssessorHandler:
    """ Class to handle assessor label string"""
    def __init__(self, label):
        """
        The purpose of this method is to split an assessor label and parse out its associated pieces
        :param label: An assessor label of the form ProjectID-x-Subject_label-x-SessionLabel-x-ScanId-x-proctype
        :return: None
        """
        self.assessor_label = label
        if len(re.findall('-x-', label)) == 3:
            self.project_id, self.subject_label, self.session_label, self.proctype = label.split('-x-')
            self.scan_id = None
        elif len(re.findall('-x-', label)) == 4:
            self.project_id, self.subject_label, self.session_label, self.scan_id, self.proctype = label.split('-x-')
        else:
            self.assessor_label = None

    def is_valid(self):
        """return true if the assessor is a valid label"""
        return self.assessor_label != None

    def get_project_id(self):
        """ This method retreives the project label from self
        :return: The XNAT project label
        """
        return self.project_id

    def get_subject_label(self):
        """ This method retrieves the subject label from self
        :return: The XNAT subject label
        """
        return self.subject_label

    def get_session_label(self):
        """ This method retrieves the session label from self
        :return: The XNAT session label
        """
        return self.session_label

    def get_scan_id(self):
        """ This method retrieves the scan id from the assessor label
        :return: The XNAT scan ID for the assessor
        """
        return self.scan_id

    def get_proctype(self):
        """ This method retrieves the process type from the assessor label
        :return: The XNAT process type for the assessor
        """
        return self.proctype

    def select_assessor(self, intf):
        """ return XNAT object for the assessor
        :return: None
        """
        string_obj = '''/project/{project}/subject/{subject}/experiment/{session}/assessor/{label}'''.format(project=self.project_id, subject=self.subject_label, session=self.session_label, label=self.assessor_label)
        return intf.select(string_obj)

class SpiderProcessHandler:
    """ Handle the results of a spider """
    def __init__(self, script_name, suffix, project, subject, experiment, scan=None, time_writer=None):
        """ initialization """
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

        #if suffix:
        if suffix:
            if suffix[0] !='_': #check that it starts with an underscore
                suffix = '_'+suffix
            # suffix: remove any special characters and replace by '_'
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
        self.print_msg('''-Creating folder {folder} for {label}'''.format(folder=self.directory, label=assessor_label))

    def print_msg(self, msg):
        """ Print message using time_writer if set, print otherwise """
        if self.time_writer:
            self.time_writer(msg)
        else:
            print msg

    def print_err(self, msg):
        """ Print error message using time writer if set, print otherwise"""
        if self.time_writer:
            self.time_writer.print_stderr_message(err_message)
        else:
            print "Error: "+msg

    def set_error(self):
        """ set the error to one """
        self.error = 1

    def file_exists(self, fpath):
        """ check if file exists """
        if not os.path.isfile(fpath.strip()):
            self.error = 1
            self.print_err('''file {file} does not exists.'''.format(file=fpath))
            return False
        else:
            return True

    def folder_exists(self, fpath):
        """ check if folder exists """
        if not os.path.isdir(fpath.strip()):
            self.error = 1
            self.print_err('''folder {folder} does not exists.'''.format(folder=fpath))
            return False
        else:
            return True

    def print_copying_statement(self, label, src, dest):
        """ print statement for copying data """
        self.print_msg('''  -Copying {label}: {src} to {dest}'''.format(label=label, src=src, dest=dest))

    def add_pdf(self, filepath):
        """ add a file to resource pdf in the upload dir """
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
        """ add a file to resource snapshot in the upload dir """
        self.add_file(snapshot, 'SNAPSHOTS')

    def add_file(self, filepath, resource):
        """ add a file to the upload dir under the resource name """
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
        """ add a folder to the upload dir (with a specific name if specified) """
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
        """ Set the status of an assessor """
        # Connection to Xnat
        try:
            xnat = get_interface()
            assessor = self.assr_handler.select_assessor(xnat)
            if self.assr_handler.get_proctype() == 'FS':
                former_status = assessor.attrs.get('fs:fsdata/procstatus')
            else:
                former_status = assessor.attrs.get('proc:genProcData/procstatus')
            if assessor.exists() and former_status == JOB_RUNNING :
                if self.assr_handler.get_proctype() == 'FS':
                    assessor.attrs.set('fs:fsdata/procstatus', status)
                    self.print_msg('  -status set for FreeSurfer to '+str(status))
                else:
                    assessor.attrs.set('proc:genProcData/procstatus', status)
                    self.print_msg('  -status set for assessor to '+str(status))
        except:
            # fail to access XNAT -- let dax_upload set the status
            pass
        finally:
            if 'xnat' in locals() or xnat != None: xnat.disconnect()

    def done(self):
        """ create the flagfile and set the assessor with the new status """
        #creating the version file to give the spider version:
        f_obj = open(os.path.join(self.directory, 'version.txt'), 'w')
        f_obj.write(self.version)
        f_obj.close()
        #Finish the folder
        if not self.error and self.has_pdf:
            self.print_msg('INFO: Job ready to be upload, error: '+ str(self.error))
            #make the flag folder
            open(os.path.join(self.directory, READY_TO_UPLOAD+'.txt'), 'w').close()
            #set status to ReadyToUpload
            self.set_assessor_status(READY_TO_UPLOAD)
        else:
            self.print_msg('INFO: Job failed, check the outlogs, error: '+ str(self.error))
            #make the flag folder
            open(os.path.join(self.directory, JOB_FAILED+'.txt'), 'w').close()
            #set status to JOB_FAILED
            self.set_assessor_status(JOB_FAILED)

    def clean(self, directory):
        """ clean directory if no error and pdf created """
        if self.has_pdf and not self.error:
            #Remove the data
            shutil.rmtree(directory)

####################################################################################
#                     2) Query XNAT and Access XNAT obj                            #
####################################################################################
def get_interface(host=None, user=None, pwd=None):
    """ open interface with XNAT using your log-in information """
    if user == None:
        user = os.environ['XNAT_USER']
    if pwd == None:
        pwd = os.environ['XNAT_PASS']
    if host == None:
        host = os.environ['XNAT_HOST']
    # Don't sys.exit, let callers catch KeyErrors
    return InterfaceTemp(host, user, pwd)

def list_projects(intf):
    """ list of dictionaries for project that you have access to """
    post_uri = '/REST/projects'
    projects_list = intf._get_json(post_uri)
    return projects_list

def list_project_resources(intf, projectid):
    """ list of dictionaries for the project resources """
    post_uri = '/REST/projects/'+projectid+'/resources'
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_subjects(intf, projectid=None):
    """ list of dictionaries for subjects in a project """
    if projectid:
        post_uri = '/REST/projects/'+projectid+'/subjects'
    else:
        post_uri = '/REST/subjects'

    post_uri += '?columns=ID,project,label,URI,last_modified,src,handedness,gender,yob'

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
    """ list of dictionaries for the subjects resources """
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/resources'
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_experiments(intf, projectid=None, subjectid=None):
    """ list of dictionaries for sessions in a project or subject with less details than list_session"""
    if projectid and subjectid:
        post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments'
    elif projectid == None and subjectid == None:
        post_uri = '/REST/experiments'
    elif projectid and subjectid == None:
        post_uri = '/REST/projects/'+projectid+'/experiments'
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
    """ list of dictionaries for the session resources """
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/resources'
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_sessions(intf, projectid=None, subjectid=None):
    """ list of dictionaries for sessions in one project or one subject """
    type_list = []
    full_sess_list = []

    if projectid and subjectid:
        post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments'
    elif projectid == None and subjectid == None:
        post_uri = '/REST/experiments'
    elif projectid and subjectid == None:
        post_uri = '/REST/projects/'+projectid+'/experiments'
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
        post_uri_type = post_uri + '?xsiType='+sess_type+'&columns=ID,URI,subject_label,subject_ID,modality,project,date,xsiType,'+sess_type+'/age,label,'+sess_type+'/meta/last_modified,'+sess_type+'/original'
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

def list_scans(intf, projectid, subjectid, experimentid):
    """ list of dictionaries for scans in one session """
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments'
    post_uri += '?columns=ID,URI,label,subject_label,project'
    post_uri += ',xnat:imagesessiondata/scans/scan/id'
    post_uri += ',xnat:imagesessiondata/scans/scan/type'
    post_uri += ',xnat:imagesessiondata/scans/scan/quality'
    post_uri += ',xnat:imagesessiondata/scans/scan/note'
    post_uri += ',xnat:imagesessiondata/scans/scan/frames'
    post_uri += ',xnat:imagesessiondata/scans/scan/series_description'
    post_uri += ',xnat:imagesessiondata/subject_id'
    scan_list = intf._get_json(post_uri)
    new_list = []

    for scan in scan_list:
        if scan['ID'] == experimentid or scan['label'] == experimentid:
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
    """ list of dictionaries for scans in a project """
    scans_dict = dict()

    #Get the sessions list to get the modality:
    session_list = list_sessions(intf, projectid)
    sess_id2mod = dict((sess['session_id'], [sess['handedness'], sess['gender'], sess['yob'], sess['age'], sess['last_modified'], sess['last_updated']]) for sess in session_list)

    post_uri = '/REST/archive/experiments'
    post_uri += '?project='+projectid
    post_uri += '&xsiType=xnat:imageSessionData'
    post_uri += '&columns=ID,URI,label,subject_label,project'
    post_uri += ',xnat:imagesessiondata/subject_id'
    post_uri += ',xnat:imagescandata/id'
    post_uri += ',xnat:imagescandata/type'
    post_uri += ',xnat:imagescandata/quality'
    post_uri += ',xnat:imagescandata/note'
    post_uri += ',xnat:imagescandata/frames'
    post_uri += ',xnat:imagescandata/series_description'
    post_uri += ',xnat:imagescandata/file/label'
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
        post_uri = '/REST/archive/experiments'
        post_uri += '?xnat:imagesessiondata/sharing/share/project='+projectid
        post_uri += '&xsiType=xnat:imageSessionData'
        post_uri += '&columns=ID,URI,label,subject_label,project'
        post_uri += ',xnat:imagesessiondata/subject_id'
        post_uri += ',xnat:imagescandata/id'
        post_uri += ',xnat:imagescandata/type'
        post_uri += ',xnat:imagescandata/quality'
        post_uri += ',xnat:imagescandata/note'
        post_uri += ',xnat:imagescandata/frames'
        post_uri += ',xnat:imagescandata/series_description'
        post_uri += ',xnat:imagescandata/file/label'
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

def list_scan_resources(intf, projectid, subjectid, experimentid, scanid):
    """ list of dictionaries for the scan resources """
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/scans/'+scanid+'/resources'
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_assessors(intf, projectid, subjectid, experimentid):
    """ list of dictionaries for assessors in one session """
    new_list = []

    # First get FreeSurfer
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/assessors'
    post_uri += '?columns=ID,label,URI,xsiType,project,xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,xnat:imagesessiondata/label,URI,fs:fsData/procstatus,fs:fsData/validation/status&xsiType=fs:fsData'
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

    # Then add genProcData
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/assessors'
    post_uri += '?columns=ID,label,URI,xsiType,project,xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,xnat:imagesessiondata/label,proc:genprocdata/procstatus,proc:genprocdata/proctype,proc:genprocdata/validation/status&xsiType=proc:genprocdata'
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
    """ list of dictionaries for assessors in a project """
    assessors_dict = dict()

    #Get the sessions list to get the different variables needed:
    session_list = list_sessions(intf, projectid)
    sess_id2mod = dict((sess['session_id'], [sess['subject_label'], sess['type'], sess['handedness'], sess['gender'], sess['yob'], sess['age'], sess['last_modified'], sess['last_updated']]) for sess in session_list)

    # First get FreeSurfer
    post_uri = '/REST/archive/experiments'
    post_uri += '?project='+projectid
    post_uri += '&xsiType=fs:fsdata'
    post_uri += '&columns=ID,label,URI,xsiType,project'
    post_uri += ',xnat:imagesessiondata/subject_id,subject_label,xnat:imagesessiondata/id'
    post_uri += ',xnat:imagesessiondata/label,URI,fs:fsData/procstatus'
    post_uri += ',fs:fsData/validation/status,fs:fsData/procversion,fs:fsData/jobstartdate,fs:fsData/memused,fs:fsData/walltimeused,fs:fsData/jobid,fs:fsData/jobnode'
    post_uri += ',fs:fsData/out/file/label'
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

    # Then add genProcData
    post_uri = '/REST/archive/experiments'
    post_uri += '?project='+projectid
    post_uri += '&xsiType=proc:genprocdata'
    post_uri += '&columns=ID,label,URI,xsiType,project'
    post_uri += ',xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id'
    post_uri += ',xnat:imagesessiondata/label,proc:genprocdata/procstatus'
    post_uri += ',proc:genprocdata/proctype,proc:genprocdata/validation/status,proc:genprocdata/procversion'
    post_uri += ',proc:genprocdata/jobstartdate,proc:genprocdata/memused,proc:genprocdata/walltimeused,proc:genprocdata/jobid,proc:genprocdata/jobnode'
    post_uri += ',proc:genprocdata/out/file/label'
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

def list_assessor_out_resources(intf, projectid, subjectid, experimentid, assessorid):
    """ list of dictionaries for the assessor resources """
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/assessors/'+assessorid+'/out/resources'
    resource_list = intf._get_json(post_uri)
    return resource_list

def get_resource_lastdate_modified(xnat, resource):
    """ get the last modified data for a resource on XNAT (NOT WORKING: bug on XNAT side) """
    # xpaths for times in resource xml
    created_xpath = "/cat:Catalog/cat:entries/cat:entry/@createdTime"
    modified_xpath = "/cat:Catalog/cat:entries/cat:entry/@modifiedTime"
    # Get the resource object and its uri
    res_xml_uri = resource._uri+'?format=xml'
    # Get the XML for resource
    xmlstr = xnat._exec(res_xml_uri, 'GET')
    # Parse out the times
    root = etree.fromstring(xmlstr)
    create_times = root.xpath(created_xpath, namespaces=root.nsmap)
    mod_times = root.xpath(modified_xpath, namespaces=root.nsmap)
    # Find the most recent time
    all_times = create_times + mod_times
    if all_times:
        max_time = max(all_times)
        date = max_time.split('.')[0]
        res_date = date.split('T')[0].replace('-', '')+date.split('T')[1].replace(':', '')
    else:
        res_date = ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())).strip().replace('-', '').replace(':', '').replace(' ', '')
    return res_date

def select_assessor(intf, assessor_label):
    """ select assessor from his label """
    labels = assessor_label.split('-x-')
    return intf.select('/project/'+labels[0]+'/subject/'+labels[1]+'/experiment/'+labels[2]+'/assessor/'+assessor_label)

def get_full_object(intf, obj_dict):
    """ select object on XNAT from dictionary """
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
    """ select assessor from ids or labels """
    assessor = xnat.select('/projects/'+projid+'/subjects/'+subjid+'/experiments/'+sessid+'/assessors/'+assrid)
    return assessor

def select_obj(intf, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None):
    """ Select different level object from XNAT by giving the label or id """
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

####################################################################################
#                     Functions to access/check object                             #
####################################################################################
def is_cscan_unusable(cscan):
    """ return true if scan unusable """
    return cscan.info()['quality'] == "unusable"

def is_cscan_good_type(cscan, types_list):
    """ return true if scan has the right type """
    return cscan.info()['type'] in types_list

def is_scan_unusable(scan_obj):
    """ return true if scan unusable """
    return scan_obj.attrs.get('xnat:imageScanData/quality') == "unusable"

def is_scan_good_type(scan_obj, types_list):
    """ return true if scan has the right type """
    return scan_obj.attrs.get('xnat:imageScanData/type') in types_list

def has_resource(cobj, resource_label):
    """ return True if the resource exists and has files from the CachedObject"""
    res_list = [res for res in cobj.get_resources() if res['label'] == resource_label]
    if len(res_list) > 0 and res_list[0]['file_count'] > 0:
        return True
    return False

def is_assessor_same_scan_unusable(cscan, proctype):
    """ Check status of an assessor for an other proctype from the same scan:
        return 0 if assessor not ready or doesn't exist
        return -1 if assessor failed
        return 1 if ok
        Example: dtiQA for Bedpost, same cscan, different proctype
    """
    scan_info = cscan.info()
    assr_label = '-x-'.join([scan_info['project_id'], scan_info['subject_label'], scan_info['session_label'], scan_info['ID'], proctype])
    assr_list = [cassr.info() for cassr in cscan.parent().assessors() if cassr.info()['label'] == assr_label]
    if not assr_list:
        return 0
    else:
        return is_bad_qa(assr_list[0]['qcstatus'])

def is_cassessor_good_type(cassr, types_list):
    """ return true if cassr has the right type """
    assr_info = cassr.info()
    return assr_info['proctype'] in types_list

def is_cassessor_usable(cassr):
    """ return 0 if assessor not ready or doesn't exist
        return -1 if assessor failed
        return 1 if ok
    """
    assr_info = cassr.info()
    return is_bad_qa(assr_info['qcstatus'])

def is_assessor_good_type(assessor_obj, types_list):
    """ return true if assessor obj has the right type """
    atype = assessor_obj.attrs.get('xsiType')
    proctype = assessor_obj.attrs.get(atype+'/proctype')
    return proctype in types_list

def is_assessor_usable(assessor_obj):
    """ return 0 if assessor not ready or doesn't exist
        return -1 if assessor failed
        return 1 if ok
    """
    atype = assessor_obj.attrs.get('xsiType')
    qcstatus = assessor_obj.attrs.get(atype+'/validation/status')
    return is_bad_qa(qcstatus)

def is_bad_qa(qcstatus):
    """ function to return False if status is bad qa status """
    if qcstatus in [JOB_PENDING, NEEDS_QA, REPROC]:
        return 0
    for qc in BAD_QA_STATUS:
        if qc in qcstatus.lower():
            return -1
    return 1

def get_good_cscans(csess, scantypes):
    """ return cscans list from a csess if there is a good scan """
    cscans_list = list()
    for cscan in csess.scans():
        if is_cscan_good_type(cscan, scantypes) and not is_cscan_unusable(cscan):
            cscans_list.append(cscan)
    return cscans_list

def get_good_scans(session_obj, scantypes):
    """ return scan object list if there is a good scan """
    scans = list()
    for scan_obj in session_obj.scans().fetchall('obj'):
        if is_scan_good_type(scan_obj, scantypes) and not is_scan_unusable(scan_obj):
            scans.append(scan_obj)
    return scans

def get_good_cassr(csess, proctypes):
    """ return cassr list from a csess if there is a good assessor """
    cassr_list = list()
    for cassr in csess.assessors():
        if is_cassessor_good_type(cassr, proctypes) and is_cassessor_usable(cassr):
            cassr_list.append(cassr)
    return cassr_list

def get_good_assr(session_obj, proctypes):
    """ return assessor object list if there is a good assessor """
    assessors = list()
    for assessor_obj in session_obj.assessors().fetchall('obj'):
        if is_assessor_good_type(assessor_obj, proctypes) and is_assessor_usable(assessor_obj):
            assessors.append(assessor_obj)
    return assessors

####################################################################################
#                     Download/Upload resources from XNAT                          #
####################################################################################
def check_dl_inputs(directory, xnat_obj, fctname):
    """ Check the inputs for the download function: directory and xnat_obj """
    if not os.path.exists(directory):
        print '''ERROR: {fct} in XnatUtils: Folder {path} does not exist.'''.format(fct=fctname, path=directory)
        return False
    if not xnat_obj.exists():
        print '''ERROR: {fct} in XnatUtils: xnat object for parent <{label}> does not exist on XNAT.'''.format(fct=fctname, label=xnat_obj.parent().label())
        return False
    return True

def islist(argument, argname):
    """ check if the input is a list. If a string, convert to list, else error """
    if isinstance(argument, list):
        pass
    elif isinstance(argument, str):
        argument = [argument]
    else:
        print """ERROR: download_scantypes in XnatUtils: wrong format for {name}.""".format(name=argname)
        argument = list()
    return argument

def download_file_from_obj(directory, resource_obj, fname=None):
    """ Download file with the path fname from a resource object from XNAT
        Inputs:
            directory: directory where the data will be downloaded
            resource_obj: resource object from XNAT for any level (project/subject/session/scan/assessor)
            fname: filepath on XNAT for the resource you want to download
                   e.g: download_file(...., fname='slicesdir/index.html')
                   if not set, download biggest file
        Return:
            return the file path on your local computer for the file downloaded
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
    """ Download file with the path fname from a resource information (project/subject/...) from XNAT
        Inputs:
            directory: directory where the data will be downloaded
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            scan_id: scan ID on XNAT
            assessor_id: assessor ID or label on XNAT
            resource: resource name on XNAT
            fname: filepath on XNAT for the resource you want to download
                   e.g: download_file(...., fname='slicesdir/index.html')
                   if not set, download biggest file
        Return:
            return the file path on your local computer for the file downloaded
    """
    xnat = get_interface()
    resource_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id, resource)
    fpath = download_file_from_obj(directory, resource_obj, fname)
    xnat.disconnect()
    return fpath

def download_files_from_obj(directory, resource_obj):
    """ Download all files from a resource object from XNAT
        Inputs:
            directory: directory where the data will be downloaded
            resource_obj: resource object from XNAT for any level (project/subject/session/scan/assessor)
        Return:
            return list of filepaths on your local computer for the files downloaded
    """
    fpaths = list()
    if not check_dl_inputs(directory, resource_obj, 'download_files_from_obj'):
        return fpaths #return empty list without anything being download

    resource_obj.get(directory, extract=True)
    resource_dir = os.path.join(directory, resource_obj.label())
    for root, _, filenames in os.walk(resource_dir):
        fpaths.extend([os.path.join(root, filename) for filename in filenames])

    return fpaths

def download_files(directory, resource, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None):
    """ Download all files from a resource information (project/subject/...) from XNAT
        Inputs:
            directory: directory where the data will be downloaded
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            scan_id: scan ID on XNAT
            assessor_id: assessor ID or label on XNAT
            resource: resource name on XNAT
        Return:
            return list of filepaths on your local computer for the files downloaded
    """
    xnat = get_interface()
    resource_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id, resource)
    fpaths = download_files_from_obj(directory, resource_obj)
    xnat.disconnect()
    return fpaths

def download_biggest_file_from_obj(directory, resource_obj):
    """ Download biggest file from a resource object from XNAT
        Inputs:
            directory: directory where the data will be downloaded
            resource_obj: resource object from XNAT for any level (project/subject/session/scan/assessor)
        Return:
            return filepath on your local computer for the file downloaded
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

def download_biggest_file(directory, resource, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None):
    """ Download biggest file from a resource information (project/subject/...) from XNAT
        Inputs:
            directory: directory where the data will be downloaded
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            scan_id: scan ID on XNAT
            assessor_id: assessor ID or label on XNAT
            resource: resource name on XNAT
        Return:
            return filepath on your local computer for the file downloaded
    """
    xnat = get_interface()
    resource_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id, resource)
    fpath = download_biggest_file_from_obj(directory, resource_obj)
    xnat.disconnect()
    return fpath

def download_from_obj(directory, xnat_obj, resources, all_files=False):
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
    """ Download resources from information provided for an object from XNAT (project/subject/session/scan(or)assessor)
        Inputs:
            directory: directory where the data will be downloaded
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            scan_id: scan ID on XNAT
            assessor_id: assessor ID or label on XNAT
            resources: list of resources name on XNAT
            all_files: download all the files from the resources. If False, download the biggest file.
        Return:
            list of files downloaded on your local computer
    """
    xnat = get_interface()
    xnat_obj = select_obj(xnat, project_id, subject_id, session_id, scan_id, assessor_id)
    fpaths = download_from_obj(directory, xnat_obj, resources, all_files)
    xnat.disconnect()
    return fpaths

def download_scan_types(directory, project_id, subject_id, session_id, scantypes, resources, all_files=False):
    """ Download resources for a session for specific scantypes
        Inputs:
            directory: directory where the data will be downloaded
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            scantypes: list of scantypes on XNAT (e.g: ['T1','fMRI'])
            resources: list of resources name on XNAT
            all_files: download all the files from the resources. If False, download the biggest file.
        Return:
            list of files downloaded
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
    """ Download resources for a session for specific series description
        Inputs:
            directory: directory where the data will be downloaded
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            seriesdescription: list of series description on XNAT
            resources: list of resources name on XNAT
            all_files: download all the files from the resources. If False, download the biggest file.
        Return:
            list of files downloaded
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
    """ Download resources for a session for specific assessor type (proctype)
        Inputs:
            directory: directory where the data will be downloaded
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            proctypes: list of proctypes on XNAT (e.g: ['fMRIQA_v2','dtiQA_v3'])
            resources: list of resources name on XNAT
            all_files: download all the files from the resources. If False, download the biggest file.
        Return:
            list of files downloaded
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
    """ Upload file to the resource_obj given to the function
        Inputs:
            filepath: path of the file on your local computer
            resource_obj: resource object on XNAT (select resource for project or subject or session or scan or assessor)
            remove: remove files that already exists on the resource.
            removeall: remove all previous files on the resource.
            fname: give a different name for the file on XNAT (e.g: target.nii.gz --> results/target.nii.gz)
                   this will create a folder results and put the file in it for the resource.
        Return:
            status of the upload (True or False)
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
    """ Upload the file to a resource information (project/subject/...) from XNAT
        Inputs:
            filepath: path of the file on your local computer
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            scan_id: scan ID on XNAT
            assessor_id: assessor ID or label on XNAT
            resource: resource name on XNAT
            remove: remove files that already exists on the resource.
            removeall: remove all previous files on the resource.
            fname: give a different name for the file on XNAT (e.g: target.nii.gz --> results/target.nii.gz)
                   this will create a folder results and put the file in it for the resource.
        Return:
            status of the upload (True or False)
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
    """ Upload a list of files to the resource_obj given to the function
        Inputs:
            filepaths: list of files on your local computer
            resource_obj: resource object on XNAT (select resource for project or subject or session or scan or assessor)
            remove: remove files that already exists on the resource.
            removeall: remove all previous files on the resource.
        Return:
            list of status of the upload (one status per files you want to upload)
    """
    if removeall and resource_obj.exists: #Remove previous resource to upload the new one
        resource_obj.delete()
    status = list()
    for filepath in filepaths:
        status.append(upload_file_to_obj(filepath, resource_obj, remove=remove, removeall=False))
    return status

def upload_files(filepaths, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None, remove=False, removeall=False):
    """ Upload a list of files to a resource information (project/subject/...) from XNAT
        Inputs:
            filepaths: list of files on your local computer
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            scan_id: scan ID on XNAT
            assessor_id: assessor ID or label on XNAT
            resource: resource name on XNAT
            remove: remove files that already exists on the resource.
            removeall: remove all previous files on the resource.
        Return:
            list of status of the upload (one status per files you want to upload)
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
    """ Upload folder (all content) to the resource_obj given to the function
        Inputs:
            directory: folder on your local computer (all content will be upload)
            reosurce_obj: resource object on XNAT (select resource for project or subject or session or scan or assessor)
            remove: remove files that already exists on the resource.
            removeall: remove all previous files on the resource.
        Return:
            status of the upload (True or False)
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
    """ Upload folder (all content) to a resource information (project/subject/...) from XNAT
        Inputs:
            directory: folder on your local computer (all content will be upload)
            project_id: project ID on XNAT
            subject_id: subject ID or label on XNAT
            session_id: session ID or label on XNAT
            scan_id: scan ID on XNAT
            assessor_id: assessor ID or label on XNAT
            resource: resource name on XNAT
            remove: remove files that already exists on the resource.
            removeall: remove all previous files on the resource.
        Return:
            status of the upload (True or False)
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
    """ Copy resource for one object from an old resource to the new resource"""
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
    """ Copy resource for one xnat object (project/subject/session/scan/assessor) from an old resource to the new resource"""
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
    """ upload to assessor the original snapshots and thumbnail files """
    if not os.path.isfile(original) or not os.path.isfile(thumbnail):
        print "ERROR: upload_assessor_snapshots in XnatUtils: original or thumbnail snapshots don't exist."
        return False

    assessor_obj.out_resource('SNAPSHOTS').file(os.path.basename(thumbnail)).put(thumbnail, thumbnail.split('.')[1].upper(), 'THUMBNAIL', overwrite=True)
    assessor_obj.out_resource('SNAPSHOTS').file(os.path.basename(original)).put(original, original.split('.')[1].upper(), 'ORIGINAL', overwrite=True)
    return True

####################################################################################
#                                4) Other Methods                                  #
####################################################################################
def clean_directory(directory):
    """ Empty a directory"""
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isdir(fpath):
            shutil.rmtree(fpath)
        else:
            os.remove(fpath)

def gzip_nii(directory):
    """ Gzip all niftis in the directory """
    for fpath in glob.glob(os.path.join(directory, '*.nii')):
        os.system('gzip '+fpath)

def ungzip_nii(directory):
    """ Ungzip all nifti.gz in the directory """
    for fpath in glob.glob(os.path.join(directory, '*.nii.gz')):
        os.system('gzip -d '+fpath)

def run_matlab(matlab_script, verbose=False):
    """ run matlab script
        inputs:
            matlab_script: filepath to the script
            verbose: if you want to see the matlab print statement
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

def makedir(directory, prefix='TempDir'):
    """ make tmp directory if already exist"""
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
    """ print arguments for Spider"""
    print "--Arguments given to the spider--"
    for info, value in vars(options).items():
        if value:
            print """{info}: {value}""".format(info=info, value=value)
        else:
            print info, ": Not set. The process might fail without this argument."
    print "---------------------------------"

def get_files_in_folder(folder, label=''):
    """ Get all the files recursively starting from the folder"""
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
    """ Check if the path is a nifti or rec image that need to be compress"""
    if fpath.endswith('.nii') or fpath.endswith('.rec'):
        os.system('gzip '+fpath)
        fpath = fpath+'.gz'
    return fpath

def upload_list_records_redcap(redcap_project, data):
    """ Upload data of a dict to a redcap_project project
        Inputs:
            redcap_project: project on REDCap open with request
            data: list of dictionaries that need to be upload
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
    """ function to convert inputs into a list """
    if isinstance(input_val, list):
        return input_val
    elif isinstance(input_val, str):
        return input_val.split(',')
    else:
        return default_val

def get_input_str(input_val, default_val):
    """ function to convert inputs into a str (if a list, first element) """
    if isinstance(input_val, list):
        return input_val[0]
    elif isinstance(input_val, str):
        return input_val
    else:
        return default_val

####################################################################################
#                                5) Cached Class                                   #
####################################################################################
class CachedImageSession():
    """ Class to cache the session XML information from XNAT """
    def __init__(self, xnat, proj, subj, sess):
        """ Init function """
        #self.sess_element = ET.fromstring(xnat.session_xml(proj,sess))
        xml_str = xnat.select('/project/'+proj+'/subject/'+subj+'/experiment/'+sess).get()
        self.sess_element = ET.fromstring(xml_str)
        self.project = proj
        self.subject = subj

    def label(self):
        """ return label of the session """
        return self.sess_element.get('label')

    def get(self, name):
        """ return value of a variable name for the session """
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
        """ return a list of cachescans objects for the session """
        scan_list = []
        scan_elements = self.sess_element.find('xnat:scans', NS)
        if scan_elements:
            for scan in scan_elements:
                scan_list.append(CachedImageScan(scan, self))

        return scan_list

    def assessors(self):
        """ return a list of cacheassessors objects for the session """
        assr_list = []

        assr_elements = self.sess_element.find('xnat:assessors', NS)
        if assr_elements:
            for assr in assr_elements:
                assr_list.append(CachedImageAssessor(assr, self))

        return assr_list

    def info(self):
        """ return a dict with the XNAT information for the session """
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
        """ return the list of cached Resources object """
        res_list = []

        file_elements = self.sess_element.findall('xnat:resources/xnat:resource', NS)
        if file_elements:
            for file_element in file_elements:
                xsi_type = file_element.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                if xsi_type == 'xnat:resourceCatalog':
                    res_list.append(CachedResource(file_element, self))

        return res_list

    def get_resources(self):
        """ return list of dictionaries of the resources for the session """
        return [res.info() for res in self.resources()]

class CachedImageScan():
    """ Class to cache the scan XML information from XNAT """
    def __init__(self, scan_element, parent):
        """ Init function """
        self.scan_parent = parent
        self.scan_element = scan_element

    def parent(self):
        """ return parent the session """
        return self.scan_parent

    def label(self):
        """ return the ID/label of the scan """
        return self.scan_element.get('ID')

    def get(self, name):
        """ return the value of a variable name """
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
        """ return a dictionary of the scan information """
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
        """ return the list of cached Resources object """
        res_list = []

        file_elements = self.scan_element.findall('xnat:file', NS)
        if file_elements:
            for file_element in file_elements:
                xsi_type = file_element.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                if xsi_type == 'xnat:resourceCatalog':
                    res_list.append(CachedResource(file_element, self))

        return res_list

    def get_resources(self):
        """ return list of dictionaries of the resources for the scan """
        return [res.info() for res in self.resources()]

class CachedImageAssessor():
    """ Class to cache the assessor XML information from XNAT """
    def __init__(self, assr_element, parent):
        """ Init function """
        self.assr_parent = parent
        self.assr_element = assr_element

    def parent(self):
        """ return the session """
        return self.assr_parent

    def label(self):
        """ return label of assessor """
        return self.assr_element.get('label')

    def get(self, name):
        """ return value of a variable for the assessor """
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
        """ return dictionary with the assessor information """
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
        """ return list of cached resource object for in resources"""
        res_list = []

        file_elements = self.assr_element.findall('xnat:in/xnat:file', NS)
        if file_elements:
            for file_element in file_elements:
                res_list.append(CachedResource(file_element, self))

        return res_list

    def out_resources(self):
        """ return list of cached resource object for out resources"""
        res_list = []

        file_elements = self.assr_element.findall('xnat:out/xnat:file', NS)
        if file_elements:
            for file_element in file_elements:
                res_list.append(CachedResource(file_element, self))

        return res_list

    def get_in_resources(self):
        """ return list of dictionaries of the in resources for the assessor """
        return [res.info() for res in self.in_resources()]

    def get_out_resources(self):
        """ return list of dictionaries of the out resources for the assessor """
        return [res.info() for res in self.out_resources()]

    def get_resources(self):
        """ return list of dictionaries of the out resources for the assessor """
        return [res.info() for res in self.out_resources()]
        #same as get_out_resources()
        #to be used in has_resource with a cassessor

class CachedResource():
    """ Class to cache the resource XML information from XNAT """
    def __init__(self, element, parent):
        """ Init function """
        self.res_parent = parent
        self.res_element = element

    def parent(self):
        """ get parent from the resource """
        return self.res_parent

    def label(self):
        """ return label of the resource """
        return self.res_element.get('label')

    def get(self, name):
        """ return value of variable for resource """
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
        """ return dictionary for the resource information """
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
    """Method to gzip a file without using os.system"""
    content = open(file_not_zipped, 'rb')
    content = content.read()
    fout = gzip.open(file_not_zipped + '.gz', 'wb')
    fout.write(content)
    fout.close()
    files_out.append(file_not_zipped + '.gz')
    os.remove(file_not_zipped)

def gunzip_file(file_zipped):
    """Method to gunzip a file without using os.system. Same file name w/o gz"""
    gzfile = gzip.GzipFile(file_zipped)
    gzdata = gzfile.read()
    gzfile.close()
    open(file_zipped[:-3],'w').write(gzdata)


####################### OLD Functions used in different Spiders ##########################
# It will need to be removed when the spiders are updated
def download_Scan(Outputdirectory,projectName,subject,experiment,scan,resource_list,all_resources=0):
    """ Download resources from a specific project/subject/experiment/scan from Xnat into a folder.
    parameters :
        - Outputdirectory = directory where the files are going to be download
        - projectName = project name on Xnat
        - subject = subject label of the files you want to download from Xnat
        - experiment = experiment label of the files you want to download from Xnat
        - scan = scan label of the files you want to download from Xnat
        - resource_list = List of resources name
            E.G resource_list=['NIFTI','bval,'bvec']
        - all_resources : download all the resources. If 0, download the biggest one.
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
    """ Same than download_Scan but you give a list of scan type instead of the scan ID
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

## from a list of scan series_description given, download the resources
def download_ScanSeriesDescription(Outputdirectory,projectName,subject,experiment,List_scanSD,resource_list,all_resources=0):
    """ Same than download_Scan but you give a list of series description instead of the scan ID
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

## from an assessor given, download the resources :
def download_Assessor(Outputdirectory,assessor_label,resource_list,all_resources=0):
    """ Download resources from a specific process from Xnat into a folder.
    parameters :
        - Outputdirectory = directory where the files are going to be download
        - assessor_label = assessor label on XNAT -> Project-x-subject-x-session(-x-scan)-x-process
        - resource_list = List of resources name
            E.G resource_list=['NIFTI','bval,'bvec']
        - all_resources : download all the resources. If 0, download the biggest one.
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
    """ Same than download_Scan but you give a list of series description instead of the scan ID
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
            dl,DLFileName=download_biggest_resources(Scan.resource(Resource),Outputdirectory)
            if not dl:
                print 'ERROR: Download failed, the size of file for the resource is zero.'

def dl_good_resources_assessor(Assessor,resource_list,Outputdirectory,all_resources):
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
            dl,DLFileName=download_biggest_resources(Assessor.out_resource(Resource),Outputdirectory)
            if not dl:
                print 'ERROR: Download failed, the size of file for the resource is zero.'

def download_biggest_resources(Resource,directory,filename='0'):
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
                    upload_zip(filename,directory+'/'+filename)
                elif filename.lower().endswith('.zip'):
                    Resource.put_zip(directory+'/'+filename, overwrite=True, extract=True)
                else:
                    #upload the file
                    Resource.file(filename).put(directory+'/'+filename, overwrite=True)
    else:
        print'ERROR upload_all_resources in XnatUtils: Folder '+directory+' does not exist.'

def upload_zip(Resource,directory):
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
    """ Download the resources from the list for the assessor given in the argument (if resource_list[0]='all' -> download all)"""

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
        post_uri_resource = '/REST/projects/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor_label+'/out/resources'
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

# Upload a folder to a resource all files are zip and then unzip in Xnat
def Upload_folder_to_resource(resourceObj,directory):
    filenameZip=resourceObj.label()+'.zip'
    initDir=os.getcwd()
    #Zip all the files in the directory
    os.chdir(directory)
    os.system('zip -r '+filenameZip+' *')
    #upload
    resourceObj.put_zip(directory+'/'+filenameZip, overwrite=True, extract=True)
    #return to the initial directory:
    os.chdir(initDir)

# Download all resources in a folder. the folder will have the name Resource.label(),
# removes the previous folder if there is one.
def Download_resource_to_folder(Resource,directory):
    Res_path=os.path.join(directory,Resource.label())
    if os.path.exists(Res_path):
        os.remove(Res_path)
    Resource.get(directory,extract=True)
