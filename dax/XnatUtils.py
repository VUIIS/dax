""" XnatUtils contains useful function to interface with XNAT using Pyxnat.

The functions are several categories:

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

from __future__ import print_function

from builtins import next
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
from past.builtins import basestring

import collections
import csv
from datetime import datetime
from pydicom.dataset import Dataset, FileDataset
import pydicom
import fnmatch
import getpass
import glob
import gzip
from lxml import etree
import nibabel as nib
import numpy as np
from pyxnat import Interface
from pyxnat.core.errors import DatabaseError
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
import xlrd
import xml.etree.cElementTree as ET
import yaml
import zipfile

from . import utilities
from .task import (JOB_FAILED, JOB_RUNNING, JOB_PENDING, READY_TO_UPLOAD,
                   NEEDS_QA, RERUN, REPROC, FAILED_NEEDS_REPROC, BAD_QA_STATUS)
from .errors import (XnatUtilsError, XnatAccessError,
                     XnatAuthentificationError)
from .dax_settings import (DAX_Settings, DAX_Netrc, DEFAULT_DATATYPE,
                           DEFAULT_FS_DATATYPE)


try:
    basestring
except NameError:
    basestring = str

__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ["InterfaceTemp", "AssessorHandler", "SpiderProcessHandler",
           "CachedImageSession", "CachedImageScan", "CachedImageAssessor",
           "CachedResource"]
DAX_SETTINGS = DAX_Settings()
NS = {'xnat': 'http://nrg.wustl.edu/xnat',
      'proc': 'http://nrg.wustl.edu/proc',
      'fs': 'http://nrg.wustl.edu/fs',
      'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

# REST URI for XNAT
PROJECTS_URI = '/REST/projects'
PROJECT_URI = '%s/{project}' % PROJECTS_URI
P_RESOURCES_URI = '%s/resources' % PROJECT_URI
P_RESOURCE_URI = '%s/{resource}' % P_RESOURCES_URI
ALL_SUBJ_URI = '/REST/subjects'
SUBJECTS_URI = '%s/subjects' % PROJECT_URI
SUBJECT_URI = '%s/{subject}' % SUBJECTS_URI
SU_RESOURCES_URI = '%s/resources' % SUBJECT_URI
SU_RESOURCE_URI = '%s/{resource}' % SU_RESOURCES_URI
SE_ARCHIVE_URI = '/REST/archive/experiments'
ALL_SESS_URI = '/REST/experiments'
ALL_SESS_PROJ_URI = '%s/experiments' % PROJECT_URI
SESSIONS_URI = '%s/experiments' % SUBJECT_URI
SESSION_URI = '%s/{session}' % SESSIONS_URI
SE_RESOURCES_URI = '%s/resources' % SESSION_URI
SE_RESOURCE_URI = '%s/{resource}' % SE_RESOURCES_URI
SCANS_URI = '%s/scans' % SESSION_URI
SCAN_URI = '%s/{scan}' % SCANS_URI
SC_RESOURCES_URI = '%s/resources' % SCAN_URI
SC_RESOURCE_URI = '%s/{resource}' % SC_RESOURCES_URI
ASSESSORS_URI = '%s/assessors' % SESSION_URI
ASSESSOR_URI = '%s/{assessor}' % ASSESSORS_URI
A_RESOURCES_URI = '%s/out/resources' % ASSESSOR_URI
A_RESOURCE_URI = '%s/{resource}' % A_RESOURCES_URI

# List post URI variables for XNAT:
SUBJECT_POST_URI = '''?columns=ID,project,label,URI,last_modified,src,\
handedness,gender,yob,dob'''
SESSION_POST_URI = '''?xsiType={stype}&columns=ID,URI,subject_label,subject_ID\
,modality,project,date,xsiType,{stype}/age,label,{stype}/meta/last_modified\
,{stype}/original'''
NO_MOD_SESSION_POST_URI = '''?xsiType={stype}&columns=ID,URI,subject_label,\
subject_ID,project,date,xsiType,{stype}/age,label,{stype}/meta/last_modified,\
{stype}/original'''
SCAN_POST_URI = '''?columns=ID,URI,label,subject_label,project,\
xnat:imagesessiondata/scans/scan/id,\
xnat:imagesessiondata/scans/scan/type,\
xnat:imagesessiondata/scans/scan/quality,\
xnat:imagesessiondata/scans/scan/note,\
xnat:imagesessiondata/scans/scan/frames,\
xnat:imagesessiondata/scans/scan/series_description,\
xnat:imagesessiondata/subject_id'''
SCAN_PROJ_POST_URI = '''?project={project}&xsiType=xnat:imageSessionData&\
columns=ID,URI,label,subject_label,project,xnat:imagesessiondata/subject_id,\
xnat:imagescandata/id,xnat:imagescandata/type,xnat:imagescandata/quality,\
xnat:imagescandata/note,xnat:imagescandata/frames,\
xnat:imagescandata/series_description,xnat:imagescandata/file/label'''
SCAN_PROJ_INCLUDED_POST_URI = '''?xnat:imagesessiondata/sharing/share/\
project={project}&xsiType=xnat:imageSessionData&columns=ID,URI,label,\
subject_label,project,xnat:imagesessiondata/subject_id,xnat:imagescandata/id,\
xnat:imagescandata/type,xnat:imagescandata/quality,xnat:imagescandata/note,\
xnat:imagescandata/frames,xnat:imagescandata/series_description,\
xnat:imagescandata/file/label'''
ASSESSOR_FS_POST_URI = '''?columns=ID,label,URI,xsiType,project,\
xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,\
xnat:imagesessiondata/label,URI,{fstype}/procstatus,\
{fstype}/validation/status&xsiType={fstype}'''
ASSESSOR_PR_POST_URI = '''?columns=ID,label,URI,xsiType,project,\
xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,\
xnat:imagesessiondata/label,{pstype}/procstatus,{pstype}/proctype,\
{pstype}/validation/status&xsiType={pstype}'''
ASSESSOR_FS_PROJ_POST_URI = '''?project={project}&xsiType={fstype}&columns=ID,\
label,URI,xsiType,project,xnat:imagesessiondata/subject_id,subject_label,\
xnat:imagesessiondata/id,xnat:imagesessiondata/label,URI,{fstype}/procstatus,\
{fstype}/validation/status,{fstype}/procversion,{fstype}/jobstartdate,\
{fstype}/memused,{fstype}/walltimeused,{fstype}/jobid,{fstype}/jobnode,\
{fstype}/out/file/label'''
ASSESSOR_PR_PROJ_POST_URI = '''?project={project}&xsiType={pstype}&columns=ID,\
label,URI,xsiType,project,xnat:imagesessiondata/subject_id,\
xnat:imagesessiondata/id,xnat:imagesessiondata/label,{pstype}/procstatus,\
{pstype}/proctype,{pstype}/validation/status,{pstype}/procversion,\
{pstype}/jobstartdate,{pstype}/memused,{pstype}/walltimeused,\
{pstype}/jobid,{pstype}/jobnode,{pstype}/inputs,{pstype}/out/file/label'''
EXPERIMENT_POST_URI = '''?columns=ID,URI,subject_label,subject_ID,modality,\
project,date,xsiType,label,xnat:subjectdata/meta/last_modified'''

###############################################################################
#                                    1) CLASS                                 #
###############################################################################
class InterfaceTemp(Interface):
    """
    Extends the pyxnat.Interface class to make a temporary directory, write the
     cache to it and then blow it away on the Interface.disconnect call()
     NOTE: This is deprecated in pyxnat 1.0.0.0

    Using netrc to get username password if not given.
    """


    # Select XNAT Path
    P_XPATH = '/projects/{project}'
    S_XPATH = '%s/subjects/{subject}' % P_XPATH
    E_XPATH = '%s/experiments/{session}' % S_XPATH
    C_XPATH = '%s/scans/{scan}' % E_XPATH
    CR_XPATH = '%s/resources/{resource}' % C_XPATH
    A_XPATH = '%s/assessors/{assessor}' % E_XPATH
    R_XPATH = '{xpath}/resources/{resource}'  # TODO: BenM/xnatutils refactor/this isn't used; remove it
    AR_XPATH = '%s/out/resources/{resource}' % A_XPATH

    def __init__(self, xnat_host=None, xnat_user=None, xnat_pass=None,
                 temp_dir=None):
        """Entry point for the InterfaceTemp class.

        :param xnat_host: XNAT Host url
        :param xnat_user: XNAT User ID
        :param xnat_pass: XNAT Password
        :param temp_dir: Directory to write the Cache to
        :return: None

        """
        # Host
        self.host = xnat_host
        self.user = xnat_user
        self.pwd = xnat_pass
        if not xnat_host:
            self.host = os.environ['XNAT_HOST']
        # User:
        if not self.user:
            netrc_obj = DAX_Netrc()
            self.user, self.pwd = netrc_obj.get_login(self.host)
        else:
            if not self.pwd:
                msg = 'Please provide password for host <%s> and user <%s>: '
                self.pwd = getpass.getpass(msg % (self.host, self.user))

        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        self.temp_dir = temp_dir
        self.authenticate()

    def __enter__(self, xnat_host=None, xnat_user=None, xnat_pass=None,
                  temp_dir=None):
        """Enter method for with statement."""
        return self

    def __exit__(self, type, value, traceback):
        """Exit method for with statement."""
        self.disconnect()

    def connect(self):
        """Connect to XNAT."""
        super(InterfaceTemp, self).__init__(server=self.host,
                                            user=self.user,
                                            password=self.pwd,
                                            cachedir=self.temp_dir)

    def disconnect(self):
        """Disconnect the JSESSION and blow away the cache.

        :return: None
        """
        self._exec('/data/JSESSION', method='DELETE')
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def authenticate(self):
        """Authenticate to XNAT.

        Connect to XNAT and try to Disconnect the JSESSION before reconnecting.
        Raise XnatAuthentificationError if it failes.

        :return: True or False
        """
        self.connect()
        try:
            self._exec('/data/JSESSION', method='DELETE')
            # Reconnect the JSession for XNAT
            self.connect()
            return True
        except DatabaseError as e:
            print(e)
            raise XnatAuthentificationError(self.host, self.user)

    # TODO: string.format wants well-formed strings and will, for example, throw
    #a KeyError if any named variables in the format string are missing. Put
    #proper validation in place for these methods
    def get_project_path(self, project):
        return InterfaceTemp.P_XPATH.format(project=project)

    def select_project(self, project):
        xpath = self.get_project_path(project)
        return self.select(xpath)


    def get_subject_path(self, project, subject):
        return InterfaceTemp.S_XPATH.format(project=project,
                                            subject=subject)

    def select_subject(self, project, subject):
        xpath = self.get_subject_path(project, subject)
        return self.select(xpath)


    def get_experiment_path(self, project, subject, session):
        return InterfaceTemp.E_XPATH.format(project=project,
                                            subject=subject,
                                            session=session)

    def select_experiment(self, project, subject, session):
        xpath = self.get_experiment_path(project, subject, session)
        return self.select(xpath)


    def get_scan_path(self, project, subject, session, scan):
        return InterfaceTemp.C_XPATH.format(project=project,
                                            subject=subject,
                                            session=session,
                                            scan=scan)

    def select_scan(self, project, subject, session, scan):
        xpath = self.get_scan_path(project, subject, session, scan)
        return self.select(xpath)


    def get_scan_resource_path(self, project, subject, session, scan, resource):
        return InterfaceTemp.CR_XPATH.format(project=project,
                                             subject=subject,
                                             session=session,
                                             scan=scan,
                                             resource=resource)

    def select_scan_resource(self, project, subject, session, scan, resource):
        xpath = self.get_scan_resource_path(
            project, subject, session, scan, resource)
        return self.select(xpath)


    def get_assessor_path(self, project, subject, session, assessor):
        return InterfaceTemp.A_XPATH.format(project=project,
                                            subject=subject,
                                            session=session,
                                            assessor=assessor)

    def select_assessor(self, project, subject, session, assessor):
        xpath = self.get_assessor_path(project, subject, session, assessor)
        return self.select(xpath)


    def get_assessor_resource_path(
            self, project, subject, session, assessor, resource):
        return InterfaceTemp.AR_XPATH.format(project=project,
                                             subject=subject,
                                             session=session,
                                             assessor=assessor,
                                             resource=resource)

    def select_assessor_resource(
            self, project, subject, session, assessor, resource):
        xpath = self.get_assessor_resource_path(
            project, subject, session, assessor, resource)
        return self.select(xpath)

    def select_all_projects(self, intf):
        return intf.select('/project/')

    def get_projects(self):
        return self._getjson(PROJECTS_URI)

    def get_project_scans(self, project_id, include_shared=True):
        """
        List all the scans that you have access to based on passed project.

        :param intf: pyxnat.Interface object
        :param projectid: ID of a project on XNAT
        :param include_shared: include the shared data in this project
        :return: List of all the scans for the project
        """
        scans_dict = dict()

        # Get the sessions list to get the modality:
        session_list = self.get_sessions(project_id)
        sess_id2mod = dict((sess['session_id'], [sess['handedness'],
                                                 sess['gender'], sess['yob'], sess['age'],
                                                 sess['last_modified'], sess['last_updated']])
                           for sess in session_list)

        post_uri = SE_ARCHIVE_URI
        post_uri += SCAN_PROJ_POST_URI.format(project=project_id)
        scan_list = self._get_json(post_uri)

        pfix = 'xnat:imagescandata'
        for scan in scan_list:
            key = '%s-x-%s' % (scan['ID'], scan['%s/id' % pfix])
            if scans_dict.get(key):
                res = '%s/file/label' % pfix
                scans_dict[key]['resources'].append(scan[res])
            else:
                snew = {}
                snew['scan_id'] = scan['%s/id' % pfix]
                snew['scan_label'] = scan['%s/id' % pfix]
                snew['scan_quality'] = scan['%s/quality' % pfix]
                snew['scan_note'] = scan['%s/note' % pfix]
                snew['scan_frames'] = scan['%s/frames' % pfix]
                snew['scan_description'] = scan['%s/series_description' % pfix]
                snew['scan_type'] = scan['%s/type' % pfix]
                snew['ID'] = scan['%s/id' % pfix]
                snew['label'] = scan['%s/id' % pfix]
                snew['quality'] = scan['%s/quality' % pfix]
                snew['note'] = scan['%s/note' % pfix]
                snew['frames'] = scan['%s/frames' % pfix]
                snew['series_description'] = scan['%s/series_description' % pfix]
                snew['type'] = scan['%s/type' % pfix]
                snew['project_id'] = project_id
                snew['project_label'] = project_id
                snew['subject_id'] = scan['xnat:imagesessiondata/subject_id']
                snew['subject_label'] = scan['subject_label']
                snew['session_type'] = scan['xsiType'].split('xnat:')[1] \
                    .split('Session')[0] \
                    .upper()
                snew['session_id'] = scan['ID']
                snew['session_label'] = scan['label']
                snew['session_uri'] = scan['URI']
                snew['handedness'] = sess_id2mod[scan['ID']][0]
                snew['gender'] = sess_id2mod[scan['ID']][1]
                snew['yob'] = sess_id2mod[scan['ID']][2]
                snew['age'] = sess_id2mod[scan['ID']][3]
                snew['last_modified'] = sess_id2mod[scan['ID']][4]
                snew['last_updated'] = sess_id2mod[scan['ID']][5]
                snew['resources'] = [scan['%s/file/label' % pfix]]
                # make a dictionary of dictionaries
                scans_dict[key] = (snew)

        if include_shared:
            post_uri = SE_ARCHIVE_URI
            post_uri += SCAN_PROJ_INCLUDED_POST_URI.format(project=project_id)
            scan_list = self._get_json(post_uri)

            for scan in scan_list:
                key = '%s-x-%s' % (scan['ID'], scan['%s/id' % pfix])
                if scans_dict.get(key):
                    res = '%s/file/label' % pfix
                    scans_dict[key]['resources'].append(scan[res])
                else:
                    snew = {}
                    snew['scan_id'] = scan['%s/id' % pfix]
                    snew['scan_label'] = scan['%s/id' % pfix]
                    snew['scan_quality'] = scan['%s/quality' % pfix]
                    snew['scan_note'] = scan['%s/note' % pfix]
                    snew['scan_frames'] = scan['%s/frames' % pfix]
                    snew['scan_description'] = scan['%s/series_description' % pfix]
                    snew['scan_type'] = scan['%s/type' % pfix]
                    snew['ID'] = scan['%s/id' % pfix]
                    snew['label'] = scan['%s/id' % pfix]
                    snew['quality'] = scan['%s/quality' % pfix]
                    snew['note'] = scan['%s/note' % pfix]
                    snew['frames'] = scan['%s/frames' % pfix]
                    snew['series_description'] = scan['%s/series_description'
                                                      % pfix]
                    snew['type'] = scan['%s/type' % pfix]
                    snew['project_id'] = project_id
                    snew['project_label'] = project_id
                    snew['subject_id'] = scan['xnat:imagesessiondata/subject_id']
                    snew['subject_label'] = scan['subject_label']
                    snew['session_type'] = scan['xsiType'].split('xnat:')[1] \
                        .split('Session')[0] \
                        .upper()
                    snew['session_id'] = scan['ID']
                    snew['session_label'] = scan['label']
                    snew['session_uri'] = scan['URI']
                    snew['handedness'] = sess_id2mod[scan['ID']][0]
                    snew['gender'] = sess_id2mod[scan['ID']][1]
                    snew['yob'] = sess_id2mod[scan['ID']][2]
                    snew['age'] = sess_id2mod[scan['ID']][3]
                    snew['last_modified'] = sess_id2mod[scan['ID']][4]
                    snew['last_updated'] = sess_id2mod[scan['ID']][5]
                    snew['resources'] = [scan['%s/file/label' % pfix]]
                    # make a dictionary of dictionaries
                    scans_dict[key] = (snew)

        return sorted(list(scans_dict.values()), key=lambda k: k['session_label'])

    def get_project_assessors(self, projectid):
        """
        List all the assessors that you have access to based on passed project.

        :param projectid: ID of a project on XNAT
        :return: List of all the assessors for the project
        """
        assessors_dict = dict()

        # Get the sessions list to get the different variables needed:
        session_list = self.get_sessions(projectid)
        sess_id2mod = dict((sess['session_id'], [sess['subject_label'],
                            sess['type'], sess['handedness'], sess['gender'],
                            sess['yob'], sess['age'], sess['last_modified'],
                            sess['last_updated']]) for sess in session_list)

        if has_fs_datatypes(self):
            # First get FreeSurfer
            post_uri = SE_ARCHIVE_URI
            post_uri += ASSESSOR_FS_PROJ_POST_URI.format(
                project=projectid, fstype=DEFAULT_FS_DATATYPE)
            assessor_list = self._get_json(post_uri)

            pfix = DEFAULT_FS_DATATYPE.lower()
            for asse in assessor_list:
                if asse['label']:
                    key = asse['label']
                    if assessors_dict.get(key):
                        res = '%s/out/file/label' % pfix
                        assessors_dict[key]['resources'].append(asse[res])
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
                        sfix = 'xnat:imagesessiondata'
                        anew['subject_id'] = asse['%s/subject_id' % sfix]
                        anew['subject_label'] = asse['subject_label']
                        anew['session_type'] = sess_id2mod[asse['session_ID']][1]
                        anew['session_id'] = asse['session_ID']
                        anew['session_label'] = asse['session_label']
                        anew['procstatus'] = asse['%s/procstatus' % pfix]
                        anew['qcstatus'] = asse['%s/validation/status' % pfix]
                        anew['proctype'] = 'FreeSurfer'

                        if len(asse['label'].rsplit('-x-FS')) > 1:
                            anew['proctype'] = (anew['proctype'] +
                                                asse['label'].rsplit('-x-FS')[1])

                        anew['version'] = asse.get('%s/procversion' % pfix)
                        anew['xsiType'] = asse['xsiType']
                        anew['jobid'] = asse.get('%s/jobid' % pfix)
                        anew['jobstartdate'] = asse.get('%s/jobstartdate' % pfix)
                        anew['memused'] = asse.get('%s/memused' % pfix)
                        anew['walltimeused'] = asse.get('%s/walltimeused' % pfix)
                        anew['jobnode'] = asse.get('%s/jobnode' % pfix)
                        anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                        anew['gender'] = sess_id2mod[asse['session_ID']][3]
                        anew['yob'] = sess_id2mod[asse['session_ID']][4]
                        anew['age'] = sess_id2mod[asse['session_ID']][5]
                        anew['last_modified'] = sess_id2mod[asse['session_ID']][6]
                        anew['last_updated'] = sess_id2mod[asse['session_ID']][7]
                        anew['resources'] = [asse['%s/out/file/label' % pfix]]
                        assessors_dict[key] = anew

        if has_genproc_datatypes(self):
            # Then add genProcData
            post_uri = SE_ARCHIVE_URI
            post_uri += ASSESSOR_PR_PROJ_POST_URI.format(project=projectid,
                                                         pstype=DEFAULT_DATATYPE)
            assessor_list = self._get_json(post_uri)

            pfix = DEFAULT_DATATYPE.lower()
            for asse in assessor_list:
                if asse['label']:
                    key = asse['label']
                    if assessors_dict.get(key):
                        res = '%s/out/file/label' % pfix
                        assessors_dict[key]['resources'].append(asse[res])
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
                        sfix = 'xnat:imagesessiondata'
                        anew['subject_id'] = asse['%s/subject_id' % sfix]
                        anew['subject_label'] = sess_id2mod[asse['session_ID']][0]
                        anew['session_type'] = sess_id2mod[asse['session_ID']][1]
                        anew['session_id'] = asse['session_ID']
                        anew['session_label'] = asse['session_label']
                        anew['procstatus'] = asse['%s/procstatus' % pfix]
                        anew['proctype'] = asse['%s/proctype' % pfix]
                        anew['qcstatus'] = asse['%s/validation/status' % pfix]
                        anew['version'] = asse['%s/procversion' % pfix]
                        anew['xsiType'] = asse['xsiType']
                        anew['jobid'] = asse.get('%s/jobid' % pfix)
                        anew['jobnode'] = asse.get('%s/jobnode' % pfix)
                        anew['jobstartdate'] = asse.get('%s/jobstartdate' % pfix)
                        anew['memused'] = asse.get('%s/memused' % pfix)
                        anew['walltimeused'] = asse.get('%s/walltimeused' % pfix)
                        anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                        anew['gender'] = sess_id2mod[asse['session_ID']][3]
                        anew['yob'] = sess_id2mod[asse['session_ID']][4]
                        anew['age'] = sess_id2mod[asse['session_ID']][5]
                        anew['last_modified'] = sess_id2mod[asse['session_ID']][6]
                        anew['last_updated'] = sess_id2mod[asse['session_ID']][7]
                        anew['resources'] = [asse['%s/out/file/label' % pfix]]
                        anew['inputs'] = asse.get('%s/inputs' % pfix)
                        assessors_dict[key] = anew

        return sorted(list(assessors_dict.values()), key=lambda k: k['label'])

    def get_subjects(self, project_id):
        if project_id:
            post_uri = SUBJECTS_URI.format(project=project_id)
        else:
            post_uri = ALL_SUBJ_URI

        post_uri += SUBJECT_POST_URI

        subject_list = self._get_json(post_uri)

        for subj in subject_list:
            if project_id:
                # Override the project returned to be the one we queried
                subj['project'] = project_id

            subj['project_id'] = subj['project']
            subj['project_label'] = subj['project']
            subj['subject_id'] = subj['ID']
            subj['subject_label'] = subj['label']
            subj['last_updated'] = subj['src']

        return sorted(subject_list, key=lambda k: k['subject_label'])

    def get_subject_resources(self, project_id, subject_id):
        post_uri = SU_RESOURCES_URI.format(project=project_id, subject=subject_id)
        resource_list = self._get_json(post_uri)
        return resource_list

    def get_resources(self, project_id):
        return self._getjson(P_RESOURCES_URI.format(project=project_id))

    def get_sessions(self, projectid=None, subjectid=None):
        """
        List all the sessions either:
            1) that you have access to
         or
            2) in a single project (and single subject) based on kargs

        :param intf: pyxnat.Interface object
        :param projectid: ID of a project on XNAT
        :param subjectid: ID/label of a subject
        :return: List of sessions
        """
        type_list = []
        full_sess_list = []

        if projectid and subjectid:
            post_uri = SESSIONS_URI.format(project=projectid, subject=subjectid)
        elif projectid is None and subjectid is None:
            post_uri = ALL_SESS_URI
        elif projectid and subjectid is None:
            post_uri = ALL_SESS_PROJ_URI.format(project=projectid)
        else:
            return None

        # First get a list of all experiment types
        post_uri_types = '%s?columns=xsiType' % post_uri
        sess_list = self._get_json(post_uri_types)
        for sess in sess_list:
            sess_type = sess['xsiType'].lower()
            if sess_type not in type_list:
                type_list.append(sess_type)

        # Get the subjects list to get the subject ID:
        subj_list = self.get_subjects(projectid)
        subj_id2lab = dict((subj['ID'], [subj['handedness'], subj['gender'],
                                         subj['yob'], subj['dob']]) for subj in subj_list)

        # Get list of sessions for each type since we have to specific
        # about last_modified field
        for sess_type in type_list:
            if sess_type.startswith('xnat:') and 'session' in sess_type:
                add_uri_str = SESSION_POST_URI.format(stype=sess_type)
            else:
                add_uri_str = NO_MOD_SESSION_POST_URI.format(stype=sess_type)
            post_uri_type = '%s%s' % (post_uri, add_uri_str)
            sess_list = self._get_json(post_uri_type)

            for sess in sess_list:
                # Override the project returned to be the one we queried
                if projectid:
                    sess['project'] = projectid

                sess['project_id'] = sess['project']
                sess['project_label'] = sess['project']
                sess['subject_id'] = sess['subject_ID']
                sess['session_id'] = sess['ID']
                sess['session_label'] = sess['label']
                if sess_type.startswith('xnat:') and 'session' in sess_type:
                    sess['session_type'] = sess_type.split('xnat:')[1] \
                        .split('session')[0] \
                        .upper()
                    sess['type'] = sess_type.split('xnat:')[1] \
                        .split('session')[0] \
                        .upper()
                else:
                    sess['session_type'] = sess_type
                    sess['type'] = sess_type
                last_modified_str = '%s/meta/last_modified' % sess_type
                sess['last_modified'] = sess.get(last_modified_str, None)
                sess['last_updated'] = sess.get('%s/original' % sess_type, None)
                sess['age'] = sess.get('%s/age' % sess_type, None)
                try:
                    sess['handedness'] = subj_id2lab[sess['subject_ID']][0]
                    sess['gender'] = subj_id2lab[sess['subject_ID']][1]
                    sess['yob'] = subj_id2lab[sess['subject_ID']][2]
                    sess['dob'] = subj_id2lab[sess['subject_ID']][3]
                except KeyError as KE:
                    sess['handedness'] = 'UNK'
                    sess['gender'] = 'UNK'
                    sess['yob'] = 'UNK'
                    sess['dob'] = 'UNK'

            # Add sessions of this type to full list
            full_sess_list.extend(sess_list)

        # Return list sorted by label
        return sorted(full_sess_list, key=lambda k: k['session_label'])

    def get_session_resources(self, projectid, subjectid, sessionid):
        """
        Gets a list of all of the resources for a session associated to a
         subject/project requested by the user

        :param intf: pyxnat.Interface object
        :param projectid: ID of a project on XNAT
        :param subjectid: ID/label of a subject
        :param sessionid: ID/label of a session to get resources for
        :return: List of resources for the session

        """
        post_uri = SE_RESOURCES_URI.format(project=projectid, subject=subjectid,
                                           session=sessionid)
        resource_list = self._get_json(post_uri)
        return resource_list

    def get_scans(self, projectid, subjectid, sessionid):
        """
        List all the scans that you have access to based on passed
         session/subject/project.

        :param intf: pyxnat.Interface object
        :param projectid: ID of a project on XNAT
        :param subjectid: ID/label of a subject
        :param sessionid: ID/label of a session
        :return: List of all the scans
        """
        post_uri = SESSIONS_URI.format(project=projectid, subject=subjectid)
        post_uri += SCAN_POST_URI
        scan_list = self._get_json(post_uri)
        new_list = []

        for scan in scan_list:
            if scan['ID'] == sessionid or scan['label'] == sessionid:
                snew = {}
                pfix = 'xnat:imagesessiondata/scans/scan'
                snew['scan_id'] = scan['%s/id' % pfix]
                snew['scan_label'] = scan['%s/id' % pfix]
                snew['scan_quality'] = scan['%s/quality' % pfix]
                snew['scan_note'] = scan['%s/note' % pfix]
                snew['scan_frames'] = scan['%s/frames' % pfix]
                snew['scan_description'] = scan['%s/series_description' % pfix]
                snew['scan_type'] = scan['%s/type' % pfix]
                snew['ID'] = scan['%s/id' % pfix]
                snew['label'] = scan['%s/id' % pfix]
                snew['quality'] = scan['%s/quality' % pfix]
                snew['note'] = scan['%s/note' % pfix]
                snew['frames'] = scan['%s/frames' % pfix]
                snew['series_description'] = scan['%s/series_description' % pfix]
                snew['type'] = scan['%s/type' % pfix]
                snew['project_id'] = projectid
                snew['project_label'] = projectid
                snew['subject_id'] = scan['xnat:imagesessiondata/subject_id']
                snew['subject_label'] = scan['subject_label']
                snew['session_id'] = scan['ID']
                snew['session_label'] = scan['label']
                snew['session_uri'] = scan['URI']
                new_list.append(snew)

        return sorted(new_list, key=lambda k: k['label'])

    @staticmethod
    def object_type_from_path(path):
        elems = path.split('/')
        if elems[0] == 'xnat:':
            elems = elems[1:]
        elems = filter(lambda e: len(e) > 0, elems)
        if elems[0] == 'data':
            elems = elems[1:]
        if elems[0] not in ['project', 'projects']:
            raise RuntimeError('badly formed path')
        if len(elems) == 2:
            return 'project'
        elems = elems[2:]
        if elems[0] not in ['subject', 'subjects']:
            raise RuntimeError('badly formed path')
        if len(elems) == 2:
            return 'subject'
        elems = elems[2:]
        if elems[0] not in ['experiment', 'experiments']:
            raise RuntimeError('badly formed path')
        if len(elems) == 2:
            return 'experiment'
        elems = elems[2:]
        if elems[0] in ['scan', 'scans']:
            if len(elems) == 2:
                return 'scan'
        if elems[0] in ['assessor', 'assessors']:
            if len(elems) == 2:
                return 'assessor'
        return 'resource'





# TODO: BenM/assessor_of_assessor/should be able to go
class AssessorHandler(object):
    """
    Class to intelligently deal with the Assessor labels.
    Make the splitting of the strings easier.
    """
    def __init__(self, label):
        """
        The purpose of this method is to split an assessor label and
        parse out its associated pieces

        :param label: An assessor label of the form
         ProjectID-x-Subject_label-x-SessionLabel-x-ScanId-x-proctype or
         ProjectID-x-Subject_label-x-SessionLabel-x-proctype
        :return: None
        """
        self.assessor_label = label
        self.is_session_assessor = False
        self.is_scan_assessor = False
        if len(re.findall('-x-', label)) == 3:
            labels = label.split('-x-')
            self.project_id = labels[0]
            self.subject_label = labels[1]
            self.session_label = labels[2]
            self.proctype = labels[3]
            self.scan_id = None
            self.is_session_assessor = True
        elif len(re.findall('-x-', label)) == 4:
            labels = label.split('-x-')
            self.project_id = labels[0]
            self.subject_label = labels[1]
            self.session_label = labels[2]
            self.scan_id = labels[3]
            self.proctype = labels[4]
            self.is_scan_assessor = True
        else:
            self.assessor_label = None

    def is_valid(self):
        """
        Check to see if we have a valid assessor label (aka not None)

        :return: True if valid, False if not valid
        """
        return self.assessor_label is not None

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
        return intf.select(self.project_id,
                           self.subject_id,
                           self.session_label,
                           self.assessor_label)


# TODO: BenM/assessor_of_assessor/use path.txt here to associate results with
# xnat assessors
class SpiderProcessHandler(object):
    """Class to handle the uploading of results for a spider."""
    def __init__(self, script_name, suffix, project=None, subject=None,
                 experiment=None, scan=None, alabel=None,
                 assessor_handler=None, time_writer=None,
                 host=os.environ.get('XNAT_HOST', None)):
        """
        Entry point to the SpiderProcessHandler Class.
        You can generate a SpiderProcessHandler by giving:
            project / subject / session and or scan

            or

            assessor label via label

            or

            AssessorHandler via assessor_handler

        :param script_name: Basename of the Spider
                            (full path works as well, it will be removed)
        :param suffix: Processor suffix
        :param project: Project on XNAT
        :param subject: Subject on XNAT
        :param experiment: Session on XNAT
        :param scan: Scan (if needed) On Xnat
        :param time_writer: TimedWriter object if wanted
        :return: None

        """
        # Variables:
        self.error = 0
        self.has_pdf = 0
        self.time_writer = time_writer
        self.host = host
        proctype, self.version = get_proctype(script_name, suffix)

        # Create the assessor handler
        if assessor_handler:
            self.assr_handler = assessor_handler
        else:
            if alabel:
                assessor_label = alabel
            else:
                xnat_info = [project, subject, experiment]
                if scan:
                    xnat_info.append(scan)
                xnat_info.append(proctype)
                if None in xnat_info:
                    err = 'A label is not defined for SpiderProcessHandler: %s'
                    raise XnatUtilsError(err % str(xnat_info))
                assessor_label = '-x-'.join(xnat_info)
            self.assr_handler = AssessorHandler(assessor_label)
        if not self.assr_handler.is_valid:
            err = 'SpiderProcessHandler: assessor handler not valid. \
Wrong label.'
            raise XnatUtilsError(err)

        # Create the upload directory
        self.directory = os.path.join(DAX_SETTINGS.get_results_dir(),
                                      self.assr_handler.assessor_label)
        # if the folder already exists : remove it
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        else:
            # Remove files in directories
            clean_directory(self.directory)

        self.print_msg("INFO: Handling results ...")
        self.print_msg('-Creating folder %s for %s'
                       % (self.directory, self.assr_handler.assessor_label))

    def print_msg(self, msg):
        """
        Prints a message using TimedWriter or print

        :param msg: Message to print
        :return: None

        """
        if self.time_writer:
            self.time_writer(msg)
        else:
            print(msg)

    def print_err(self, msg):
        """
        Print error message using time writer if set, print otherwise

        :param msg: Message to print
        :return: None

        """
        if self.time_writer:
            self.time_writer.print_stderr_message(msg)
        else:
            print("Error: %s" % msg)

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
            self.print_err('file %s does not exists.' % fpath)
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
            self.print_err('folder %s does not exists.' % fpath)
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
        self.print_msg('  -Copying %s: %s to %s' % (label, src, dest))

    def add_pdf(self, filepath):
        """
        Add the PDF and run ps2pdf on the file if it ends with .ps

        :param filepath: Full path to the PDF/PS file
        :return: None

        """
        if self.file_exists(filepath):
            # Check if it's a ps:
            if filepath.lower().endswith('.ps'):
                pdf_path = '%s.pdf' % os.path.splitext(filepath)[0]
                ps2pdf_cmd = 'ps2pdf %s %s' % (filepath, pdf_path)
                self.print_msg('  -Convertion %s ...' % ps2pdf_cmd)
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
            # make the resource folder
            respath = os.path.join(self.directory, resource)
            if not os.path.exists(respath):
                os.mkdir(respath)
            # mv the file
            self.print_copying_statement(resource, filepath, respath)
            shutil.copy(filepath, respath)
            # if it's a nii or a rec file, gzip it:
            if filepath.lower().endswith('.nii') or \
               filepath.lower().endswith('.rec'):
                ifile = os.path.join(respath, os.path.basename(filepath))
                os.system('gzip %s' % ifile)

    def add_folder(self, folderpath, resource_name=None):
        """
        Add a folder to the assessor in the upload directory.

        :param folderpath: Full path to the folder to upoad
        :param resource_name: Resource name chosen (if different than basename)
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
                raise XnatUtilsError('Directory not copied. Error: %s' % excep)
            # Any error saying that the directory doesn't exist
            except OSError as excep:
                raise XnatUtilsError('Directory not copied. Error: %s' % excep)

    def set_assessor_status(self, status):
        """
        Set the status of the assessor based on passed value

        :param status: Value to set the procstatus to
        :except: All catchable errors.
        :return: None
        """
        # Connection to Xnat
        try:
            with get_interface(host=self.host) as intf:
                assessor = self.assr_handler.select_assessor(intf)
                if assessor.exists():
                    dtype = DEFAULT_DATATYPE
                    if self.assr_handler.get_proctype() == 'FS':
                        dtype = DEFAULT_FS_DATATYPE
                    former_status = assessor.attrs.get('%s/procstatus' % dtype)
                    if former_status == JOB_RUNNING:
                        assessor.attrs.set('%s/procstatus' % dtype, status)
                        msg = '  - job status set to %s'
                        self.print_msg(msg % str(status))
        except XnatAuthentificationError as e:
            print('Failed to connect to XNAT. Error: ', e)
            pass

    def done(self):
        """
        Create a flag file that the assessor is ready to be uploaded and set
         the status as READY_TO_UPLOAD

        :return: None

        """
        # Creating the version file to give the spider version:
        f_obj = open(os.path.join(self.directory, 'version.txt'), 'w')
        f_obj.write(self.version)
        f_obj.close()
        # Finish the folder
        if not self.error and self.has_pdf:
            self.print_msg('INFO: Job ready to be upload, error: %s'
                           % str(self.error))
            # make the flag folder
            fname = '%s.txt' % READY_TO_UPLOAD
            flag_file = os.path.join(self.directory, fname)
            open(flag_file, 'w').close()
            if DAX_SETTINGS.get_launcher_type() == 'xnatq-combined':
                # set status on XNAT to ReadyToUpload
                self.set_assessor_status(READY_TO_UPLOAD)
        else:
            self.print_msg('INFO: Job failed, check the outlogs, error: %s'
                           % str(self.error))
            # make the flag folder
            fname = '%s.txt' % JOB_FAILED
            flag_file = os.path.join(self.directory, fname)
            open(flag_file, 'w').close()
            if DAX_SETTINGS.get_launcher_type() == 'xnatq-combined':
                # set status on XNAT to JOB_FAILED
                self.set_assessor_status(JOB_FAILED)

    def clean(self, directory):
        """
        Clean directory if no error and pdf created

        :param directory: directory to be cleaned
        """
        if self.has_pdf and not self.error:
            # Remove the data
            shutil.rmtree(directory)


def get_proctype(spider, suffix=None):
    """ Return the proctype from the spider_path

    :param spider: path to the spider
    :return: proctype, version
    """
    # Get the process name and the version
    if len(spider.split('/')) > 1:
        spider = os.path.basename(spider)
    if spider.endswith('.py'):
        spider = spider[:-3]
    if 'Spider' in spider:
        spider = spider[7:]

    # get the processname from spider
    proctype = spider
    version = '1.0.0'
    if len(re.split('/*_v[0-9]/*', spider)) > 1:
        version = spider.split('_v')[-1].replace('_', '.')
        ptype = re.split('/*_v[0-9]/*', spider)[0]
        proctype = '%s_v%s' % (ptype, version.split('.')[0])

    if suffix:
        if suffix[0] != '_':
            suffix = '_{}'.format(suffix)
        suffix = re.sub('[^a-zA-Z0-9]', '_', suffix)
        if suffix[-1] == '_':
            suffix = suffix[:-1]
        proctype = '{}{}'.format(proctype, suffix)
    return proctype, version


###############################################################################
#                     2) Query XNAT and Access XNAT obj                       #
###############################################################################
def get_interface(host=None, user=None, pwd=None):
    """
    Opens a connection to XNAT.

    :param host: URL to connect to XNAT
    :param user: XNAT username
    :param pwd: XNAT password
    :return: InterfaceTemp object which extends functionaly of pyxnat.Interface

    """
    return InterfaceTemp(host, user, pwd)


def list_scan_resources(intf, projectid, subjectid, sessionid, scanid):
    """
    Gets a list of all of the resources for a scan associated to a
     session/subject/project requested by the user.

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
    List all the assessors that you have access to based on passed
     session/subject/project.

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :param sessionid: ID/label of a session
    :return: List of all the assessors

    """
    new_list = list()

    if has_fs_datatypes(intf):
        # First get FreeSurfer
        post_uri = ASSESSORS_URI.format(project=projectid,
                                        subject=subjectid,
                                        session=sessionid)
        post_uri += ASSESSOR_FS_POST_URI.format(fstype=DEFAULT_FS_DATATYPE)
        assessor_list = intf._get_json(post_uri)

        pfix = DEFAULT_FS_DATATYPE.lower()
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
            anew['procstatus'] = asse['%s/procstatus' % pfix]
            anew['qcstatus'] = asse['%s/validation/status' % pfix]
            anew['proctype'] = 'FreeSurfer'
            anew['xsiType'] = asse['xsiType']
            new_list.append(anew)

    if has_genproc_datatypes(intf):
        # Then add genProcData
        post_uri = ASSESSORS_URI.format(project=projectid,
                                        subject=subjectid,
                                        session=sessionid)
        post_uri += ASSESSOR_PR_POST_URI.format(pstype=DEFAULT_DATATYPE)
        assessor_list = intf._get_json(post_uri)

        pfix = DEFAULT_DATATYPE.lower()
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
            anew['procstatus'] = asse['%s/procstatus' % pfix]
            anew['proctype'] = asse['%s/proctype' % pfix]
            anew['qcstatus'] = asse['%s/validation/status' % pfix]
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

    # Get the sessions list to get the different variables needed:
    session_list = intf.get_sessions(projectid)
    sess_id2mod = dict((sess['session_id'], [sess['subject_label'],
                        sess['type'], sess['handedness'], sess['gender'],
                        sess['yob'], sess['age'], sess['last_modified'],
                        sess['last_updated']]) for sess in session_list)

    if has_fs_datatypes(intf):
        # First get FreeSurfer
        post_uri = SE_ARCHIVE_URI
        post_uri += ASSESSOR_FS_PROJ_POST_URI.format(
            project=projectid, fstype=DEFAULT_FS_DATATYPE)
        assessor_list = intf._get_json(post_uri)

        pfix = DEFAULT_FS_DATATYPE.lower()
        for asse in assessor_list:
            if asse['label']:
                key = asse['label']
                if assessors_dict.get(key):
                    res = '%s/out/file/label' % pfix
                    assessors_dict[key]['resources'].append(asse[res])
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
                    sfix = 'xnat:imagesessiondata'
                    anew['subject_id'] = asse['%s/subject_id' % sfix]
                    anew['subject_label'] = asse['subject_label']
                    anew['session_type'] = sess_id2mod[asse['session_ID']][1]
                    anew['session_id'] = asse['session_ID']
                    anew['session_label'] = asse['session_label']
                    anew['procstatus'] = asse['%s/procstatus' % pfix]
                    anew['qcstatus'] = asse['%s/validation/status' % pfix]
                    anew['proctype'] = 'FreeSurfer'

                    if len(asse['label'].rsplit('-x-FS')) > 1:
                        anew['proctype'] = (anew['proctype'] +
                                            asse['label'].rsplit('-x-FS')[1])

                    anew['version'] = asse.get('%s/procversion' % pfix)
                    anew['xsiType'] = asse['xsiType']
                    anew['jobid'] = asse.get('%s/jobid' % pfix)
                    anew['jobstartdate'] = asse.get('%s/jobstartdate' % pfix)
                    anew['memused'] = asse.get('%s/memused' % pfix)
                    anew['walltimeused'] = asse.get('%s/walltimeused' % pfix)
                    anew['jobnode'] = asse.get('%s/jobnode' % pfix)
                    anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                    anew['gender'] = sess_id2mod[asse['session_ID']][3]
                    anew['yob'] = sess_id2mod[asse['session_ID']][4]
                    anew['age'] = sess_id2mod[asse['session_ID']][5]
                    anew['last_modified'] = sess_id2mod[asse['session_ID']][6]
                    anew['last_updated'] = sess_id2mod[asse['session_ID']][7]
                    anew['resources'] = [asse['%s/out/file/label' % pfix]]
                    assessors_dict[key] = anew

    if has_genproc_datatypes(intf):
        # Then add genProcData
        post_uri = SE_ARCHIVE_URI
        post_uri += ASSESSOR_PR_PROJ_POST_URI.format(project=projectid,
                                                     pstype=DEFAULT_DATATYPE)
        assessor_list = intf._get_json(post_uri)

        pfix = DEFAULT_DATATYPE.lower()
        for asse in assessor_list:
            if asse['label']:
                key = asse['label']
                if assessors_dict.get(key):
                    res = '%s/out/file/label' % pfix
                    assessors_dict[key]['resources'].append(asse[res])
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
                    sfix = 'xnat:imagesessiondata'
                    anew['subject_id'] = asse['%s/subject_id' % sfix]
                    anew['subject_label'] = sess_id2mod[asse['session_ID']][0]
                    anew['session_type'] = sess_id2mod[asse['session_ID']][1]
                    anew['session_id'] = asse['session_ID']
                    anew['session_label'] = asse['session_label']
                    anew['procstatus'] = asse['%s/procstatus' % pfix]
                    anew['proctype'] = asse['%s/proctype' % pfix]
                    anew['qcstatus'] = asse['%s/validation/status' % pfix]
                    anew['version'] = asse['%s/procversion' % pfix]
                    anew['xsiType'] = asse['xsiType']
                    anew['jobid'] = asse.get('%s/jobid' % pfix)
                    anew['jobnode'] = asse.get('%s/jobnode' % pfix)
                    anew['jobstartdate'] = asse.get('%s/jobstartdate' % pfix)
                    anew['memused'] = asse.get('%s/memused' % pfix)
                    anew['walltimeused'] = asse.get('%s/walltimeused' % pfix)
                    anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                    anew['gender'] = sess_id2mod[asse['session_ID']][3]
                    anew['yob'] = sess_id2mod[asse['session_ID']][4]
                    anew['age'] = sess_id2mod[asse['session_ID']][5]
                    anew['last_modified'] = sess_id2mod[asse['session_ID']][6]
                    anew['last_updated'] = sess_id2mod[asse['session_ID']][7]
                    anew['resources'] = [asse['%s/out/file/label' % pfix]]
                    anew['inputs'] = asse.get('%s/inputs' % pfix)
                    assessors_dict[key] = anew

    return sorted(list(assessors_dict.values()), key=lambda k: k['label'])


def list_assessor_out_resources(intf, projectid, subjectid, sessionid,
                                assessorid):
    """
    Gets a list of all of the resources for an assessor associated to a
     session/subject/project requested by the user.

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :param sessionid: ID/label of a session
    :param assessorid: ID/label of an assessor to get resources for
    :return: List of resources for the assessor
    """
    # Check that the assessors types are present on XNAT
    if not has_genproc_datatypes(intf):
        print('WARNING: datatypes %s not found on XNAT. \
Needed by default for dax.' % DEFAULT_DATATYPE)
        return list()

    post_uri = A_RESOURCES_URI.format(project=projectid,
                                      subject=subjectid,
                                      session=sessionid,
                                      assessor=assessorid)
    resource_list = intf._get_json(post_uri)
    return resource_list


def get_resource_lastdate_modified(intf, resource_obj):
    """
    Get the last modified data for a resource on XNAT.
     (NOT WORKING: bug on XNAT side for version<1.6.5)

    :param intf: pyxnat.Interface object
    :param resource: resource pyxnat Eobject
    :return: date of last modified data with the format %Y%m%d%H%M%S
    """
    # xpaths for times in resource xml
    created_dcm_xpath = "/cat:DCMCatalog/cat:entries/cat:entry/@createdTime"
    modified_dcm_xpath = "/cat:DCMCatalog/cat:entries/cat:entry/@modifiedTime"
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
        create_times = root.xpath(created_dcm_xpath, namespaces=root.nsmap)
    mod_times = root.xpath(modified_xpath, namespaces=root.nsmap)
    if not mod_times:
        mod_times = root.xpath(modified_dcm_xpath, namespaces=root.nsmap)
    # Find the most recent time
    all_times = create_times + mod_times
    if all_times:
        max_time = max(all_times)
        date = max_time.split('.')[0]
        res_date = (date.split('T')[0].replace('-', '') +
                    date.split('T')[1].replace(':', ''))
    else:
        res_date = ('{:%Y%m%d%H%M%S}'.format(datetime.now()))
    return res_date


# TODO: BenM/xnatutils refactor/select_assessor and get_assessor are doing
# essentially the same thing
# TODO: BenM/xnatutils refactor/we really should know the context we are
# working in wrt project,subject, etc. The only valid scenario for this
# method is if we are loading a task from file rather than going back to xnat
# for assessors
def select_assessor(intf, assessor_label):
    """
    Select assessor from his label

    :param assessor_label: label for the assessor requested
    :return: pyxnat EObject for the assessor selected
    """
    labels = assessor_label.split('-x-')
    return intf.select_assessor(labels[0],
                                labels[1],
                                labels[2],
                                assessor_label)


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
        return intf.select_scan(obj_dict['project_id'],
                                obj_dict['subject_id'],
                                obj_dict['session_id'],
                                obj_dict['scan_id'])
    elif 'xsiType' in obj_dict and \
            obj_dict['xsiType'] in [DEFAULT_FS_DATATYPE, DEFAULT_DATATYPE]:
        return intf.select_assessor(obj_dict['project_id'],
                                    obj_dict['subject_id'],
                                    obj_dict['session_id'],
                                    obj_dict['assessor_id'])
    elif 'experiments' in obj_dict['URI']:
        # TODO: BenM/xnatutils refactor/ids should be consistent
        return intf.select_experiment(obj_dict['project'],
                                      obj_dict['subject_ID'],
                                      obj_dict['ID'])
    elif 'subjects' in obj_dict['URI']:
        # TODO: BenM/xnatutils refactor/ids should be consistent
        return intf.select_subject(obj_dict['project'],
                                   obj_dict['ID'])
    elif 'projects' in obj_dict['URI']:
        return intf.select_project(obj_dict['project'])
    else:
        return intf.select_all_projects()
        # xpath = '/project/'
        # Return non existing object: obj.exists() -> False
    # return intf.select(xpath)


# TODO: BenM/xnatutils refactor/this method isn't really needed, why not just
# call interface directory?
def get_assessor(intf, projid, subjid, sessid, assrid):
    """
    Run Interface.select down to the assessor level

    :param intf: pyxnat.Interface Object
    :param projid: XNAT Project ID
    :param subjid: XNAT Subject ID
    :param sessid: XNAT Session ID
    :param assrid: XNAT Assesor label
    :return: pyxnat EObject of the assessor

    """
    return intf.select_assessor(projid, subjid, sessid, assrid)


def select_obj(intf, project_id=None, subject_id=None, session_id=None,
               scan_id=None, assessor_id=None, resource=None):
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
        raise XnatUtilsError("select_obj: can not select if no project_id \
given.")
    if scan_id and assessor_id:
        raise XnatUtilsError("select_obj: can not select scan_id and \
assessor_id at the same time.")
    tmp_dict = collections.OrderedDict([('project', project_id),
                                        ('subject', subject_id),
                                        ('experiment', session_id),
                                        ('scan', scan_id),
                                        ('assessor', assessor_id)])
    if assessor_id:
        tmp_dict['out/resource'] = resource
    else:
        tmp_dict['resource'] = resource

    for key, value in list(tmp_dict.items()):
        if value:
            select_str += '''/{key}/{label}'''.format(key=key, label=value)
    return intf.select(select_str)


# TODO: BenM/assessor_of_assessor/assessor handler should be removable in the
# medium term
def generate_assessor_handler(project, subject, session, proctype, scan=None):
    """
    Generate an assessorHandler object corresponding to the labels in the
     parameters.

    :param project: project label on XNAT
    :param subject: subject label on XNAT
    :param session: session label on XNAT
    :param proctype: proctype for the assessor
    :param scan: scan label on XNAT if apply
    :return: assessorHandler object
    """
    if scan:
        assessor_label = '-x-'.join([project, subject, session, scan,
                                     proctype])
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
    for dax_datatype in DAX_SETTINGS.get_xsitype_include():
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


###############################################################################
#                     Functions to access/check object                        #
###############################################################################
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


def is_cscan_good_type(cscan, types_list, full_regex=False):
    """
    Check to see if the CachedImageScan type is of type(s) specificed by user.

    :param cassr: CachedImageScan object from XnatUtils
    :param types_list: List of scan types (regex on)
    :param full_regex: use full regex expression
    :return: True if type is in the list, False if not.

    """
    for exp in types_list:
        regex = extract_exp(exp, full_regex)
        if regex.match(cscan.info()['type']):
            return True
    return False


def is_scan_unusable(scan_obj):
    """
    Check to see if a scan is usable

    :param scan_obj: Scan EObject from Interface.select()
    :return: True if usable, False otherwise

    """
    return scan_obj.attrs.get('xnat:imageScanData/quality') == "unusable"


def is_scan_good_type(scan_obj, types_list, full_regex=False):
    """
    Check to see if a scan is of good type.

    :param scan_obj: Scan EObject from Interface.select()
    :param types_list: List of scan types
    :param full_regex: use full regex expression
    :return: True if scan is in type list, False if not.

    """
    for exp in types_list:
        regex = extract_exp(exp, full_regex)
        if regex.match(scan_obj.attrs.get('xnat:imageScanData/type')):
            return True
    return False


def parse_assessor_inputs(inputs):
    try:
        if inputs == '':
            return None
        return utilities.decode_url_json_string(inputs)
    except IndexError:
        return None


def get_assessor_inputs(assessor):
    datatype = assessor.datatype()
    inputs = assessor.attrs.get(datatype + '/inputs')
    return parse_assessor_inputs(inputs)


def has_resource(cobj, resource_label):
    """
    Check to see if a CachedImageObject has a specified resource

    :param cobj: CachedImageObject object from XnatUtils
    :param resource_label: label of the resource to check
    :return: True if cobj has the resource and there is at least one file,
             False if not.

    """
    res_list = [res for res in cobj.get_resources()
                if res['label'] == resource_label]
    if len(res_list) > 0 and res_list[0]['file_count'] > 0:
        return True
    return False


def get_cassr_on_same_session(cobj, proctype, is_scan_proc=False):
    """
    Get the list of all CachedImageAssessor object with the proctype given
     associated to a cobj (session, scan -> for scan, same scan used)

    :param cobj: CachedImage object from XnatUtils (scan/session)
    :param proctype: Process type of the assessor to check
    :param is_scan_proc: if the assessor you are looking for
                         is attached to a scan (scan level processor)
    :return: list of CachedImageAssessor objects
    """
    obj_info = cobj.info()
    cassr_list = list()
    if isinstance(cobj, CachedImageScan):
        if is_scan_proc:
            assr_label = '-x-'.join([obj_info['project_id'],
                                     obj_info['subject_label'],
                                     obj_info['session_label'],
                                     obj_info['ID'],
                                     proctype])
        else:
            assr_label = '-x-'.join([obj_info['project_id'],
                                     obj_info['subject_label'],
                                     obj_info['session_label'],
                                     proctype])
        cassr_list = [cassr for cassr in cobj.parent().assessors()
                      if cassr.info()['label'] == assr_label]
    elif isinstance(cobj, CachedImageSession):
        cassr_list = [cassr for cassr in cobj.assessors()
                      if cassr.info()['proctype'] == proctype]
    return cassr_list


# TODO: BenM/assessor_of_assessor/unused; can be removed - DANGER, this is
# probably being used by third party code
def is_assessor_on_same_session_usable(cobj, proctype, is_scan_proc=False):
    """
    Check to see if the assessor matching the user passed proctype has
     passed QC.

    :param cobj: CachedImage object from XnatUtils (scan/session)
    :param proctype: Process type of the assessor to check
    :param is_scan_proc: if the assessor you are looking for
                         is attached to a scan (scan level processor)
    :return: 0 if the assessor is not ready or doesn't exist. -1 if it failed,
            or 1 if OK
    """
    cassr_list = get_cassr_on_same_session(cobj, proctype, is_scan_proc)

    if not cassr_list:
        return 0
    elif len(cassr_list) == 1:
        return is_bad_qa(cassr_list[0].info()['qcstatus'])
    else:
        # too many assessors checked if one rdy??
        good_cassr_list = [cassr.info() for cassr in cassr_list
                           if is_bad_qa(cassr.info()['qcstatus']) == 1]
        if len(good_cassr_list) == 1:
            return 1
        elif len(good_cassr_list) > 1:
            msg = "WARNING: too many assessors %s with a good QC status."
            print(msg % proctype)
            return 0
    return 0


def is_assessor_same_scan_unusable(cscan, proctype):
    """
    Deprecated method to check to see if the assessor matching the user
     passed scan and proctype has passed QC.
     (See is_assessor_on_same_session_usable)

    :param cscan: CachedImageScan object from XnatUtils
    :param proctype: Process type of the assessor
    :return: 0 if the assessor is not ready or doesn't exist. -1 if it failed,
     or 1 if OK

    """
    scan_info = cscan.info()
    assr_label = '-x-'.join([scan_info['project_id'],
                             scan_info['subject_label'],
                             scan_info['session_label'],
                             scan_info['ID'], proctype])
    assr_list = [cassr.info() for cassr in cscan.parent().assessors()
                 if cassr.info()['label'] == assr_label]
    if not assr_list:
        return 0
    else:
        return is_bad_qa(assr_list[0]['qcstatus'])


def is_cassessor_good_type(cassr, types_list, full_regex=False):
    """
    Check to see if the CachedImageAssessor proctype is of type(s)
     specificed by user.

    :param cassr: CachedImageAssessor object from XnatUtils
    :param types_list: List of proctypes
    :param full_regex: use full regex expression
    :return: True if proctype is in the list, False if not.

    """
    assr_info = cassr.info()
    for exp in types_list:
        regex = extract_exp(exp, full_regex)
        if regex.match(assr_info['proctype']):
            return True
    return False


def is_cassessor_usable(cassr):
    """
    Check to see if the CachedImageAssessor is usable

    :param cassr: CachedImageAssessor object from XnatUtils
    :return: 0 if the assessor is not ready or doesn't exist, -1 if failed,
     1 if OK.

    """
    return is_bad_qa(cassr.info()['qcstatus'])


def is_assessor_good_type(assessor_obj, types_list, full_regex=False):
    """
    Check to see if an assessor is of good type.

    :param assessor_obj: Assessor EObject from Interface.select()
    :param types_list: List of proctypes
    :param full_regex: use full regex expression
    :return: True if assessor is in proctypes list, False if not.

    """
    atype = assessor_obj.attrs.get('xsiType')
    proctype = assessor_obj.attrs.get('%s/proctype' % atype)
    for exp in types_list:
        regex = extract_exp(exp, full_regex)
        if regex.match(proctype):
            return True
    return False


def is_assessor_usable(assessor_obj):
    """
    Check to see if the assessor is usable

    :param cassr: Assessor EObject object from Interface.select()
    :return: 0 if the assessor is not ready or doesn't exist, -1 if failed,
     1 if OK.

    """
    atype = assessor_obj.attrs.get('xsiType')
    qcstatus = assessor_obj.attrs.get('%s/validation/status' % atype)
    return is_bad_qa(qcstatus)


def is_bad_qa(qcstatus):
    """
    Check to see if the QA status of an assessor is bad (aka unusable)

    :param qcstatus: String of the QC status of the assessor
    :return: -1 if bad, 1 if not bad, 0 if still in progress.
        (NOTE: doesn't follow boolean logic)

    """
    if qcstatus in [JOB_PENDING, NEEDS_QA, REPROC, RERUN,
                    FAILED_NEEDS_REPROC]:
        return 0
    for qc in BAD_QA_STATUS:
        if qc.lower() in qcstatus.split(' ')[0].lower():
            return -1
    return 1


def get_good_cscans(csess, scantypes, needs_qc=True):
    """
    Given a CachedImageSession, get the list of all of the usable
     CachedImageScan objects in the session

    :param csess: CachedImageSession object from XnatUtils
    :param scantypes: List of scantypes to filter for
    :param needs_qc: if we are looking for assessor with qc that passed
    :return: List of CachedImageScan objects that fit the scantypes and that
     are usable

    """
    cscans_list = list()
    for cscan in csess.scans():
        if is_cscan_good_type(cscan, scantypes) and \
           (not needs_qc or not is_cscan_unusable(cscan)):
            cscans_list.append(cscan)
    return cscans_list


def get_good_scans(session_obj, scantypes, needs_qc=True):
    """
    Get usable scans from a session.

    :param session_obj: Pyxnat session EObject
    :param scantypes: List of scanttypes (regex) to filter for
    :param needs_qc: if we are looking for scans that are not unusable
    :return: List of python scan EObjects that fit the scantypes and that are
     usable

    """
    scans = list()
    for scan_obj in session_obj.scans().fetchall('obj'):
        if is_scan_good_type(scan_obj, scantypes) and \
           (not needs_qc or not is_scan_unusable(scan_obj)):
            scans.append(scan_obj)
    return scans


def get_good_cassr(csess, proctypes, needs_qc=True):
    """
    Get all the assessors in the session and filter out the ones that are
     usable and that have the proctype(s) specified

    :param csess: CachedImageSession object from XnatUtils
    :param proctypes: List of proctypes to filter for
    :param needs_qc: if we are looking for assessor with qc that passed
    :return: List of CachedImageAssessor objects that are usable and have
     one of the proctype(s) specified.

    """
    cassr_list = list()
    for cassr in csess.assessors():
        usable_status = is_cassessor_usable(cassr)
        if is_cassessor_good_type(cassr, proctypes) and \
           (not needs_qc or usable_status == 1) and \
           cassr.info()['procstatus'] != 'NEED_INPUTS':
            cassr_list.append(cassr)
    return cassr_list


def get_good_assr(session_obj, proctypes, needs_qc=True):
    """
    Get all the assessors in the session and filter out the ones
     that are usable and that have the proctype(s) specified

    :param session_obj: Session EObject from Pyxnat
    :param proctypes: List of proctype(s) to filter for
    :param needs_qc: if we are looking for assessor with qc that passed
    :return: List of Assessor EObjects that are usable and have one of the
     proctype(s) specified.

    """
    assessors = list()
    for assessor_obj in session_obj.assessors().fetchall('obj'):
        usable_status = is_assessor_usable(assessor_obj)
        if is_assessor_good_type(assessor_obj, proctypes) and \
           (not needs_qc or usable_status == 1):
            assessors.append(assessor_obj)
    return assessors


###############################################################################
#                     Download/Upload resources from XNAT                     #
###############################################################################
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
        err = '%s: Folder %s does not exist.'
        raise XnatUtilsError(err % (function_name, directory))
    if not xnat_obj.exists():
        err = '%s: xnat object for parent <%s> does not exist on XNAT.'
        raise XnatAccessError(err % (function_name, xnat_obj.parent().label()))


def islist(argument, argname, function_name):
    """
    Check to see if the input argument is a list. If it's a string, convert it
     to a list, if it's not a list or string, print an error

    :param argument: Input datatype to check to see if it is a list or a string
    :param argname: Name of the argument?
    :param function_name: name of function
    :return: List of the string or an empty list
             (if argument is not of type list or str)

    """
    if isinstance(argument, list):
        pass
    elif isinstance(argument, basestring):
        argument = [argument]
    else:
        err = "%s: Wrong format for %s. Format allowed: list or str."
        raise XnatUtilsError(err % (function_name, argname))
    return argument


def download_file_from_obj(directory, resource_obj, fname=None):
    """
    Downloads a file from a Pyxnat EObject

    :param directory: Full path to the download directory
    :param resource_obj: Pyxnat EObject to download a file from
    :param fname: Name of the file that you want to download
    :return: File path to the file downloaded.

    """
    check_dl_inputs(directory, resource_obj, 'download_file_from_obj')

    if fname:
        if resource_obj.file(fname).exists():
            fpath = os.path.join(directory, os.path.basename(fname))
            resource_obj.file(fname).get(fpath)
            return fpath
        else:
            err = 'file %s does not exist for resource %s.'
            raise XnatAccessError(err % (fname, resource_obj.label()))
    else:
        return download_biggest_file_from_obj(directory, resource_obj)


def download_file(directory, resource, project_id=None, subject_id=None,
                  session_id=None, scan_id=None, assessor_id=None, fname=None):
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
    with get_interface() as intf:
        resource_obj = select_obj(intf, project_id, subject_id, session_id,
                                  scan_id, assessor_id, resource)
        fpath = download_file_from_obj(directory, resource_obj, fname)

    return fpath


def download_files_from_obj(directory, resource_obj):
    """
    Download ALL of the files from a Pyxnat EObject

    :param directory: Full path to the download directory
    :param resource_obj: Pyxnat EObject to download all the files from
    :return: List of all the files downloaded

    """
    fpaths = list()
    check_dl_inputs(directory, resource_obj, 'download_files_from_obj')
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
    with get_interface() as intf:
        resource_obj = select_obj(intf, project_id, subject_id, session_id,
                                  scan_id, assessor_id, resource)
        fpaths = download_files_from_obj(directory, resource_obj)

    return fpaths


def download_biggest_file_from_obj(directory, resource_obj):
    """
    Downloads the largest file (based on file size in bytes) from a resource.

    :param directory: Full path to the download directory
    :param resource_obj: Pyxnat EObject to download from
    :return: path for the file downloaded

    """
    file_index = 0
    biggest_size = 0
    fpath = None
    check_dl_inputs(directory, resource_obj, 'download_biggest_file_from_obj')

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
    with get_interface() as intf:
        resource_obj = select_obj(intf, project_id, subject_id, session_id,
                                  scan_id, assessor_id, resource)
        fpath = download_biggest_file_from_obj(directory, resource_obj)

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
    fpaths = list()
    check_dl_inputs(directory, xnat_obj, 'download_from_obj')
    resources = islist(resources, 'resources', 'download_from_obj')

    for resource in resources:
        if xnat_obj.datatype() in [DEFAULT_DATATYPE, DEFAULT_FS_DATATYPE]:
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


def download(directory, resources, project_id=None, subject_id=None,
             session_id=None, scan_id=None, assessor_id=None, all_files=False):
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
    with get_interface() as intf:
        xnat_obj = select_obj(intf, project_id, subject_id, session_id,
                              scan_id, assessor_id)
        fpaths = download_from_obj(directory, xnat_obj, resources, all_files)
    return fpaths


def download_scan_types(directory, project_id, subject_id, session_id,
                        scantypes, resources, all_files=False):
    """
    Downloads resources from a scan given a scan type, rather than a scan ID

    :param directory: Directory to download the data to
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param scantypes: List of scan types to download resources from.
    :param resources: List of resources to download data from.
    :param all_files: If 1, download from all resources for the scan object,
                      otherwise use the list.
    :return: list of filepaths for the files downloaded

    """
    fpaths = list()
    scantypes = islist(scantypes, 'scantypes', 'download_scan_types')
    with get_interface() as intf:
        for scan in intf.get_scans(project_id, subject_id, session_id):
            if scan['type'] in scantypes:
                scan_obj = select_obj(intf, project_id, subject_id, session_id,
                                      scan['ID'])
                fpaths.extend(download_from_obj(directory, scan_obj, resources,
                                                all_files))

    return fpaths


def download_scan_seriesdescriptions(directory, project_id, subject_id,
                                     session_id, seriesdescriptions, resources,
                                     all_files=False):
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
    seriesdescriptions = islist(seriesdescriptions, 'seriesdescription',
                                'download_scan_seriesdescriptions')

    with get_interface() as intf:
        for scan in intf.get_scans(project_id, subject_id, session_id):
            if scan['series_description'] in seriesdescriptions:
                scan_obj = select_obj(intf, project_id, subject_id, session_id,
                                      scan['ID'])
                fpaths.extend(download_from_obj(directory, scan_obj, resources,
                                                all_files))

    return fpaths


def download_assessor_proctypes(directory, project_id, subject_id, session_id,
                                proctypes, resources, all_files=False):
    """
    Download resources from an assessor based on a list of proctypes

    :param directory: Directory to download the data to
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param proctypes: list of proctypes to download from
    :param resources: list of resources to download from
    :param all_files: True if download all the files,
                      False if download the biggest file
    :return: List of filepaths for the files downloaded

    """
    fpaths = list()
    proctypes = islist(proctypes, 'proctypes', 'download_assessor_proctypes')
    proctypes = set([proctype.replace('FreeSurfer', 'FS')
                     for proctype in proctypes])

    with get_interface() as intf:
        li_assrs = list_assessors(intf, project_id, subject_id, session_id)
        for assessor in li_assrs:
            if assessor['proctype'] in proctypes:
                assessor_obj = select_obj(intf, project_id, subject_id,
                                          session_id,
                                          assessor_id=assessor['label'])
                fpaths.extend(download_from_obj(directory, assessor_obj,
                                                resources, all_files))

    return fpaths


def upload_file_to_obj(filepath, resource_obj, remove=False, removeall=False,
                       fname=None):
    """
    Upload a file to a pyxnat EObject

    :param filepath: Full path to the file to upload
    :param resource_obj: pyxnat EObject to upload the file to.
                         Note this should be a resource
    :param remove: Remove the file if it exists
    :param removeall: Remove all of the files
    :param fname: save the file on disk with this value as file name
    :return: True if upload was OK, False otherwise

    """
    if not os.path.isfile(filepath):  # Check existence of the file
        err = "%s: file %s doesn't exist."
        raise XnatUtilsError(err % ('upload_file_to_obj', filepath))
    elif os.path.getsize(filepath) == 0:  # Check for empty file
        err = "%s: empty file, not uploading %s."
        raise XnatUtilsError(err % ('upload_file_to_obj', filepath))
    else:
        # Remove previous resource to upload the new one
        if removeall and resource_obj.exists():
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
                print("WARNING: upload_file_to_obj in XnatUtils: resource %s \
already exists." % filename)
                return False
        resource_obj.file(str(filename)).put(str(filepath), overwrite=True, params={"event_reason": "DAX uploading file"})
        return True


def upload_file(filepath, project_id=None, subject_id=None, session_id=None,
                scan_id=None, assessor_id=None, resource=None, remove=False,
                removeall=False, fname=None):
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
    :param removeall: remove all of files that exist for the resource if True
    :param fname: save the file on disk with this value as file name
    :return: True if upload was OK, False otherwise
    """
    status = False
    if not resource:
        err = '%s: resource argument not provided.'
        raise XnatUtilsError(err % ('upload_file'))
    else:
        with get_interface() as intf:
            resource_obj = select_obj(intf, project_id, subject_id, session_id,
                                      scan_id, assessor_id, resource)
            status = upload_file_to_obj(filepath, resource_obj, remove,
                                        removeall, fname)

    return status


def upload_files_to_obj(filepaths, resource_obj, remove=False,
                        removeall=False):
    """
    Upload a list of files to a resource on XNAT
    :param filepaths: list of files to upload
    :param resource_obj: pyxnat EObject to upload all of the files to
    :param remove: remove files that already exist for the resource.
    :param removeall: remove all previous files on the resource.
    :return: True if upload was OK, False otherwise

    """
    # Remove previous resource to upload the new one
    if removeall and resource_obj.exists():
        resource_obj.delete()
    status = list()
    for filepath in filepaths:
        status.append(upload_file_to_obj(filepath, resource_obj, remove=remove,
                                         removeall=False))
    return status


def upload_files(filepaths, project_id=None, subject_id=None, session_id=None,
                 scan_id=None, assessor_id=None, resource=None, remove=False,
                 removeall=False):
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
    status = [False] * len(filepaths)
    if not resource:
        err = '%s: resource argument not provided.'
        raise XnatUtilsError(err % ('upload_files'))
    else:
        with get_interface() as intf:
            resource_obj = select_obj(intf, project_id, subject_id, session_id,
                                      scan_id, assessor_id, resource)
            status = upload_files_to_obj(filepaths, resource_obj, remove,
                                         removeall)

    return status


def upload_folder_to_obj(directory, resource_obj, resource_label, remove=False,
                         removeall=False, extract=True):
    """
    Upload all of the files in a folder based on the pyxnat EObject passed

    :param directory: Full path of the directory to upload
    :param resource_obj: pyxnat EObject to upload the data to
    :param resource_label: label of where you want the contents of the
     directory to be stored under on XNAT. Note this is a level down
     from resource_obj
    :param remove: Remove the file if it exists if True
    :param removeall: Remove all of the files if they exist if True
    :param extract: extract the files if it's a zip
    :return: True if upload was OK, False otherwise

    """
    if not os.path.exists(directory):
        err = '%s: directory %s does not exist.'
        raise XnatUtilsError(err % ('upload_folder_to_obj', directory))

    if resource_obj.exists():
        if removeall:
            resource_obj.delete()
        elif not remove:
            # check if any files already exists on XNAT, if yes return FALSE
            for fpath in get_files_in_folder(directory):
                if resource_obj.file(fpath).exists():
                    print("Warning: upload_folder_to_obj in XnatUtils: file \
%s already found on XNAT. No upload. Use remove/removeall." % fpath)
                    return False

    fzip = '%s.zip' % resource_label
    initdir = os.getcwd()
    # Zip all the files in the directory
    os.chdir(directory)
    os.system('zip -r %s * > /dev/null' % fzip)
    # upload
    resource_obj.put_zip(os.path.join(directory, fzip), overwrite=True,
                         extract=extract)
    # return to the initial directory:
    os.chdir(initdir)
    return True


def upload_folder(directory, project_id=None, subject_id=None, session_id=None,
                  scan_id=None, assessor_id=None, resource=None, remove=False,
                  removeall=False, extract=True):
    """
    Upload a folder to some URI in XNAT based on the inputs

    :param directory: Full path to directory to upload
    :param project_id: XNAT project ID
    :param subject_id: XNAT subject ID/label
    :param session_id: XNAT session ID/label
    :param scan_id: XNAT scan ID
    :param assessor_id: XNAT assessor ID
    :param resource: resource label of where to upload the data to
    :param remove: Remove the file if it already exists (if True).
                   Otherwise don't upload if exists
    :param removeall: Remove all of the files that exist, and upload what is in
                      the local directory.
    :param extract: extract the files if it's a zip
    :return: True if upload was OK, False otherwise

    """
    status = False
    if not resource:
        err = '%s: resource argument not provided.'
        raise XnatUtilsError(err % ('upload_folder'))
    else:
        with get_interface() as intf:
            resource_obj = select_obj(intf, project_id, subject_id, session_id,
                                      scan_id, assessor_id, resource)
            status = upload_folder_to_obj(directory, resource_obj, resource,
                                          remove, removeall, extract)

    return status

def upload_reference(reference, assessor_obj, resource):
    """
    Upload path by reference

    :param reference: Full path of the directory on xnat server to be uploaded
    :param resource: pyxnat object resource to be uploaded
    """
    _uri = '{}/out/resources/{}/files?overwrite=True&label={}&reference={}'
    _uri = _uri.format(assessor_obj._uri, resource, resource, reference)
    _xnat = assessor_obj._intf
    _resp = _xnat.put(_uri)
    if (_resp is not None and not _resp.ok):
        err = 'bad response on put:{}'.format(_resp.content)
        raise XnatUtilsError(err)

def copy_resource_from_obj(directory, xnat_obj, old_res, new_res):
    """
    Copy a resource from an old location to a new location,

    :param directory: Temporary directory to download the old resource to
    :param xnat_obj: pyxnat EObject of the parent of the old_res
    :param old_res: pyxnat EObject of resource to copy
    :param new_res: pyxnat EObject of where to copy the old_res to
    :return: True if upload was OK, false otherwise.

    """
    if not old_res or not new_res:
        err = '%s: old_res or new_res argument not provided.'
        raise XnatUtilsError(err % ('copy_resource_from_obj'))

    # resources objects:
    if xnat_obj.datatype() in [DEFAULT_DATATYPE, DEFAULT_FS_DATATYPE]:
        old_resource_obj = xnat_obj.out_resource(old_res)
        new_resource_obj = xnat_obj.out_resource(new_res)
    else:
        old_resource_obj = xnat_obj.resource(old_res)
        new_resource_obj = xnat_obj.resource(new_res)
    # Copy
    fpaths = download_files_from_obj(directory, old_resource_obj)
    if not fpaths:
        return False
    folder = os.path.join(directory, old_resource_obj.label())
    status = upload_folder_to_obj(folder, new_resource_obj, new_res)
    # clean director
    clean_directory(directory)
    return status


def copy_resource(directory, project_id=None, subject_id=None, session_id=None,
                  scan_id=None, assessor_id=None, old_res=None, new_res=None):
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
        err = '%s: old_res or new_res argument not provided.'
        raise XnatUtilsError(err % ('copy_resource'))
    else:
        with get_interface() as intf:
            xnat_obj = select_obj(intf, project_id, subject_id, session_id,
                                  scan_id, assessor_id)
            status = copy_resource_from_obj(directory, xnat_obj, old_res,
                                            new_res)

    return status


def upload_assessor_snapshots(assessor_obj, original, thumbnail):
    """
    Upload the snapshots of the assessor PDF.
     (both the original and the thumbnail)

    :param assessor_obj: pyxnat EObject of the assessor to upload the snapshots
    :param original: The original file (full size)
    :param thumbnail: The thumbnail of the original file
    :return: True if it uploaded OK, False if it failed.

    """
    if not os.path.isfile(original) or not os.path.isfile(thumbnail):
        err = "%s: original or thumbnail snapshots don't exist."
        raise XnatUtilsError(err % ('upload_assessor_snapshots'))

    assessor_obj.out_resource('SNAPSHOTS')\
                .file(os.path.basename(thumbnail))\
                .put(thumbnail, thumbnail.split('.')[1].upper(), 'THUMBNAIL',
                     overwrite=True, params={"event_reason": "DAX uploading file"})
    assessor_obj.out_resource('SNAPSHOTS')\
                .file(os.path.basename(original))\
                .put(original, original.split('.')[1].upper(), 'ORIGINAL',
                     overwrite=True, params={"event_reason": "DAX uploading file"})
    return True


def filter_list_dicts_regex(list_dicts, key, expressions, nor=False,
                            full_regex=False):
    """Filter the list of dictionary from XnatUtils.list_* using the regex.

    :param list_dicts: list of dictionaries to filter
    :param key: key from dictionary to filter using regex
    :param expressions: list of regex expressions to use (OR)
    :param full_regex: use full regex
    :return: list of items from the list_dicts that match the regex
    """
    flist = list()
    if nor:
        flist = list_dicts
    if isinstance(expressions, basestring):
        expressions = [expressions]
    elif isinstance(expressions, list):
        pass
    else:
        err = "Wrong type for 'expressions' in filter_list_dicts_regex: %s \
found, <type 'str'> or <type 'list'> required." % type(expressions)
        raise XnatUtilsError(err)

    for exp in expressions:
        regex = extract_exp(exp, full_regex)
        if nor:
            flist = [d for d in flist if not regex.match(d[key])]
        else:
            flist.extend([d for d in list_dicts
                          if regex.match(d[key])])
    return flist


def extract_exp(expression, full_regex=False):
    """Extract the experession with or without full_regex.

    :param expression: string to filter
    :param full_regex: using full regex
    :return: regex Object from re package
    """
    if not full_regex:
        exp = fnmatch.translate(expression)
    return re.compile(exp)


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
        os.system('gzip %s' % fpath)


def ungzip_nii(directory):
    """
    Gunzip all of the NIfTI files in a directory via system call.

    :param directory: The directory to filter for *.nii.gz files
    :return: None

    """
    for fpath in glob.glob(os.path.join(directory, '*.nii.gz')):
        os.system('gzip -d %s' % fpath)


def run_matlab(matlab_script, verbose=False, matlab_bin='matlab'):
    """
    Call MATLAB with -nodesktop -nosplash and -singlecompthread.

    :param matlab_script: Full path to the .m file to run
    :param verbose: True to print all MATLAB output to terminal, False to
     suppress.
    :return: None

    """
    print("Matlab script: %s running ..." % matlab_script)
    # with xvfb-run: xvfb-run  -e {err} -f {auth} -a
    # --server-args="-screen 0 1600x1280x24 -ac -extension GLX"
    cmd = ("%s -singleCompThread -nodesktop -nosplash < %s"
           % (matlab_bin, matlab_script))
    if not verbose:
        matlabdir = os.path.dirname(matlab_script)
        prefix = os.path.basename(matlab_script).split('.')[0]
        cmd = '%s > %s_outlog.log' % (cmd, os.path.join(matlabdir, prefix))
    os.system(cmd)
    print("Matlab script: %s done" % matlab_script)


def run_matlab_by_version(matlab_script, verbose=False, matlab_bin='matlab'):
    """
    Call MATLAB with -nodesktop -nosplash and -singlecompthread.

    :param matlab_script: Full path to the .m file to run
    :param verbose: True to print all MATLAB output to terminal, False to
     suppress.
    :return: None

    """
    run_matlab(matlab_script, verbose=verbose, matlab_bin=matlab_bin)


def run_subprocess(args):
    """
    Runs a subprocess call

    :param args: Args for the call
    :return: STDOUT, and STDERR

    """
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr


def make_temp_dir():
    """
    Makes a directory using tempfile

    :return: Full path of the directory created
    """
    return tempfile.mkdtemp()


def makedir(directory, prefix='TempDir', subdir=True):
    """
    Makes a directory if it doesn't exist and if it does, makes a sub directory
     with the format prefix_date in the directory specified.
    :param directory: The directory to create
    :param prefix: prefix for the base directory, default: TempDir
    :param subdir: create a subdir if directory exists using the prefix and
                   the date
    :return: Full path of the directory created.
    """
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        if subdir:
            ts = time.time()
            ftime = str(ts).replace('.','_')
            directory = os.path.join(directory, '%s_%s' % (prefix, ftime))
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
    print("--Arguments given to the spider--")
    for info, value in list(vars(options).items()):
        if value:
            print("{info}: {value}".format(info=info, value=value))
        else:
            print("%s: Not set. The process might fail without this argument."
                  % info)
    print("---------------------------------")


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


def executable_exists(executable):
    """ Return True if the executable exists.

    If the full path is given, check that it's an executable.
    Else check in PATH for the file.
    """
    if '/' in executable and os.path.isfile(executable):
        return os.access(os.path.abspath(executable), os.X_OK)
    else:
        if True in [os.path.isfile(os.path.join(path, executable)) and
                    os.access(os.path.join(path, executable), os.X_OK)
                    for path in os.environ["PATH"].split(os.pathsep)]:
            return True
    return False


def check_image_format(fpath):
    """
    Check to see if a NIfTI file or REC file are uncompress and runs gzip via
     system command if not compressed

    :param fpath: Filepath of a NIfTI or REC file
    :return: the new file path of the gzipped file.

    """
    if fpath.endswith('.nii') or fpath.endswith('.rec'):
        os.system('gzip %s' % fpath)
        fpath = '%s.gz' % fpath
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
            err = 'upload_list_records_redcap: Creation of record failed.'
            raise XnatUtilsError(err)
        except Exception:
            err = 'upload_list_records_redcap: connection to REDCap \
interrupted.'
            raise XnatUtilsError(err)


def get_input_list(input_val, default_val):
    """
    Method to get a list from a comma separated string.

    :param input_val: Input string or list
    :param default_val: Default value (generally used for a spider)
    :return: listified string or default_val if input is not a list or string.

    """
    if isinstance(input_val, list):
        return input_val
    elif isinstance(input_val, basestring):
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
    elif isinstance(input_val, basestring):
        return input_val
    else:
        return default_val


def get_random_sessions(xnat, project_id, num_sessions):
    """
    Get a random list of session labels from an XNAT project

    :param xnat: pyxnat Interface object
    :param project_id: XNAT Project ID
    :param num_sessions: Number of sessions if <1 and >0,
                         it is assumed to be a percent.
    :return: List of session labels for the project

    """
    sessions = xnat.get_sessions(project_id)
    session_labels = [x['label'] for x in sessions]
    if num_sessions > 0 and num_sessions < 1:
        num_sessions = int(num_sessions * len(session_labels))
    return ','.join(random.sample(session_labels, num_sessions))


###############################################################################
#                                5) Cached Class                              #
###############################################################################
class CachedImageSession(object):
    """
    Enumeration for assessors function, to control what assessors are returned
    """
    class AssessorSelect:
        all_inputs = 0,
        with_inputs = 1

        @classmethod
        def valid(cls, value):
            return value in [cls.all_inputs, cls.with_inputs]

    """
    Class to cache the XML information for a session on XNAT
    """
    def __init__(self, intf, proj, subj, sess):
        """
        Entry point for the CachedImageSession class

        :param intf: pyxnat Interface object
        :param proj: XNAT project ID
        :param subj: XNAT subject ID/label
        :param sess: XNAT session ID/label
        :return: None

        """
        experiment = intf.select_experiment(proj, subj, sess)
        self.datatype_ = experiment.datatype()
        xml_str = experiment.get()
        self.creation_timestamp_ =\
            experiment.attrs.get(self.datatype_+'/meta/insert_date')
        self.sess_element = ET.fromstring(xml_str)
        self.project = proj
        self.subject = subj
        self.session = sess
        self.intf = intf  # cache for later usage

    def entity_type(self):
        return 'session'

    def reload(self):
        experiment = self.intf.select_experiment(self.project,
                                              self.subject,
                                              self.session)
        self.sess_element = ET.fromstring(experiment.get())

    def label(self):
        """
        Get the label of the session

        :return: String of the session label

        """
        return self.sess_element.get('label')

    def full_path(self):
        self.intf.get_session_path(self.project, self.subject, self.session)

    def get(self, name):
        """
        Get the value of a variable name in the session

        :param name: The variable name that you want to get the value of
        :return: The value of the variable or '' if not found.

        """
        value = self.sess_element.get(name)
        if value is not None:
            return value

        element = self.sess_element.find(name, NS)
        if element is not None:
            return element.text

        # TODO:BenM/xnat refactor/according to the lxml spec, find does this anyway
        split_array = name.rsplit('/', 1)
        if len(split_array) == 2:
            tag, attr = split_array
            element = self.sess_element.find(tag, NS)
            if element is not None:
                value = element.get(attr)
                if value is not None:
                    return value

        return ''

    def project_id(self):
        return self.project

    def subject_id(self):
        return self.subject

    def session_id(self):
        return self.session

    def session(self):
        """
        Get the session associated with this object
        :return: session asscoiated with this object
        """
        return self

    def has_shared_project(self):
        """
        Get the project if shared.

        :return: project_shared_id if shared, None otherwise
        """
        project_id = self.sess_element.get('project')
        if project_id != self.project:
            return project_id
        return None

    def scans(self):
        """
        Get a list of CachedImageScan objects for the XNAT session

        :return: List of CachedImageScan objects for the session.

        """
        scan_list = []
        scan_elements = self.sess_element.find('xnat:scans', NS)
        if scan_elements:
            for scan in scan_elements:
                scan_list.append(CachedImageScan(self.intf, scan, self))

        return scan_list

    def assessors(self, select=AssessorSelect.all_inputs):
        """
        Get a list of CachedImageAssessor objects for the XNAT session

        :return: List of CachedImageAssessor objects for the session.

        """
        if not self.AssessorSelect.valid(select):
            raise ValueError("'select' must be a valid AssessorSelect.value")


        assr_list = []

        assr_elements = self.sess_element.find('xnat:assessors', NS)
        if assr_elements:
            for assr in assr_elements:
                assr_list.append(CachedImageAssessor(self.intf, assr, self))

            if select == CachedImageSession.AssessorSelect.with_inputs:
                assr_list = assr_list.filter(
                    parse_assessor_inputs(self.get("proc:inputs") is not None)
                )

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
        sess_info['URI'] = '/data/experiments/%s' % sess_info['ID']
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

        ruri = 'xnat:resources/xnat:resource'
        file_elements = self.sess_element.findall(ruri, NS)
        if file_elements:
            for file_element in file_elements:
                xmltype = '{http://www.w3.org/2001/XMLSchema-instance}type'
                xsi_type = file_element.get(xmltype)
                if xsi_type == 'xnat:resourceCatalog':
                    res_list.append(CachedResource(file_element, self))

        return res_list

    def get_resources(self):
        """
        Return a list of dictionaries that correspond to the information
         for each resource

        :return: List of dictionaries
        """
        return [res.info() for res in self.resources()]

    def full_object(self):
        """
        Return a the full pyxnat Session object of this sessions

        :return: pyxnat Session object

        """
        return self.intf.select_experiment(self.project, self.subject, self.session)


    def creation_timestamp(self):
        return self.creation_timestamp_


    def datatype(self):
        return self.datatype_


class CachedImageScan(object):
    """
    Class to cache the XML information for a scan on XNAT
    """
    def __init__(self, intf, scan_element, parent):
        """
        Entry point for the CachedImageScan class

        :param scan_element: XML string corresponding to a scan
        :param parent: Parent XML string of the session
        :return: None

        """
        self.intf = intf
        self.scan_parent = parent
        self.scan_element = scan_element
        self.scan_label = self.label()
        self.type_ = self.get('type')

    def entity_type(self):
        return 'scan'

    def type(self):
        return self.type_

    def parent(self):
        """
        Get the parent of the scan

        :return: XML String of the scan parent

        """
        return self.scan_parent

    def project_id(self):
        return self.scan_parent.project_id()

    def subject_id(self):
        return self.scan_parent.subject_id()

    def session_id(self):
        return self.scan_parent.session_id()

    def label(self):
        """
        Get the ID of the scan

        :return: String of the scan ID

        """
        return self.scan_element.get('ID')

    def full_path(self):
        return self.intf.get_scan_path(self.scan_parent.project_id(),
                                       self.scan_parent.subject_id(),
                                       self.scan_parent.session_id(),
                                       self.scan_label)

    def get(self, name):
        """
        Get the value of a variable associated with a scan.

        :param name: Name of the variable to get the value of
        :return: Value of the variable if it exists, or '' otherwise.

        """
        value = self.scan_element.get(name)
        if value is not None:
            return value

        element = self.scan_element.find(name, NS)
        if element is not None:
            return element.text

        if ':' in name:
            tag, attr = name.rsplit(':', 1)
            element = self.scan_element.find(tag, NS)
            if element is not None:
                value = element.get(attr)
                if value is not None:
                    return value

        return ''

    def session(self):
        """
        Get the session associated with this object
        :return: session asscoiated with this object
        """
        return self.parent()

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

    def type(self):
        return self.info()['type']

    def usable(self):
        return self.info()['quality'] == 'usable'

    def unusable(self):
        return self.info()['quality'] == 'unusable'

    def resources(self):
        """
        Get a list of the CachedResource (s) associated with this scan.

        :return: List of the CachedResource (s) associated with this scan.
        """
        res_list = []

        file_elements = self.scan_element.findall('xnat:file', NS)
        if file_elements:
            for file_element in file_elements:
                xmltype = '{http://www.w3.org/2001/XMLSchema-instance}type'
                xsi_type = file_element.get(xmltype)
                if xsi_type == 'xnat:resourceCatalog':
                    res_list.append(CachedResource(file_element, self))

        return res_list

    def get_resources(self):
        """
        Get a list of dictionaries of info for each CachedResource.

        :return: List of dictionaries of infor for each CachedResource.
        """
        return [res.info() for res in self.resources()]

    def full_object(self):
        info = self.info()
        return self.intf.select_scan(info['project_id'],
                                     info['subject_id'],
                                     info['session_id'],
                                     info['scan_id'])


class CachedImageAssessor(object):
    """
    Class to cache the XML information for an assessor on XNAT
    """
    def __init__(self, intf, assr_element, parent):
        """
        Entry point for the CachedImageAssessor class on XNAT

        :param assr_element: the assessor XML string on XNAT
        :param parent: the parent element of the assessor
        :return: None

        """
        self.intf = intf
        self.assr_parent = parent
        self.assr_element = assr_element
        self.proctype = None

    def entity_type(self):
        return 'assessor'

    def parent(self):
        """
        Get the parent element of the assessor (session)

        :return: The session element XML string

        """
        return self.assr_parent

    def project_id(self):
        return self.assr_parent.project_id()

    def subject_id(self):
        return self.assr_parent.subject_id()

    def session_id(self):
        return self.assr_parent.session_id()

    def label(self):
        """
        Get the label of the assessor

        :return: String of the assessor label

        """
        return self.assr_element.get('label')

    # TODO: BenM/legacy_assessor_support/full label needs to support legacy
    # naming convention assessors
    def full_label(self):
        return '-x-'.join([self.project_id(),
                           self.subject_id(),
                           self.session_id(),
                           self.label()])

    # TODO: BenM/legacy_assessor_support/full_path needs to support legacy
    # naming convention assessors
    def full_path(self):
        return self.intf.get_assessor_path(self.project_id(),
                                           self.subject_id(),
                                           self.session_id(),
                                           self.label())

    def get(self, name):
        """
        Get the value of a variable associated with the assessor

        :param name: Variable name to get the value of
        :return: Value of the variable, otherwise ''.

        """
        value = self.assr_element.get(name)
        if value is not None:
            return value

        element = self.assr_element.find(name, NS)
        if element is not None:
            return element.text

        # tag, attr = name.rsplit('/', 1)
        # element = self.assr_element.find(tag, NS)
        # if element is not None:
        #     value = element.get(attr)
        #     if value is not None:
        #         return value

        split_array = name.rsplit('/', 1)
        if len(split_array) == 2:
            tag, attr = split_array
            element = self.assr_element.find(tag, NS)
            if element is not None:
                value = element.get(attr)
                if value is not None:
                    return value

        return ''

    def type(self):
        if self.proctype is None:
            self.proctype = self.info()['proctype']
        return self.proctype

    def info(self):
        """
        Get a dictionary of information associated with the assessor

        :return: None

        """
        assr_info = {}

        assr_info['inputs'] = parse_assessor_inputs(self.get('proc:inputs'))
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
        xmltype = '{http://www.w3.org/2001/XMLSchema-instance}type'
        assr_info['xsiType'] = self.get(xmltype).lower()

        if assr_info['xsiType'].lower() == DEFAULT_FS_DATATYPE.lower():
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

        elif assr_info['xsiType'].lower() == DEFAULT_DATATYPE.lower():
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
            msg = 'Warning:unknown xsitype for assessor: %s'
            print(msg % assr_info['xsiType'])

        return assr_info


    # TODO: BenM/assessor_of_assessor/implment this once the schema is
    # extended
    def get_inputs(self):
        return parse_assessor_inputs(self.get('proc:inputs'))


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

    def resources(self):
        return self.out_resources()

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

    def full_object(self):
        info = self.info()
        return self.intf.select_assessor(info['project_id'],
                                         info['subject_id'],
                                         info['session_id'],
                                         info['assessor_id'])


class CachedResource(object):
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

    def entity_type(self):
        return 'resource'

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

    def file_count(self):
        file_count = self.get('filecount')
        return file_count if file_count != '' else 0

    def get(self, name):
        """
        Get the value of a variable associated with the resource

        :param name: Variable name to get the value of
        :return: The value of the variable, '' otherwise.

        """
        value = self.res_element.get(name)
        if value is not None:
            return value

        element = self.res_element.find(name, NS)
        if element is not None:
            return element.text

        split_array = name.rsplit('/', 1)
        if len(split_array) == 2:
            tag, attr = split_array
            element = self.res_element.find(tag, NS)
            if element is not None:
                value = element.get(attr)
                if value is not None:
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


# File Utils
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
    open(file_zipped[:-3], 'w').write(gzdata)


def find_files(directory, ext):
    """Return the files in subdirectories with the right extension.

    :param directory: directory where the data are located
    :param ext: extension to look for
    :return: python list of files
    """
    li_files = list()
    for root, _, filenames in os.walk(directory):
        li_files.extend([os.path.join(root, f) for f in filenames
                         if f.lower().endswith(ext.lower())])
    return li_files


def zip_list(li_files, zip_path, subdir=False):
    """Zip all the files in the list into a zip file.

    :param li_files: python list of files for the zip
    :param zip_path: zip path
    :param subdir: copy the subdirectories as well. Default: False.
    """
    if not zip_path.lower().endswith('.zip'):
        zip_path = '%s.zip' % zip_path
    with zipfile.ZipFile(zip_path, 'w') as myzip:
        for fi in li_files:
            if subdir:
                myzip.write(fi, compress_type=zipfile.ZIP_DEFLATED)
            else:
                myzip.write(fi, arcname=os.path.basename(fi),
                            compress_type=zipfile.ZIP_DEFLATED)


def unzip_list(zip_path, directory):
    """Unzip all the files from the zip file and give the list of files.

    :param zip_path: zip path
    :param directory: directory where to extract the data
    :return: python list of files
    """
    li_files = list()
    if not os.path.exists(directory):
        raise XnatUtilsError('Folder %s does not exist.' % directory)
    with zipfile.ZipFile(zip_path, 'r') as myzip:
        for member in myzip.infolist():
            path = directory
            words = member.filename.split('/')
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            myzip.extract(member, path)
            li_files.append(path)
    return li_files


def read_csv(csv_file, header=None, delimiter=','):
    """Read CSV file (.csv files).

    :param csv_file: path to the csv file
    :param header: list of label for the header, if None, use first line
    :param delimiter: delimiter for the csv, default comma
    :return: list of rows
    """
    if not os.path.isfile(csv_file):
        raise XnatUtilsError('File not found: %s' % csv_file)
    if not csv_file.endswith('.csv'):
        raise XnatUtilsError('File format unknown. Need .csv: %s' % csv_file)
    # Read csv
    csv_info = list()
    with open(csv_file, 'rb') as f:
        reader = csv.reader(f, delimiter=delimiter)
        if not header:
            header = next(reader)
        for row in reader:
            if row == header:
                continue
            csv_info.append(dict(list(zip(header, row))))
    return csv_info


def read_excel(excel_file, header_indexes=None):
    """Read Excel spreadsheet (.xlsx files).

    :param excel_file: path to the Excel file
    :param header_indexes: dictionary with sheet name and header position
                           or use first value
    :return: dictionary of the sheet with the data
    """
    if not os.path.isfile(excel_file):
        raise XnatUtilsError('File not found: %s' % excel_file)
    if not excel_file.endswith('.xlsx'):
        raise XnatUtilsError('File format unknown. Need .xlsx: %s'
                             % excel_file)
    # Read the xlsx file:
    book = xlrd.open_workbook(excel_file)
    excel_sheets = dict()
    for sht in book.sheets():
        sheet_info = list()
        if header_indexes:
            header = sht.row_values(int(header_indexes[sht.name]))
            start = int(header_indexes[sht.name])
        else:
            header = sht.row_values(0)
            start = 0
        for row_index in range(start + 1, sht.nrows):
            row = list()
            for col_index in range(sht.ncols):
                value = sht.cell(rowx=row_index, colx=col_index).value
                row.append(value)
            sheet_info.append(dict(list(zip(header, row))))
        excel_sheets[sht.name] = sheet_info

    return excel_sheets


def read_yaml(yaml_file):
    """Functio to read a yaml file and return the document info

    :param yaml_file: yaml file path
    """
    with open(yaml_file, "r") as yaml_stream:
        try:
            return yaml.load(yaml_stream)
        except yaml.error.YAMLError as exc:
            err = 'YAML File {} could not be loaded properly. Error: {}'
            raise XnatUtilsError(err.format(yaml_file, exc))
    return None


# DICOM Utils
def is_dicom(fpath):
    """Check if the file is a DICOM medical data.

    :param fpath: path of the file
    :return boolean: true if it's a DICOM, false otherwise
    """
    if not os.path.isfile(fpath):
        raise XnatUtilsError('File not found: %s' % fpath)
    file_call = '''file {fpath}'''.format(fpath=fpath)
    output = subprocess.check_output(file_call.split())
    if 'dicom' in output.split(':')[1].lower():
        return True

    return False


def order_dicoms(folder):
    """Order the dicoms in a folder by the Slice Location.

    :param folder: path to the folder
    :return: dictionary of the files with the key is the slice location
    """
    if not os.path.isdir(folder):
        raise XnatUtilsError('Folder not found: %s' % folder)
    dcm_files = dict()
    for dc in glob.glob(os.path.join(folder, '*.dcm')):
        dst = pydicom.read_file(dc)
        dcm_files[float(dst.SliceLocation)] = dc
    return collections.OrderedDict(sorted(dcm_files.items()))


def find_dicom_in_folder(folder, recursively=True):
    """Find a dicom file in folder.

    :param folder: path to folder to search
    :param recursively: search sub folder
    :return: list of dicoms
    """
    dicom_list = list()
    if not os.path.isdir(folder):
        raise XnatUtilsError('Folder not found: %s' % folder)
    for ffname in os.listdir(folder):
        ffpath = os.path.join(folder, ffname)
        if os.path.isfile(ffpath):
            if is_dicom(ffpath):
                dicom_list.append(ffpath)
        elif os.path.isdir(ffpath) and recursively:
            dicom_list.extend(find_dicom_in_folder(ffpath, recursively=True))
    return dicom_list


def write_dicom(pixel_array, filename, ds_copy, ds_ori, volume_number,
                series_number, sop_id):
    """Write data in dicom file and copy the header from different dicoms.

    :param pixel_array: data to write in a dicom
    :param filename: file name for the dicom
    :param ds_copy: pydicom object of the dicom to copy info from
    :param ds_ori: pydicom object of the dicom where the array comes from
    :param volume_number: numero of volume being processed
    :param series_number: number of the series being written
    :param sop_id: SOPID for the dicom
    :return: None
    """
    # Set to zero negatives values in the image:
    pixel_array[pixel_array < 0] = 0

    # Set the DICOM dataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = 'Secondary Capture Image Storage'
    file_meta.MediaStorageSOPInstanceUID = ds_ori.SOPInstanceUID
    file_meta.ImplementationClassUID = ds_ori.SOPClassUID
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble="\0" * 128)

    # Copy the tag from the original DICOM
    for tag, value in list(ds_ori.items()):
        if tag != ds_ori.data_element("PixelData").tag:
            ds[tag] = value

    # Other tags to set
    ds.SeriesNumber = series_number
    ds.SeriesDescription = ds_ori.SeriesDescription + ' fromNifti'
    sop_uid = sop_id + str(datetime.now()).replace('-', '')\
                                          .replace(':', '')\
                                          .replace('.', '')\
                                          .replace(' ', '')
    ds.SOPInstanceUID = sop_uid[:-1]
    ds.ProtocolName = ds_ori.ProtocolName
    ds.InstanceNumber = volume_number + 1

    # Copy from T2 the orientation tags:
    ds.PatientPosition = ds_copy.PatientPosition
    ds[0x18, 0x50] = ds_copy[0x18, 0x50]  # Slice Thicknes
    ds[0x18, 0x88] = ds_copy[0x18, 0x88]  # Spacing Between Slices
    ds[0x18, 0x1312] = ds_copy[0x18, 0x1312]  # In-plane Phase Encoding
    ds[0x20, 0x32] = ds_copy[0x20, 0x32]  # Image Position
    ds[0x20, 0x37] = ds_copy[0x20, 0x37]  # Image Orientation
    ds[0x20, 0x1041] = ds_copy[0x20, 0x1041]  # Slice Location
    ds[0x28, 0x10] = ds_copy[0x28, 0x10]  # rows
    ds[0x28, 0x11] = ds_copy[0x28, 0x11]  # columns
    ds[0x28, 0x30] = ds_copy[0x28, 0x30]  # Pixel spacing

    # Set the Image pixel array
    if pixel_array.dtype != np.uint16:
        pixel_array = pixel_array.astype(np.uint16)
    ds.PixelData = pixel_array.tostring()

    # Save the image
    ds.save_as(filename)


def convert_nifti_2_dicoms(nifti_path, dicom_targets, dicom_source,
                           output_folder, label=None):
    """Convert 4D niftis into DICOM files (2D dicoms).

    :param nifti_path: path to the nifti file
    :param dicom_target: list of dicom files from the target
     for the registration for header info
    :param dicom_source: one dicom file from the source
     for the registration for header info
    :param output_folder: folder where the DICOM files will be saved
    :param label: name for the output dicom files
    :return: None
    """
    if not os.path.isfile(nifti_path):
        raise XnatUtilsError("NIFTI File %s not found." % nifti_path)
    # Load image from NIFTI
    f_img = nib.load(nifti_path)
    f_img_data = f_img.get_data()

    # Load dicom headers
    if not os.path.isfile(dicom_source):
        raise XnatUtilsError("DICOM File %s not found ." % dicom_source)
    adc_dcm_obj = pydicom.read_file(dicom_source)

    # Make output_folder:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Series Number and SOP UID
    ti = time.time()
    series_number = 86532 + int(str(ti)[2:4]) + int(str(ti)[4:6])
    sop_id = adc_dcm_obj.SOPInstanceUID.split('.')
    sop_id = '.'.join(sop_id[:-1]) + '.'

    # Sort the DICOM T2 to create the ADC registered DICOMs
    dcm_obj_sorted = dict()
    for dcm_file in dicom_targets:
        # Load dicom headers
        if not os.path.isfile(dcm_file):
            raise XnatUtilsError("DICOM File %s not found." % dcm_file)
        t2_dcm_obj = pydicom.read_file(dcm_file)
        dcm_obj_sorted[t2_dcm_obj.InstanceNumber] = t2_dcm_obj

    for vol_i in range(f_img_data.shape[2]):
        if f_img_data.shape[2] > 100:
            filename = os.path.join(output_folder, '%s_%03d.dcm' % (label,
                                                                    vol_i + 1))
        elif f_img_data.shape[2] > 10:
            filename = os.path.join(output_folder, '%s_%02d.dcm' % (label,
                                                                    vol_i + 1))

        else:
            filename = os.path.join(output_folder, '%s_%d.dcm' % (label,
                                                                  vol_i + 1))

        write_dicom(np.rot90(f_img_data[:, :, vol_i]), filename,
                    dcm_obj_sorted[vol_i + 1], adc_dcm_obj, vol_i,
                    series_number, sop_id)


# DEPRECATED Methods still in used in different Spiders
#======================================================
# It will need to be removed when the spiders are updated
def list_experiments(intf, projectid=None, subjectid=None):
    """
    Deprecated method to list all the experiments that you have access to.
     Or, alternatively, list the experiments in a single project
     (and single subject) based on passed project ID (/subject ID)

    :param intf: pyxnat.Interface object
    :param projectid: ID of a project on XNAT
    :param subjectid: ID/label of a subject
    :return: List of experiments
    """
    print('Warning: Deprecated method. Use InterfaceTemp.get_sessions().')
    if projectid and subjectid:
        post_uri = SESSIONS_URI.format(project=projectid, subject=subjectid)
    elif projectid is None and subjectid is None:
        post_uri = ALL_SESS_URI
    elif projectid and subjectid is None:
        post_uri = ALL_SESS_PROJ_URI.format(project=projectid)
    else:
        return None

    post_uri += EXPERIMENT_POST_URI
    experiment_list = intf._get_json(post_uri)

    for exp in experiment_list:
        if projectid:
            # Override the project returned to be the one we queried
            # and add others for convenience
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
    print('Warning: Deprecated method. Use InterfaceTemp.get_session_resources().')
    post_uri = SE_RESOURCES_URI.format(project=projectid, subject=subjectid,
                                       session=experimentid)
    resource_list = intf._get_json(post_uri)
    return resource_list


# TODO: BenM/xnatutils refactor/Why isn't an intf instance passed to this method?
def download_Scan(Outputdirectory, projectName, subject, experiment, scan,
                  resource_list, all_resources=0):
    """
    Deprecated method to download resources from a scan given a scan ID

    :param Outputdirectory: Directory to download the data to
    :param projectName: XNAT project ID
    :param subject: XNAT subject ID/label
    :param experiment: XNAT session ID/label
    :param scan: Scan ID to download from
    :param resource_list: List of resources to download data from.
    :param all_resources: If 1, download from all resources for scan object,
                          otherwise use the list.
    :return: None

    """
    print('Warning: Deprecated method. Use download_file(), download_files(), \
download_file_from_obj(), or download_files_from_obj().')
    msg = 'Download resources from %s / %s / %s / %s'
    print(msg % (projectName, subject, experiment, scan))

    # Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, basestring):
        resource_list = [resource_list]
    else:
        raise XnatUtilsError("INPUTS ERROR: Check the format of the list of \
resources in download_Scan function. Not a list.")

    with get_interface() as intf:
        SCAN = intf.select_scan(projectName, subject, experiment, scan)
        if SCAN.exists():
            if SCAN.attrs.get('quality') != 'unusable':
                dl_good_resources_scan(SCAN, resource_list, Outputdirectory,
                                       all_resources)
            else:
                print('DOWNLOAD WARNING: Scan unusable!')
        else:
            err = '%s: xnat object for <%s> does not exist on XNAT.'
            raise XnatAccessError(err % ('download_Scan', intf))

    print('================================================================\n')


# from a list of scantype given, Download the resources
def download_ScanType(Outputdirectory, projectName, subject, experiment,
                      List_scantype, resource_list, all_resources=0):
    """
    Deprecated method to download resources from a scan given scan types

    :param Outputdirectory: Directory to download the data to
    :param projectName: XNAT project ID
    :param subject: XNAT subject ID/label
    :param experiment: XNAT session ID/label
    :param List_scantype: List of scan types to download resources from.
    :param resource_list: List of resources to download data from.
    :param all_resources: If 1, download from all resources for scan object,
                          otherwise use the list.
    :return: None

    """
    print('Warning: Deprecated method.')
    msg = 'Download resources from %s / %s / %s and the scan types %s'
    print(msg % (projectName, subject, experiment, str(List_scantype)))

    # Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, basestring):
        resource_list = [resource_list]
    else:
        raise XnatUtilsError("INPUTS ERROR: Check the format of the list of \
resources in download_ScanType function. Not a list.")

    # check list of SD:
    if isinstance(List_scantype, list):
        pass
    elif isinstance(List_scantype, basestring):
        List_scantype = [List_scantype]
    else:
        raise XnatUtilsError("INPUTS ERROR: Check the format of the list of \
scantypes in download_ScanType function. Not a list.")

    with get_interface() as intf:
        for scan in intf.get_scans(projectName, subject, experiment):
            if scan['type'] in List_scantype:
                if scan['quality'] != 'unusable':
                    SCAN = intf.select_scan(projectName, subject, experiment, scan['ID'])
                    dl_good_resources_scan(SCAN, resource_list,
                                           Outputdirectory, all_resources)
                else:
                    print('DOWNLOAD WARNING: Scan unusable!')

    print('================================================================\n')


def download_ScanSeriesDescription(Outputdirectory, projectName, subject,
                                   experiment, List_scanSD, resource_list,
                                   all_resources=0):
    """
    Deprecated method to download resources from a scan given a series
     description, rather than a scan ID

    :param Outputdirectory: Directory to download the data to
    :param projectName: XNAT project ID
    :param subject: XNAT subject ID/label
    :param experiment: XNAT session ID/label
    :param List_scanSD: List of series descriptions to download resources from.
    :param resource_list: List of resources to download data from.
    :param all_resources: If 1, download from all resources for scan object,
                          otherwise use the list.
    :return: None

    """
    print('Warning: Deprecated method.')
    msg = 'Download resources from %s / %s / %s and the series description %s'
    print(msg % (projectName, subject, experiment, str(List_scanSD)))

    # Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, basestring):
        resource_list = [resource_list]
    else:
        raise XnatUtilsError("INPUTS ERROR: Check the format of the list of \
resources in download_ScanSeriesDescription function. Not a list.")

    # check list of SD:
    if isinstance(List_scanSD, list):
        pass
    elif isinstance(List_scanSD, basestring):
        List_scanSD = [List_scanSD]
    else:
        raise XnatUtilsError("INPUTS ERROR: Check the format of the list of \
series_description in download_ScanSeriesDescription function. Not a list.")

    with get_interface() as intf:
        for scan in intf.get_scans(projectName, subject, experiment):
            SCAN = intf.select_scan(projectName, subject, experiment, scan['ID'])
            if SCAN.attrs.get('series_description') in List_scanSD:
                if scan['quality'] != 'unusable':
                    dl_good_resources_scan(SCAN, resource_list,
                                           Outputdirectory, all_resources)
                else:
                    print('DOWNLOAD WARNING: Scan unusable!')

    print('================================================================\n')


def download_Assessor(Outputdirectory, assessor_label, resource_list,
                      all_resources=0):
    """
    Deprecated method to download resources from a specific assessor.

    :param Outputdirectory: Directory to download data to
    :param assessor_label: The label of the assessor to download from
    :param resource_list: list of resource(s) to download
    :param all_resources: if 1, download all of the resources.
    :return: None

    """
    print('Warning: Deprecated method.')
    print('Download resources from process %s' % assessor_label)

    # Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, basestring):
        resource_list = [resource_list]
    else:
        raise XnatUtilsError("INPUTS ERROR: Check the format of the list of \
resources in the download_Assessor function. Not a list.")

    with get_interface() as intf:
        ASSESSOR = select_assessor(intf, assessor_label)
        dl_good_resources_assessor(ASSESSOR, resource_list, Outputdirectory,
                                   all_resources)

    print('================================================================\n')


# from an assessor type, download the resources :
def download_AssessorType(Outputdirectory, projectName, subject, experiment,
                          List_process_type, resource_list, all_resources=0):
    """
    Deprecated method to download an assessor by the proctype.
     Can download a resource, or all resources

    :param Outputdirectory: Directory to download data to
    :param projectName: XNAT project ID
    :param subject: XNAT project subject ID/label
    :param experiment: XNAT project session ID/label
    :param List_process_type: List of process type(s)to download from
    :param resource_list: List of resources to download from each proctype
    :param all_resources: if 1, download from all resources,
                          otherwise use resource_list
    :return: None

    """
    print('Warning: Deprecated method.')
    msg = 'Download resources from %s / %s / %s and the process %s'
    print(msg % (projectName, subject, experiment, str(List_process_type)))

    # Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, basestring):
        resource_list = [resource_list]
    else:
        raise XnatUtilsError("INPUTS ERROR: Check the format of the list of \
resources in the download_AssessorType function. Not a list.")

    # Check input for subjects_exps_list :
    if isinstance(List_process_type, list):
        pass
    elif isinstance(List_process_type, basestring):
        List_process_type = [List_process_type]
    else:
        raise XnatUtilsError("INPUTS ERROR: Check the format of the list of \
process type in the download_AssessorType function. Not a list.")

    # if FreeSurfer in the list, change it to FS
    List_process_type = [process_type.replace('FreeSurfer', 'FS')
                         for process_type in List_process_type]

    with get_interface() as intf:
        for assessor in list_assessors(intf, projectName, subject, experiment):
            for proc_type in List_process_type:
                if proc_type == assessor['label'].split('-x-')[-1]:
                    ASSESSOR = select_assessor(intf, assessor['label'])
                    dl_good_resources_assessor(ASSESSOR, resource_list,
                                               Outputdirectory, all_resources)

    print('================================================================\n')


def dl_good_resources_scan(Scan, resource_list, Outputdirectory,
                           all_resources):
    """
    Deprecated method to download "good" resources from a scan

    :param Scan: pyxnat EObject of the scan
    :param resource_list: List of resource names to download from for the scan
    :param Outputdirectory: Directory to download all of the data from
    :param all_resources: Override the list and download all the files from
     all the resources if true, otherwise use the list
    :return: None

    """
    print('Warning: Deprecated method.')
    for Resource in resource_list:
        resourceOK = 0
        if Scan.resource(Resource).exists():
            resourceOK = 1
        elif Scan.resource(Resource.upper()).exists():
            Resource = Resource.upper()
            resourceOK = 1
        elif Scan.resource(Resource.lower()).exists():
            Resource = Resource.lower()
            resourceOK = 1

        if resourceOK and all_resources:
            download_all_resources(Scan.resource(Resource), Outputdirectory)
        elif resourceOK and not all_resources:
            dl, _ = download_biggest_resources(Scan.resource(Resource),
                                               Outputdirectory)
            if not dl:
                print('ERROR: Download failed, Size for the resource is zero.')


def dl_good_resources_assessor(Assessor, resource_list, Outputdirectory,
                               all_resources):
    """
    Deprecated method to download all "good" resources from an assessor

    :param Assessor: pyxnat EObject of the assessor
    :param resource_list: List of resources labels to download resources from
    :param Outputdirectory: directory where data downloaded
    :param all_resources: If true, download from all resources,
                          otherwise only the specified ones.
    :return: None

    """
    print('Warning: Deprecated method.')
    for Resource in resource_list:
        resourceOK = 0
        if Assessor.out_resource(Resource).exists():
            resourceOK = 1
        elif Assessor.out_resource(Resource.upper()).exists():
            Resource = Resource.upper()
            resourceOK = 1
        elif Assessor.out_resource(Resource.lower()).exists():
            Resource = Resource.lower()
            resourceOK = 1

        if resourceOK and all_resources:
            download_all_resources(Assessor.out_resource(Resource),
                                   Outputdirectory)
        elif resourceOK and not all_resources:
            dl, _ = download_biggest_resources(Assessor.out_resource(Resource),
                                               Outputdirectory)
            if not dl:
                print('ERROR: Download failed. Size for the resource is zero.')


def download_biggest_resources(Resource, directory, filename='0'):
    """
    Deprecated method to download the biggest file from a resource

    :param Resource: pyxnat EObject to download the biggest file from
    :param directory: Download directory
    :param filename: Filename to override the current name of. If changed,
     the value of filename will be the filename as downlaoded.
    :return: 1 if download worked and then the full path to the file,
             0 and nan otherwise.

    """
    print('Warning: Deprecated method. Use download_biggest_file() or \
download_biggest_file_from_obj().')
    if os.path.exists(directory):
        number = 0
        Bigger_file_size = 0
        for index, fname in enumerate(Resource.files().get()[:]):
            size = int(Resource.file(fname).size())
            if Bigger_file_size < size:
                Bigger_file_size = size
                number = index

        if Bigger_file_size == 0:
            return 0, 'nan'
        else:
            Input_res_label_fname = Resource.files().get()[number]
            if filename == '0':
                DLFileName = os.path.join(directory, Input_res_label_fname)
            else:
                DLFileName = os.path.join(directory, filename)
            Resource.file(Input_res_label_fname).get(DLFileName)
            return 1, str(DLFileName)
    else:
        msg = 'ERROR in download_biggest_resources: Folder %s does not exist.'
        print(msg % directory)


def download_all_resources(Resource, directory):
    """
    Deprecated method from a pyxnat EObject, download all of the files in it

    :param Resource: pyxnat EObject to download resources from
    :param directory: Directory to download all of the files to
    :return: None

    """
    print('Warning: Deprecated method. Use download_files() or \
download_files_from_obj().')
    unzip_cmd = 'unzip -d %s %s > /dev/null'
    if os.path.exists(directory):
        # if more than one file:
        if len(Resource.files().get()) > 1:
            # create a dir with the resourcename:
            rlabel = Resource.label()
            Outputdir = os.path.join(directory, rlabel)
            if not os.path.exists(Outputdir):
                os.mkdir(Outputdir)
            print('   ->Downloading all resources as a zip')
            Resource.get(Outputdir, extract=False)
            print('   ->Unzipping ...')
            fpath = os.path.join(Outputdir, '%s.zip' % rlabel)
            os.system(unzip_cmd % (Outputdir, fpath))
        else:
            print('   ->Downloading resource for %s' % Resource.label())
            Input_res_label_fname = Resource.files().get()[0]
            fpath = os.path.join(directory, Input_res_label_fname)
            Resource.file(Input_res_label_fname).get(fpath)
            if os.path.join(directory, Input_res_label_fname)[-3:] == 'zip':
                print('   -> Unzipping ...')
                os.system(unzip_cmd % (directory, fpath))
    else:
        msg = 'ERROR in download_all_resources: Folder %s does not exist.'
        print(msg % directory)


def upload_all_resources(Resource, directory):
    """
    Deprecated method to upload all of the files in a directory to a resource

    :param Resource: pyxnat EObject of the resource to put the files
    :param directory: Directory to scrape for files to upload to the resource
    :return: None

    """
    print('Warning: Deprecated method. Use either upload_files(), \
upload_files_to_obj(), upload_folder(), or upload_folder_to_obj().')
    if os.path.exists(directory):
        if not Resource.exists():
            Resource.create()
        # for each files in this folderl, Upload files in the resource :
        Resource_files_list = os.listdir(directory)
        # for each folder=resource in the assessor directory
        # more than 2 files, use the zip from XNAT
        if len(Resource_files_list) > 2:
            upload_zip(directory, Resource)
        # One or two file, let just upload them:
        else:
            for filename in Resource_files_list:
                # if it's a folder, zip it and upload it
                if os.path.isdir(filename):
                    upload_zip(filename, os.path.join(directory, filename))
                elif filename.lower().endswith('.zip'):
                    Resource.put_zip(os.path.join(directory, filename),
                                     overwrite=True, extract=True)
                else:
                    # upload the file
                    fpath = os.path.join(directory, filename)
                    Resource.file(filename).put(fpath, overwrite=True)
    else:
        msg = 'ERROR in upload_all_resources: Folder %s does not exist.'
        print(msg % directory)


def upload_zip(Resource, directory):
    """
    Deprecated method to upload a folder to XNAT as a zip file and then unzips
      when put. The label of the resource will be the folder name

    :param Resource: pyxnat EObject of the resource to upload to
    :param directory: Full path to the directory to upload
    :return: None

    """
    Upload_folder_to_resource(Resource, directory)


def download_resource_assessor(directory, intf, project, subject, experiment,
                               assessor_label, resources_list, quiet):
    """
    Deprecated method to download resource(s) from an assessor.

    :param directory: The directory to download data to
    :param intf: pyxnat Interface object
    :param project: Project ID on XNAT
    :param subject: Subject ID/label on XNAT
    :param experiment: Session ID/label on XNAT
    :param assessor_label: Assessor ID/label on XNAT
    :param resources_list: list of resource(s) to download from the assessor
    :param quiet: Suppress print statements
    :return: None

    """
    print('Warning: Deprecated method. Use download_files() or \
download_files_from_obj().')
    if not quiet:
        print('    +Process: %s' % assessor_label)

    assessor = select_assessor(intf, assessor_label)
    if not assessor.exists():
        print('      !!WARNING: No assessor with the ID selected.')
        return

    if 'fMRIQA' in assessor_label:
        labels = assessor_label.split('-x-')
        SCAN = intf.select_scan(project, subject, experiment, labels[3])
        SD = SCAN.attrs.get('series_description')
        SD = SD.replace('/', '_')
        SD = SD.replace(" ", "")

        if SD != '':
            directory = '%s-x-%s' % (directory, SD)

    if not os.path.exists(directory):
        os.mkdir(directory)

    # all resources
    if resources_list[0] == 'all':
        resources_list = intf.get_assessor_out_resources(project,
                                                         subject,
                                                         experiment,
                                                         assessor_label)
        for resource in resources_list:
            Resource = intf.select_assessor_resource(project,
                                                     subject,
                                                     experiment,
                                                     assessor_label,
                                                     resource['label'])
            if Resource.exists():
                if not quiet:
                    print('      *download resource %s' % resource['label'])

                assessor_real_type = assessor_label.split('-x-')[-1]
                if 'FS' in assessor_real_type:
                    # make a directory for each of the resource
                    Res_path = os.path.join(directory, resource['label'])
                    if not os.path.exists(Res_path):
                        os.mkdir(Res_path)
                    Resource.get(Res_path, extract=False)
                else:
                    if len(Resource.files().get()) > 0:
                        # make a directory for each of the resource
                        Res_path = os.path.join(directory, resource['label'])
                        if not os.path.exists(Res_path):
                            os.mkdir(Res_path)

                        for fname in Resource.files().get()[:]:
                            Resfile = Resource.file(fname)
                            local_fname = os.path.join(Res_path, fname)
                            Resfile.get(local_fname)
                    else:
                        print("\t    *ERROR : The size of the resource is 0.")

    # resources in the options
    else:
        for resource in resources_list:
            Resource = intf.select_assessor_resource(project,
                                                     subject,
                                                     experiment,
                                                     assessor_label,
                                                     resource)
            if Resource.exists():
                if not quiet:
                    print('      *download resource %s' % resource)

                assessor_real_type = assessor_label.split('-x-')[-1]
                if 'FS' in assessor_real_type:
                    # make a directory for each of the resource
                    Res_path = os.path.join(directory, resource)
                    if not os.path.exists(Res_path):
                        os.mkdir(Res_path)

                    Resource.get(Res_path, extract=False)
                else:
                    if len(Resource.files().get()) > 0:
                        # make a directory for each of the resource
                        Res_path = os.path.join(directory, resource)
                        if not os.path.exists(Res_path):
                            os.mkdir(Res_path)

                        for fname in Resource.files().get()[:]:
                            Resfile = Resource.file(fname)
                            local_fname = os.path.join(Res_path, fname)
                            Resfile.get(local_fname)
                    else:
                        print("      !!ERROR : The size of the resource is 0.")
            else:
                msg = '      !!WARNING : no resource %s for this assessor.'
                print(msg % resource)
    print('\n')


def Upload_folder_to_resource(resourceObj, directory):
    """
    Deprecated method to upload a folder to XNAT as a zip file and then unzips
     when put. The label of the resource will be the folder name

    :param resourceObj: pyxnat EObject of the resource to upload to
    :param directory: Full path to the directory to upload
    :return: None

    """
    print('Warning: Deprecated method. Use either upload_folder() or \
upload_folder_to_obj().')
    filenameZip = '%s.zip' % resourceObj.label()
    initDir = os.getcwd()
    # Zip all the files in the directory
    os.chdir(directory)
    os.system('zip -r %s *' % filenameZip)
    # upload
    zip_path = os.path.join(directory, filenameZip)
    resourceObj.put_zip(zip_path, overwrite=True, extract=True)
    # return to the initial directory:
    os.chdir(initDir)


def Download_resource_to_folder(Resource, directory):
    """
    Deprecated method to download all of the files for a resource to a
     directory with basename == resource label

    :param Resource: pyxnat EObject of the resource to download files from
    :param directory: The directory to download the data to.
     The resource label name is appeneded as basename
    :return: None

    """
    print('Warning: Deprecated method. Use either download_files() or \
download_files_from_obj().')
    Res_path = os.path.join(directory, Resource.label())
    if os.path.exists(Res_path):
        os.remove(Res_path)
    Resource.get(directory, extract=True)
