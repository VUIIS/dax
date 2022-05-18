#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" File containing functions called by dax executables """

from datetime import datetime
import imp
import os
import sys
from multiprocessing import Pool
import logging

from . import lockfiles
from . import dax_tools_utils
from . import launcher
from . import assessor_utils
from . import log
from . import XnatUtils
from . import utilities
from . import processors
from .dax_settings import DAX_Settings
from .errors import DaxError
DAX_SETTINGS = DAX_Settings()


def set_logger(logfile, debug):
    """
    Set the logging depth

    :param logfile: File to log output to
    :param debug: Should debug depth be used?
    :return: logger object

    """
    # Logger for logs
    if debug:
        logger = log.setup_debug_logger('dax', logfile)
    else:
        logger = log.setup_info_logger('dax', logfile)
    return logger


def read_settings(settings_path, logger, exe):
    logger.info('Current Process ID: %s' % str(os.getpid()))
    msg = 'Current Process Name: dax.bin.{}({})'
    logger.info(msg.format(exe, settings_path))

    # Load the settings file
    logger.info('loading settings from: %s' % settings_path)
    if settings_path.endswith('.py'):
        settings = imp.load_source('settings', settings_path)
        dax_launcher = settings.myLauncher
    elif settings_path.endswith('.yaml'):
        dax_launcher = read_yaml_settings(settings_path, logger)
    else:
        raise DaxError('Wrong type of settings file given. Please use a \
python file describing the Launcher object or a YAML file.')

    # Run the updates
    logger.info('running launcher, Start Time: %s' % str(datetime.now()))
    return dax_launcher


def launch_jobs(settings_path, logfile, debug, projects=None, sessions=None,
                writeonly=False, pbsdir=None, force_no_qsub=False):
    """
    Method to launch jobs on the grid

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be launched
    :param sessions: Session(s) that need to be updated
    :param writeonly:  write the job files without submitting them
    :param pbsdir: folder to store the pbs file
    :param force_no_qsub: run the job locally on the computer (serial mode)
    :return: None

    """
    # Logger for logs
    logger = set_logger(logfile, debug)

    _launcher_obj = read_settings(settings_path, logger, exe='launch_jobs')
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]
    try:
        _launcher_obj.launch_jobs(lockfile_prefix, projects, sessions,
                                  writeonly, pbsdir,
                                  force_no_qsub=force_no_qsub)
    except KeyboardInterrupt:
        logger.warn('Killed by user.')
        flagfile = os.path.join(
            os.path.join(_launcher_obj.resdir, 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.LAUNCH_SUFFIX))
        lockfiles.unlock_flagfile(flagfile)
    except Exception as e:
        logger.critical('Caught exception launching jobs in bin.launch_jobs')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                str(e)))
        flagfile = os.path.join(
            os.path.join(_launcher_obj.resdir, 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.LAUNCH_SUFFIX))
        lockfiles.unlock_flagfile(flagfile)

    logger.info('finished launcher, End Time: %s' % str(datetime.now()))


def build(settings_path, logfile, debug, projects=None, sessions=None,
          mod_delta=None, proj_lastrun=None, start_sess=None):
    """
    Method that is responsible for running all modules and putting assessors
     into the database

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be built
    :param sessions: Session(s) that need to be built
    :return: None

    """
    # Logger for logs
    logger = set_logger(logfile, debug)

    _launcher_obj = read_settings(settings_path, logger, exe='build')
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]
    try:
        _launcher_obj.build(lockfile_prefix, projects, sessions,
                            mod_delta=mod_delta, proj_lastrun=proj_lastrun,
                            start_sess=start_sess)
    except KeyboardInterrupt:
        logger.warn('Killed by user.')
        # TODO: pass in the flag file path
        flagfile = os.path.join(
            os.path.join(_launcher_obj.resdir, 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.BUILD_SUFFIX))
        lockfiles.unlock_flagfile(flagfile)
    except Exception as e:
        logger.critical('Caught exception building Project in bin.build')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                str(e)))
        flagfile = os.path.join(
            os.path.join(_launcher_obj.resdir, 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.BUILD_SUFFIX))
        lockfiles.unlock_flagfile(flagfile)

    logger.info('finished build, End Time: %s' % str(datetime.now()))


def update_tasks(settings_path, logfile, debug, projects=None, sessions=None):
    """
    Method that is responsible for updating a Task.

    :param settings_path: Path to the project settings file
    :param logfile: Full file of the file used to log to
    :param debug: Should debug mode be used
    :param projects: Project(s) that need to be launched
    :param sessions: Session(s) that need to be updated
    :return: None

    """
    # Logger for logs
    logger = set_logger(logfile, debug)

    _launcher_obj = read_settings(settings_path, logger, exe='update_tasks')
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]
    try:
        _launcher_obj.update_tasks(lockfile_prefix, projects, sessions)
    except KeyboardInterrupt:
        logger.warn('Killed by user.')
        flagfile = os.path.join(
            os.path.join(_launcher_obj.resdir, 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.UPDATE_SUFFIX))
        lockfiles.unlock_flagfile(flagfile)
    except Exception as e:
        logger.critical('Caught exception updating tasks in bin.update_tasks')
        logger.critical('Exception Class %s with message %s' % (e.__class__,
                                                                str(e)))
        flagfile = os.path.join(
            os.path.join(_launcher_obj.resdir, 'FlagFiles'),
            '%s_%s' % (lockfile_prefix, launcher.UPDATE_SUFFIX))
        lockfiles.unlock_flagfile(flagfile)

    logger.info('finished updating tasks, End Time: %s' % str(datetime.now()))


def read_yaml_settings(yaml_file, logger):
    """
    Method to read the settings yaml file and generate the launcher object.

    :param yaml_file: path to yaml file defining the settings
    :return: launcher object
    """
    if not os.path.isfile(yaml_file):
        err = 'Path not found for {}'
        raise DaxError(err.format(yaml_file))

    doc = utilities.read_yaml(yaml_file)

    # Set Inputs from Yaml
    check_default_keys(yaml_file, doc)

    # Set attributes for settings
    attrs = doc.get('attrs')

    # Set singularity image dir
    singularity_imagedir = doc.get('singularity_imagedir')
    job_template = doc.get('jobtemplate')

    # Read modules
    modulelib = doc.get('modulelib')
    mods = dict()
    modules = doc.get('modules', list())
    for mod_dict in modules:
        if mod_dict.get('filepath') is None:
            err = 'Filepath not set for {}'.format(mod_dict.get('name'))
            raise DaxError(err)

        mod_path = mod_dict.get('filepath')
        if not os.path.isabs(mod_path) and modulelib:
            # Preprend lib location
            mod_path = os.path.join(modulelib, mod_path)

        mods[mod_dict.get('name')] = load_from_file(
            mod_path, mod_dict.get('arguments'), logger)

    # Read processors
    procs = dict()
    processors = doc.get('processors', list())
    for proc_dict in processors:
        if proc_dict.get('filepath') is None:
            err = 'Filepath not set for {}'.format(proc_dict.get('name'))
            raise DaxError(err)
        procs[proc_dict.get('name')] = load_from_file(
            proc_dict.get('filepath'), proc_dict.get('arguments'), logger)

    # Read yaml processors
    processorlib = doc.get('processorlib')
    yamlprocs = dict()
    yamls = doc.get('yamlprocessors', list())
    for yaml_dict in yamls:
        if yaml_dict.get('filepath') is None:
            err = 'Filepath not set for {}'.format(yaml_dict.get('name'))
            raise DaxError(err)

        yaml_path = yaml_dict.get('filepath')
        if not os.path.isabs(yaml_path) and processorlib:
            # Preprend lib location
            yaml_path = os.path.join(processorlib, yaml_path)

        yamlprocs[yaml_dict.get('name')] = load_from_file(
            yaml_path, yaml_dict.get('arguments'),
            logger, singularity_imagedir, job_template)

    # Read sgp processors
    processorlib = doc.get('processorlib')
    sgpprocs = {}
    for s in doc.get('sgpprocessors', []):
        yaml_name = s['name']
        try:
            yaml_path = s['filepath']
        except KeyError:
            raise DaxError('Filepath not set for {}'.format(yaml_name))

        if not os.path.isabs(yaml_path) and processorlib:
            # Preprend lib location
            yaml_path = os.path.join(processorlib, yaml_path)

        yaml_args = s.get('arguments', None)
        sgpprocs[yaml_name] = load_from_file(
            yaml_path,
            yaml_args,
            logger,
            singularity_imagedir,
            job_template)

    # Read projects
    proj_mod = dict()
    proj_proc = dict()
    yaml_proc = dict()
    sgp_processors = {}
    projects = doc.get('projects')
    for proj_dict in projects:
        project = str(proj_dict.get('project'))
        if project:
            # modules:
            if proj_dict.get('modules'):
                for mod_n in proj_dict.get('modules').split(','):
                    if project not in list(proj_mod.keys()):
                        proj_mod[project] = [mods[mod_n]]
                    else:
                        proj_mod[project].append(mods[mod_n])

            # processors:
            if proj_dict.get('processors'):
                for proc_n in [s.strip() for s in proj_dict.get(
                        'processors').split(',')]:
                    if project not in list(proj_proc.keys()):
                        proj_proc[project] = [procs[proc_n]]
                    else:
                        proj_proc[project].append(procs[proc_n])

            # yaml_proc:
            if proj_dict.get('yamlprocessors'):
                for yaml_n in [s.strip() for s in proj_dict.get(
                        'yamlprocessors').split(',')]:
                    if project not in list(yaml_proc.keys()):
                        yaml_proc[project] = [yamlprocs[yaml_n]]
                    else:
                        yaml_proc[project].append(yamlprocs[yaml_n])

            # sgp processors:
            _list = proj_dict.get('sgpprocessors', '').split(',')
            _list = [s.strip() for s in _list if s]
            for yaml_n in _list:
                if project not in list(sgp_processors.keys()):
                    sgp_processors[project] = [sgpprocs[yaml_n]]
                else:
                    sgp_processors[project].append(sgpprocs[yaml_n])

    # set in attrs:
    attrs['project_process_dict'] = proj_proc
    attrs['project_modules_dict'] = proj_mod
    attrs['yaml_dict'] = yaml_proc
    attrs['project_sgp_processors'] = sgp_processors

    # Delete unsupported arguments
    attrs.pop('skip_lastupdate', None)

    attrs['job_template'] = doc.get('jobtemplate')
    attrs['timeout_emails'] = doc.get('timeout_emails')
    attrs['smtp_host'] = doc.get('smtp_host')

    # Return a launcher with specified arguments
    resdir = doc.get('resdir')
    return launcher.Launcher(resdir, **attrs)


def check_default_keys(yaml_file, doc):
    """ Static method to raise error if key not found in dictionary from
    yaml file.
    :param yaml_file: path to yaml file defining the processor
    :param doc: doc dictionary extracted from the yaml file
    """
    # processors / modules / yamlprocessors are not required
    for key in ['projects', 'attrs']:
        raise_yaml_error_if_no_key(doc, yaml_file, key)


def raise_yaml_error_if_no_key(doc, yaml_file, key):
    """Method to raise an execption if the key is not in the dict
    :param doc: dict to check
    :param yaml_file: YAMLfile path
    :param key: key to search
    """
    if key not in list(doc.keys()):
        err = 'YAML File {} does not have {} defined. See example.'
        raise DaxError(err.format(yaml_file, key))


def load_from_file(filepath, args, logger, singularity_imagedir=None, job_template=None):
    """
    Check if a file exists and if it's a python file
    :param filepath: path to the file to test
    :return: True the file pass the test, False otherwise
    """
    if args is not None:
        _tmp = 'test.{}(**args)'
    else:
        _tmp = 'test.{}()'

    if not os.path.isfile(filepath):
        raise DaxError('File %s does not exists.' % filepath)

    if filepath.endswith('.py'):
        test = imp.load_source('test', filepath)
        try:
            #print('evaling:' + _tmp.format(os.path.basename(filepath)[:-3]))
            return eval(_tmp.format(os.path.basename(filepath)[:-3]))
        except AttributeError as e:
            #print('attribute error', str(e))
            pass

        err = '[ERROR] Module or processor NOT FOUND in the python file {}.'
        logger.error(err.format(filepath))

    elif filepath.endswith('.yaml'):
        return processors.load_from_yaml(
            XnatUtils, filepath, args, singularity_imagedir, job_template)

    return None


def upload(settings_path, max_threads=1):
    logger = logging.getLogger('dax')

    # Load settings from file
    _launcher_obj = read_yaml_settings(settings_path, logger)

    host = _launcher_obj.xnat_host
    resdir = _launcher_obj.resdir

    lock_dir = os.path.join(resdir, 'FlagFiles')

    # TODO: filter based on projects/sessions

    # Load list of assessors to be uploaded
    upload_queue = launcher.load_task_queue(
        resdir,
        status='COMPLETE',
        proj_filter=None,
        sess_filter=None)

    alist = [_.assessor_label for _ in upload_queue]
    acount = len(alist)

    # Clean lock files
    lockfiles.clean_lockfiles(lock_dir, logger)

    # Count running uploads
    lock_list = os.listdir(lock_dir)
    lock_list = [x for x in lock_list if x.endswith('_Upload.txt')]
    cur_upload_count = len(lock_list)
    logger.info('count of already running uploads:' + str(cur_upload_count))

    num_threads = max_threads - cur_upload_count
    if num_threads < 1:
        logger.info('max uploads already:{}'.format(str(cur_upload_count)))
        return

    logger.info('starting {} upload thread(s)'.format(str(num_threads)))
    sys.stdout.flush()

    pool = Pool(processes=num_threads)
    for aindex, alabel in enumerate(alist):
        sys.stdout.flush()
        pool.apply_async(upload_thread, [host, aindex, alabel, acount, resdir])

    logger.info('waiting for upload pool to finish...')
    sys.stdout.flush()

    pool.close()
    pool.join()

    logger.info('upload pool finished')
    sys.stdout.flush()


def upload_thread(xnat_host, pindex, assessor_label, pcount, resdir):
    # TODO: move this and associated functions to launcher
    logger = logging.getLogger('dax')

    lock_dir = os.path.join(resdir, 'FlagFiles')

    # Get lock file name
    lock_file = os.path.join(lock_dir, '{}_Upload.txt'.format(assessor_label))

    # Try to lock
    success = lockfiles.lock_flagfile(lock_file)
    if not success:
        # Failed to get lock
        logger.warn('failed to get lock:{}'.format(lock_file))
        return

    try:
        logger.info('connecting to xnat for upload:{}'.format(xnat_host))
        # Upload the assessor
        with XnatUtils.get_interface(xnat_host) as xnat:
            msg = '*Upload Process:{}/{}:{}'.format(
                pindex + 1, pcount, assessor_label)
            logger.info(msg)

            assessor_path = os.path.join(resdir, assessor_label)

            if assessor_utils.is_sgp_assessor(assessor_label):
                # It's a subject gen proc assessor, handle it specifically
                dax_tools_utils.upload_assessor_subjgenproc(
                    xnat, assessor_path)
            else:
                assessor_dict = assessor_utils.parse_full_assessor_name(
                    assessor_label)
                if assessor_dict:
                    uploaded = dax_tools_utils.upload_assessor(
                        xnat, assessor_dict, assessor_path, resdir)
                    if not uploaded:
                        msg = 'not uploaded:{}'.format(assessor_label)
                        logger.warn(msg)
                else:
                    logger.warn('     --> wrong label')
    except Exception as err:
        logger.error('error uploading:{}'.format(err))

    finally:
        # Delete the lock file
        logger.debug('deleting lock file:{}'.format(lock_file))
        lockfiles.unlock_flagfile(lock_file)


def undo_processing(assessor_label, logger=None):
    """
    Unset job information for the assessor on XNAT, Delete files, set to run.

    :return: None

    """

    if not logger:
        logger = logging.getLogger()

    logger.info('undo assessor')

    with XnatUtils.get_interface() as xnat:

        # First use the assessor label to find the assessor on XNAT
        if assessor_utils.is_sgp_assessor(assessor_label):
            logger.info('connect to sgp assessor')
            adict = assessor_utils.parse_full_assessor_name(assessor_label)
            assr = xnat.select_sgp_assessor(
                adict['project_id'],
                adict['subject_label'],
                adict['label'])
        else:
            logger.info('connect to genproc assessor')
            adict = assessor_utils.parse_full_assessor_name(assessor_label)
            assr = xnat.select_assessor(
                adict['project_id'],
                adict['subject_label'],
                adict['session_label'],
                adict['label'])

        # Reset job related fields
        logger.info('setting job info to null')
        xsitype = assr.datatype().lower()
        assr.attrs.set('{}/{}'.format(xsitype, 'jobnode'), 'null')
        assr.attrs.set('{}/{}'.format(xsitype, 'jobid'), 'null')
        assr.attrs.set('{}/{}'.format(xsitype, 'jobstartdate'), 'null')
        assr.attrs.set('{}/{}'.format(xsitype, 'memused'), 'null')
        assr.attrs.set('{}/{}'.format(xsitype, 'walltimeused'), 'null')
        assr.attrs.mset({
            '{}/{}'.format(xsitype, 'procstatus'): 'NEED_INPUTS',
            '{}/{}'.format(xsitype, 'validation/status'): 'Job Pending'})

        # Get list of file resources
        if assessor_utils.is_sgp_assessor(assessor_label):
            resources = assr.resources()
        else:
            resources = assr.out_resources()

        # Delete the resources
        for res in resources:
            res_label = res.label()

            if res_label in ['OLD', 'EDITS']:
                logger('skipping resource:{}'.format(res_label))
                continue

            logger.info('removing:{}'.format(res_label))
            try:
                res.delete()
            except Exception:
                logger.error('deleting resource')
