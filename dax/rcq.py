""" rcq implements a job queue for DAX in REDCap. Launch/Update/Finish, no build or upload here."""

import os
import logging
import json
import subprocess
from datetime import date
import shutil

from .processors import load_from_yaml
from .dax_manager import get_this_instance
from .cluster import PBS, count_jobs
from .lockfiles import lock_flagfile, unlock_flagfile


logger = logging.getLogger('dax.rcq')

DONE_STATUSES = ['COMPLETE', 'JOB_FAILED', 'FAILED']

SUBDIRS = ['OUTLOG', 'PBS', 'PROCESSOR']


# TODO: handle analysis job that only needs to be launched/updated but not
# uploaded. The job will upload it's own output. so when it's "completed" it's
# done. On finish we just need to update on redcap and delete from disk.
# Does Analysis job have a taskqueue entry or is job information stored in
# Analysis table?


# TODO: move this to dax_manager as a static method
def load_instance_settings(rc):
    """Load DAX settings for current instance from REDCap"""
    instance_name = get_this_instance()
    logger.debug(f'instance={instance_name}')

    # Return the record associated with this instance_name
    return rc.export_records(records=[instance_name], raw_or_label='label')[0]


def launch(task):
    """Launch task as SLURM Job, write batch and submit. Return job id."""
    assr = task['task_assessor']
    outdir = task['outdir']
    walltime = task['task_walltime']
    memreq = task['task_memreq']
    inputlist = json.loads(task['task_inputlist'], strict=False)
    var2val = json.loads(task['task_var2val'], strict=False)
    yaml_file = task['task_yamlfile']
    user_inputs = task['task_userinputs']
    imagedir = task['imagedir']
    xnat_host = task['xnat_host']
    xnat_user = task.get('xnat_user', 'daxspider')
    job_template = task['job_template']
    job_rungroup = task['job_rungroup']
    batch_file = f'{outdir}/PBS/{assr}.slurm'
    outlog = f'{outdir}/OUTLOG/{assr}.txt'
    jobdir = task['jobdir']
    spec_file = f'{outdir}/PROCESSOR/{assr}.txt'

    # Load the processor
    processor = load_from_yaml(
        None,
        yaml_file,
        user_inputs=user_inputs,
        singularity_imagedir=imagedir,
        job_template=job_template
    )

    # Build the command text
    cmds = processor.build_text(
        var2val,
        inputlist,
        jobdir,
        outdir,
        xnat_host,
        xnat_user)

    # Write the script
    logger.info(f'writing batch file:{batch_file}')
    batch = PBS(
        batch_file,
        outlog,
        [cmds],
        walltime,
        mem_mb=memreq,
        ppn=1,
        env=None,
        email=None,
        email_options='FAIL',
        rungroup=job_rungroup,
        xnat_host=xnat_host,
        job_template=job_template)

    # Save to file
    batch.write()

    # Write the processor spec file to be used for info on pdf
    processor.write_processor_spec(spec_file)

    # Submit the saved file
    jobid, job_failed = batch.submit(outlog=outlog)
    logger.info(f'job submit results:{jobid}:{job_failed}')

    return jobid


def save_file(project, record_id, event_id, repeat_id, field_id, outdir):
    """Save file by exporting from given REDCap record and writing to output directory using source filename."""

    # Get the file contents from REDCap
    try:
        (cont, hdr) = project.export_file(
            record=record_id,
            field=field_id,
            event=event_id,
            repeat_instance=repeat_id)

        if cont == '':
            raise Exception('error exporting file from REDCap')
    except Exception as err:
        logging.error(f'downloading file:{err}')
        return None

    # Save contents to local file
    filename = os.path.join(outdir, hdr['name'])
    try:
        with open(filename, 'wb') as f:
            f.write(cont)

        return filename
    except FileNotFoundError as err:
        logging.error(f'file not found:{filename}:{err}')
        return None


def make_task_dirs(taskdir):
    """Make subdirectories for task directory."""
    for subdir in SUBDIRS:
        try:
            os.makedirs(os.path.join(taskdir, subdir))
        except FileExistsError:
            pass


def update_info(projects_redcap, task):
    """Update information about given task from local SLURM to REDCap."""
    assr = task['task_assessor']
    task_updates = {}

    if 'task_jobid' not in task:
        logger.info(f'no jobid for task:{assr}')
        return

    jobid = task['task_jobid']
    cmd = f'sacct -j {jobid}.batch --units G --noheader -p --format MaxRss,cputime,NodeList,Start,End,State'

    logger.debug(f'running command:{cmd}')

    try:
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode().strip()
    except subprocess.CalledProcessError:
        logger.info(f'error running command:{cmd}')
        return

    if not output:
        logger.debug(f'no output')
        return

    logger.debug(output)

    job_mem,job_time,job_node,job_start,job_end,job_state,_ = output.split('|')

    # only update usage if job is not still running
    if job_state == 'RUNNING':
        logger.debug(f'job still running not setting used:{assr}')
    else:
        if job_mem and job_mem != task.get('task_memused', ''):
            task_updates['task_memused'] = job_mem

        if job_time and job_time != task.get('task_timeused', ''):
            task_updates['task_timeused'] = job_time

    if job_node and job_node != task.get('task_jobnode', ''):
        task_updates['task_jobnode'] = job_node

    if job_state != task['task_status']:
        logger.debug(f'changing status to:{job_state}')
        task_updates['task_status'] = job_state

    if task_updates:
        _def = projects_redcap.def_field
        task_updates[_def] = task[_def]
        task_updates['redcap_repeat_instrument'] = 'taskqueue'
        task_updates['redcap_repeat_instance'] = task['redcap_repeat_instance']

        logger.debug(f'updating task info on redcap:{assr}:{task_updates}')
        try:
            projects_redcap.import_records([task_updates])
        except Exception as err:
            logger.error(err)
    else:
        logger.debug(f'nothing to update:{assr}')


def task_to_diskq(task, diskq):
    """Transfer a task from rcq to diskq (for uploading) by writing task information from REDCap to local files on disk."""
    assr = task['task_assessor']

    today_str = str(date.today())
    save_attr(f'{diskq}/jobstartdate/{assr}', today_str)
    save_attr(f'{diskq}/jobid/{assr}', task['task_jobid'])
    save_attr(f'{diskq}/memused/{assr}', task['task_memused'])
    save_attr(f'{diskq}/walltimeused/{assr}', task['task_timeused'])
    save_attr(f'{diskq}/jobnode/{assr}', task['task_jobnode'])

    if task['task_status'] == 'COMPLETED':
        save_attr(f'{diskq}/procstatus/{assr}', 'COMPLETE')

    # Copy batch file to diskq so upload works correctly
    try:
        os.makedirs(f'{diskq}/BATCH')
    except FileExistsError:
        pass
    shutil.copyfile(
        task['task_batchfile'],
        f'{diskq}/BATCH/{assr}.slurm',
    )

    # Copy processor files for info on pdf
    try:
        os.makedirs(f'{diskq}/processor')
    except FileExistsError:
        pass
    shutil.copy(task['task_yamlfile'], f'{diskq}/processor')
    shutil.copyfile(task['task_specfile'], f'{diskq}/processor/{assr}')


def save_attr(path, value):
    """Save attribute by writing given value to given file path."""
    try:
        os.makedirs(os.path.dirname(path))
    except FileExistsError:
        pass

    with open(path, 'w') as f:
        f.write(str(value) + '\n')


def update(projects_redcap, instance_redcap):
    """Update all tasks in taskqueue of projects_redcap using DAX settings in instance_redcap."""
    launch_list = []
    updates = []
    instance_settings = load_instance_settings(instance_redcap)
    resdir = instance_settings['main_resdir']

    # Try to lock
    lock_file = f'{resdir}/FlagFiles/rcq.pid'
    success = lock_flagfile(lock_file)
    if not success:
        # Failed to get lock
        logger.warn('failed to get lock:{}'.format(lock_file))
        return

    try:
        # Get the current task table
        logger.info('loading current taskqueue records')
        rec = projects_redcap.export_records(
            forms=['taskqueue'],
            fields=[projects_redcap.def_field])

        # Filter to only open jobs
        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'taskqueue']
        rec = [x for x in rec if x['task_status'] not in DONE_STATUSES]

        # Update each task
        logger.debug('updating each task')
        for i, t in enumerate(rec):
            assr = t['task_assessor']
            status = t['task_status']

            logger.info(f'{i}:{assr}:{status}')

            if status == 'NEED_INPUTS':
                pass
            elif status == 'UPLOADING':
                pass
            elif status == 'RUNNING':
                # check on running job
                logger.debug('checking on running job')
                update_info(projects_redcap, t)
            elif status == 'COMPLETED':
                # finish completed job by moving to upload
                logger.debug('setting to upload')

                # Locate the processor yaml file
                if t['task_yamlfile'] == 'CUSTOM':
                    t['task_yamlfile'] = os.path.join(
                        resdir,
                        assr,
                        'PROCESSOR',
                        t['task_yamlupload']
                    )
                else:
                    t['task_yamlfile'] = os.path.join(
                        resdir,
                        assr,
                        'PROCESSOR',
                        t['task_yamlfile']
                    )

                t['task_batchfile'] = f'{resdir}/{assr}/PBS/{assr}.slurm'
                t['task_specfile'] = f'{resdir}/{assr}/PROCESSOR/{assr}.txt'
                task_to_diskq(t, f'{resdir}/DISKQ')

                # Set ready to complete flag to trigger upload
                open(f'{resdir}/{assr}/READY_TO_COMPLETE.txt', 'w').close()

                # Add to redcap updates
                updates.append({
                    projects_redcap.def_field: t[projects_redcap.def_field],
                    'redcap_repeat_instrument': 'taskqueue',
                    'redcap_repeat_instance': t['redcap_repeat_instance'],
                    'task_status': 'UPLOADING',
                })
            elif status == 'QUEUED':
                logger.debug('adding queued job to launch list')
                launch_list.append(t)
            else:
                logger.debug(f'unknown status:{status}')
                continue

        if updates:
            # upload changes
            logger.debug(f'updating redcap:{updates}')
            try:
                response = projects_redcap.import_records(updates)
            except Exception as err:
                err = 'connection to REDCap interrupted'
                logger.error(err)

        # TODO: sort or randomize list???

        q_limit = int(instance_settings['main_queuelimit'])
        p_limit = int(instance_settings['main_queuelimit_pending'])
        u_limit = int(instance_settings['main_limit_pendinguploads'])

        # Launch jobs
        updates = []
        for i, t in enumerate(launch_list):

            launched, pending, uploads = count_jobs(resdir)

            logger.info(f'Cluster:{launched}/{q_limit} total, {pending}/{p_limit} pending, {u_limit}/{uploads} uploads')

            if launched >= q_limit:
                logger.info(f'queue limit reached:{q_limit}')
                break

            if pending >= p_limit:
                logger.info(f'pending limit reached:{p_limit}')
                break

            if uploads >= u_limit:
                logger.info(f'upload limit reached:{u_limit}')
                break

            assr = t['task_assessor']
            outdir = f'{resdir}/{assr}'

            if os.path.exists(outdir):
                logger.info(f'cannot launch, found existing job dir:{outdir}')
                continue

            make_task_dirs(outdir)

            try:
                logger.debug(f'launch:{i}:{assr}')

                # Locate the processor yaml file
                if t['task_yamlfile'] == 'CUSTOM':
                    # Download it locally
                    logger.info('get custom yaml file')
                    t['task_yamlfile'] = save_file(
                        projects_redcap,
                        t[projects_redcap.def_field],
                        None,
                        t['redcap_repeat_instance'],
                        'task_yamlupload',
                        f'{outdir}/PROCESSOR'
                    )
                else:
                    # Copy from local
                    src = os.path.join(
                        instance_settings['main_processorlib'],
                        t['task_yamlfile']
                    )
                    dst = os.path.join(
                        f'{outdir}/PROCESSOR',
                        t['task_yamlfile']
                    )
                    shutil.copyfile(src, dst)
                    t['task_yamlfile'] = dst

                t['outdir'] = outdir
                t['imagedir'] = instance_settings['main_singularityimagedir']
                t['xnat_host'] = instance_settings['main_xnathost']
                t['job_template'] = instance_settings['main_jobtemplate']
                t['job_rungroup'] = instance_settings['main_rungroup']
                t['jobdir'] = f'/tmp/{assr}'

                # Launch it
                jobid = launch(t)
                if jobid:
                    updates.append({
                        projects_redcap.def_field: t[projects_redcap.def_field],
                        'redcap_repeat_instrument': 'taskqueue',
                        'redcap_repeat_instance': t['redcap_repeat_instance'],
                        'task_status': 'RUNNING',
                        'task_jobid': jobid,
                    })
            except Exception as err:
                logger.error(err)
                import traceback
                traceback.print_exc()

        if updates:
            # upload changes
            logger.debug(f'updating redcap:{updates}')
            try:
                projects_redcap.import_records(updates)
            except Exception as err:
                err = 'connection to REDCap interrupted'
                logger.error(err)
    finally:
        # Delete the lock file
        logger.debug(f'deleting lock file:{lock_file}')
        unlock_flagfile(lock_file)
