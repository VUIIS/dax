from . import subjgenproc
from . import bin
import sys
import logging

# should we have a "project" class which loads all the assr,scan, and sgp
# and has functions to get info at each level?
# for now let's try to build from context that has access to all those lists of data
# need to decide if/when to reload, wil we know when we need to?

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


project = 'DepMIND2'
settingspath = '/Users/boydb1/settings-subjgenproc.yaml'
xnat = XnatUtils.get_interface()
daxlauncher = bin.read_yaml_settings(settingspath, logging.getLogger())

subjgenproc.build_project_subjgenproc(xnat, daxlauncher, project)


# TODO: sgp processor.parse
# TODO: sgp task.build_task
