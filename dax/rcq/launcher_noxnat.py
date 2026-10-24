""" Launches and track job queue for DAX."""

import os
import logging
import json
import subprocess
from datetime import date
import shutil
import time
import traceback

import pandas as pd

from ..cluster import PBS, cj_subcmd, DAX_SETTINGS, command_found
from ..lockfiles import lock_flagfile, unlock_flagfile
from ..processors_noxnat import ProcessorNoXnat, load_from_yaml_noxnat
from .database_noxnat import DatabaseNoXnat


logger = logging.getLogger('dax')


DONE_STATUSES = ['COMPLETE', 'JOB_FAILED', 'LOST']

SUBDIRS = ['OUTLOG', 'PBS', 'PROCESSOR']

COMPLETED_STATUSES = ['COMPLETED', 'FAILED', 'CANCELLED', 'NODE_FAIL', 'OUT_OF_MEMORY', 'TIMEOUT']


class TaskLauncherNoXnat(object):
    # Launches tasks on cluster and tracks updates

    def __init__(self, rootdir):
        self._rootdir = rootdir
        self._dbfile = f'{rootdir}/db/dax.duckdb'
        self._db = DatabaseNoXnat(self._dbfile)
        self._data = self._load_data()
        self._singularitys_dir = f'{rootdir}/singularitys'
        self._yamldir = f'{rootdir}/processors'
        self._logs_dir = f'{rootdir}/logs'
        self._assrs_dir = f'{rootdir}/assessors'
        self._flags_dir = f'{rootdir}/flagfiles'
        self._templates_dir = f'{rootdir}/templates'
        self._perlimit = 25
        self._qlimit = 10
        self._plimit = 10

    def _load_data(self):
        return self._db.load_data()

    def _load_queue(self):
        logger.debug('loading current taskqueue records')
        records = self._db.load_taskqueue().to_dict('records')

        # Filter to only open jobs
        records = [x for x in records if x['PROCSTATUS'] not in DONE_STATUSES]

        # Ignore deleted
        records = [x for x in records if x['PROCSTATUS'] != 'DELETED']

        return records

    def _update_running(self):
        """Update running jobs and apply to db"""
        records = self._load_queue()
        updates = []
        running_list = [x for x in records if x['PROCSTATUS'] == 'RUNNING']

        # Update each task
        for i, t in enumerate(running_list):
            # check on running job
            assr = t['ASSR']
            logger.debug(f'checking on running job:{assr}')
            task_updates = get_running_updates(t)
            if task_updates:
                # Add to batch updates
                logger.info(f'task updates:{task_updates}')
                updates.append(task_updates)

        if updates:
            # apply changes
            logger.info(f'updating database:{updates}')
            try:
                self._apply_updates(updates)
            except Exception as err:
                logger.error(f'error while applying task updates:{err}')

    def _update_completed(self):
        """Update completed jobs and apply to db"""
        records = self._load_queue()
        updates = []
        completed_list = [x for x in records if x['PROCSTATUS'] in [COMPLETED_STATUSES]]

        # Finish completed jobs
        for i, t in enumerate(completed_list):
            try:
                logger.info(f'complete task:{assr}')
                task_updates = self._complete_task(t)
            except FileNotFoundError as err:
                print(assr, err)
                logger.error(f'failed to complete, skipping:{assr}:{err}')
                continue

            # Add to updates
            updates.append(task_updates)

        if updates:
            # apply changes
            logger.info(f'updating database:{updates}')
            try:
                self._apply_updates(updates)
            except Exception as err:
                logger.error(f'error while applying task updates:{err}')

    def _launch(self):
        q_limit = self._qlimit
        p_limit = self._plimit
        updates = []
        launch_list = []
        running_list = []
        records = self._load_queue()

        # Load lists of tasks currently running and ready to launch
        running_list = [x for x in records if x['PROCSTATUS'] == 'RUNNING']
        launch_list = [x for x in records if x['PROCSTATUS'] == 'QUEUED']

        if self._perlimit:
            # Apply proc/proj limits, filter out proc/proj over limits
            logger.info(f'applying proc/proj limits to launch list:n={len(launch_list)}')
            launch_list = self._apply_perlimit(launch_list, running_list)
            logger.info(f'ready to launch:n={len(launch_list)}')

        # Launch jobs
        for i, t in enumerate(launch_list):
            launched, pending = count_jobs()
            logger.info(f'Cluster:{launched}/{q_limit} total, {pending}/{p_limit} pending')

            if launched >= q_limit:
                logger.info(f'queue limit reached:{q_limit}')
                break

            if pending >= p_limit:
                logger.info(f'pending limit reached:{p_limit}')
                break

            assr = t['ASSR']
            proj = t['PROJECT']
            outdir = f'{self._assrs_dir}/{proj}/{assr}'

            if os.path.exists(outdir):
                logger.info(f'cannot launch, found existing dir, setting status to RUNNING:{outdir}')
                updates.append({
                    'ASSR': assr,
                    'STATUS': 'RUNNING',
                })
                continue

            try:
                logger.debug(f'launch:{i}:{assr}')

                make_task_dirs(outdir)

                # Copy from local
                src = os.path.join(self._yamldir, t['YAMLFILE'])
                dst = os.path.join(
                    f'{outdir}/PROCESSOR',
                    os.path.basename(t['YAMLFILE'])
                )
                shutil.copyfile(src, dst)
                t['YAMLFILE'] = dst
                t['outdir'] = outdir

                # Launch it!
                jobid = self.launch_task(t)
                if not jobid:
                    raise Exception('launch failed')

                updates.append({
                    'ASSR': assr,
                    'STATUS': 'RUNNING',
                    'JOBID': jobid,
                })

            except Exception as err:
                logger.error(err)
                traceback.print_exc()
                updates.append({
                    'ASSR': assr,
                    'STATUS': 'LAUNCH_FAILED',
                })
                #delete_task_dirs(outdir)
                print(f'delete_task_dirs:{outdir}')

        if updates:
            # upload changes
            logger.debug(f'updating database:{updates}')
            try:
                self._apply_updates(updates)
            except Exception as err:
                logger.error(f'error while applying updates:{err}')

    def _apply_updates(self, updates):
        print(f'applyihg updates to db:{updates}')

    def update(self, launch_enabled=True, projects=None):
        """Update all tasks in taskqueue of projects_redcap."""

        # Try to lock
        lock_file = f'{self._flags_dir}/rcq.pid'
        success = lock_flagfile(lock_file)
        if not success:
            # Failed to get lock
            logger.error('failed to get lock:{}'.format(lock_file))
            return

        try:
            # Update currently running
            self._update_running()

            # Update completed
            self._update_completed()

            # Launch
            if launch_enabled:
                self._launch()

        finally:
            # Delete the lock file
            logger.debug(f'deleting lock file:{lock_file}')
            unlock_flagfile(lock_file)

    def _apply_perlimit(self, launch_list, running_list):
        result_list = []
        per_limit = int(self._perlimit)
        running_counts = {}

        # Get the proj/proc tuples from launch list, count existing, count new, apply
        if len(running_list) > 0:
            df = pd.DataFrame(running_list)
            df['PROCTYPE'] = df['ASSR'].str.rsplit('-x-', n=2).str[1]
            running_counts = df.groupby(['PROJECT', 'PROCTYPE']).size().to_dict()

        for x in launch_list:
            proctype = x['ASSR'].rsplit('-x-', 2)[1]
            project = x['PROJECT']

            if (project, proctype) not in running_counts:
                # Initialize proj/type with nothing yet running
                running_counts[(project, proctype)] = 0

            if running_counts[(project, proctype)] >= per_limit:
                logger.debug(f'cannot launch, too many already running:{project}:{proctype}')
                continue

            # Append to list and increment counter for proj/type
            logger.debug(f'appending to launch list:{project}:{proctype}')
            result_list.append(x)
            running_counts[(project, proctype)] += 1

        return result_list

    def create_complete_flag(self, assr):
        open(f'{self._assrs_dir}/{assr}/READY_TO_COMPLETE.txt', 'w').close()

    def create_failed_flag(self, assr):
        open(f'{self._assrs_dir}/{assr}/JOB_FAILED.txt', 'w').close()

    def has_ready_flag(self, assr):
        return os.path.exists(f'{self._assrs_dir}/{assr}/READY_TO_UPLOAD.txt')

    def has_failed_flag(self, assr):
        return os.path.exists(f'{self._assrs_dir}/{assr}/JOB_FAILED.txt')

    def launch_task(self, task):
        """Launch task as SLURM Job, write batch and submit. Return job id."""
        assr = task['ASSR']
        outdir = task['outdir']
        walltime = task['WALLTIME']
        memreq = task['MEMREQ']
        inputlist = json.loads(task['INPUTLIST'], strict=False)
        var2val = json.loads(task['VAR2VAL'].replace('\\\\', '\\'), strict=False)
        yaml_file = task['YAMLFILE']
        user_inputs = json.loads(task['USERINPUTS'] or 'null', strict=False)
        imagedir = self._singularitys_dir
        job_template = f'{self._templates_dir}/job_template_noxnat.txt'
        batch_file = f'{outdir}/PBS/{assr}.slurm'
        outlog = f'{outdir}/OUTLOG/{assr}.txt'
        jobdir = f'/tmp/{assr}'
        spec_file = f'{outdir}/PROCESSOR/{assr}.txt'

        # Load the processor
        processor = load_from_yaml_noxnat(
            yaml_file,
            user_inputs=user_inputs,
            job_template=job_template,
            singularity_imagedir=imagedir,
        )

        # Build the command text
        cmds = processor.build_text(
            var2val,
            inputlist,
            jobdir,
            outdir,
            'NOXNAT',
            'NOXNAT')

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
            job_template=job_template,
            xnat_host='NOXNAT'
        )

        # Save to file
        batch.write()

        # Write the processor spec file to be used for info on pdf
        processor.write_processor_spec(spec_file)

        # Submit the saved file
        if not command_found('squeue'):
            raise Exception('squeue command not found')

        jobid, job_failed = batch.submit(outlog=outlog)
        logger.info(f'job submit results:{jobid}:{job_failed}')

        return jobid

    def complete_task(self, task):
        """Complete task"""
        assr = task['ASSR']
        today_str = str(date.today())

        # Check for failed job
        if not self.has_ready_flag(assr):

            # Create failed flag
            if not self.has_failed_flag(assr):
                self.create_failed_flag(assr)

            # Set task status to be saved as failed
            task['task_status'] = 'JOB_FAILED'

        # Save attributes to disk
        self.save_results(task, filename)

        # Finally, complete flag
        self.create_complete_flag(assr)

    def _save_results(self, task, filename):
        with open(filename, 'w') as f:
            for keys in ['JOBID', 'JOBNODE', 'JOBSTART', 'MEMUSED', 'TIMEUSED', 'STATUS']:
                f.write(key +'=' + value + '\n')


def get_running_updates(task):
    """Update information about given task from local SLURM."""
    assr = task['ASSR']
    task_updates = {}

    if not task.get('JOBID', ''):
        logger.info(f'no jobid for task:{assr}')
        return {}

    jobid = task['JOBID']
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
        if job_mem and job_mem != task.get('MEMUSED', ''):
            task_updates['MEMUSED'] = job_mem

        if job_time and job_time != task.get('TIMEUSED', ''):
            task_updates['TIMEUSED'] = job_time

    if job_node and job_node != task.get('JOBNODE', ''):
        task_updates['JOBNODE'] = job_node

    if job_start and job_start != task.get('JOBSTART', ''):
        task_updates['JOBSTART'] = job_start

    if job_end and job_end != 'Unknown' and job_end != task.get('task_jobend', ''):
        task_updates['JOBEND'] = job_end

    if job_state != task['PROCSTATUS']:
        logger.debug(f'changing status to:{job_state}')
        task_updates['PROCSTATUS'] = job_state

    return task_updates


def count_jobs():
    """
    Count the number of jobs in the queue on the cluster
    :return: number of jobs in the queue as tuple of (launched, pending)
    """
    if not command_found('squeue'):
        raise Exception('cannot count jobs, squeue command not found')    

    try:
        launched = cj_subcmd(DAX_SETTINGS.get_cmd_count_jobs_launched())
        pending = cj_subcmd(DAX_SETTINGS.get_cmd_count_jobs_pending())
    except Exception as err:
        raise 'failed to count jobs:{err}'
 
    print(f'{launched=}, {pending=}')
    return (launched, pending)


def make_task_dirs(taskdir):
    """Make subdirectories for task directory."""
    for subdir in ['OUTLOG', 'PBS', 'PROCESSOR']:
        try:
            os.makedirs(os.path.join(taskdir, subdir))
        except FileExistsError:
            pass
