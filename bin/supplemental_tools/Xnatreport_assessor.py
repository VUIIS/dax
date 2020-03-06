#!/usr/bin/env python

import json
import sys
import pandas
import pyxnat
from dax import XnatUtils
from dax import utilities

if len(sys.argv)!=4 :
    print('Usage:')
    print('python Xnatreport_assessor.py <project> <proctype> <output_csvfile>')
    sys.exit()


project = sys.argv[1]
proctype = sys.argv[2]
outfile = sys.argv[3]

xnat = XnatUtils.get_interface()

Assrs = xnat.list_project_assessors(project)

R = list()
for assr in Assrs :

    if assr.get('proctype') != proctype : continue

    #print(assr['assessor_label'])

    # Get desired fields
    thisR = {}
    for key in ('project_label','subject_label','session_label','proctype',
                'assessor_id','procstatus','qcstatus','assessor_label') :
        thisR[key] = assr[key]

    # Clean up the inputs field, split on / and keep the last bit
    inps = utilities.decode_url_json_string(assr['inputs'])
    #inps = json.loads(assr['inputs'].replace('&quot;','"'))
    for key in inps.keys() :
        thisR[key] = inps[key].split('/')[-1]
    
    # We need to explicitly copy here to avoid overwriting R
    R.append(thisR.copy())


D = pandas.DataFrame(R)

# Reorder columns
colorder = ('project_label','subject_label','session_label','proctype',
            'assessor_id','procstatus','qcstatus')
oldcols = D.columns.tolist()
newcols = list()
for col in colorder :
    newcols.append(col)
    oldcols.remove(col)
newcols.extend(oldcols)

D.to_csv(outfile,index=False,columns=newcols)

