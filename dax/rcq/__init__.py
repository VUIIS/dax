""" rcq implements a job queue for DAX in REDCap. Launch/Update/Finish, no build or upload here."""
import logging

from .taskbuilder import TaskBuilder
from .tasklauncher import TaskLauncher
from .taskqueue import TaskQueue

logger = logging.getLogger('dax.rcq')


# TODO: handle analysis job that only needs to be launched/updated but not
# uploaded. The job will upload it's own output. so when it's "completed" it's
# done. On finish we just need to update on redcap and delete from disk.
# Does Analysis job have a taskqueue entry or is job information stored in
# Analysis table?

# LAUNCH: requires TaskQueue from projects_redcap and slurm
# BUILD: requires Processors and TaskQueue from projects_redcap and xnat
# UPDATE: required projects_redcap and slurm
# SYNC: requires TaskQueue from projects_redcap and xnat


# TaskBuilder:
# instances_redcap
# projects_redcap
# xnat
# build()

# TaskQueue:
# projects_redcap
# get_open_tasks()
# add_task()
# apply_updates()


def update_all(rc, instances, xnat, yamldir):
    logging.info('connecting to redcap')
    def_field = rc.def_field
    projects = [x[def_field] for x in rc.export_records(fields=[def_field])]

    logging.info('Running build of tasks in XNAT and REDCap queue')
    task_builder = TaskBuilder(rc, xnat, yamldir)
    for p in projects:
        logging.debug(f'building:{p}')
        task_builder.update(p)

    logging.info('Running update of queue from REDCap to SLURM')
    task_launcher = TaskLauncher(instances, rc)
    task_launcher.update()

    logging.info('Running sync of queue status from XNAT to REDCap')
    task_queue = TaskQueue(rc)
    task_queue.sync(xnat)

    logging.info('Done!')
