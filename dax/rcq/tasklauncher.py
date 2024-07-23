""" rcq implements a job queue for DAX in REDCap. Launch and Finish."""

import os
import logging
import json
import subprocess
from datetime import date
import shutil
import time

from ..processors import load_from_yaml
from ..cluster import PBS, count_jobs
from ..lockfiles import lock_flagfile, unlock_flagfile


logger = logging.getLogger('manager.rcq.tasklauncher')

DONE_STATUSES = ['COMPLETE', 'JOB_FAILED']

SUBDIRS = ['OUTLOG', 'PBS', 'PROCESSOR']


class TaskLauncher(object):
    def __init__(self, projects_redcap, instance_settings):
        self._projects_redcap = projects_redcap
        self._instance_settings = instance_settings
        self.resdir = self._instance_settings['main_resdir']

    def update(self, launch_enabled=True, projects=None):
        """Update all tasks in taskqueue of projects_redcap."""
        launch_list = []
        updates = []
        resdir = self._instance_settings['main_resdir']
        def_field = self._projects_redcap.def_field
        projects_redcap = self._projects_redcap
        instance_settings = self._instance_settings

        # Try to lock
        lock_file = f'{resdir}/FlagFiles/rcq.pid'
        success = lock_flagfile(lock_file)
        if not success:
            # Failed to get lock
            logger.warn('failed to get lock:{}'.format(lock_file))
            return

        try:
            # Get the current task table
            if projects:
                logger.info(f'loading current taskqueue records:{projects}')
                rec = projects_redcap.export_records(
                    records=projects,
                    forms=['taskqueue'],
                    fields=[def_field])
            else:
                logger.info('loading current taskqueue records')
                rec = projects_redcap.export_records(
                    forms=['taskqueue'],
                    fields=[def_field])

            # Filter to only open jobs
            rec = [x for x in rec if x['redcap_repeat_instrument'] == 'taskqueue']
            rec = [x for x in rec if x['task_status'] not in DONE_STATUSES]

            # Update each task
            logger.debug('updating each task')
            for i, t in enumerate(rec):
                assr = t['task_assessor']
                status = t['task_status']

                logger.debug(f'{i}:{assr}:{status}')

                if status in ['NEED_INPUTS', 'UPLOADING']:
                    pass
                elif status == 'RUNNING':
                    # check on running job
                    logger.debug('checking on running job')
                    task_updates = get_updates(t)
                    if task_updates:
                        task_updates.update({
                            def_field: t[def_field],
                            'redcap_repeat_instrument': 'taskqueue',
                            'redcap_repeat_instance': t['redcap_repeat_instance'],
                        })

                        # Add to redcap updates
                        updates.append(task_updates)
                elif status in ['COMPLETED', 'FAILED', 'CANCELLED']:
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

                    try:
                        # Move to disk queue for upload
                        self.task_to_diskq(t)
                        task_status = 'UPLOADING'
                    except FileNotFoundError as err:
                        logger.warn(f'failed to update, lost:{assr}:{err}')
                        task_status = 'LOST'

                    # Add to redcap updates
                    updates.append({
                        def_field: t[def_field],
                        'redcap_repeat_instrument': 'taskqueue',
                        'redcap_repeat_instance': t['redcap_repeat_instance'],
                        'task_status': task_status,
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
                    projects_redcap.import_records(updates)
                except Exception as err:
                    err = 'connection to REDCap interrupted'
                    logger.error(err)

            # TODO: sort or randomize list???

            if launch_enabled:
                q_limit = int(instance_settings['main_queuelimit'])
                p_limit = int(instance_settings['main_queuelimit_pending'])
                u_limit = int(instance_settings['main_limit_pendinguploads'])
                launch_delay = int(instance_settings['main_launch_delay_sec'])

                # Launch jobs
                updates = []
                for i, t in enumerate(launch_list):
                    launched, pending, uploads = count_jobs(resdir)
                    logger.info(f'Cluster:{launched}/{q_limit} total, {pending}/{p_limit} pending, {uploads}/{u_limit} uploads')

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
                        logger.info(f'cannot launch, found existing dir:{outdir}')
                        continue

                    make_task_dirs(outdir)

                    try:
                        logger.debug(f'launch:{i}:{assr}')

                        # Locate the processor yaml file
                        if t['task_yamlfile'] == 'CUSTOM':
                            # Download it locally
                            logger.debug('get custom yaml file')
                            t['task_yamlfile'] = self.save_processor_file(
                                t[def_field],
                                t['redcap_repeat_instance'],
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

                        # Launch it!
                        jobid = self.launch_task(t)
                        if jobid:
                            updates.append({
                                def_field: t[def_field],
                                'redcap_repeat_instrument': 'taskqueue',
                                'redcap_repeat_instance': t['redcap_repeat_instance'],
                                'task_status': 'RUNNING',
                                'task_jobid': jobid,
                            })

                        time.sleep(launch_delay)

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

    def create_complete_flag(self, assr):
        open(f'{self.resdir}/{assr}/READY_TO_COMPLETE.txt', 'w').close()

    def create_failed_flag(self, assr):
        open(f'{self.resdir}/{assr}/JOB_FAILED.txt', 'w').close()

    def has_ready_flag(self, assr):
        return os.path.exists(f'{self.resdir}/{assr}/READY_TO_UPLOAD.txt')

    def has_failed_flag(self, assr):
        return os.path.exists(f'{self.resdir}/{assr}/JOB_FAILED.txt')

    def launch_task(self, task):
        """Launch task as SLURM Job, write batch and submit. Return job id."""
        instance_settings = self._instance_settings

        assr = task['task_assessor']
        outdir = task['outdir']
        walltime = task['task_walltime']
        memreq = task['task_memreq']
        inputlist = json.loads(task['task_inputlist'], strict=False)
        var2val = json.loads(task['task_var2val'].replace('\\\\', '\\'), strict=False)
        yaml_file = task['task_yamlfile']
        user_inputs = json.loads(
            task['task_userinputs'] or 'null', strict=False)
        imagedir = instance_settings['main_singularityimagedir']
        xnat_host = instance_settings['main_xnathost']
        xnat_user = task.get('xnat_user', 'daxspider')
        job_template = instance_settings['main_rcqjobtemplate']
        job_rungroup = instance_settings['main_rungroup']
        batch_file = f'{outdir}/PBS/{assr}.slurm'
        outlog = f'{outdir}/OUTLOG/{assr}.txt'
        jobdir = f'/tmp/{assr}'
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

    def task_to_diskq(self, task):
        """Transfer task from rcq to diskq (for uploading)."""
        resdir = self._instance_settings['main_resdir']
        diskq = f'{resdir}/DISKQ'
        assr = task['task_assessor']
        today_str = str(date.today())

        # Check for failed job
        if not self.has_ready_flag(assr):

            # Create failed flag  
            if not self.has_failed_flag(assr):
                self.create_failed_flag(assr)

            # Set task status to be saved as failed
            task['task_status'] = 'JOB_FAILED'

        # Save attributes to disk
        save_attr(f'{diskq}/jobstartdate/{assr}', today_str)
        save_attr(f'{diskq}/jobid/{assr}', task['task_jobid'])
        save_attr(f'{diskq}/memused/{assr}', task['task_memused'])
        save_attr(f'{diskq}/walltimeused/{assr}', task['task_timeused'])
        save_attr(f'{diskq}/jobnode/{assr}', task['task_jobnode'])

        if task['task_status'] in ['COMPLETED', 'COMPLETE']:
            save_attr(f'{diskq}/procstatus/{assr}', 'COMPLETE')
        else:
            save_attr(f'{diskq}/procstatus/{assr}', 'JOB_FAILED')

        # Copy batch file to diskq so upload works correctly
        try:
            os.makedirs(f'{diskq}/BATCH')
        except FileExistsError:
            pass
        shutil.copyfile(
            f'{resdir}/{assr}/PBS/{assr}.slurm',
            f'{diskq}/BATCH/{assr}.slurm'
        )

        # Copy processor files for info on pdf
        try:
            os.makedirs(f'{diskq}/processor')
        except FileExistsError:
            pass

        shutil.copy(
            task['task_yamlfile'],
            f'{diskq}/processor'
        )
        shutil.copyfile(
            f'{resdir}/{assr}/PROCESSOR/{assr}.txt',
            f'{diskq}/processor/{assr}'
        )

        # Finally, Set ready to complete flag to trigger upload
        self.create_complete_flag(assr)

    def save_processor_file(self, project, repeat_id, outdir):
        """Export file from REDCap, write to outdir with source filename."""

        # Get the file contents from REDCap
        try:
            (cont, hdr) = self._projects_redcap.export_file(
                record=project,
                field='task_yamlupload',
                repeat_instance=repeat_id)

            if cont == '':
                raise Exception('error exporting file from REDCap')
        except Exception as err:
            logger.error(f'downloading file:{err}')
            return None

        # Save contents to local file
        filename = os.path.join(outdir, hdr['name'])
        try:
            with open(filename, 'wb') as f:
                f.write(cont)

            return filename
        except FileNotFoundError as err:
            logger.error(f'file not found:{filename}:{err}')
            return None


def make_task_dirs(taskdir):
    """Make subdirectories for task directory."""
    for subdir in SUBDIRS:
        try:
            os.makedirs(os.path.join(taskdir, subdir))
        except FileExistsError:
            pass


def get_updates(task):
    """Update information about given task from local SLURM."""
    assr = task['task_assessor']
    task_updates = {}

    if not task.get('task_jobid', ''):
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

    return task_updates


def save_attr(path, value):
    """Save attribute by writing given value to given file path."""
    try:
        os.makedirs(os.path.dirname(path))
    except FileExistsError:
        pass

    with open(path, 'w') as f:
        f.write(str(value) + '\n')
