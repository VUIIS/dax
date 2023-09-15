#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from dax import XnatUtils
import ast
import os
import pandas as pd
import pyxnat
import re
import requests

host = os.environ['XNAT_HOST']
user = 'admin'


def parse_args():
    argp = ArgumentParser(prog='SwitchProjects', formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('--proj', dest='project', default=None, help='Project we want to push from')
    argp.add_argument('--txt', dest='txtFile', default=None, help='Name of file we want to store session list')
    return argp


if __name__ == '__main__':
    PARSER = parse_args()
    OPTIONS = PARSER.parse_args()

    project = OPTIONS.project
    f = open(OPTIONS.txtFile,'a')

    with XnatUtils.get_interface(host=host, user=user) as XNAT:
        subjects = XNAT.get_subjects(project)

        for subject in subjects:
            sessions = XNAT.get_sessions(project, subject['label'])
            for session in sessions:
                scans = XNAT.get_scans(project, subject['label'], session['label'])
                df = pd.DataFrame(scans)
                df = df[['subject_label','session_label','scan_type','scan_label']]
                if 'unknown' in str(df.loc[0]):
                    print('ExamCard found')
                else:
                    patient_id = session['session_label'].split('_')
                    request = 'http://10.109.20.19:8080/dcm4chee-arc/aets/DCM4CHEE57/rs/studies/?PatientID=*{}'.format(patient_id[1])
                    res = requests.get(request)
                    instances = ast.literal_eval(res.text)
                    for j, instance in enumerate(instances):
                        instanceUID = instance['00081190']['Value'][0]
                        instanceUID = instanceUID + '/series'
                        res = requests.get(instanceUID)
                        experiment = ast.literal_eval(res.text)
                        for k, instances in enumerate(experiment):
                            if '0008103E' not in instances:
                                url = instances['00081190']['Value'][0]
                                url = url + '/export/VandyXNAT'
                                res = requests.post(url)
                                print('*****************************')
                                print(patient_id[1])
                                f.write(session['subject_label'] + ' ' + session['session_label'] + ' ' + patient_id[1] + '\n')

    f.close()
