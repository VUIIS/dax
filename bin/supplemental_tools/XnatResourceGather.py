from dax import XnatUtils
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', dest='project', help='Project name', required=True)
parser.add_argument('--sub', dest='subject', help='Subject ID', required=True)
parser.add_argument('--sess', dest='session', help='Session ID', required=True)
args = parser.parse_args()

print('Project: {}'.format(args.project))
print('Subject: {}'.format(args.subject))
print('Session: {}'.format(args.session))
print('Assessors:')

# Get assessor list given proj/subj/sess
xnat = XnatUtils.get_interface()
assessors = xnat.get_assessors(args.project,args.subject,args.session)

# Loop through assessors
for assessor in assessors:
    assessor_string = xnat.get_assessor_path(args.project,args.subject,args.session,assessor['assessor_label'])
    assessor_obj = xnat.select(assessor_string)
    
    # Split assessor_obj string for printing
    assess = str(assessor_obj)
    assess = assess.split(' ')
  
    print('  - assessor_label: {}'.format(assess[2]))

    # Gather assessor inputs
    inputs = XnatUtils.get_assessor_inputs(assessor_obj)

    # If assessor has inputs, print them out here; otherwise say no inputs
    if inputs:
        values = list(inputs.values())
        print('    inputs:')
        cnt = 1
        for fp in values:
            val = fp.split('/')
            print('      - input_{}: {}'.format(cnt,val[7:]))
            cnt += 1
    else:
        print('    inputs: NO INPUTS FOUND')
