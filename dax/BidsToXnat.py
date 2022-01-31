'''
BIDS to XNAT

Extract the information from BIDS for Xnatupload

@author: Praitayini Kanakaraj, Electrical Engineering, Vanderbilt University

'''
import os
import sys
import json
import glob

# check if valid bids
# extract and map to dict.


def split_name_with_nii(filename):
    """
    Returns the clean basename and extension of a file.
    Means that this correctly manages the ".nii.gz" extensions.

    Parameters
    ----------
    filename: str
        The filename to clean

    Returns
    -------
        base, ext : tuple(str, str)
        Clean basename and the full extension
    """
    base, ext = os.path.splitext(filename)

    if ext == ".gz":
        # Test if we have a .nii additional extension
        temp_base, add_ext = os.path.splitext(base)

        if add_ext == ".nii":
            ext = add_ext + ext
            base = temp_base

    return base, ext


def transform_to_xnat(bids_dir, project):
    """
    Method to transfrom bids to xnat

    :param bids_dir: BIDS Directory
    :param project: XNAT project ID
    :return: uplaod_scan -> the dict with info of scans to upload
    """
    # Check bids dir path exists
    if not os.path.exists(bids_dir):
        print('ERROR: %s path does not exists' % (bids_dir))
        exit()

    # Extract the values from the bids data
    bids_dict = {}
    upload_scan = []
    unq_scan_id = 1
    pre_dir = None
    xnat_dataset = dataset_source_xnat(bids_dir)
    diffusion_dict = {}
    for root, dirs, files in os.walk(bids_dir):

        # increment scan id if the previous dir is different
        cur_dir = root.rsplit('/', 1)[0]
        if pre_dir is not None and cur_dir != pre_dir:
            unq_scan_id = 1
        pre_dir = cur_dir

        # Sorting the files helps with DWI files, files will be
        # grouped together in this order: bval/bvec/nii.gz
        for i in sorted(files):
            if i.endswith('nii.gz') or i.endswith('.bvec') \
                    or i.endswith('.bval'):
                bids_filename_contents = i.split('_')

                if xnat_dataset:
                    # get info from json file for data dervied from XNAT
                    bids_filename = i.split('.')[0]
                    json_file = bids_filename + '.json'
                    with open(os.path.join(root, json_file), 'r') as f:
                        json_contents = json.load(f)

                    # subj from json
                    subject = json_contents['XNATProvenance'].split('/')[8]
                    bids_dict['subject_label'] = subject

                    # sess from json
                    session = json_contents['XNATProvenance'].split('/')[10]
                    bids_dict['session_label'] = session

                    # series des (on xnat/bidsmap) from bids
                    bids_dict['series_description'] = json_contents['SeriesDescription']

                    # label <project>-x-<subject>-x-<session>-x-<ID>
                    scan_id = json_contents['XNATProvenance'].split('/')[12]
                    bids_dict['label'] = '-'.join((project,
                                                  subject, session, scan_id))

                    # type quality from json
                    bids_dict['ID'] = scan_id
                    bids_dict['type'] = json_contents['ScanType']
                    bids_dict['quality'] = json_contents['ScanQuality']

                    # resource and resource path
                    bids_filepath = os.path.join(root, i)

                    if bids_filepath.endswith('nii.gz'):
                        bids_dict['resource'] = {'NIFTI': [bids_filepath]}
                    if bids_filepath.endswith('bvec'):
                        bids_dict['resource'] = {'BVEC': [bids_filepath]}
                    if bids_filepath.endswith('bval'):
                        bids_dict['resource'] = {'BVAL': [bids_filepath]}

                else:
                    # get data from filename for public bids dataset
                    # sub, sess from bids
                    subject = [(i.split('-')[1])
                               for i in bids_filename_contents if i.startswith('sub')][0]
                    bids_dict['subject_label'] = subject
                    try:
                        session = [(i.split('-')[1])
                                   for i in bids_filename_contents if i.startswith('ses')][0]
                    except IndexError:
                        session = subject
                    # xnatupload needs unique session id
                    bids_dict['session_label'] = subject + '-' + session

                    basename, ext = split_name_with_nii(i)
                    if ext == '.bval' and basename not in diffusion_dict:
                        diffusion_dict[basename] = unq_scan_id
                    elif basename in diffusion_dict:
                        unq_scan_id = diffusion_dict[basename]
                    # id increment unique value
                    bids_dict['ID'] = "{0:0=2d}".format(unq_scan_id)

                    # label from bids datatype
                    datatype = root.split('/')[-1]
                    scan_id = datatype
                    bids_dict['label'] = '-'.join((project,
                                                  subject, session, scan_id))

                    # series_des type from last key in bids + run + acq
                    try:
                        run_number = [(i.split('-')[1])
                                      for i in bids_filename_contents if i.startswith('run')][0]
                    except IndexError:
                        run_number = ''

                    bids_dict['series_description'] = i.split(
                        '.')[0].split('_')[-1] + run_number
                    bids_dict['type'] = i.split(
                        '.')[0].split('_')[-1] + run_number

                    bids_dict['quality'] = 'questionable'

                    bids_filepath = os.path.join(root, i)
                    if bids_filepath.endswith('nii.gz'):
                        bids_dict['resource'] = {'NIFTI': [bids_filepath]}
                    if bids_filepath.endswith('bvec'):
                        bids_dict['resource'] = {'BVEC': [bids_filepath]}
                    if bids_filepath.endswith('bval'):
                        bids_dict['resource'] = {'BVAL': [bids_filepath]}
                    unq_scan_id += 1

                # other keys
                bids_dict['object_type'] = 'scan'
                bids_dict['project_id'] = project
                # check the 4 datatypes for MR
                if bids_filepath.split('/')[-2] == 'anat' or 'func' or 'dwi' \
                        or 'fmap' or 'perf':
                    bids_dict['session_type'] = 'MR'
                else:
                    sys.exit()

                upload_scan.append(bids_dict.copy())

    return upload_scan


def dataset_source_xnat(bids_dir):
    """
    Method to check if the data was downloaded from xnat

    :param bids_dir: BIDS Directory
    :return: True or False
    """
    dataset_description_file = glob.glob(
        bids_dir + "/**/dataset_description.json", recursive=True)
    if not os.path.exists(dataset_description_file[0]):
        return False
    else:
        with open(dataset_description_file[0], 'r') as f:
            json_contents = json.load(f)
            if 'DatasetDOI' not in json_contents:
                return False
            elif not json_contents['DatasetDOI'].endswith('xnat'):
                return False
    return True
    