#!/usr/bin/env python

import json
import sys
import pandas
import pyxnat
import argparse
import time
from dax import XnatUtils
from dax import utilities

# Specify and parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('project',help='Project name')
args = parser.parse_args()
print('Project: {}'.format(args.project))


xnat = XnatUtils.get_interface()
Assrs = xnat.list_project_assessors(args.project)
xnat.disconnect()

timestamp = time.strftime("%Y%m%d%H%M%S")
outfile1 = 'status_by_assessor_{}_{}.csv'.format(args.project,timestamp)
outfile2 = 'status_by_session_{}_{}.csv'.format(args.project,timestamp)

R = list()
for assr in Assrs :

    #print(assr['assessor_label'])

    # Get desired fields
    thisR = {}
    for key in ('project_label','subject_label','session_label','proctype',
            'assessor_id','procstatus','qcstatus','qcnotes','assessor_label') :
        thisR[key] = assr[key]

    # Clean up the inputs field, split on / and keep the last bit
    if assr['inputs']:
        inps = utilities.decode_url_json_string(assr['inputs'])
        for key in inps.keys():
            if isinstance(inps[key],list):
                thisR[key] = '(list)'
            else:
                thisR[key] = inps[key].split('/')[-1]
    
    # We need to explicitly copy here to avoid overwriting R
    R.append(thisR.copy())

D = pandas.DataFrame(R)

# Reorder columns
colorder = ('project_label','subject_label','session_label','proctype',
            'assessor_id','procstatus','qcstatus','qcnotes')
oldcols = D.columns.tolist()
newcols = list()
for col in colorder :
    newcols.append(col)
    oldcols.remove(col)
newcols.extend(oldcols)

# Store the full list by assessor
D.to_csv(outfile1,index=False,columns=newcols)


# For each subject, count how many are present and how many complete

proctypes = D['proctype'].unique()
sessions = D['session_label'].unique()

# Loop through sessions, loop through uniques, count statuses
S = list()
for session in sessions:
    
    thisS = {}
    thisD = D.loc[D['session_label']==session,:]

    # Check that we only got one session's data
    sinfo = thisD[['project_label','subject_label','session_label']].drop_duplicates()
    if sinfo.shape[0]!=1:
         # Seems to happen when a label is empty
        print('Unexpected value - skipping in session report:')
        for s in range(sinfo.shape[0]) :
            print('   ' + sinfo['project_label'].values[s] + ' - ' + 
                  sinfo['subject_label'].values[s]  + ' - ' + 
                  sinfo['session_label'].values[s])
        print(' ')

    thisS['project_label'] = sinfo['project_label'].values[0]
    thisS['subject_label'] = sinfo['subject_label'].values[0]
    thisS['session_label'] = sinfo['session_label'].values[0]

    for proctype in proctypes:
        thisthisD = thisD.loc[thisD['proctype']==proctype,:]
        total = thisthisD.shape[0]
        notcomplete = thisthisD.loc[thisthisD['procstatus']!='COMPLETE',:].shape[0]
        thisS[proctype+'_total'] = total
        thisS[proctype+'_notcomplete'] = notcomplete

    S.append(thisS.copy())

DS = pandas.DataFrame(S)

colorder = ('project_label','subject_label','session_label')
oldcols = DS.columns.tolist()
newcols = list()
for col in colorder :
    newcols.append(col)
    oldcols.remove(col)
newcols.extend(oldcols)

DS.to_csv(outfile2,index=False,columns=newcols)

