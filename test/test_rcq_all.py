'''Test rcq REDCap Queue sync by running an update.'''
import logging
import os

import redcap

from dax import XnatUtils
from dax.rcq.taskqueue import TaskQueue
from dax.rcq.tasklauncher import TaskLauncher

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s:%(module)s:%(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('connecting to redcap')
    api_url = 'https://redcap.vanderbilt.edu/api/'
    projects_redcap = redcap.Project(
        api_url, os.environ['API_KEY_DAX_RCQ'])
    task_queue = TaskQueue(projects_redcap)

    logging.info('Running it')
    with XnatUtils.get_interface() as xnat:
        task_queue.sync(xnat)
        logging.info('Done!')

    instance_redcap = redcap.Project(
        api_url, os.environ['API_KEY_DAX_INSTANCES'])
    task_launcher = TaskLauncher(instance_redcap, projects_redcap)
    task_launcher.update()
