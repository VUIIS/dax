""" rcq implements a job queue for DAX in REDCap. Launch/Update/Finish, no build or upload here."""
import logging

from ..utilities import get_this_instance
from ..XnatUtils import get_interface

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


def update(rc, instances, build_enabled=True, launch_enabled=True):
    logger.info('connecting to redcap')
    def_field = rc.def_field
    projects = [x[def_field] for x in rc.export_records(fields=[def_field])]
    instance_settings = _load_instance_settings(instances)
    yamldir = instance_settings['main_processorlib']

    with get_interface() as xnat:

        if build_enabled:
            logger.info('Running build of tasks in XNAT and REDCap queue')
            task_builder = TaskBuilder(rc, xnat, yamldir)
            for p in projects:
                logger.debug(f'building:{p}')
                task_builder.update(p)

        logger.info('Running update of queue from REDCap to SLURM')
        task_launcher = TaskLauncher(rc, instance_settings)
        task_launcher.update(launch_enabled=launch_enabled)

        logger.info('Running sync of queue status from XNAT to REDCap')
        task_queue = TaskQueue(rc)
        task_queue.sync(xnat)


def _load_instance_settings(instance_redcap):
    """Load DAX settings for current instance from REDCap"""
    instance_name = get_this_instance()
    logger.debug(f'instance={instance_name}')

    # Return the record associated with this instance_name
    return instance_redcap.export_records(
        records=[instance_name], raw_or_label='label')[0]
