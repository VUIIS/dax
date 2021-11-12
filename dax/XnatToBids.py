'''
Tranform XNAT folder to BIDS format

@author: Praitayini Kanakaraj, Electrical Engineering, Vanderbilt University

'''
import os
import re
import sys
import json
import bond
import shutil
import nibabel as nib
from distutils.dir_util import copy_tree
from xml.etree import cElementTree as ET


def transform_to_bids(XNAT, DIRECTORY, project, BIDS_DIR, xnat_tag, LOGGER):
    """
    Method to move the data from XNAT folders to BIDS format (based on datatype) by looping through
    subjects/projects.
    :param XNAT: XNAT interface (connection between your python script and the XNAT database)
    :param DIRECTORY: XNAT Directory
    :param project: XNAT Project ID
    :param BIDS_DIR: BIDS Directory
    :param xnat_tag: boolean check for xnat tag
    :param LOGGER: Logging
    """
    LOGGER.info("INFO: Moving files to the BIDS folder...")
    # All the BIDS datattype
    data_type_l = ["anat", "func", "fmap", "dwi", "perf", "unknown_bids"]
    # Loop throught the XNAT folders
    for proj in os.listdir(DIRECTORY):
        if proj == project and os.path.isdir(os.path.join(DIRECTORY, proj)):
            subj_idx = 1
            for subj in os.listdir(os.path.join(DIRECTORY, proj)):
                LOGGER.info("* Subject %s" % (subj))
                sess_idx = 1
                for sess in os.listdir(os.path.join(DIRECTORY, proj, subj)):
                    LOGGER.info(" * Session %s" % (sess))
                    sess_path = os.path.join(DIRECTORY, proj, subj, sess)
                    for scan in os.listdir(sess_path):
                        if scan not in data_type_l:
                            for scan_resources in os.listdir(os.path.join(sess_path, scan)):
                                for scan_file in os.listdir(os.path.join(sess_path, scan, scan_resources)):
                                    scan_id = scan.split('-x-')[0]
                                    res_dir = (os.path.join(sess_path, scan, scan_resources))
                                    scan_path = '/projects/%s/subjects/%s/experiments/%s/scans/%s' % (
                                    project, subj, sess, scan.split('-x-')[0])
                                    scan_info = XNAT.select(scan_path)
                                    uri = XNAT.host + scan_info._uri
                                    # Do the BIDS conversion for only nifti, bval, bval scans
                                    if scan_file.endswith('.nii.gz') or scan_file.endswith(
                                            'bvec.txt') or scan_file.endswith('bval.txt') or scan_file.endswith(
                                            'bvec') or scan_file.endswith('bval'):
                                        LOGGER.info("  * Scan File %s" % (scan_file))
                                        nii_file = scan_file
                                        # Call the main BIDS function that is compatible with yaml
                                        bids_yaml(XNAT, project, scan_id, subj, res_dir, scan_file, uri, sess, nii_file,
                                                  sess_idx, subj_idx, xnat_tag)
                                        # Create the BIDS directory
                                        if not os.path.exists(os.path.join(BIDS_DIR, project)):
                                            os.makedirs(os.path.join(BIDS_DIR, project))
                                        # Move the BIDS conversion inside the XNAT resource folder to BIDS folder and then delete
                                        if os.path.exists(os.path.join(res_dir, "BIDS_DATA")):
                                            copy_tree(os.path.join(res_dir, "BIDS_DATA"),
                                                      os.path.join(BIDS_DIR, project))
                                            shutil.rmtree(os.path.join(res_dir, "BIDS_DATA"))
                                        else:
                                            # Delete XNAT files/folders after BIDS Conversion
                                            LOGGER.info("\t\t>Removing XNAT scan %s file because no BIDS datatype" % (
                                                scan_file))
                                            os.remove(os.path.join(sess_path, scan, scan_resources, scan_file))
                                LOGGER.info("\t\t>Removing XNAT resource %s folder" % (scan_resources))
                                os.rmdir(os.path.join(sess_path, scan, scan_resources))
                            LOGGER.info("\t>Removing XNAT scan %s folder" % (scan))
                            os.rmdir(os.path.join(sess_path, scan))
                    sess_idx = sess_idx + 1
                    LOGGER.info("\t>Removing XNAT session %s folder" % (sess))
                    os.rmdir(sess_path)
                subj_idx = subj_idx + 1
                LOGGER.info("\t>Removing XNAT subject %s folder" % (subj))
                os.rmdir(os.path.join(DIRECTORY, proj, subj))
    BIDS_PROJ_DIR = os.path.join(BIDS_DIR, project)
    dataset_description_file(BIDS_PROJ_DIR, XNAT, project)


def bids_yaml(XNAT, project, scan_id, subj, res_dir, scan_file, uri, sess, nii_file, sess_idx, subj_idx, xnat_tag):
    """
    Main method to put the scans in the BIDS datatype folder, create json
    sidecar and remane filenames based on the BIDS format.
    :param XNAT: XNAT interface
    :param project: XNAT project ID
    :param scan_id: Scan ID of the scan on XNAT
    :param subj: Subject of the scan on XNAT
    :param res_dir: XNAT Resource directory
    :param scan_file: Scan file
    :param uri: Link of the scan on XNAT
    :param sess: XNAT Session
    :param nii_file: Scan file (for yaml it is $col1 in the INLIST )
    :param sess_idx: Session count number
    :param subj_idx: Subject count number
    """
    # Check if the json sidecar is present or not
    if scan_file.endswith('.nii.gz'):
        is_json_present = False
        if nii_file.split('.')[0] + ".json" in os.listdir(res_dir):
            json_file = nii_file.split('.')[0] + ".json"
            is_json_present = True
        else:
            json_file = "empty.json"

    # Get the series_description and scan_type of the scan in XNAT
    project_scans = XNAT.get_project_scans(project)
    for x in project_scans:
        if x['ID'] == scan_id and x['subject_label'] == subj and x['session_label'] == sess:
            scan_type = x['type']
            series_description = x['series_description']
            scan_quality = x['scan_quality']
    # Get the xnat_type from Project level
    if XNAT.select('/data/projects/' + project + '/resources/BIDS_xnat_type/files/xnat_type.txt').exists():
        with open(XNAT.select('/data/projects/' + project + '/resources/BIDS_xnat_type/files/xnat_type.txt').get(),
                  "r+") as f:
            xnat_mapping_type = f.read()
            if xnat_mapping_type == 'scan_type':
                xnat_mapping_type = scan_type
            elif xnat_mapping_type == 'series_description':
                xnat_mapping_type = series_description
            # print(xnat_mapping_type)
    else:
        print(
            "ERROR: The type of XNAT to BIDS mapping info (for eg. scan_type or series_description) is not given. Use BidsMapping Tool")
        print("ERROR: BIDS Conversion not complete")
        sys.exit()

    # Get the datatype for the scan
    sd_dict = sd_datatype_mapping(XNAT, project)
    data_type = sd_dict.get(xnat_mapping_type, "unknown_bids")
    if data_type == "unknown_bids":
        print((
            '\t\t>WARNING: The type %s does not have a BIDS datatype mapping at default and project level. Use BidsMapping Tool' % xnat_mapping_type))

    else:
        # If datatype is known, Create the BIDS directory and do the rest
        # If XNAT_TAG is false the format is subj_<01>-ses-<01>
        sess_idx = "{0:0=2d}".format(int(sess_idx))
        subj_idx = "{0:0=2d}".format(int(subj_idx))
        bids_dir = os.path.join(res_dir, "BIDS_DATA")
        if not os.path.exists(bids_dir):
            os.makedirs(bids_dir)
        # If XNAT_TAG is true the format is subj_<SUBJID>-ses-<SESSID>
        if xnat_tag:
            sess_idx = sess
            subj_idx = subj
        data_type_dir = os.path.join(bids_dir, "sub-" + subj_idx, "ses-" + sess_idx, data_type)
        if not os.path.exists(os.path.join(bids_dir, data_type_dir)):
            os.makedirs(os.path.join(bids_dir, data_type_dir))

        # XNAT Project Scanner info
        session_info = XNAT.select('/project/' + project + '/subject/' + subj + '/experiment/' + sess).get()
        session_info = ET.fromstring(session_info)
        try:
            acquisition_site = session_info.find('{http://nrg.wustl.edu/xnat}acquisition_site').text
        except AttributeError:
            acquisition_site = 'NA'
        try:
            scanner = session_info.find('{http://nrg.wustl.edu/xnat}scanner').text
        except AttributeError:
            scanner = 'NA'
        try:
            manufacturer = session_info.find('{http://nrg.wustl.edu/xnat}scanner').attrib['manufacturer']
        except AttributeError:
            manufacturer = 'NA'
        try:
            model = session_info.find('{http://nrg.wustl.edu/xnat}scanner').attrib['model']
        except AttributeError:
            model = 'NA'

        # For only nifti scans, handle json sidecar should be checked and the json sidecar filename should changed
        if scan_file.endswith('.nii.gz'):
            xnat_prov = yaml_create_json(XNAT, data_type, res_dir, scan_file, uri, project, xnat_mapping_type, sess,
                                         is_json_present, nii_file, json_file, series_description, scan_type,
                                         scan_quality, acquisition_site, scanner, manufacturer, model)
            with open(os.path.join(res_dir, json_file), "w+") as f:
                json.dump(xnat_prov, f, indent=2)
            print('\t\t-Handling json file')
            bids_fname_json = yaml_bids_filename(XNAT, data_type, scan_id, subj, sess, project, json_file,
                                                 xnat_mapping_type, sess_idx, subj_idx, series_description)
            os.rename(os.path.join(res_dir, json_file), os.path.join(res_dir, bids_fname_json))
            shutil.move(os.path.join(res_dir, bids_fname_json), data_type_dir)

        # Change the filename and move the file
        print('\t\t-Handling nifti/bvec/bval file')
        bids_fname = yaml_bids_filename(XNAT, data_type, scan_id, subj, sess, project, scan_file, xnat_mapping_type,
                                        sess_idx, subj_idx, series_description)
        os.rename(os.path.join(res_dir, nii_file), os.path.join(res_dir, bids_fname))
        shutil.move(os.path.join(res_dir, bids_fname), data_type_dir)


def yaml_bids_filename(XNAT, data_type, scan_id, subj, sess, project, scan_file, xnat_mapping_type, sess_idx, subj_idx,
                       series_description):
    """
    Main method to put the scans in the BIDS datatype folder, create json
    sidecar and remane filenames based on the BIDS format.
    :param XNAT: XNAT interface
    :param data_type: BIDS datatype of scan
    :param scan_id: Scan id
    :param subj: XNAT Subject
    :param sess: XNAT Session
    :param project: XANT Project
    :param scan_file: Scan file on XNAT
    :param xnat_mapping_type:
    :param sess_idx: Session count number
    :param subj_idx: Subject count number
    :param series_description: series_description of the scan
    :return: BIDS filename
    """
    series_description = series_description.replace(" ","").replace('/', "").replace(":", "")
    if data_type == "anat":
        rn_dict = sd_run_mapping(XNAT, project)
        run_number = rn_dict.get(xnat_mapping_type, scan_id)
        bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + series_description + '_run-' + run_number + '_T1w' + \
                     '.' + ".".join(scan_file.split('.')[1:])
        return bids_fname

    elif data_type == "func":
        # Get the task for the scan
        tk_dict = sd_tasktype_mapping(XNAT, project)
        task_type = tk_dict.get(xnat_mapping_type)
        if task_type == None:
            print(('ERROR: Scan type %s does not have a BIDS tasktype mapping at default and project level ' \
                  'Use BidsMapping tool. Func folder not created' % xnat_mapping_type))
            print("ERROR: BIDS Conversion not complete")
            sys.exit()
        # Get the run_number for the scan
        rn_dict = sd_run_mapping(XNAT, project)
        # Map scan and with run_number, if run_number
        # not present for scan then 01 is used
        run_number = rn_dict.get(xnat_mapping_type, scan_id)
        bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_task-' + task_type + '_acq-' + series_description + '_run-' \
                     + run_number + '_bold' + '.' + ".".join(scan_file.split('.')[1:])
        return bids_fname

    elif data_type == "dwi":
        rn_dict = sd_run_mapping(XNAT, project)
        run_number = rn_dict.get(xnat_mapping_type, scan_id)
        if scan_file.endswith('bvec.txt'):
            bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + series_description + '_run-' + run_number + '_dwi.bvec'

        elif scan_file.endswith('bval.txt'):
            bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + series_description + '_run-' + run_number + '_dwi.bval'
        else:
            bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + series_description + '_run-' + run_number + '_dwi' + \
                         '.' + ".".join(scan_file.split('.')[1:])
        return bids_fname

    elif data_type == "fmap":
        rn_dict = sd_run_mapping(XNAT, project)
        run_number = rn_dict.get(xnat_mapping_type, scan_id)
        #TODO: Include all the four different cases for fieldmap
        bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + series_description + '_run-' + run_number + '_fieldmap' + \
                     '.' + ".".join(scan_file.split('.')[1:])
        return bids_fname

    elif data_type == "perf":
        asl_dict = sd_asltype_mapping(XNAT, project)
        asl_type = asl_dict.get(xnat_mapping_type, scan_id)
        if asl_type == None:
            print(('ERROR: Scan type %s does not have a BIDS asltype mapping at default and project level. ' \
                  'Use BidsMapping tool. Perf folder not created' % xnat_mapping_type))
            print("ERROR: BIDS Conversion not complete")
            sys.exit()
        # Get the run_number for the scan
        rn_dict = sd_run_mapping(XNAT, project)
        run_number = rn_dict.get(xnat_mapping_type, scan_id)

        bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + series_description + '_run-' + run_number + '_' + asl_type + \
                '.' + ".".join(scan_file.split('.')[1:])      
        return bids_fname

def yaml_create_json(XNAT, data_type, res_dir, scan_file, uri, project, xnat_mapping_type, sess, is_json_present,
                     nii_file, json_file, series_description, scan_type, scan_quality, acquisition_site, scanner, manufacturer, model):
    """
    :param XNAT: XNAT interface
    :param data_type: BIDS datatype of the scan
    :param res_dir: XNAT Resource directory
    :param scan_file: XNAT Scan file
    :param uri: Link of scan file on XNAT
    :param project: Project ID
    :param xnat_mapping_type: Type of mapping used on XNAT (scan_type or series_description)
    :param sess: Xnat sesssion
    :param is_json_present: json sidecar present or absent in XNAT (boolean)
    :param nii_file: Scan file ($col1 in yaml)
    :param json_file: json sidecar filename
    :param series_description: series description for scan file on XNAT
    :return: xnat_prov - json that needs to be uploaded with nifti
    """
    # For dwi, fmap and anat - add only XNAT details to json sidecar
    if data_type != 'func':
        xnat_detail = {"XNATfilename": scan_file,
                       "XNATProvenance": uri,
                       "SeriesDescription": series_description,
                       "ScanType": scan_type,
                       "ScanQuality": scan_quality,
                       "AcquisitionSite": acquisition_site,
                       "ScannerManufacturer": manufacturer,
                       "Scanner": scanner,
                       "ScannerModel": model}

        if not is_json_present:
            print('\t\t>No json sidecar. Created json sidecar with xnat info.')
            xnat_prov = xnat_detail
        else:
            with open(os.path.join(res_dir, json_file), "r+") as f:
                print('\t\t>Json sidecar exists. Added xnat info.')
                xnat_prov = json.load(f)
                xnat_prov.update(xnat_detail)


    else:
        # For func check out details in nifti and json is required
        xnat_prov = yaml_func_json_sidecar(XNAT, data_type, res_dir, scan_file, uri, project, xnat_mapping_type,
                                           nii_file, is_json_present, sess, json_file, series_description, scan_type,
                                           scan_quality, acquisition_site, scanner, manufacturer, model)
    return xnat_prov


def yaml_func_json_sidecar(XNAT, data_type, res_dir, scan_file, uri, project, xnat_mapping_type, nii_file,
                           is_json_present, sess, json_file, series_description, scan_type, scan_quality, 
                           acquisition_site, scanner, manufacturer, model):
    """

    :param XNAT: XNAT interface
    :param data_type: BIDS datatype of the scan
    :param res_dir: XNAT Resource directory
    :param scan_file: XNAT Scan file
    :param uri: Link of scan file on XNAT
    :param project: Project ID
    :param xnat_mapping_type:  Type of mapping used on XNAT (scan_type or series_description)
    :param nii_file: Scan file ($col1 in yaml)
    :param is_json_present: json sidecar present or absent in XNAT (boolean)
    :param sess: XNAT Session ID
    :param json_file: json sidecar filename
    :return: json sidecare for func datatype
    """
    xnat_prov = None
    tr_dict = sd_tr_mapping(XNAT, project)
    TR_bidsmap = tr_dict.get(xnat_mapping_type)
    if TR_bidsmap == None:
        print(('\t\t>ERROR: Scan type %s does not have a TR mapping' % xnat_mapping_type))
        print("\t\t>ERROR: BIDS Conversion not complete")
        sys.exit()
    TR_bidsmap = round((float(TR_bidsmap)), 3)
    tk_dict = sd_tasktype_mapping(XNAT, project)
    task_type = tk_dict.get(xnat_mapping_type)
    img = nib.load(os.path.join(res_dir, nii_file))
    units = img.header.get_xyzt_units()[1]
    if units != 'sec':
        print("\t\t>ERROR: the units in nifti header is not secs")
        print("\t\t>ERROR: BIDS Conversion not complete")
        func_folder = os.path.dirname(bids_res_path)
        os.rmdir(func_folder)
        sys.exit()
    TR_nifti = round(img.header['pixdim'][4].item(), 3)
    # If json not present - if TR in nifti and XNAT (project level) is equal, USE TR FROM NIFTI
    #                       if TR in nifti and XNAT (project level) is not equal, USE TR FROM XNAT (Project level) and
    #                                                                             UPDATE THE NIFTI HEADER
    if not is_json_present:
        xnat_prov = {"XNATfilename": scan_file,
                     "XNATProvenance": uri,
                     "TaskName": task_type,
                     "SeriesDescription": series_description,
                     "ScanType": scan_type,
                     "ScanQuality": scan_quality,
                     "AcquisitionSite": acquisition_site,
                     "ScannerManufacturer": manufacturer,
                     "Scanner": scanner,
                     "ScannerModel": model}

        if TR_nifti == TR_bidsmap:
            print((
                '\t\t>No existing json. TR %.3f sec in BIDS mapping and NIFTI header. Using TR %.3f sec in nifti header ' \
                'for scan file %s in session %s. ' % (TR_bidsmap, TR_bidsmap, scan_file, sess)))
            xnat_prov["RepetitionTime"] = float(TR_nifti)
        else:
            print((
                '\t\t>No existing json. WARNING: The TR is %.3f sec in project level BIDS mapping, which does not match the TR of %.3f sec in NIFTI header.\n  ' \
                '\t\tUPDATING NIFTI HEADER to match BIDS mapping TR %.3f sec for scan file %s in session %s.' \
                % (TR_bidsmap, TR_nifti, TR_bidsmap, scan_file, sess)))
            xnat_prov["RepetitionTime"] = float(TR_bidsmap)
            img.header['pixdim'][4] = TR_bidsmap
            nib.save(img, os.path.join(res_dir, nii_file))
    # If json present - if TR in JSON and XNAT (project level) is equal,     USE THE SAME JSON
    #                 - if TR in JSON and XNAT (project level) is not equal, USE TR FROM XNAT (Project level) and
    #                                                                         UPDATE THE NIFTI HEADER
    else:
        with open(os.path.join(res_dir, json_file), "r+") as f:
            xnat_prov = json.load(f)
            TR_json = round((xnat_prov['RepetitionTime']), 3)
            xnat_detail = {"XNATfilename": scan_file,
                           "XNATProvenance": uri,
                           "TaskName": task_type,
                           "SeriesDescription": series_description,
                           "ScanType": scan_type,
                           "ScanQuality": scan_quality,
                           "AcquisitionSite": acquisition_site,
                           "ScannerManufacturer": manufacturer,
                           "Scanner": scanner,
                           "ScannerModel": model}

            if TR_json != TR_bidsmap:
                print((
                    '\t\t>JSON sidecar exists. WARNING: TR is %.3f sec in project level BIDS mapping, which does not match the TR in JSON sidecar %.3f.\n ' \
                    '\t\tUPDATING JSON with TR %.3f sec in BIDS mapping and UPDATING NIFTI header for scan %s in session %s.' \
                    % (TR_bidsmap, TR_json, TR_bidsmap, scan_file, sess)))
                xnat_detail['RepetitionTime'] = float(TR_bidsmap)
                xnat_prov.update(xnat_detail)
                img.header['pixdim'][4] = TR_bidsmap
                nib.save(img, os.path.join(res_dir, nii_file))
            else:
                print((
                    '\t\t>JSON sidecar exists. TR is %.3f sec in BIDS mapping and JSON sidecar for scan %s in session %s. ' \
                    'Created json sidecar with XNAT info' \
                    % (TR_bidsmap, scan_file, sess)))
                xnat_prov.update(xnat_detail)
    return xnat_prov


def sd_tr_mapping(XNAT, project):
    """
    Method to get the Repetition Time mapping from Project level
    :param XNAT: XNAT interface
    :param project: XNAT Project ID
    :return: Dictonary with scan_type/series_description and  Repetition Time mapping
    """
    tr_dict = {}
    if XNAT.select('/data/projects/' + project + '/resources/BIDS_repetition_time_sec').exists():
        for res in XNAT.select('/data/projects/' + project + '/resources/BIDS_repetition_time_sec/files').get():
            if res.endswith('.json'):
                with open(XNAT.select(
                        '/data/projects/' + project + '/resources/BIDS_repetition_time_sec/files/' + res).get(),
                          "r+") as f:
                    tr_mapping = json.load(f)
                    print(('\t\t>Using BIDS Repetition Time in secs mapping in project level %s' % (project)))
                    tr_dict = tr_mapping[project]

    else:
        print("\t\t>ERROR: no TR mapping at project level. Func folder not created")
        print("\t\t>ERROR: BIDS Conversion not complete")
        sys.exit()
    return tr_dict

def sd_asltype_mapping(XNAT, project):
    """
    Method to get the asl type mapping from Project level
    Mapping options: asl, m0scan

    :param XNAT: XNAT interface
    :param project: XNAT Project ID
    :return: Dictonary with scan_type/series_description and  asl type mapping
    """
    asl_dict = {}
    if XNAT.select('/data/projects/' + project + '/resources/BIDS_asltype').exists():
        for res in XNAT.select('/data/projects/' + project + '/resources/BIDS_asltype/files').get():
            if res.endswith('.json'):
                with open(XNAT.select(
                        '/data/projects/' + project + '/resources/BIDS_asltype/files/' + res).get(),
                          "r+") as f:
                    asl_mapping = json.load(f)
                    print(('\t\t>Using BIDS asltype mapping in project level %s' % (project)))
                    asl_dict = asl_mapping[project]

    else:
        print("\t\t>ERROR: no asl mapping at project level. Perf folder not created")
        print("\t\t>ERROR: BIDS Conversion not complete")
        sys.exit()
    return asl_dict

def sd_datatype_mapping(XNAT, project):
    """
    Method to get the Datatype mapping from Project level
    :param XNAT: XNAT interface
    :param project: XNAT Project ID
    :return: Dictonary with scan_type/series_description and datatype mapping
    """
    sd_dict = {}

    if XNAT.select('/data/projects/' + project + '/resources/BIDS_datatype').exists():
        for res in XNAT.select('/data/projects/' + project + '/resources/BIDS_datatype/files').get():
            if res.endswith('.json'):
                with open(XNAT.select('/data/projects/' + project + '/resources/BIDS_datatype/files/' + res).get(),
                          "r+") as f:
                    datatype_mapping = json.load(f)
                    sd_dict = datatype_mapping[project]
                    print(('\t\t>Using BIDS datatype mapping in project level %s' % (project)))

    else:
        # Edit here to set default mapping options
        print(('\t\t>WARNING: No BIDS datatype mapping in project %s - using default mapping' % (project)))
        scans_list_global = XNAT.get_project_scans('LANDMAN')

        for sd in scans_list_global:
            c = re.search('T1|T2|T1W', sd['scan_type'])
            if not c == None:
                sd_anat = sd['scan_type'].strip().replace('/', '_').replace(" ", "").replace(":", '_')
                sd_dict[sd_anat] = "anat"

        for sd in scans_list_global:
            c = re.search('rest|Resting state|Rest', sd['scan_type'], flags=re.IGNORECASE)
            if not c == None:
                sd_func = sd['scan_type'].strip().replace('/', '_').replace(" ", "").replace(":", '_')
                sd_dict[sd_func] = "func"

        for sd in scans_list_global:
            c = re.search('dwi|dti', sd['scan_type'], flags=re.IGNORECASE)
            if not c == None:
                sd_dwi = sd['scan_type'].strip().replace('/', '_').replace(" ", "").replace(":", '_')
                sd_dict[sd_dwi] = "dwi"

        for sd in scans_list_global:
            c = re.search('Field|B0', sd['scan_type'], flags=re.IGNORECASE)
            if not c == None:
                sd_fmap = sd['scan_type'].strip().replace('/', '_').replace(" ", "").replace(":", '_')
                sd_dict[sd_fmap] = "fmap"
        with open("global_mapping.json", "w+") as f:
            json.dump(sd_dict, f, indent=2)

    return sd_dict


def sd_tasktype_mapping(XNAT, project):
    """
    Method to get the Task type mapping at Project level
    :param XNAT: XNAT interface
    :param project: XNAT Project ID
    :return: Dictonary with scan_type/series_description and tasktype mapping
    """
    tk_dict = {}
    if XNAT.select('/data/projects/' + project + '/resources/BIDS_tasktype').exists():
        for res in XNAT.select('/data/projects/' + project + '/resources/BIDS_tasktype/files').get():
            if res.endswith('.json'):
                with open(XNAT.select('/data/projects/' + project + '/resources/BIDS_tasktype/files/'
                                      + res).get(), "r+") as f:
                    datatype_mapping = json.load(f)
                    tk_dict = datatype_mapping[project]

    else:
        print(('\t\t>WARNING: No BIDS task type mapping in project %s - using default mapping' % (project)))
        scans_list_global = XNAT.get_project_scans('LANDMAN')
        for sd in scans_list_global:
            c = re.search('rest|Resting state|Rest', sd['scan_type'], flags=re.IGNORECASE)
            if not c == None:
                sd_func = sd['scan_type'].strip().replace('/', '_').replace(" ", "").replace(":", '_')
                tk_dict[sd_func] = "rest"
        with open("global_tk_mapping.json", "w+") as f:
            json.dump(tk_dict, f, indent=2)
    return tk_dict


def sd_run_mapping(XNAT, project):
    """
    Method to get the Run number mapping at Project level
    :param XNAT: XNAT interface
    :param project: XNAT Project ID
    :return: Dictonary with scan_type/series_description and run number mapping
    """
    rn_dict = {}
    if XNAT.select('/data/projects/' + project + '/resources/BIDS_run_number').exists():
        for res in XNAT.select('/data/projects/' + project + '/resources/BIDS_run_number/files').get():
            if res.endswith('.json'):
                with open(XNAT.select('/data/projects/' + project + '/resources/BIDS_run_number/files/'
                                      + res).get(), "r+") as f:
                    datatype_mapping = json.load(f)
                    rn_dict = datatype_mapping[project]

    else:
        print("\t\t>WARNING: No Run number mapping at project level. Using scan id as run number")

    return rn_dict

def dataset_description_file(BIDS_PROJ_DIR, XNAT, project):
    """
    Build BIDS dataset description json file
    :param BIDS_PROJ_DIR: Project BIDS directory
    :param XNAT: XNAT interface
    :param project: XNAT Project
    """
    BIDSVERSION = "1.0.1"
    dataset_description = dict()
    dataset_description['BIDSVersion'] = BIDSVERSION
    dataset_description['Name'] = project
    dataset_description['DatasetDOI'] = XNAT.host
    project_info = XNAT.select('/project/' + project).get()
    project_info = ET.fromstring(project_info)
    PI_element = project_info.findall('{http://nrg.wustl.edu/xnat}PI')
    if len(PI_element) > 0:
        dataset_description['Author'] = PI_element[0][1].text, PI_element[0][0].text
    else:
        dataset_description['Author'] = "No Author defined on XNAT"
    if not os.path.exists(BIDS_PROJ_DIR):
        os.makedirs(BIDS_PROJ_DIR)
    with open(os.path.join(BIDS_PROJ_DIR, 'dataset_description.json'), 'w+') as f:
        json.dump(dataset_description, f, indent=2)

class XNATBond(object):
    def __init__(self, bids_dir):
        self.bids_dir = bids_dir

    def generate_params(self, bond_dir):
        if not os.path.exists(bond_dir):
            os.makedirs(bond_dir)
        bond.BOnD(self.bids_dir).get_CSVs(os.path.join(bond_dir, 'keyparam_original'))

    def edit_params(self, keyparam_edited,keyparam_files,new_keyparam_prefix):
        print(self.bids_dir,keyparam_edited,keyparam_files,new_keyparam_prefix)
        bond.BOnD(self.bids_dir).apply_csv_changes(keyparam_edited,keyparam_files,new_keyparam_prefix)