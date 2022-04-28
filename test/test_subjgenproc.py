# TODO: daxlauncher.upload()

import logging

from dax import bin, XnatUtils


# Create the launcher
settingspath = '/Users/boydb1/.dax/settings/settings-subjgenproc.yaml'
daxlauncher = bin.read_yaml_settings(settingspath, logging.getLogger())

# Get xnat connection
xnat = XnatUtils.get_interface(host=daxlauncher.xnat_host)

# Build
print('building')
project = 'DepMIND2'
daxlauncher.build_project_subjgenproc(xnat, project)

print('All Done!')
