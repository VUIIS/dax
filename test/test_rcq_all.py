'''Test rcq REDCap Queue sync by running an update.'''
import logging
import os

import redcap

from dax import XnatUtils
from dax import rcq

# dax manager will run builder update, launcher update, then queue sync

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s:%(module)s:%(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

    api_url = 'https://redcap.vanderbilt.edu/api/'
    rc = redcap.Project(api_url, os.environ['API_KEY_DAX_RCQ'])
    instances = redcap.Project(api_url, os.environ['API_KEY_DAX_INSTANCES'])

    rcq.update(rc, instances)
