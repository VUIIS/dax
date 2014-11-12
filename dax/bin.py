#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, imp
from datetime import datetime

def update(settings_path):
    # Load the settings file
    print('INFO:loading settings from:'+settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the updates
    print('INFO:running update, Start Time:'+str(datetime.now()))
    settings.myLauncher.update(lockfile_prefix)
    print('INFO:finished update, End Time: '+str(datetime.now()))

def update_open_tasks(settings_path):
    # Load the settings file
    print('INFO:loading settings from:'+settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the update
    print('INFO:updating open tasks, Start Time:'+str(datetime.now()))
    settings.myLauncher.update_open_tasks(lockfile_prefix)
    print('INFO:finished open tasks, End Time: '+str(datetime.now()))
