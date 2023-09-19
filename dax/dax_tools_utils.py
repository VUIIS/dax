#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions used by dax_tools
"""

import csv
from datetime import datetime
import getpass
import glob
import imp
import json
import logging
import os
import shutil
import sys
from multiprocessing import Pool
import re

from . import bin
from . import XnatUtils
from . import utilities
from . import assessor_utils
from .dax_settings import (DAX_Settings, DAX_Netrc, DEFAULT_DATATYPE,
                           DEFAULT_FS_DATATYPE)
from .errors import (DaxUploadError, DaxError, DaxNetrcError, DaxSetupError)

from .task import (READY_TO_COMPLETE, COMPLETE, UPLOADING, JOB_FAILED,
                   JOB_PENDING, NEEDS_QA)
from .task import ClusterTask
from .XnatUtils import XnatUtilsError
from .version import VERSION as __version__
from .git_revision import git_revision as __git_revision__
from .suppdf import suppdf


# Global Variables
LOGGER = logging.getLogger('dax')

BASH_PROFILE_XNAT = """# XNAT host for dax:
{export_cmd}
"""

# Variables for upload
ERR_MSG = 'Error from XnatUtils when uploading: %s'
DAX_SETTINGS = DAX_Settings()
JOB_EXTENSION_FILE = DAX_SETTINGS.get_job_extension_file()
_COMPLETE_FLAG_FILE = 'READY_TO_COMPLETE.txt'
_READY_FLAG_FILE = 'READY_TO_UPLOAD.txt'
_FAILED_FLAG_FILE = 'JOB_FAILED.txt'
_EMAILED_FLAG_FILE = 'ALREADY_SEND_EMAIL.txt'
_OUTLOG = 'OUTLOG'
_TRASH = 'TRASH'
_PBS = 'PBS'
_FLAG_FILES = 'FlagFiles'
_UPLOAD_SKIP_LIST = [_OUTLOG, _TRASH, _PBS, _FLAG_FILES, 'TRIALSQ', 'SAVE', 'DISKQ']
SNAPSHOTS_ORIGINAL = 'snapshot_original.png'
SNAPSHOTS_PREVIEW = 'snapshot_preview.png'
DEFAULT_HEADER = ['host', 'username', 'password', 'projects']

# Cmd:
GS_CMD = """gs -q -o {original} -sDEVICE=pngalpha -dLastPage=1 {pdf_path}"""
CONVERT_CMD = """convert {original} -resize x200 {preview}"""
GS_CMD2 = """gs -q -o {original} -sDEVICE=pngalpha {pdf_path}"""

# WARNING content for emails
WARNING_START_CONTENT = """
The following assessors already exist and the Spider try to upload files on \
existing files :
"""
WARNING_END_CONTENT = """
You should:
    - remove the assessor if you want to upload the data
    - set the status of the assessor to "uploading"
    - remove the data from the upload folder if you do not want to upload.
"""
WARNING_SUBJECT = 'ERROR/WARNING: dax_upload'


def default_resdir():
    return os.path.join(
        '/scratch',
        os.environ.get('USER', 'USER'),
        'Spider_Upload_Dir')


def upload_tasks(logfile, debug, upload_settings=None,
                 host=None, username=None, password=None,
                 projects=None, suffix='', emailaddress=None,
                 uselocking=True, resdir=default_resdir(), num_threads=1):
    """
    Upload tasks from the queue folder.

    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param upload_settings: settings file (csv, py, json) to define
                            xnat host/project relationship.
    :param host: XNAT host
    :param username: XNAT username
    :param password: XNAT password
    :param suffix: suffix for flagfile
    :param emailaddress: email address for warnings
    :param projects: Project(s) to upload

    """
    bin.set_logger(logfile, debug)

    FLAGFILE_TEMPLATE = os.path.join(resdir, _FLAG_FILES, 'Process_Upload_running')
    flagfile = "%s%s.txt" % (FLAGFILE_TEMPLATE, suffix)

    # Load the settings for upload
    upload_settings = load_upload_settings(upload_settings, host, username,
                                           password, projects)
    print_upload_settings(upload_settings, resdir)
    # create the flag file showing that the spider is running
    if uselocking and is_dax_upload_running(flagfile):
        return

    try:
        upload_results(upload_settings, emailaddress, resdir, num_threads)
    finally:
        if uselocking:
            # remove flagfile
            os.remove(flagfile)


def select_assessor(xnat, assessor_dict):
    """
    Select the assessor pyxnat Eobject from the assessor dictionary information

    :param xnat: pyxnat.interface object
    :param assessor_dict: assessor dictionary
    :return: assessor pyxnat Eobject
    """
    return xnat.select_assessor(
        assessor_dict['project_id'],
        assessor_dict['subject_label'],
        assessor_dict['session_label'],
        assessor_id=assessor_dict['label'])


def is_dax_upload_running(flagfile):
    """
    Check if dax_upload is not already running on the station

    :return: True if dax_upload already running, False otherwise.
    """
    if os.path.exists(flagfile):
        LOGGER.warn('Upload already running.')
        return True
    else:
        f_obj = open(flagfile, 'w')
        today = datetime.now()
        datestr = "Date: %s%s%s_%s:%s:%s" % (str(today.year),
                                             str(today.month),
                                             str(today.day),
                                             str(today.hour),
                                             str(today.minute),
                                             str(today.second))
        f_obj.write(datestr + '\n')
        f_obj.close()
        LOGGER.debug('Flagfile created: %s with date: %s'
                     % (flagfile, datestr))
        return False


def get_assessor_list(projects, resdir):
    """
    Get the list of assessors labels to upload to XNAT from the queue folder.

    :param projects: list of projects to upload to XNAT
    :return: list of assessor to upload from upload folder
    """
    assessor_label_list = list()

    LOGGER.debug(' - Get Processes names from the upload folder...')
    # check all files/folder in the directory
    dirs = list(filter(os.path.isdir,glob.glob(os.path.join(resdir, '*'))))
    dirs.sort(key=lambda x: os.path.getmtime(x))
    for assessor_label in dirs:
        assessor_label = os.path.basename(assessor_label)
        if assessor_label in _UPLOAD_SKIP_LIST:
            continue
        # If projects set, check that the project is in the list of projects
        # to upload to XNAT
        if projects and assessor_label.split('-x-')[0] not in projects:
            continue

        assessor_path = os.path.join(resdir, assessor_label)
        if not os.path.isdir(assessor_path):
            continue
        if os.path.exists(os.path.join(assessor_path, _EMAILED_FLAG_FILE)):
            LOGGER.debug('skipping, exists on XNAT:{}'.format(assessor_label))
            continue

        rflag = os.path.join(assessor_path, _READY_FLAG_FILE)
        fflag = os.path.join(assessor_path, _FAILED_FLAG_FILE)
        cflag = os.path.join(assessor_path, _COMPLETE_FLAG_FILE)

        if not (os.path.exists(rflag) or os.path.exists(fflag)):
            LOGGER.debug('skipping, still running:{}'.format(assessor_label))
            continue

        if not os.path.exists(cflag):
            LOGGER.debug('skipping, not completed:{}'.format(assessor_label))
            continue

        # Passed all checks, so add it to upload list
        assessor_label_list.append(assessor_label)

    return assessor_label_list


def get_pbs_list(projects, pbsdir):
    """
    Get the list of PBS file to upload to XNAT.

    :param projects: list of projects to upload to XNAT
    :return: list of pbs file from the PBS folder
    """
    pbs_list = list()

    LOGGER.debug(' - Get the PBS for the processes...')
    # check all files/folder in the directory
    for pbs_name in os.listdir(os.path.join(pbsdir)):
        # If projects set, check that the project is in the list of
        # projects to upload to XNAT
        if projects and pbs_name.split('-x-')[0] not in projects:
            continue

        pbs_file = os.path.join(pbsdir, pbs_name)
        if os.path.isfile(pbs_file):
            pbs_list.append(pbs_name)

    return pbs_list


def get_version_assessor(assessor_path):
    """
    Get the version of the assessor that we are uploading from text file

    :param assessor_path: path for the assessor
    :return: version of the assessor from the version.txt file
    """
    version = '1.0.0'
    if os.path.exists(os.path.join(assessor_path, 'version.txt')):
        f_obj = open(os.path.join(assessor_path, 'version.txt'), 'r')
        version = f_obj.read().strip()
        f_obj.close()
    return version


def get_dax_docker_version_assessor(assessor_path):
    """
    Get the dax_docker_version of assessor we are uploading from text file

    :param assessor_path: path for the assessor
    :return: version of the assessor from the version.txt file
    """
    dax_docker_version = ''
    fpath = os.path.join(assessor_path, 'dax_docker_version.txt')

    try:
        with open(fpath, 'r') as f_obj:
            dax_docker_version = f_obj.read().strip()

    except IOError as e:
        LOGGER.warn('failed to read dax_docker_version:' + str(e))

    return dax_docker_version


def generate_snapshots(assessor_path):
    """
    Generate Snapshots from the PDF if it exists.

    :param assessor_path: path for the assessor
    :return: None
    """
    snapshot_dir = os.path.join(assessor_path, 'SNAPSHOTS')
    snapshot_original = os.path.join(snapshot_dir, SNAPSHOTS_ORIGINAL)
    snapshot_preview = os.path.join(snapshot_dir, SNAPSHOTS_PREVIEW)
    try:
        pdf_path = glob.glob(assessor_path + '/PDF/*.pdf')[0]
    except Exception as err:
        LOGGER.debug('skipping generate_snapshots:{}:err={}'.format(assessor_path, err))
        return False

    if not os.path.exists(snapshot_original):
        LOGGER.debug('    +creating original of SNAPSHOTS')

        if not os.path.exists(snapshot_dir):
            os.mkdir(snapshot_dir)

        # Make the snapshots for the assessors with ghostscript
        cmd = GS_CMD.format(original=snapshot_original, pdf_path=pdf_path)
        LOGGER.debug(cmd)
        os.system(cmd)

    # Check for empty file
    if os.path.exists(snapshot_original) and os.stat(snapshot_original).st_size == 0:
        # Delete the empty file
        os.remove(snapshot_original)

        # Try the alternate ghostscript call
        cmd = GS_CMD2.format(original=snapshot_original, pdf_path=pdf_path)
        LOGGER.debug(cmd)
        os.system(cmd)

    # Create the preview snapshot from the original if Snapshots exist
    if os.path.exists(snapshot_original):
        # Make the snapshot_thumbnail
        LOGGER.debug('    +creating preview of SNAPSHOTS')
        cmd = CONVERT_CMD.format(
            original=snapshot_original, preview=snapshot_preview)
        LOGGER.debug(cmd)
        os.system(cmd)


def copy_outlog(assessor_dict, assessor_path, resdir):
    """
    Copy the oulog files to the assessor folder if we are uploading.

    :param assessor_dict: dictionary for the assessor
    :return: None
    """
    outlog_path = os.path.join(resdir, _OUTLOG,
                               assessor_dict['label'] + '.output')
    new_outlog_path = os.path.join(assessor_path, _OUTLOG,
                                   assessor_dict['label'] + '.output')
    if os.path.exists(outlog_path):
        os.makedirs(os.path.join(assessor_path, _OUTLOG))
        shutil.move(outlog_path, new_outlog_path)


def get_xsitype(assessor_dict):
    """
    Copy the outlog files to the assessor folder if we are uploading.

    :param assessor_dict: dictionary for the assessor
    :return: xsitype for the assessor_dict
    """
    proctype = assessor_dict['proctype']
    if proctype == 'FS':
        return DEFAULT_FS_DATATYPE
    else:
        return DEFAULT_DATATYPE


def is_complete(assessor_dict, assessor_path, procstatus):
    """
    Copy the oulog files to the assessor folder if we are uploading.

    :param assessor_dict: dictionary for the assessor
    :param procstatus: status to set for the assessor
    :return: True if the assessor is Complete, False otherwise
    """
    if procstatus == READY_TO_COMPLETE or procstatus == COMPLETE:
        eflag = os.path.join(assessor_path, _EMAILED_FLAG_FILE)
        open(eflag, 'w').close()
        LOGGER.warn('  -->Data already present on XNAT.\n')
        return True
    else:
        return False


def create_freesurfer_assessor(assessor_obj):
    """
    Create freesurfer specific assessor using the DEFAULT_FS_DATATYPE from dax

    :param assessor_obj: pyxnat assessor Eobject
    :return: None
    """
    # create the assessor and set the status
    assessor_obj.create(assessors=DEFAULT_FS_DATATYPE,
                        **{DEFAULT_FS_DATATYPE + '/fsversion': '0'})
    now = datetime.now()
    today = '%s-%s-%s-' % (str(now.year), str(now.month), str(now.day))

    assessor_obj.attrs.mset(
        {DEFAULT_FS_DATATYPE + '/validation/status': JOB_PENDING,
         DEFAULT_FS_DATATYPE + '/date': today})


def create_default_assessor(assessor_obj, proctype):
    """
    Create default assessor using the DEFAULT_DATATYPE from dax

    :param assessor_obj: pyxnat assessor Eobject
    :param proctype: proctype for the assessor
    :return: None
    """
    # Create the assessor and set attributes
    now = datetime.now()
    today = '%s-%s-%s-' % (str(now.year), str(now.month), str(now.day))

    assessor_obj.create(assessors=DEFAULT_DATATYPE)
    # Call mset to only make a single HTTP request
    assessor_obj.attrs.mset(
        {DEFAULT_DATATYPE + '/validation/status': JOB_PENDING,
         DEFAULT_DATATYPE + '/proctype': proctype,
         DEFAULT_DATATYPE + '/date': today})


def should_upload_assessor(assessor_obj,
                           assessor_dict, assessor_path, version):
    """
    Check if the assessor is ready to be uploaded to XNAT

    :param assessor_obj: pyxnat assessor Eobject
    :param assessor_dict: assessor dictionary
    :param xsitype: xsitype for the assessor (fsData or proc:GenProcData, ...)
    :param version: version for the assessor
    :return: True if the assessor should be upload, False otherwise
    """
    if not assessor_obj.exists():
        return False
        # if xsitype == DEFAULT_FS_DATATYPE:
        #     create_freesurfer_assessor(assessor_obj)
        # else:
        #     create_default_assessor(assessor_obj, assessor_dict['proctype'])
    else:
        xsitype = assessor_obj.datatype()
        # Check if not already complete assessor
        procstatus = assessor_obj.attrs.get(xsitype + '/procstatus')
        if is_complete(assessor_dict, assessor_path, procstatus):
            return False
    # set the status to UPLOADING
    assessor_obj.attrs.mset({xsitype + '/procstatus': UPLOADING,
                             xsitype + '/procversion': version})
    return True


def upload_assessor(xnat, assessor_dict, assessor_path, resdir):
    """
    Upload results to an assessor

    :param xnat: pyxnat.Interface object
    :param assessor_dict: assessor dictionary
    :return: None
    """
    # get spiderpath from version.txt file:
    diskq_dir = os.path.join(resdir, 'DISKQ')
    version = get_version_assessor(assessor_path)
    dax_docker_version = get_dax_docker_version_assessor(assessor_path)
    session_obj = xnat.select_session(
        assessor_dict['project_id'],
        assessor_dict['subject_label'],
        assessor_dict['session_label'])

    if not session_obj.exists():
        LOGGER.error('Cannot upload assessor, session does not exist.')
        return True

    # Select assessor
    assessor_dict = assessor_utils.parse_full_assessor_name(
            os.path.basename(assessor_path))
    assessor_obj = session_obj.assessor(assessor_dict['label'])
    if should_upload_assessor(assessor_obj,
                              assessor_dict,
                              assessor_path,
                              version):
        xsitype = assessor_obj.datatype()
        # Before Upload
        LOGGER.debug('suppdf')
        suppdf(assessor_path, assessor_obj)
        LOGGER.debug('generate_snapshots')
        generate_snapshots(assessor_path)
        LOGGER.debug('copy_outlog')
        copy_outlog(assessor_dict, assessor_path, resdir)

        # Upload the XML if FreeSurfer
        if xsitype == DEFAULT_FS_DATATYPE:
            xmlpath = os.path.join(assessor_path, 'XML')
            if os.path.exists(xmlpath):
                LOGGER.debug('    +setting XML for FreeSurfer')
                xml_files_list = os.listdir(xmlpath)
                if len(xml_files_list) != 1:
                    fpath = assessor_path
                    msg = 'cannot upload FreeSurfer assessor, \
unable to find XML file: %s'
                    LOGGER.error(msg % (fpath))
                    return
                xml_path = os.path.join(assessor_path, 'XML',
                                        xml_files_list[0])
                assessor_obj.create(xml=xml_path, allowDataDeletion=False)

        # Upload
        # for each folder=resource in the assessor directory
        for resource in os.listdir(assessor_path):
            resource_path = os.path.join(assessor_path, resource)
            # Need to be in a folder to create the resource :
            if os.path.isdir(resource_path):
                LOGGER.debug('    +uploading %s' % (resource))
                try:
                    upload_resource(assessor_obj, resource, resource_path)
                except Exception as e:
                    try:
                        LOGGER.warn('failed to upload, trying again')
                        upload_resource(assessor_obj, resource, resource_path)
                    except Exception as e:
                        import traceback
                        LOGGER.error(traceback.format_exc())
                        _msg = 'failed to upload, skipping assessor:{}:{}'.format(
                            resource_path, str(e))
                        LOGGER.error(_msg)
                        return

        # after Upload
        if is_diskq_assessor(os.path.basename(assessor_path), resdir):
            # was this run using the DISKQ option
            # Read attributes
            ctask = ClusterTask(assessor_dict['label'], resdir, diskq_dir)

            # Set on XNAT
            assessor_obj.attrs.mset({
                xsitype + '/procstatus': ctask.get_status(),
                xsitype + '/validation/status': NEEDS_QA,
                xsitype + '/jobid': ctask.get_jobid(),
                xsitype + '/jobnode': ctask.get_jobnode(),
                xsitype + '/memused': ctask.get_memused(),
                xsitype + '/walltimeused': ctask.get_walltime(),
                xsitype + '/jobstartdate': ctask.get_jobstartdate(),
                xsitype + '/dax_version': __version__,
                xsitype + '/dax_version_hash': __git_revision__,
                xsitype + '/dax_docker_version': dax_docker_version
            })

            # Delete the task from diskq
            ctask.delete()
        elif os.path.exists(os.path.join(assessor_path, _READY_FLAG_FILE)):
            assessor_obj.attrs.set(xsitype + '/procstatus', READY_TO_COMPLETE)
        else:
            assessor_obj.attrs.set(xsitype + '/procstatus', JOB_FAILED)

        # Remove the folder
        shutil.rmtree(assessor_path)

        return True

    return False


def is_diskq_assessor(assr_label, resdir):
    # Does a batch file exist for this assessor?
    afile = os.path.join(resdir, 'DISKQ', 'BATCH', assr_label + JOB_EXTENSION_FILE)
    return os.path.exists(afile)


def upload_resource(assessor_obj, resource, resource_path):
    """
    Upload a resource folder to an assessor

    :param assessor_obj: pyxnat assessor Eobject
    :param resource: resource to upload
    :param resource_path: resource path on the station
    :return: None
    """
    if resource == 'SNAPSHOTS':
        upload_snapshots(assessor_obj, resource_path)
    else:
        rfiles_list = os.listdir(resource_path)
        if not rfiles_list:
            LOGGER.warn('No files in {}'.format(resource_path))
        elif len(rfiles_list) > 1 or os.path.isdir(os.path.join(resource_path, rfiles_list[0])):
            try:
                XnatUtils.upload_folder_to_obj(
                    resource_path, assessor_obj.out_resource(resource),
                    resource, removeall=True)
            except XnatUtilsError as err:
                print((ERR_MSG % err))
        else:
            # One file, just upload it
            fpath = os.path.join(resource_path, rfiles_list[0])
            try:
                XnatUtils.upload_file_to_obj(
                    fpath, assessor_obj.out_resource(resource), removeall=True)
            except XnatUtilsError as err:
                print((ERR_MSG % err))


def upload_snapshots(assessor_obj, resource_path):
    """
    Upload snapshots to an assessor

    :param assessor_obj: pyxnat assessor Eobject
    :param resource_path: resource path on the station
    :return: None
    """
    # Remove the previous Snapshots:
    if assessor_obj.out_resource('SNAPSHOTS').exists:
        assessor_obj.out_resource('SNAPSHOTS').delete()
    original = os.path.join(resource_path, SNAPSHOTS_ORIGINAL)
    thumbnail = os.path.join(resource_path, SNAPSHOTS_PREVIEW)
    status = None
    try:
        status = XnatUtils.upload_assessor_snapshots(
            assessor_obj, original, thumbnail)
    except XnatUtilsError as err:
        print((ERR_MSG % err))

    if status:
        os.remove(original)
        os.remove(thumbnail)
    else:
        LOGGER.warn('No snapshots original or preview were uploaded')

    # Upload the rest of the files in snapshots
    if len(os.listdir(resource_path)) > 0:
        try:
            XnatUtils.upload_folder_to_obj(
                resource_path, assessor_obj.out_resource('SNAPSHOTS'),
                'SNAPSHOTS')
        except XnatUtilsError as err:
            print((ERR_MSG % err))


def upload_assessors(xnat, projects, resdir, num_threads=1):
    """
    Upload all assessors to XNAT

    :param xnat: pyxnat.Interface object
    :param projects: list of projects to upload to XNAT
    :return: None
    """
    # Get the assessor label from the directory :
    assessors_list = get_assessor_list(projects, resdir)
    number_of_processes = len(assessors_list)
    warnings = list()

    LOGGER.info(('Starting upload pool:{} threads'.format(str(num_threads))))
    sys.stdout.flush()

    pool = Pool(processes=num_threads)
    for index, assessor_label in enumerate(assessors_list):
        LOGGER.info(index)
        sys.stdout.flush()

        pool.apply_async(
            upload_thread,
            [xnat, index, assessor_label, number_of_processes, resdir])

    LOGGER.info('waiting for upload pool to finish...')
    sys.stdout.flush()

    pool.close()
    pool.join()

    LOGGER.info('upload pool finished')
    sys.stdout.flush()

    return warnings


def upload_resource_subjgenproc(sassr, resource, dirpath):
    # TODO: merge this with the other upload_resource

    if resource == 'SNAPSHOTS':
        upload_snapshots_subjgenproc(sassr, dirpath)
    else:
        # Get list of files in the dir
        rfiles_list = os.listdir(dirpath)

        # Handle none, multiple or one file found
        if not rfiles_list:
            LOGGER.warn('No files in {}'.format(dirpath))
        elif len(rfiles_list) > 1 or os.path.isdir(rfiles_list[0]):
            # Upload the whole dir
            XnatUtils.upload_folder_to_obj(
                dirpath,
                sassr.resource(resource),
                resource,
                removeall=True)
        else:
            # One file, upload it
            fpath = os.path.join(dirpath, rfiles_list[0])
            XnatUtils.upload_file_to_obj(
                fpath,
                sassr.resource(resource),
                removeall=True)


def upload_snapshots_subjgenproc(sassr, dirpath):
    # TODO: merge this with the other upload_snapshots
    """
    Upload snapshots to an assessor
    :param assessor_obj: pyxnat assessor Eobject
    :param dirpath: local path
    :return: None
    """
    orig = os.path.join(dirpath, SNAPSHOTS_ORIGINAL)
    thumb = os.path.join(dirpath, SNAPSHOTS_PREVIEW)

    if not os.path.isfile(orig):
        LOGGER.warn('original snapshot not found:{}'.format(orig))
    else:
        # Upload the full size image
        sassr.resource('SNAPSHOTS').file(os.path.basename(orig)).put(
            orig,
            orig.split('.')[1].upper(),
            'ORIGINAL',
            overwrite=True,
            params={"event_reason": "DAX upload"})

    if not os.path.isfile(thumb):
        LOGGER.warn('thumbnail snapshot not found:{}'.format(thumb))
    else:
        # Upload the thumbnail image
        sassr.resource('SNAPSHOTS').file(os.path.basename(thumb)).put(
            thumb,
            thumb.split('.')[1].upper(),
            'THUMBNAIL',
            overwrite=True,
            params={"event_reason": "DAX upload"})


def upload_assessor_subjgenproc(xnat, dirpath):
    resdir = os.path.dirname(dirpath)
    diskq_dir = os.path.join(resdir, 'DISKQ')
    assr = os.path.basename(dirpath)
    [proj, subj, proctype, guid] = assr.split('-x-')

    # Get the assessor object on XNAT
    LOGGER.debug('connecting to assessor on xnat')

    sassr = xnat.select('/projects/{}/subjects/{}/experiments/{}'.format(
        proj, subj, assr))

    if not sassr.exists():
        # LOGGER.info('creating subject asssessor'.format(assr))
        # sassr.create(experiments='proc:subjgenprocdata')
        # We will assume the assessor has already been made elsewhere
        # with the inputs field complete as well
        # as proctype, procversion, and date
        LOGGER.info('assessor does not exist, refusing to create')
        return

    # Double-check the status
    procstatus = sassr.attrs.get(sassr.datatype() + '/procstatus')
    if procstatus in [READY_TO_COMPLETE, COMPLETE]:
        # LOGGER.info('creating subject asssessor'.format(assr))
        # sassr.create(experiments='proc:subjgenprocdata')
        # We will assume the assessor has already been made elsewhere
        # with the inputs field complete as well
        # as proctype, procversion, and date
        LOGGER.info('assessor complete, refusing to overwite')
        return

    LOGGER.info('uploading:{}'.format(dirpath))

    # Before Upload
    LOGGER.debug('suppdf')
    suppdf(dirpath, sassr)
    LOGGER.debug('generate_snapshots')
    generate_snapshots(dirpath)
    # note, we don't need to copy outlog, we assume it's been done during
    # update()

    # Upload each resource
    for resource in os.listdir(dirpath):
        resource_path = os.path.join(dirpath, resource)
        if not os.path.isdir(resource_path):
            LOGGER.debug('skipping, not a directory:{}'.format(resource_path))
            continue

        LOGGER.debug('+uploading:{}'.format(resource))
        try:
            upload_resource_subjgenproc(sassr, resource, resource_path)
        except Exception as e:
            _msg = 'upload failed, skipping assessor:{}:{}'.format(
                resource_path, str(e))
            LOGGER.error(_msg)

    # after Upload
    ctask = ClusterTask(assr, resdir, diskq_dir)

    # Set on XNAT
    _docker_version = get_dax_docker_version_assessor(dirpath) or 'null'
    _status = ctask.get_status() or 'null'
    _jobid = ctask.get_jobid() or 'null'
    _jobnode = ctask.get_jobnode() or 'null'
    _memused = ctask.get_memused() or 'null'
    _walltime = ctask.get_walltime() or 'null'
    _jobstartdate = ctask.get_jobstartdate() or 'null'
    LOGGER.debug('setting attributes on xnat')
    sassr.attrs.mset({
        'proc:subjgenprocdata/procstatus': _status,
        'proc:subjgenprocdata/validation/status': NEEDS_QA,
        'proc:subjgenprocdata/jobid': _jobid,
        'proc:subjgenprocdata/jobnode': _jobnode,
        'proc:subjgenprocdata/memused': _memused,
        'proc:subjgenprocdata/walltimeused': _walltime,
        'proc:subjgenprocdata/dax_docker_version': _docker_version,
        'proc:subjgenprocdata/jobstartdate': _jobstartdate,
        'proc:subjgenprocdata/dax_version': __version__,
        'proc:subjgenprocdata/dax_version_hash': __git_revision__,
    })

    # Delete the task from diskq
    ctask.delete()

    # Remove the folder
    shutil.rmtree(dirpath)


def upload_thread(xnat, index, assessor_label, number_of_processes, resdir):
    assessor_path = os.path.join(resdir, assessor_label)
    msg = "    *Process: %s/%s -- label: %s / time: %s"
    LOGGER.info(msg % (str(index + 1),str(number_of_processes), assessor_label, str(datetime.now())))

    if assessor_utils.is_sgp_assessor(assessor_label):
        uploaded = upload_assessor_subjgenproc(
            xnat, assessor_path)
    else:
        assessor_dict = assessor_utils.parse_full_assessor_name(assessor_label)
        if assessor_dict:
            uploaded = upload_assessor(
                xnat, assessor_dict, assessor_path, resdir)
            if not uploaded:
                mess = """    - Assessor label : {label}\n"""
                LOGGER.warn(mess.format(label=assessor_dict['label']))
        else:
            LOGGER.warn('     --> wrong label')

    # Disconnecting here because each thread actually acquires
    # a unique JSESSIONOID, not sure why yet or if this is what we want
    # but have confirmed this is what is happening - bdb 2020-01-28
    xnat.disconnect()


def upload_pbs(xnat, projects, resdir):
    """
    Upload all pbs files to XNAT

    :param xnat: pyxnat.Interface object
    :param projects: list of projects to upload to XNAT
    :return: None
    """
    pbsdir = os.path.join(resdir, _PBS)
    pbs_list = get_pbs_list(projects, pbsdir)
    number_pbs = len(pbs_list)
    for index, pbsfile in enumerate(pbs_list):
        pbs_fpath = os.path.join(pbsdir, pbsfile)
        mess = """   *Uploading PBS {index}/{max} -- File name: {file}"""
        LOGGER.info(mess.format(index=str(index + 1),
                                max=str(number_pbs),
                                file=pbsfile))
        assessor_label = os.path.splitext(pbsfile)[0]
        assessor_dict = assessor_utils.parse_full_assessor_name(assessor_label)
        if not assessor_dict:
            LOGGER.warn('wrong assessor label for %s' % (pbsfile))
            os.rename(pbs_fpath, os.path.join(resdir, _TRASH, pbsfile))
        else:
            assessor_obj = select_assessor(xnat, assessor_dict)
            if not assessor_obj.exists():
                LOGGER.warn('assessor does not exist for %s' % (pbsfile))
                new_location = os.path.join(resdir, _TRASH, pbsfile)
                os.rename(pbs_fpath, new_location)
            else:
                resource_obj = assessor_obj.out_resource(_PBS)
                if resource_obj.exists():
                    label = assessor_dict['label']
                    msg = 'the PBS resource already exists for the assessor %s'
                    LOGGER.warn(msg % (label))
                    adir = os.path.join(resdir, assessor_dict['label'])
                    if os.path.isdir(adir):
                        msg = 'Copying the pbs file in the assessor folder...'
                        LOGGER.warn(msg)
                        pbs_folder = os.path.join(adir, _PBS)
                        if not os.path.exists(pbs_folder):
                            os.mkdir(pbs_folder)
                        os.rename(pbs_fpath, os.path.join(pbs_folder, pbsfile))
                    else:
                        LOGGER.warn('Copying the pbs file in the TRASH ...')
                        trash = os.path.join(resdir, _TRASH, pbsfile)
                        os.rename(pbs_fpath, trash)
                else:
                    # upload the file
                    try:
                        status = XnatUtils.upload_file_to_obj(pbs_fpath,
                                                              resource_obj)
                    except XnatUtilsError as err:
                        LOGGER.error((ERR_MSG % err))
                    if status:
                        os.remove(pbs_fpath)


def upload_outlog(xnat, projects, resdir):
    """
    Upload all outlog files to XNAT

    :param xnat: pyxnat.Interface object
    :param projects: list of projects to upload to XNAT
    :return: None
    """
    outlogs_list = os.listdir(os.path.join(resdir, _OUTLOG))
    if projects:
        outlogs_list = [logfile for logfile in outlogs_list
                        if logfile.split('-x-')[0] in projects]

    number_outlog = len(outlogs_list)
    for index, outlogfile in enumerate(outlogs_list):
        outlog_fpath = os.path.join(resdir, _OUTLOG, outlogfile)
        mess = """   *Checking OUTLOG {index}/{max} -- File name: {file}"""
        LOGGER.info(mess.format(index=str(index + 1),
                                max=str(number_outlog),
                                file=outlogfile))
        assessor_label = os.path.splitext(outlogfile)[0]
        assessor_dict = assessor_utils.parse_full_assessor_name(assessor_label)
        if not assessor_dict:
            LOGGER.warn('     wrong outlog file. You should remove it')
        else:
            assessor_obj = select_assessor(xnat, assessor_dict)
            if not assessor_obj.exists():
                msg = '     no assessor on XNAT -- moving file to trash.'
                LOGGER.warn(msg)
                new_location = os.path.join(resdir, _TRASH, outlogfile)
                os.rename(outlog_fpath, new_location)
            else:
                if assessor_obj.attrs.get(
                        assessor_obj.datatype() + '/procstatus') == JOB_FAILED:
                    resource_obj = assessor_obj.out_resource(_OUTLOG)
                    if resource_obj.exists():
                        pass
                    else:
                        LOGGER.info('     uploading file.')
                        try:
                            status = XnatUtils.upload_file_to_obj(outlog_fpath,
                                                                  resource_obj)
                        except XnatUtilsError as err:
                            print((ERR_MSG % err))
                        if status:
                            os.remove(outlog_fpath)


def upload_results(upload_settings, emailaddress, resdir, num_threads=1):
    """
    Main function to upload the results / PBS / OUTLOG of assessors
     from the queue folder

    :param upload_settings: dictionary defining the upload information
    :return: None
    """
    # TODO: move resdir into upload_sttings
    if len(os.listdir(resdir)) == 0:
        LOGGER.warn('No data need to be uploaded.\n')
        sys.exit()

    warnings = list()

    for upload_dict in upload_settings:
        try:
            with XnatUtils.get_interface(host=upload_dict['host'],
                                         user=upload_dict['username'],
                                         pwd=upload_dict['password']) as intf:
                LOGGER.info('=' * 50)
                proj_str = (upload_dict['projects'] if upload_dict['projects']
                            else 'all')
                LOGGER.info('Connecting to XNAT <%s>, upload for projects:%s' %
                            (upload_dict['host'], proj_str))
                if not XnatUtils.has_dax_datatypes(intf):
                    msg = 'dax datatypes are not installed on xnat <%s>.'
                    raise DaxUploadError(msg % (upload_dict['host']))

                # 1) Upload the assessor data
                # For each assessor label that need to be upload :
                LOGGER.info('Uploading results for assessors')

                warnings.extend(
                    upload_assessors(intf, upload_dict['projects'], resdir,
                                     num_threads))

                # 2) Upload the PBS files
                # For each file, upload it to the PBS resource
                LOGGER.info('Uploading PBS files ...')
                upload_pbs(intf, upload_dict['projects'], resdir)

                # 3) Upload the OUTLOG files not uploaded with processes
                LOGGER.info('Checking OUTLOG files for JOB_FAILED jobs ...')
                upload_outlog(intf, upload_dict['projects'], resdir)
        except DaxNetrcError as e:
            msg = e.msg
            LOGGER.error(e.msg)


def load_upload_settings(f_settings, host, username, password, projects):
    """
    Function to parse arguments base on argparse

    :param f_settings: file to define the settings for uploading
    :param host: XNAT host
    :param username: XNAT username
    :param password: XNAT password
    :param projects: XNAT list of projects

    :return: list of dictionaries info_dict
       info_dict for the host [key:value]:
        host : string for XNAT host
        username : string for XNAT username
        password : string for XNAT password
          (can be the environment variable containing the value)
        projects : list of projects to upload for the host
    """
    host_projs = list()
    # If settings file given, load it and use it:
    if f_settings is not None:
        up_file = os.path.abspath(f_settings)
        if not os.path.isfile(up_file):
            raise DaxError('No upload settings file found: %s' % up_file)
        if f_settings.endswith('.json'):
            with open(up_file) as data_file:
                host_projs = json.load(data_file)
        elif f_settings.endswith('.py'):
            settings = imp.load_source('settings', up_file)
            host_projs = settings.host_projects
        elif f_settings.endswith('.csv'):
            with open(up_file, 'rb') as csvfileread:
                csvreader = csv.reader(csvfileread, delimiter=',')
                for index, row in (csvreader):
                    if len(row) < 4:
                        raise DaxError("error: could not read the csv row. \
Missing args. 4 needed, %s found at line %s." % (str(len(row)), str(index)))
                    else:
                        if row != DEFAULT_HEADER:
                            host_projs.append(dict(list(zip(DEFAULT_HEADER,
                                                        row[:4]))))
        elif f_settings.endswith('.yaml'):
            doc = utilities.read_yaml(f_settings)
            host_projs = doc.get('settings')
        else:
            raise DaxError("error: doesn't recognize the file format for the \
settings file. Please use either JSON/PYTHON/CSV format.")
    else:  # if not file, use the environment variables and options
        _host = os.environ['XNAT_HOST']
        if host:
            _host = host
        if projects:
            projects = projects.split(',')
        else:
            projects = []
        if username:
            username = username
            if not password:
                MSG = "Please provide the password for user <%s> on xnat(%s):"
                password = getpass.getpass(prompt=MSG % (username, _host))
                if not password:
                    raise DaxError('empty password entered')
        else:
            netrc_obj = DAX_Netrc()
            username, password = netrc_obj.get_login(_host)
        host_projs.append(dict(list(zip(DEFAULT_HEADER, [_host, username,
                                                         password,
                                                         projects]))))
    return host_projs


def print_upload_settings(upload_settings, resdir):
    """
    Display Host/Username/Projects that will be used to upload data from
     the queue.

    :return: None
    """
    LOGGER.info('Upload Settings selected by user:')
    for info in upload_settings:
        proj_str = ','.join(info['projects']) if info['projects'] else 'all'
        user_str = info['username'] if info['username'] else ''
        msg = 'XNAT Host: %s -- Xnat Username: %s -- projects: %s'
        LOGGER.info(msg % (info['host'], user_str, proj_str))
    LOGGER.info('Upload Directory: %s ' % (resdir))


def setup_dax_package():
    """ Setup dax package """
    print('########## DAX_SETUP ##########')

    # Set xnat credentials if needed
    set_xnat_netrc()

    print('########## END ##########')


def test_connection_xnat(host, user, pwd):
    """
    Method to check connection to XNAT using host, user, pwd.

    :param host: Host for XNAT
    :param user: User for XNAT
    :param pwd: Password for XNAT
    :return: True if succeeded, False otherwise.
    """
    from pyxnat.core.errors import DatabaseError
    from pyxnat import Interface
    try:
        xnat = Interface(host, user, pwd)
        # try deleting SESSION connection
        xnat._exec('/data/JSESSION', method='DELETE')
        print(' --> Good login.')
        return True
    except DatabaseError:
        print(' --> error: Wrong login.')
        return False


def set_xnat_netrc():
    """Ask User for xnat credentials and store it in xnatnetrc file.

    :return: None
    """
    netrc_obj = DAX_Netrc()
    if netrc_obj.is_empty():
        LOGGER.warn('Setting XNAT login, netrc is empty.')
        connection = False
        while not connection:
            host = input("Please enter your XNAT host: ")
            user = input("Please enter your XNAT username: ")
            pwd = getpass.getpass(prompt='Please enter your XNAT password: ')
            connection = test_connection_xnat(host, user, pwd)

        # Add host to your netrc
        netrc_obj.add_host(host, user, pwd)

        # add XNAT_HOST to your profile file:
        init_profile(host)
    else:
        print('dax setup is already complete')


def init_profile(host):
    """Function to init your profile file to call xnat_profile.

    :param host: Host of XNAT to add to your profile
    :return: None
    """
    # link the file in the bashrc or profile
    profile = os.path.join(os.path.expanduser('~'), '.bash_profile')

    if os.path.exists(os.path.join(os.path.expanduser('~'), '.bash_profile')):
        profile = os.path.join(os.path.expanduser('~'), '.bash_profile')
    elif os.path.exists(os.path.join(os.path.expanduser('~'), '.bashrc')):
        profile = os.path.join(os.path.expanduser('~'), '.bashrc')
    elif os.path.exists(os.path.join(os.path.expanduser('~'), '.profile')):
        profile = os.path.join(os.path.expanduser('~'), '.profile')
    else:
        raise DaxSetupError("could not find your profile file.")

    # Add the line to the profile
    if 'XNAT_HOST' not in open(profile).read():
        print('Adding XNAT_HOST to your profile:{}'.format(profile))
        line_to_add = 'export XNAT_HOST=%s' % host
        with open(profile, "a") as f_profile:
            f_profile.write(BASH_PROFILE_XNAT.format(export_cmd=line_to_add))
    else:
        print('XNAT_HOST already in profile:{}'.format(profile))
