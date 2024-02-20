'''Test rcq REDCap Queue sync by running an update.'''
import logging
import os
import tempfile

import redcap

from dax import XnatUtils
from dax.rcq.taskqueue import TaskQueue
from dax.rcq.tasklauncher import TaskLauncher
from dax.rcq.taskbuilder import TaskBuilder

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s:%(module)s:%(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

    api_url = 'https://redcap.vanderbilt.edu/api/'
    yamldir = '/data/mcr/centos7/dax_processors'

    logging.info('connecting to redcap')

    rc = redcap.Project(api_url, os.environ['API_KEY_DAX_RCQ'])
    instances = redcap.Project(api_url, os.environ['API_KEY_DAX_INSTANCES'])
    def_field = rc.def_field
    projects = [x[def_field] for x in rc.export_records(fields=[def_field])]

    with XnatUtils.get_interface() as xnat:
        logging.info('Running sync')
        task_queue = TaskQueue(rc)
        task_queue.sync(xnat)
        logging.info('Done!')

        logging.info('Running launch')
        task_launcher = TaskLauncher(instances, rc)
        task_launcher.update()

        logging.info('Running build')
        task_builder = TaskBuilder(rc, xnat, yamldir)
        for p in projects:
            logging.debug(f'building:{p}')
            task_builder.update(p)

    logging.info('All Done!')
