'''Test rcq REDCap Queue sync by running an update.'''
import logging
import os

import redcap

from dax import rcqsync, XnatUtils


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s:%(module)s:%(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('connecting to redcap')
    api_url = 'https://redcap.vanderbilt.edu/api/'
    projects_redcap = redcap.Project(api_url, os.environ['API_KEY_DAX_RCQ'])

    logging.info('Running it')
    with XnatUtils.get_interface() as xnat:
        rcqsync.update(projects_redcap, xnat)
        logging.info('Done!')