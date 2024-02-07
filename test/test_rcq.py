'''Test rcq REDCap Queue by running an update.'''
import os
import logging
import redcap
from dax import rcq


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s:%(module)s:%(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('connecting to redcap')
    api_url = 'https://redcap.vanderbilt.edu/api/'
    projects_redcap = redcap.Project(api_url, os.environ['API_KEY_DAX_RCQ'])
    instance_redcap = redcap.Project(api_url, os.environ['API_KEY_DAX_INSTANCES'])

    logging.info('Running it')
    rcq.update(projects_redcap, instance_redcap)
    logging.info('Done!')
