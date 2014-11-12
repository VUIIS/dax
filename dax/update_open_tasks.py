#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, imp
from datetime import datetime

def parse_args():
    from argparse import ArgumentParser
    ap = ArgumentParser(prog='dax_update_open_tasks', description="Updates open tasks")
    ap.add_argument(dest='settings_path', help='Settings Path')
    return ap.parse_args()

if __name__ == '__main__':   
    args = parse_args()
    settings_path = args.settings_path

    # Load the settings file
    print('INFO:loading settings from:'+settings_path)
    settings = imp.load_source('settings', settings_path)
    lockfile_prefix = os.path.splitext(os.path.basename(settings_path))[0]

    # Run the update
    print('INFO:updating open tasks, Start Time:'+str(datetime.now()))
    settings.myLauncher.update_open_tasks(lockfile_prefix)
    print('INFO:finished open tasks, End Time: '+str(datetime.now()))
