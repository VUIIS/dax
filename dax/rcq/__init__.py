""" rcq implements a job queue for DAX in REDCap. Launch/Update/Finish, no build or upload here."""
import logging

from ..utilities import get_this_instance
from ..XnatUtils import get_interface

from .taskbuilder import TaskBuilder
from .tasklauncher import TaskLauncher
from .taskqueue import TaskQueue
from .analysislauncher import AnalysisLauncher


logger = logging.getLogger('manager.rcq')


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


def update(rc, instances, build_enabled=True, launch_enabled=True, projects=None):
    logger.info('connecting to redcap')
    def_field = rc.def_field

    if projects is None:
        projects = [x[def_field] for x in rc.export_records(fields=[def_field])]

    instance_settings = _load_instance_settings(instances)
    if not instance_settings:
        logger.debug('no settings found for this instance')
        return

    logger.debug(f'instance_settings={instance_settings}')

    yamldir = instance_settings['main_processorlib']
    logger.debug(f'yamldir={yamldir}')

    with get_interface() as xnat:

        logger.info('Running update of analyses')
        try:
            AnalysisLauncher(xnat, rc, instance_settings).update(
                projects,
                launch_enabled=launch_enabled
            )
        except Exception as err:
            logger.error(f'analyses update failed:{err}')
            pass

        logger.info('Running sync of queue status from XNAT to REDCap')
        TaskQueue(rc).sync(xnat, projects)

        logger.info('Running update of queue from REDCap to SLURM')
        TaskLauncher(rc, instance_settings).update(
                launch_enabled=launch_enabled,
                projects=projects)

        if build_enabled:
            logger.info('Running build of tasks in XNAT and REDCap queue')
            task_builder = TaskBuilder(rc, xnat, yamldir)
            for p in projects:
                logger.debug(f'building:{p}')
                task_builder.update(p)


def _load_instance_settings(instance_redcap):
    """Load DAX settings for current instance from REDCap"""
    instance_name = get_this_instance()
    logger.debug(f'instance={instance_name}')

    # Return the record associated with this instance_name
    records = instance_redcap.export_records(records=[instance_name], raw_or_label='label')
    if len(records) == 0:
        settings = {}
    else:
        settings = records[0]

    return settings
