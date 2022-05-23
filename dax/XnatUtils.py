""" XnatUtils contains functions to interface with XNAT using Pyxnat."""


import getpass
import os
import re
import shutil
from datetime import datetime
import fnmatch
import traceback
import time
import logging
import pandas as pd
import xml.etree.cElementTree as ET
from lxml import etree
from pyxnat import Interface
from pyxnat.core.errors import DatabaseError
import requests
import json

from . import utilities
from .utilities import decode_url_json_string
from .task import (JOB_FAILED, JOB_RUNNING, READY_TO_UPLOAD)
from .errors import (XnatUtilsError, XnatAuthentificationError)
from .dax_settings import (DAX_Settings, DAX_Netrc, DEFAULT_DATATYPE,
                           DEFAULT_FS_DATATYPE)

__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ["InterfaceTemp", "AssessorHandler", "SpiderProcessHandler",
           "CachedImageSession", "CachedImageScan", "CachedImageAssessor",
           "CachedResource"]
DAX_SETTINGS = DAX_Settings()
NS = {'xnat': 'http://nrg.wustl.edu/xnat',
      'proc': 'http://nrg.wustl.edu/proc',
      'fs': 'http://nrg.wustl.edu/fs',
      'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

LOGGER = logging.getLogger('dax')

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
{fstype}/validation/status,{fstype}/validation/notes&xsiType={fstype}'''
ASSESSOR_PR_POST_URI = '''?columns=ID,label,URI,xsiType,project,\
xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,\
xnat:imagesessiondata/label,{pstype}/procstatus,{pstype}/proctype,\
{pstype}/validation/status,{pstype}/validation/notes&xsiType={pstype}'''
ASSESSOR_FS_PROJ_POST_URI = '''?project={project}&xsiType={fstype}&columns=ID,\
label,URI,xsiType,project,xnat:imagesessiondata/subject_id,subject_label,\
xnat:imagesessiondata/id,xnat:imagesessiondata/label,URI,{fstype}/procstatus,\
{fstype}/validation/status,{fstype}/validation/notes,{fstype}/procversion,{fstype}/jobstartdate,\
{fstype}/memused,{fstype}/walltimeused,{fstype}/jobid,{fstype}/jobnode,\
{fstype}/out/file/label'''
ASSESSOR_PR_PROJ_POST_URI = '''?project={project}&xsiType={pstype}&columns=ID,\
label,URI,xsiType,project,xnat:imagesessiondata/subject_id,\
xnat:imagesessiondata/id,xnat:imagesessiondata/label,{pstype}/procstatus,\
{pstype}/proctype,{pstype}/validation/status,{pstype}/validation/notes,{pstype}/procversion,\
{pstype}/jobstartdate,{pstype}/memused,{pstype}/walltimeused,\
{pstype}/dax_docker_version,{pstype}/dax_version,{pstype}/dax_version_hash,\
{pstype}/jobid,{pstype}/jobnode,{pstype}/inputs,{pstype}/out/file/label'''
EXPERIMENT_POST_URI = '''?columns=ID,URI,subject_label,subject_ID,modality,\
project,date,xsiType,label,xnat:subjectdata/meta/last_modified'''


SGP_URI = '/REST/subjects?xsiType=xnat:subjectdata\
&columns=\
project,\
label,\
proc:subjgenprocdata/label,\
proc:subjgenprocdata/procstatus,\
proc:subjgenprocdata/proctype,\
proc:subjgenprocdata/validation/status,\
proc:subjgenprocdata/inputs,\
last_modified&project={}'

SGP_RENAME = {
    'project': 'PROJECT',
    'label': 'SUBJECT',
    'proc:subjgenprocdata/label': 'ASSR',
    'proc:subjgenprocdata/procstatus': 'PROCSTATUS',
    'proc:subjgenprocdata/proctype': 'PROCTYPE',
    'proc:subjgenprocdata/validation/status': 'QCSTATUS',
    'xsiType': 'XSITYPE',
    'proc:subjgenprocdata/inputs': 'INPUTS'}

ASSR_URI = '/REST/experiments?xsiType=xnat:imagesessiondata\
&columns=\
project,\
subject_label,\
session_label,\
session_type,\
xnat:imagesessiondata/acquisition_site,\
xnat:imagesessiondata/date,\
xnat:imagesessiondata/label,\
proc:genprocdata/label,\
proc:genprocdata/procstatus,\
proc:genprocdata/proctype,\
proc:genprocdata/validation/status,\
last_modified,\
proc:genprocdata/inputs'

ASSR_RENAME = {
    'project': 'PROJECT',
    'subject_label': 'SUBJECT',
    'session_label': 'SESSION',
    'session_type': 'SESSTYPE',
    'xnat:imagesessiondata/date': 'DATE',
    'xnat:imagesessiondata/acquisition_site': 'SITE',
    'proc:genprocdata/label': 'ASSR',
    'proc:genprocdata/procstatus': 'PROCSTATUS',
    'proc:genprocdata/proctype': 'PROCTYPE',
    'proc:genprocdata/validation/status': 'QCSTATUS',
    'xsiType': 'XSITYPE',
    'proc:genprocdata/inputs': 'INPUTS'}

SCAN_URI = '/REST/experiments?xsiType=xnat:imagesessiondata\
&columns=\
project,\
subject_label,\
session_label,\
session_type,\
xnat:imagesessiondata/date,\
xnat:imagesessiondata/label,\
xnat:imagesessiondata/acquisition_site,\
xnat:imagescandata/id,\
xnat:imagescandata/type,\
xnat:imagescandata/quality'

SCAN_RENAME = {
    'project': 'PROJECT',
    'subject_label': 'SUBJECT',
    'session_label': 'SESSION',
    'session_type': 'SESSTYPE',
    'xnat:imagesessiondata/date': 'DATE',
    'xnat:imagesessiondata/acquisition_site': 'SITE',
    'xnat:imagescandata/id': 'SCANID',
    'xnat:imagescandata/type': 'SCANTYPE',
    'xnat:imagescandata/quality': 'QUALITY',
    'xsiType': 'XSITYPE'}


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
    R_XPATH = '{xpath}/resources/{resource}'
    AR_XPATH = '%s/out/resources/{resource}' % A_XPATH

    def __init__(self, xnat_host=None, xnat_user=None, xnat_pass=None,
                 smtp_host=None,
                 timeout_emails=None,
                 xnat_timeout=300,
                 xnat_retries=4,
                 xnat_wait=600):

        """Entry point for the InterfaceTemp class.

        :param xnat_host: XNAT Host url
        :param xnat_user: XNAT User ID
        :param xnat_pass: XNAT Password
        :return: None

        """
        # Host
        self.host = xnat_host
        self.user = xnat_user
        self.pwd = xnat_pass
        self.smtp_host = smtp_host
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

        self.xnat_timeout = xnat_timeout
        self.xnat_retries = xnat_retries
        self.xnat_wait = xnat_wait
        self.timeout_emails = timeout_emails

        self.authenticate()

    def __enter__(self, xnat_host=None, xnat_user=None, xnat_pass=None):
        """Enter method for with statement."""
        return self

    def __exit__(self, type, value, traceback):
        """Exit method for with statement."""
        self.disconnect()

    def connect(self):
        """Connect to XNAT."""
        super(InterfaceTemp, self).__init__(server=self.host,
                                            user=self.user,
                                            password=self.pwd)

    def disconnect(self):
        super(InterfaceTemp, self).disconnect()

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
            LOGGER.error(e)
            raise XnatAuthentificationError(self.host, self.user)

    def _exec(self, uri, method='GET', body=None, headers=None,
              force_preemptive_auth=False, **kwargs):

        result = None
        LOGGER.debug('_exec:{}:{}'.format(method, uri))

        try:
            result = super()._exec(
                    uri, method, body, headers, force_preemptive_auth,
                timeout=self.xnat_timeout, **kwargs)
        except (requests.Timeout, requests.ConnectionError):
            _err = traceback.format_exc()
            if self.timeout_emails:
                LOGGER.warn('XNAT timeout, emailing admin')

                # email the exception
                _msg = '{}\n\n'.format(uri)
                _msg += 'ERROR:{}'.format(_err)
                _host = self.smtp_host
                _to = self.timeout_emails
                _subj = 'ERROR:XNAT timeout'
                utilities.send_email_netrc(_host, _to, _subj, _msg)
            else:
                LOGGER.warn('XNAT timeout, email disabled:{}'.format(_err))

            # Retries
            for i in range(self.xnat_retries):
                # First we sleep
                LOGGER.debug('retry in {} secs'.format(self.xnat_wait))
                time.sleep(self.xnat_wait)

                # Then we try again
                LOGGER.debug('retry {} of {}'.format(
                    str(i + 1), str(self.xnat_retries)))
                LOGGER.debug('_exec:{}:{}'.format(method, uri))
                try:
                    result = super()._exec(
                        uri, method, body, headers, force_preemptive_auth,
                        timeout=self.xnat_timeout, **kwargs)
                    break
                except (requests.Timeout, requests.ConnectionError):
                    # Do nothing
                    LOGGER.debug('retry {} timed out'.format(str(i + 1)))
                    pass
        except DatabaseError as err:
            LOGGER.error(err)
            raise

        if result is None:
            # None of the retries worked
            raise XnatUtilsError('XNAT timeout')

        return result

    # TODO: string.format wants well-formed strings and will, for example,
    # throw a KeyError if any named variables in the format string are missing.
    # Put proper validation in place for these methods

    def get_project_path(self, project):
        """Given project (string),
           returns project path (string)
        """
        return InterfaceTemp.P_XPATH.format(project=project)

    def select_project(self, project):
        """Given project (string),
           returns project object
        """
        xpath = self.get_project_path(project)
        return self.select(xpath)

    def get_subject_path(self, project, subject):
        """Given project, subject (strings),
           returns subject path (string)
        """
        return InterfaceTemp.S_XPATH.format(project=project,
                                            subject=subject)

    def select_subject(self, project, subject):
        """Given project, subject (strings),
           returns subject object
        """
        xpath = self.get_subject_path(project, subject)
        return self.select(xpath)

    def get_experiment_path(self, project, subject, session):
        """Given project, subject, session (strings),
           returns session path (string)
        """
        return InterfaceTemp.E_XPATH.format(project=project,
                                            subject=subject,
                                            session=session)

    def select_experiment(self, project, subject, session):
        """Given project, subject, session (strings),
           returns session (experiment object)
           Same as select_session
        """
        xpath = self.get_experiment_path(project, subject, session)
        return self.select(xpath)

    def select_session(self, project, subject, session):
        """Given project, subject, session (strings),
           returns session (experiment object)
           Same as select_experiment
        """
        xpath = self.get_experiment_path(project, subject, session)
        return self.select(xpath)

    def get_scan_path(self, project, subject, session, scan):
        """Given project, subject, session, scan (strings),
           returns scan path (string)
        """
        return InterfaceTemp.C_XPATH.format(project=project,
                                            subject=subject,
                                            session=session,
                                            scan=scan)

    def select_scan(self, project, subject, session, scan):
        """Given project, subject, session, scan (strings),
           returns scan object
        """
        xpath = self.get_scan_path(project, subject, session, scan)
        return self.select(xpath)

    def get_scan_resource_path(self,
                               project, subject, session, scan, resource):
        """Given project, subject, session, scan, resource (strings),
           returns scan resource path (string)
        """
        return InterfaceTemp.CR_XPATH.format(project=project,
                                             subject=subject,
                                             session=session,
                                             scan=scan,
                                             resource=resource)

    def select_scan_resource(self, project, subject, session, scan, resource):
        """Given project, subject, session, scan, resource (strings),
           returns scan resource object
        """
        xpath = self.get_scan_resource_path(
            project, subject, session, scan, resource)
        return self.select(xpath)

    def get_assessor_path(self, project, subject, session, assessor):
        """Given project, subject, session, assessor (strings),
           returns assessor path (string)
        """
        return InterfaceTemp.A_XPATH.format(project=project,
                                            subject=subject,
                                            session=session,
                                            assessor=assessor)

    def get_sgp_assessor_path(self, project, subject, assessor):
        """Given project, subject, assessor (strings),
           returns assessor path (string)
        """
        return '/projects/{}/subjects/{}/assessors/{}'.format(
            project=project,
            subject=subject,
            assessor=assessor)

    def select_assessor(self, project, subject, session, assessor):
        """Given project, subject, session, assessor (strings),
           returns assessor object
        """
        xpath = self.get_assessor_path(project, subject, session, assessor)
        return self.select(xpath)

    def select_sgp_assessor(self, project, subject, assessor):
        """Given project, subject, assessor (strings),
           returns assessor object
        """
        xpath = self.get_sgp_assessor_path(project, subject, assessor)
        return self.select(xpath)

    def get_assessor_resource_path(
            self, project, subject, session, assessor, resource):
        """Given project, subject, session, assessor, resource (strings),
           returns assessor resource path (string)
        """
        return InterfaceTemp.AR_XPATH.format(project=project,
                                             subject=subject,
                                             session=session,
                                             assessor=assessor,
                                             resource=resource)

    def select_assessor_resource(
            self, project, subject, session, assessor, resource):
        """Given project, subject, session, assessor, resource (strings),
           returns assessor resource object
        """
        xpath = self.get_assessor_resource_path(
            project, subject, session, assessor, resource)
        return self.select(xpath)

    def select_all_projects(self, intf):
        return intf.select('/project/')

    def get_projects(self):
        return self._get_json(PROJECTS_URI)

    def get_project_scans(self, project_id, include_shared=True):
        """
        List all the scans that you have access to based on passed project.

        :param projectid (string): ID of a project on XNAT
        :param include_shared (boolean): include the shared data in this project
        :return: List of all the scans for the project
        """
        scans_dict = dict()

        # Get the sessions list to get the modality:
        session_list = self.get_sessions(project_id)
        sess_id2mod = dict(
            (sess['session_id'], [sess['handedness'],
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
                snew['series_description'] =\
                    scan['%s/series_description' % pfix]
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
                    snew['scan_description'] =\
                        scan['%s/series_description' % pfix]
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
                    snew['subject_id'] =\
                        scan['xnat:imagesessiondata/subject_id']
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

        return sorted(
            list(scans_dict.values()), key=lambda k: k['session_label'])

    def get_project_assessors(self, projectid):
        """
        List all the assessors that you have access to based on passed project.

        :param projectid (string): ID of a project on XNAT
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
                        anew['session_type'] =\
                            sess_id2mod[asse['session_ID']][1]
                        anew['session_id'] = asse['session_ID']
                        anew['session_label'] = asse['session_label']
                        anew['procstatus'] = asse['%s/procstatus' % pfix]
                        anew['qcstatus'] = asse['%s/validation/status' % pfix]
                        anew['proctype'] = 'FreeSurfer'

                        if len(asse['label'].rsplit('-x-FS')) > 1:
                            anew['proctype'] =\
                                (anew['proctype'] +
                                 asse['label'].rsplit('-x-FS')[1])

                        anew['version'] = asse.get('%s/procversion' % pfix)
                        anew['xsiType'] = asse['xsiType']
                        anew['jobid'] = asse.get('%s/jobid' % pfix)
                        anew['jobstartdate'] =\
                            asse.get('%s/jobstartdate' % pfix)
                        anew['memused'] = asse.get('%s/memused' % pfix)
                        anew['walltimeused'] =\
                            asse.get('%s/walltimeused' % pfix)
                        anew['jobnode'] = asse.get('%s/jobnode' % pfix)
                        anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                        anew['gender'] = sess_id2mod[asse['session_ID']][3]
                        anew['yob'] = sess_id2mod[asse['session_ID']][4]
                        anew['age'] = sess_id2mod[asse['session_ID']][5]
                        anew['last_modified'] =\
                            sess_id2mod[asse['session_ID']][6]
                        anew['last_updated'] =\
                            sess_id2mod[asse['session_ID']][7]
                        anew['resources'] = [asse['%s/out/file/label' % pfix]]
                        assessors_dict[key] = anew

        if has_genproc_datatypes(self):
            # Then add genProcData
            post_uri = SE_ARCHIVE_URI
            post_uri += ASSESSOR_PR_PROJ_POST_URI.format(
                project=projectid, pstype=DEFAULT_DATATYPE)
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
                        anew['subject_label'] =\
                            sess_id2mod[asse['session_ID']][0]
                        anew['session_type'] =\
                            sess_id2mod[asse['session_ID']][1]
                        anew['session_id'] = asse['session_ID']
                        anew['session_label'] = asse['session_label']
                        anew['procstatus'] = asse['%s/procstatus' % pfix]
                        anew['proctype'] = asse['%s/proctype' % pfix]
                        anew['qcstatus'] = asse['%s/validation/status' % pfix]
                        anew['qcnotes'] = asse['%s/validation/notes' % pfix]
                        anew['version'] = asse['%s/procversion' % pfix]
                        anew['xsiType'] = asse['xsiType']
                        anew['jobid'] = asse.get('%s/jobid' % pfix)
                        anew['jobnode'] = asse.get('%s/jobnode' % pfix)
                        anew['jobstartdate'] =\
                            asse.get('%s/jobstartdate' % pfix)
                        anew['memused'] = asse.get('%s/memused' % pfix)
                        anew['walltimeused'] =\
                            asse.get('%s/walltimeused' % pfix)
                        anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                        anew['gender'] = sess_id2mod[asse['session_ID']][3]
                        anew['yob'] = sess_id2mod[asse['session_ID']][4]
                        anew['age'] = sess_id2mod[asse['session_ID']][5]
                        anew['last_modified'] =\
                            sess_id2mod[asse['session_ID']][6]
                        anew['last_updated'] =\
                            sess_id2mod[asse['session_ID']][7]
                        anew['resources'] = [asse['%s/out/file/label' % pfix]]
                        anew['inputs'] = asse.get('%s/inputs' % pfix)
                        anew['dax_docker_version'] = asse['%s/dax_docker_version' % pfix]
                        anew['dax_version'] = asse['%s/dax_version' % pfix]
                        anew['dax_version_hash'] = asse['%s/dax_version_hash' % pfix]
                        assessors_dict[key] = anew

        return sorted(list(assessors_dict.values()), key=lambda k: k['label'])

    def get_subjects(self, project_id):
        """Given project_id (string), return list of subjects in project"""
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
        """Given project and subject (strings), return list of subject's resources"""
        post_uri = SU_RESOURCES_URI.format(
            project=project_id, subject=subject_id)
        resource_list = self._get_json(post_uri)
        return resource_list

    def get_resources(self, project_id):
        """Given project (string), return list of project's resources"""
        return self._get_json(P_RESOURCES_URI.format(project=project_id))

    def get_sessions(self, projectid=None, subjectid=None):
        """
        List all the sessions either:
            1) that you have access to
         or
            2) in a single project (and single subject) based on kargs

        :param projectid: ID of a project on XNAT
        :param subjectid: ID/label of a subject
        :return: List of sessions
        """
        type_list = []
        full_sess_list = []

        if projectid and subjectid:
            post_uri = SESSIONS_URI.format(
                project=projectid, subject=subjectid)
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

            if sess_type == 'proc:subjgenprocdata':
                # Ignore subject assessors
                continue

            if sess_type not in type_list:
                type_list.append(sess_type)

        # Get the subjects list to get the subject ID:
        subj_list = self.get_subjects(projectid)
        subj_id2lab = dict(
            (subj['ID'], [subj['handedness'], subj['gender'],
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
                sess['last_updated'] =\
                    sess.get('%s/original' % sess_type, None)
                sess['age'] = sess.get('%s/age' % sess_type, None)
                try:
                    sess['handedness'] = subj_id2lab[sess['subject_ID']][0]
                    sess['gender'] = subj_id2lab[sess['subject_ID']][1]
                    sess['yob'] = subj_id2lab[sess['subject_ID']][2]
                    sess['dob'] = subj_id2lab[sess['subject_ID']][3]
                except KeyError:
                    sess['handedness'] = 'UNK'
                    sess['gender'] = 'UNK'
                    sess['yob'] = 'UNK'
                    sess['dob'] = 'UNK'

            # Add sessions of this type to full list
            full_sess_list.extend(sess_list)

        # Return list sorted by label
        return sorted(full_sess_list, key=lambda k: k['session_label'])

    def get_sessions_minimal(self, projectid):
        """
        :param projectid: ID of a project on XNAT
        :return: List of sessions
        """
        type_list = []
        full_sess_list = []
        post_uri = ALL_SESS_PROJ_URI.format(project=projectid)

        # First get a list of all experiment types
        post_uri_types = '%s?columns=xsiType' % post_uri
        sess_list = self._get_json(post_uri_types)
        for sess in sess_list:
            sess_type = sess['xsiType'].lower()

            if sess_type == 'proc:subjgenprocdata':
                # Ignore subject assessors
                continue

            if sess_type not in type_list:
                type_list.append(sess_type)

        # Get list of sessions for each type since we have to be specific
        # about last_modified field
        for sess_type in type_list:
            post_uri_type = '''{post_uri}?xsiType={stype}&columns=ID,subject_label,subject_ID,xsiType,label,{stype}/meta/last_modified'''.format(
                post_uri=post_uri, stype=sess_type)
            sess_list = self._get_json(post_uri_type)

            # Sort by label
            sess_list = sorted(sess_list, key=lambda k: k['label'])

            for sess in sess_list:
                # Override the project returned to be the one we queried
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

            # Add sessions of this type to full list
            full_sess_list.extend(sess_list)

        # Return list
        return full_sess_list

    def get_session_resources(self, projectid, subjectid, sessionid):
        """
        Gets a list of all of the resources for a session associated to a
         subject/project requested by the user

        :param projectid (string): ID of a project on XNAT
        :param subjectid (string): ID/label of a subject
        :param sessionid (string): ID/label of a session to get resources for
        :return: List of resources for the session

        """
        post_uri = SE_RESOURCES_URI.format(
            project=projectid, subject=subjectid, session=sessionid)
        resource_list = self._get_json(post_uri)
        return resource_list

    def get_scans(self, projectid, subjectid, sessionid):
        """
        List all the scans that you have access to based on passed
         session/subject/project.

        :param projectid (string): ID of a project on XNAT
        :param subjectid (string): ID/label of a subject
        :param sessionid (string): ID/label of a session
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
                snew['series_description'] =\
                    scan['%s/series_description' % pfix]
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

    def get_scan_resources(self, projectid, subjectid, sessionid, scanid):
        """
        Gets a list of all of the resources for a scan associated to a
         session/subject/project requested by the user.
        :param projectid (string): ID of a project on XNAT
        :param subjectid (string): ID/label of a subject
        :param sessionid (string): ID/label of a session
        :param scanid (string): ID of a scan to get resources for
        :return: List of resources for the scan
        """
        post_uri = SC_RESOURCES_URI.format(project=projectid,
                                           subject=subjectid,
                                           session=sessionid,
                                           scan=scanid)
        resource_list = self._get_json(post_uri)
        return resource_list

    def get_assessor_out_resources(
        self, projectid, subjectid, sessionid, assessorid):
        """
        Gets a list of all of the resources for an assessor associated to a
         session/subject/project requested by the user.
        :param projectid (string): ID of a project on XNAT
        :param subjectid (string): ID/label of a subject
        :param sessionid (string): ID/label of a session
        :param assessorid (string): ID/label of an assessor to get resources for
        :return: List of resources for the assessor
        """
        # Check that the assessors types are present on XNAT
        if not has_genproc_datatypes(self):
            print('WARNING: DAX datatypes not found on XNAT')
            return list()

        post_uri = A_RESOURCES_URI.format(project=projectid,
                                          subject=subjectid,
                                          session=sessionid,
                                          assessor=assessorid)
        resource_list = self._get_json(post_uri)
        return resource_list

    @staticmethod
    def object_type_from_path(path):
        elems = path.split('/')
        if elems[0] == 'xnat:':
            elems = elems[1:]
        elems = [e for e in elems if len(e) > 0]
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

    def list_project_assessors(self, projectid):
        """
        List all the assessors that you have access to based on passed project.

        :param projectid (string): ID of a project on XNAT
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
                        anew['session_type'] =\
                            sess_id2mod[asse['session_ID']][1]
                        anew['session_id'] = asse['session_ID']
                        anew['session_label'] = asse['session_label']
                        anew['procstatus'] = asse['%s/procstatus' % pfix]
                        anew['qcstatus'] = asse['%s/validation/status' % pfix]
                        anew['proctype'] = 'FreeSurfer'

                        if len(asse['label'].rsplit('-x-FS')) > 1:
                            anew['proctype'] =\
                                (anew['proctype'] +
                                 asse['label'].rsplit('-x-FS')[1])

                        anew['version'] = asse.get('%s/procversion' % pfix)
                        anew['xsiType'] = asse['xsiType']
                        anew['jobid'] = asse.get('%s/jobid' % pfix)
                        anew['jobstartdate'] =\
                            asse.get('%s/jobstartdate' % pfix)
                        anew['memused'] = asse.get('%s/memused' % pfix)
                        anew['walltimeused'] =\
                            asse.get('%s/walltimeused' % pfix)
                        anew['jobnode'] = asse.get('%s/jobnode' % pfix)
                        anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                        anew['gender'] = sess_id2mod[asse['session_ID']][3]
                        anew['yob'] = sess_id2mod[asse['session_ID']][4]
                        anew['age'] = sess_id2mod[asse['session_ID']][5]
                        anew['last_modified'] =\
                            sess_id2mod[asse['session_ID']][6]
                        anew['last_updated'] =\
                            sess_id2mod[asse['session_ID']][7]
                        anew['resources'] = [asse['%s/out/file/label' % pfix]]
                        assessors_dict[key] = anew

        if has_genproc_datatypes(self):
            # Then add genProcData
            post_uri = SE_ARCHIVE_URI
            post_uri += ASSESSOR_PR_PROJ_POST_URI.format(
                project=projectid, pstype=DEFAULT_DATATYPE)
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
                        anew['subject_label'] =\
                            sess_id2mod[asse['session_ID']][0]
                        anew['session_type'] =\
                            sess_id2mod[asse['session_ID']][1]
                        anew['session_id'] = asse['session_ID']
                        anew['session_label'] = asse['session_label']
                        anew['procstatus'] = asse['%s/procstatus' % pfix]
                        anew['proctype'] = asse['%s/proctype' % pfix]
                        anew['qcstatus'] = asse['%s/validation/status' % pfix]
                        anew['qcnotes'] = asse['%s/validation/notes' % pfix]
                        anew['version'] = asse['%s/procversion' % pfix]
                        anew['xsiType'] = asse['xsiType']
                        anew['jobid'] = asse.get('%s/jobid' % pfix)
                        anew['jobnode'] = asse.get('%s/jobnode' % pfix)
                        anew['jobstartdate'] =\
                            asse.get('%s/jobstartdate' % pfix)
                        anew['memused'] = asse.get('%s/memused' % pfix)
                        anew['walltimeused'] =\
                            asse.get('%s/walltimeused' % pfix)
                        anew['handedness'] = sess_id2mod[asse['session_ID']][2]
                        anew['gender'] = sess_id2mod[asse['session_ID']][3]
                        anew['yob'] = sess_id2mod[asse['session_ID']][4]
                        anew['age'] = sess_id2mod[asse['session_ID']][5]
                        anew['last_modified'] =\
                            sess_id2mod[asse['session_ID']][6]
                        anew['last_updated'] =\
                            sess_id2mod[asse['session_ID']][7]
                        anew['resources'] = [asse['%s/out/file/label' % pfix]]
                        anew['inputs'] = asse.get('%s/inputs' % pfix)
                        anew['dax_docker_version'] = asse['%s/dax_docker_version' % pfix]
                        anew['dax_version'] = asse['%s/dax_version' % pfix]
                        anew['dax_version_hash'] = asse['%s/dax_version_hash' % pfix] 
                        assessors_dict[key] = anew

        return sorted(list(assessors_dict.values()), key=lambda k: k['label'])

    def list_project_assessor_types(self, projectid):
        """
        List all the assessors that you have access to based on passed project.

        :param projectid (string): ID of a project on XNAT
        :return: List of all the assessors for the project
        """
        assr_types = []

        if has_genproc_datatypes(self):
            # genProcData
            post_uri = SE_ARCHIVE_URI + '''?project={project}&xsiType={pstype}\
&columns=ID,xsiType,project,{pstype}/proctype'''
            post_uri = post_uri.format(project=projectid, pstype=DEFAULT_DATATYPE)
            assessor_list = self._get_json(post_uri)
            proctype_field = '{}/proctype'.format(DEFAULT_DATATYPE.lower())
            assr_types = set(x[proctype_field] for x in assessor_list)

        if has_fs_datatypes(self):
            # FreeSurfer
            post_uri = SE_ARCHIVE_URI + '''?project={project}&xsiType={fstype}\
&columns=ID,xsiType,project'''

            post_uri = post_uri.format(project=projectid, fstype=DEFAULT_FS_DATATYPE)
            assessor_list = self._get_json(post_uri)
            if len(assessor_list) > 0:
                assr_types.add('FreeSurfer')

        return list(assr_types)

    def get_assessors(self, projectid, subjectid, sessionid):
        """
        List all the assessors that you have access to based on passed
         session/subject/project.
        :param projectid (string): ID of a project on XNAT
        :param subjectid (string): ID/label of a subject
        :param sessionid (string): ID/label of a session
        :return: List of all the assessors
        """
        new_list = list()

        if has_fs_datatypes(self):
            # First get FreeSurfer
            post_uri = ASSESSORS_URI.format(project=projectid,
                                            subject=subjectid,
                                            session=sessionid)
            post_uri += ASSESSOR_FS_POST_URI.format(fstype=DEFAULT_FS_DATATYPE)
            assessor_list = self._get_json(post_uri)

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

        if has_genproc_datatypes(self):
            # Then add genProcData
            post_uri = ASSESSORS_URI.format(project=projectid,
                                            subject=subjectid,
                                            session=sessionid)
            post_uri += ASSESSOR_PR_POST_URI.format(pstype=DEFAULT_DATATYPE)
            assessor_list = self._get_json(post_uri)

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
        if len(re.findall('-x-', label)) == 3:
            labels = label.split('-x-')
            self.project_id = labels[0]
            self.subject_label = labels[1]
            self.session_label = labels[2]
            self.proctype = labels[3]
            self.scan_id = None
        elif len(re.findall('-x-', label)) == 4:
            labels = label.split('-x-')
            self.project_id = labels[0]
            self.subject_label = labels[1]
            self.session_label = labels[2]
            self.scan_id = labels[3]
            self.proctype = labels[4]
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
        return intf.select_assessor(
            self.project_id,
            self.subject_label,
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
        if not self.assr_handler.is_valid():
            err = 'SpiderProcessHandler:invalid assessor handler. Wrong label.'
            raise XnatUtilsError(err)

        # Create the upload directory
        self.directory = os.path.join(DAX_SETTINGS.get_results_dir(),
                                      self.assr_handler.assessor_label)
        # if the folder already exists : remove it
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        else:
            # Remove files in directories
            utilities.clean_directory(self.directory)

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
            print(("Error: %s" % msg))

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
            print(('Failed to connect to XNAT. Error: ', e))
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
def get_interface(host=None, user=None, pwd=None, smtp_host=None, timeout_emails=None):
    """
    Opens a connection to XNAT.

    :param host: URL to connect to XNAT
    :param user: XNAT username
    :param pwd: XNAT password
    :return: InterfaceTemp object which extends functionaly of pyxnat.Interface

    """
    return InterfaceTemp(host, user, pwd, smtp_host, timeout_emails)


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


def parse_assessor_inputs(inputs):
    try:
        if inputs == '':
            return None
        return utilities.decode_url_json_string(inputs)
    except IndexError:
        return None


def get_assessor_inputs(assessor, cached_sessions=None):
    # Try to get inputs from cached data
    if cached_sessions:
        assr_label = assessor.label()
        for csess in cached_sessions:
            for cassr in csess.assessors():
                if cassr.label() == assr_label:
                    return cassr.info()['inputs']

    # It's not in the cached data, so Query XNAT
    datatype = assessor.datatype()
    inputs = assessor.attrs.get(datatype + '/inputs')
    return parse_assessor_inputs(inputs)

###############################################################################
#                     Download/Upload resources from XNAT                     #
###############################################################################

def rename_directory_with_assessor_inputs(assessor,directory_path):
    """
    Gets download directory path for Xnatdownload and renames with scan id inclusion
    :param assessor: pyxnat Assessor object
    :param directory_path: string of directory path with assessor label
    :return assessor_path: Appending scan ID to inputs list
    """
    inputs = get_assessor_inputs(assessor)
    if inputs is not None:
        inputs_list = list(set(get_assessor_inputs(assessor).values()))  # getting a unique list of
                                                                # input list from assessor object
        scan_id_of_inputs = '-'.join([input.split('/')[-1] for input in inputs_list if \
                            'scans' in input])
        if not scan_id_of_inputs:
            return directory_path
        directory_path_parts = os.path.basename(directory_path).split('-x-')
        assessor_path = os.path.dirname(directory_path) + "/" + '-x-'.join([directory_path_parts[0], \
                                    directory_path_parts[1], directory_path_parts[2], \
                                    scan_id_of_inputs, directory_path_parts[3], \
                                    directory_path_parts[4]])
    else:
        assessor_path = directory_path
    return assessor_path

def upload_file_to_obj(
        filepath, resource_obj, remove=False, removeall=False, fname=None):

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
        filepath = utilities.check_image_format(filepath)
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
                print(("WARNING: upload_file_to_obj in XnatUtils: resource %s \
already exists." % filename))
                return False
        resource_obj.file(
            str(filename)).put(
                str(filepath),
                overwrite=True,
                params={"event_reason": "DAX uploading file"})

        return True


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
                    print(("Warning: upload_folder_to_obj in XnatUtils: file \
%s already found on XNAT. No upload. Use remove/removeall." % fpath))
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
            resource_obj = intf.select_assessor_resource(
                project_id, subject_id, session_id, scan_id, assessor_id,
                resource)
            status = upload_folder_to_obj(directory, resource_obj, resource,
                                          remove, removeall, extract)

    return status


def upload_reference(reference, assessor_obj, resource):
    """
    Upload path by reference

    :param reference: Full path of the directory on xnat server to be uploaded
    :param assessor_obj: pyxnat EObject of the assessor to upload to
    :param resource: pyxnat object resource to be uploaded
    """
    _uri = '{}/out/resources/{}/files?overwrite=True&label={}&reference={}'
    _uri = _uri.format(assessor_obj._uri, resource, resource, reference)
    _xnat = assessor_obj._intf
    _resp = _xnat.put(_uri)
    if (_resp is not None and not _resp.ok):
        err = 'bad response on put:{}'.format(_resp.content)
        raise XnatUtilsError(err)


def upload_assessor_snapshots(assessor_obj, original, thumbnail):
    """
    Upload the snapshots of the assessor PDF.
     (both the original and the thumbnail)

    :param assessor_obj: pyxnat EObject of the assessor to upload to
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
                     overwrite=True,
                     params={"event_reason": "DAX uploading file"})
    assessor_obj.out_resource('SNAPSHOTS')\
                .file(os.path.basename(original))\
                .put(original, original.split('.')[1].upper(), 'ORIGINAL',
                     overwrite=True,
                     params={"event_reason": "DAX uploading file"})
    return True


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
            fpath = utilities.check_image_format(fpath)
            if label:
                filename = os.path.join(label, fpath)
            else:
                filename = fpath
            f_list.append(filename)
        else:
            label = os.path.join(label, fpath)
            f_list.extend(get_files_in_folder(ffpath, label))
    return f_list

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
        self.reset_cached_time()
        experiment = intf.select_experiment(proj, subj, sess)
        xml_str = experiment.get()
        self.sess_element = ET.fromstring(xml_str)
        self.project = proj
        self.subject = subj
        self.session = sess
        self.intf = intf  # cache for later usage
        self.full_object_ = experiment
        self.sess_info_ = None
        self.scans_ = None
        self.assessors_ = None
        self.datatype_ = None
        self.creation_timestamp_ = None

    def reset_cached_time(self):
        self.cached_timestamp = datetime.now()

    def entity_type(self):
        return 'session'

    def reload(self):
        experiment = self.intf.select_experiment(
            self.project, self.subject, self.session)
        self.sess_element = ET.fromstring(experiment.get())
        self.full_object_ = experiment
        self.sess_info_ = None
        self.scans_ = None
        self.assessors_ = None
        self.reset_cached_time()

    def refresh(self):
        last_mod_xnat = self.full_object().attrs.get(
            self.datatype() + '/meta/last_modified')
        last_mod = datetime.strptime(last_mod_xnat[0:19], '%Y-%m-%d %H:%M:%S')
        if last_mod > self.cached_timestamp:
            self.reload()
            # return value means we did refresh
            return True
        else:
            # Nothing changed so don't reload
            # return value means we didn't refresh
            return False

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

        # TODO:BenM/xnat refactor/according to the lxml spec,
        # find does this anyway
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
        if self.scans_ is None:
            scan_list = []
            scan_elements = self.sess_element.find('xnat:scans', NS)
            if scan_elements:
                for scan in scan_elements:
                    scan_list.append(CachedImageScan(self.intf, scan, self))

            self.scans_ = scan_list

        return self.scans_

    def assessors(self, select=AssessorSelect.all_inputs):
        """
        Get a list of CachedImageAssessor objects for the XNAT session

        :return: List of CachedImageAssessor objects for the session.

        """
        if not self.AssessorSelect.valid(select):
            raise ValueError("'select' must be a valid AssessorSelect.value")

        if self.assessors_ is None:

            assr_list = []

            assr_elements = self.sess_element.find('xnat:assessors', NS)
            if assr_elements:
                for assr in assr_elements:
                    assr_list.append(
                        CachedImageAssessor(self.intf, assr, self))

                if select == CachedImageSession.AssessorSelect.with_inputs:
                    assr_list = assr_list.filter(
                        parse_assessor_inputs(
                            self.get("proc:inputs") is not None))

            self.assessors_ = assr_list

        return self.assessors_

    def info(self):
        """
        Get a dictionary of lots of variables that correspond to the session

        :return: Dictionary of variables

        """
        if self.sess_info_ is None:
            sess_info = dict()

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

            self.sess_info_ = sess_info

        return self.sess_info_

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
        if self.full_object_ is None:
            self.full_object_ = self.intf.select_experiment(
                self.project, self.subject, self.session)
        return self.full_object_

    def creation_timestamp(self): 
        if self.creation_timestamp_ is None:
            self.creation_timestamp_ = self.full_object().attrs.get(
                self.datatype() + '/meta/insert_date')

        return self.creation_timestamp_

    def datatype(self):
        if self.datatype_ is None:
            self.datatype_ = self.full_object().datatype()

        return self.datatype_


class CachedImageScan(object):
    """
    Class to cache the XML information for a scan on XNAT
    """
    def __init__(self, intf, scan_element, parent):
        """
        Entry point for the CachedImageScan class

        :param intf: pyxnat.Interface or XnatUtils.InterfaceTemp interface object
        :param scan_element: XML string corresponding to a scan
        :param parent: Parent XML string of the session
        :return: None

        """
        self.intf = intf
        self.scan_parent = parent
        self.scan_element = scan_element
        self.scan_label = self.label()
        self.type_ = self.get('type')
        self.full_object_ = None
        self.scan_info_ = None

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
        if self.scan_info_ is None:
            scan_info = dict()

            scan_info['ID'] = self.get('ID')
            scan_info['label'] = self.get('ID')
            scan_info['quality'] = self.get('xnat:quality')
            scan_info['frames'] = self.get('xnat:frames')
            scan_info['note'] = self.get('xnat:note')
            scan_info['type'] = self.get('type')
            scan_info['series_description'] =\
                self.get('xnat:series_description')
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

            self.scan_info_ = scan_info

        return self.scan_info_

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
        if self.full_object_ is None:
            info = self.info()
            self.full_object_ = self.intf.select_scan(info['project_id'],
                                                      info['subject_id'],
                                                      info['session_id'],
                                                      info['scan_id'])
        return self.full_object_


class CachedImageAssessor(object):
    """
    Class to cache the XML information for an assessor on XNAT
    """
    def __init__(self, intf, assr_element, parent):
        """
        Entry point for the CachedImageAssessor class on XNAT

        :param intf: pyxnat.Interface or XnatUtils.InterfaceTemp interface object
        :param assr_element: the assessor XML string on XNAT
        :param parent: the parent element of the assessor
        :return: None

        """
        self.intf = intf
        self.assr_parent = parent
        self.assr_element = assr_element
        self.proctype = None
        self.full_object_ = None
        self.assr_info_ = None

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
            self.proctype = self.info().get('proctype', None)
        return self.proctype

    def info(self):
        """
        Get a dictionary of information associated with the assessor

        :return: None

        """
        if self.assr_info_ is None:
            assr_info = dict()

            assr_info['inputs'] = parse_assessor_inputs(
                self.get('proc:inputs'))
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
                assr_info['qcnotes'] = self.get('xnat:validation/notes')
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
                assr_info['qcnotes'] = self.get('xnat:validation/notes')
                assr_info['version'] = self.get('proc:procversion')
                assr_info['jobid'] = self.get('proc:jobid')
                assr_info['jobstartdate'] = self.get('proc:jobstartdate')
                assr_info['memused'] = self.get('proc:memused')
                assr_info['walltimeused'] = self.get('proc:walltimeused')
                assr_info['jobnode'] = self.get('proc:jobnode')
            else:
                msg = 'Warning:unknown xsitype for assessor: %s'
                print((msg % assr_info['xsiType']))

            self.assr_info_ = assr_info

        return self.assr_info_

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
        if self.full_object_ is None:
            info = self.info()
            self.full_object_ = self.intf.select_assessor(info['project_id'],
                                                          info['subject_id'],
                                                          info['session_id'],
                                                          info['assessor_id'])
        return self.full_object_


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


def get_scan_status(sessions, scan_path):
    path_parts = scan_path.split('/')
    sess_label = path_parts[6]
    scan_label = path_parts[8]

    for csess in sessions:
        if csess.label() == sess_label:
            for cscan in csess.scans():
                if cscan.label() == scan_label:
                    return cscan.info()['quality']

    raise XnatUtilsError('Invalid scan path:' + scan_path)


def get_assr_status(sessions, assr_path):
    path_parts = assr_path.split('/')
    sess_label = path_parts[6]
    assr_label = path_parts[8]

    for csess in sessions:
        if csess.label() != sess_label:
            continue

        for cassr in csess.assessors():
            if cassr.label() != assr_label:
                continue

            cinfo = cassr.info()
            return cinfo['procstatus'], cinfo['qcstatus']

    raise XnatUtilsError('Invalid assessor path:' + assr_path)


def get_input_list(input_val, default_val):
    """
    Method to get a list from a comma separated string.
    :param input_val: Input string or list
    :param default_val: Default value (generally used for a spider)
    :return: listified string or default_val if input is not a list or string.
    """
    if isinstance(input_val, list):
        return input_val
    elif isinstance(input_val, str):
        return input_val.split(',')
    else:
        return default_val


def has_resource(cobj, resource_label):
    """
    Check to see if a CachedImageObject has a specified resource
    :param cobj: CachedImageObject object from XnatUtils
    :param resource_label: label of the resource to check
    :return: True if cobj has the resource and there is at least one file,
             False if not.
    """
    has_it = False

    res_list = [r for r in cobj.get_resources() if r['label'] == resource_label]
    if len(res_list) > 0:
        # We have resources, so grab the first one
        res = res_list[0]

        # If the resource is empty, the file_count will be blank, not 0
        if res['file_count'] != '':

            # Convert the file count to an integer
            file_count = int(res_list[0]['file_count'])

            if file_count > 0:
                # at least one file, so yep
                has_it = True

    return has_it


def is_cscan_unusable(cscan):
    """
    Check to see if a CachedImageScan is unusable
    :param cscan: XnatUtils.CachedImageScan object
    :return: True if unusable, False otherwise
    """
    return cscan.info()['quality'] == "unusable"


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
    if isinstance(expressions, str):
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
            flist.extend([d for d in list_dicts if regex.match(d[key])])

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
    root = etree.fromstring(xmlstr, parser=etree.XMLParser(huge_tree=True))
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


def get_json(xnat, uri):
    return json.loads(xnat._exec(uri, 'GET'))


def decode_inputs(inputs):
    if inputs:
        inputs = decode_url_json_string(inputs)
        return inputs
    else:
        return {}


def load_assr_data(xnat, project_filter):
    LOGGER.info('loading XNAT data, projects={}'.format(project_filter))

    # Build the uri to query with filters and run it
    _uri = ASSR_URI
    _uri += '&project={}'.format(','.join(project_filter))
    LOGGER.debug(_uri)
    _json = get_json(xnat, _uri)
    dfa = pd.DataFrame(_json['ResultSet']['Result'])

    # Rename columns
    dfa.rename(columns=ASSR_RENAME, inplace=True)

    # Fill any missing columns by reindexing with the union of current columns
    # and the destination renamed columns, this will also handle empty set
    dfa = dfa.reindex(
        dfa.columns.union(
            ASSR_RENAME.values(), sort=False), axis=1, fill_value='')

    # Set the full path for use in processors
    dfa['full_path'] = '/projects/' + dfa['PROJECT'] + '/subjects/' + dfa['SUBJECT'] + '/experiments/' +  dfa['SESSION'] + '/assessors/' + dfa['ASSR']

    # Decode inputs
    dfa['INPUTS'] = dfa['INPUTS'].apply(decode_inputs)

    return dfa


def load_scan_data(xnat, project_filter):
    #  Load data
    LOGGER.info('loading XNAT scan data, projects={}'.format(project_filter))

    # Build the uri query with filters and run it
    _uri = SCAN_URI
    _uri += '&project={}'.format(','.join(project_filter))
    LOGGER.info(_uri)
    _json = get_json(xnat, _uri)
    dfs = pd.DataFrame(_json['ResultSet']['Result'])

    dfs.rename(columns=SCAN_RENAME, inplace=True)

    # Fill any missing columns by reindexing with the union of current columns
    # and the destination renamed columns, this will also handle empty set
    dfs = dfs.reindex(
        dfs.columns.union(
            SCAN_RENAME.values(), sort=False), axis=1, fill_value='')

    # Set the full path for use in processors
    dfs['full_path'] = '/projects/' +  dfs['PROJECT'] + '/subjects/' + dfs['SUBJECT'] + '/experiments/' +  dfs['SESSION'] + '/scans/' + dfs['SCANID']

    return dfs


def load_sgp_data(xnat, project):
    LOGGER.info('loading XNAT data, project={}'.format(project))

    # Build the uri to query with filters and run it
    _uri = SGP_URI.format(project)
    LOGGER.debug(_uri)
    _json = get_json(xnat, _uri)
    dfp = pd.DataFrame(_json['ResultSet']['Result'])

    # Rename columns
    dfp.rename(columns=SGP_RENAME, inplace=True)

    # Fill any missing columns by reindexing with the union of current columns
    # and the destination renamed columns, this will also handle empty set
    dfp = dfp.reindex(
        dfp.columns.union(
            SGP_RENAME.values(), sort=False), axis=1, fill_value='')

    # Decode inputs string
    dfp['INPUTS'] = dfp['INPUTS'].apply(decode_inputs)

    return dfp
