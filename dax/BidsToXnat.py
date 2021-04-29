'''
BIDS to XNAT

Extract the information from BIDS for Xnatupload

@author: Praitayini Kanakaraj, Electrical Engineering, Vanderbilt University

'''
import os
import json
import glob

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
    filepaths_list = []
    xnat_dataset = dataset_source_xnat(bids_dir)
    for root, dir, files in os.walk(bids_dir):
        for i in files:
            if i.endswith('nii.gz') or i.endswith('.bvec') or i.endswith('.bval'):
                bids_filename_contents = i.split('_')

                if xnat_dataset:

                    #get info from json file
                    bids_filename = i.split('.')[0]
                    json_file = bids_filename + '.json'
                    with open(os.path.join(root,json_file), 'r') as f:
                        json_contents = json.load(f)

                    #subj from json
                    subject = json_contents['XNATProvenance'].split('/')[8]
                    bids_dict['subject_label'] = subject 

                    #sess from json
                    session = json_contents['XNATProvenance'].split('/')[10]
                    bids_dict['session_label'] = session

                    #series des (on xnat/bidsmap) from bids
                    bids_dict['series_description'] = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('acq')][0]                
                    
                    #label <project>-x-<subject>-x-<session>-x-<ID>
                    scan_id = json_contents['XNATProvenance'].split('/')[12]
                    bids_dict['label'] = '-'.join((project,subject,session,scan_id)) 
                    
                    #type quality from json
                    bids_dict['ID'] = scan_id
                    bids_dict['type'] = json_contents['ScanType']
                    bids_dict['quality'] = json_contents['ScanQuality']

                    #resource and resource path
                    bids_filepath = os.path.join(root,i)
                    xnat_filepath = os.path.join(root,json_contents['XNATfilename'])
                    os.rename(bids_filepath, xnat_filepath)
                    filepath_set = (bids_filepath, xnat_filepath)

                    if bids_filepath.endswith('nii.gz'):
                        bids_dict['resource'] = {'NIFTI': [xnat_filepath]}
                    if bids_filepath.endswith('bvec.gz'):
                        bids_dict['resource'] = {'BVEC': [xnat_filepath]}
                    if bids_filepath.endswith('bval.gz'):
                        bids_dict['resource'] = {'BVAL': [xnat_filepath]}
                    filepaths_list.append(filepath_set)

                else:
                    #sub, sess from bids
                    subject = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('sub')][0]
                    bids_dict['subject_label'] = subject
                    try:
                        session = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('ses')][0]
                    except IndexError:
                        session = subject
                    bids_dict['session_label'] = session

                    #id, label from bids datatype
                    datatype = root.split('/')[-1]
                    bids_dict['ID'] = datatype

                    scan_id = datatype
                    bids_dict['label'] = '-'.join((project,subject,session,scan_id))

                    #series_des type from last key in bids + run + acq
                    try:
                        run_number = [(i.split('-')[1]) for i in bids_filename_contents if i.startswith('run')][0]
                    except IndexError:
                        run_number = ''

                    bids_dict['series_description'] = i.split('.')[0].split('_')[-1] + run_number
                    bids_dict['type'] = i.split('.')[0].split('_')[-1] + run_number

                    bids_dict['quality'] = 'questionable'

                    bids_filepath = os.path.join(root,i)
                    if bids_filepath.endswith('nii.gz'):
                        bids_dict['resource'] = {'NIFTI': [bids_filepath]}
                    if bids_filepath.endswith('bvec.gz'):
                        bids_dict['resource'] = {'BVEC': [bids_filepath]}
                    if bids_filepath.endswith('bval.gz'):
                        bids_dict['resource'] = {'BVAL': [bids_filepath]}

                #other keys
                bids_dict['object_type'] = 'scan'
                bids_dict['project_id']  = project
                bids_dict['session_type'] = 'MR'

                upload_scan.append(bids_dict.copy())
                
    return upload_scan, filepaths_list, xnat_dataset

def filename_to_bids(filepaths_list, xnat_dataset):
    if xnat_dataset:
        for i in filepaths_list:
            os.rename(i[1], i[0])

def dataset_source_xnat(bids_dir):
    dataset_description_file = glob.glob(bids_dir + "/**/dataset_description.json", recursive = True)
    if not os.path.exists(dataset_description_file[0]):
        return False
    else:
        with open(dataset_description_file[0], 'r') as f:
            json_contents = json.load(f)
            if not json_contents['DatasetDOI'].endswith('xnat'):
                return False
    return True

            
    
    


    