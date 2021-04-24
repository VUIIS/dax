'''
BIDS to XNAT

Extract the information from BIDS for Xnatupload

@author: Praitayini Kanakaraj, Electrical Engineering, Vanderbilt University

'''
import os

#check if valid bids
#extract and map to dict. 
def transform_to_xnat(bids_dir, project):
    #Check bids dir path exists
    if not os.path.exists(bids_dir):
        print('ERROR: %s path does not exists' % (bids_dir))
        exit()

    #Extract the values from the bids data
    bids_dict = {}
    upload_scan = []
    for root, dir, files in os.walk(bids_dir):
        for i in files:
            if i.endswith('nii.gz') or i.endswith('.bvec') or i.endswith('.bval'):
                bids_filename_contents = i.split('_')

                #resource and resource path
                filepath = os.path.join(root,i)
                if filepath.endswith('nii.gz'):
                    bids_dict['resource'] = {'NIFTI': [filepath]}
                if filepath.endswith('bvec.gz'):
                    bids_dict['resource'] = {'BVEC': [filepath]}
                if filepath.endswith('bval.gz'):
                    bids_dict['resource'] = {'BVAL': [filepath]}

                #subj on xnat
                subject = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('sub')][0]
                bids_dict['subject_label'] = subject 

                #sess on xnat
                session = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('ses')][0]
                bids_dict['session_label'] = session

                #series des on xnat
                bids_dict['series_description'] = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('acq')][0]
                bids_dict['type'] = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('acq')][0]
                
                #scan_id on xnat
                scan_id = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('run')][0]
                bids_dict['ID'] = scan_id
                
                #label <project>-x-<subject>-x-<session>-x-<ID>
                bids_dict['label'] = '-'.join((project,subject,session,scan_id)) 
                
                #other keys
                bids_dict['object_type'] = 'scan'
                bids_dict['project_id'] = project
                bids_dict['session_type'] = 'MR'
                bids_dict['quality'] = 'questionable'

                upload_scan.append(bids_dict.copy())
    return upload_scan
    