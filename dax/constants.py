import os
from os.path import expanduser

USER_HOME = expanduser("~")

#MASIMATLAB dir:
if 'MASIMATLAB_PATH' not in os.environ:
  MASIMATLAB_PATH = os.path.join(USER_HOME,'masimatlab')
else:
  MASIMATLAB_PATH = os.environ['MASIMATLAB']

#Result dir
if 'UPLOAD_SPIDER_DIR' not in os.environ:
  RESULTS_DIR=os.path.join(USER_HOME,'RESULTS_XNAT_SPIDER')
  os.mkdir(RESULTS_DIR)
else:
  RESULTS_DIR=os.environ['UPLOAD_SPIDER_DIR']
