'''
Tranform XNAT folder to BIDS format

@author: Praitayini Kanakaraj, Electrical Engineering, Vanderbilt University

'''
import os
import re
import sys
import json
import shutil
import nibabel as nib
from distutils.dir_util import copy_tree
from xml.etree import cElementTree as ET


def transform_to_bids(XNAT, DIRECTORY, project, BIDS_DIR, LOGGER):
    """
     Method to move the data from XNAT folders to BIDS format (based on datatype) by looping through
     subjects/projects.

     :return: None
     """
    LOGGER.info("--------------- BIDS --------------")
    LOGGER.info("INFO: Moving files to the BIDS folder...")
    # sd_dict = sd_datatype_mapping(XNAT, project)
    data_type_l = ["anat", "func", "fmap", "dwi", "unknown_bids"]
    subj_idx = 1
    sess_idx = 1
    # project_scans = XNAT.get_project_scans(project)
    for proj in os.listdir(DIRECTORY):
        if proj == project and os.path.isdir(os.path.join(DIRECTORY, proj)):
            for subj in os.listdir(os.path.join(DIRECTORY, proj)):
                # subj_idx = 1
                LOGGER.info("* Subject %s" % (subj))
                for sess in os.listdir(os.path.join(DIRECTORY, proj, subj)):
                    LOGGER.info(" * Session %s" % (sess))
                    sess_path = os.path.join(DIRECTORY, proj, subj, sess)
                    # sess_idx = 1
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
                                    if scan_file.endswith('.nii.gz'):
                                        LOGGER.info("  * Scan File %s" % (scan_file))
                                        nii_file = scan_file
                                        bids_yaml(XNAT, project, scan_id, subj, res_dir, scan_file, uri, sess, nii_file,
                                                  sess_idx, subj_idx)
                                        if not os.path.exists(os.path.join(BIDS_DIR, project)):
                                            os.makedirs(os.path.join(BIDS_DIR, project))
                                        copy_tree(os.path.join(res_dir, "BIDS_DATA"), os.path.join(BIDS_DIR, project))
                                        shutil.rmtree(os.path.join(res_dir, "BIDS_DATA"))
                            LOGGER.info("\t\t>Removing XNAT resource %s folder" % (scan_resources))
                            os.rmdir(os.path.join(sess_path, scan, scan_resources))
                            os.rmdir(os.path.join(sess_path, scan))
                    sess_idx = sess_idx + 1
                    LOGGER.info("\t>Removing XNAT session %s folder" % (sess))
                    # shutil.rmtree(sess_path)
                    os.rmdir(sess_path)
                subj_idx = subj_idx + 1
                LOGGER.info("\t>Removing XNAT subject %s folder" % (subj))
                os.rmdir(os.path.join(DIRECTORY, proj, subj))
    dataset_description_file(BIDS_DIR, XNAT, project)


def bids_yaml(XNAT, project, scan_id, subj, res_dir, scan_file, uri, sess, nii_file, sess_idx, subj_idx):
    is_json_present = False
    if nii_file.split('.')[0] + ".json" in os.listdir(res_dir):
        json_file = nii_file.split('.')[0] + ".json"
        is_json_present = True
    else:
        json_file = "empty.json"
    sd_dict = sd_datatype_mapping(XNAT, project)
    project_scans = XNAT.get_project_scans(project)
    # for x in project_scans:
    #    if x['ID'] == scan_id and x['subject_label'] == subj:
    #        scan_type = x['type']
    #        series_description = x['series_description']
    if XNAT.select('/data/projects/' + project + '/resources/BIDS_xnat_type/files/xnat_type.txt').exists:
        with open(XNAT.select('/data/projects/' + project + '/resources/BIDS_xnat_type/files/xnat_type.txt').get(),
                  "r+") as f:
            xnat_mapping_type = f.read()
            print(xnat_mapping_type)
            for x in project_scans:
                if x['ID'] == scan_id and x['subject_label'] == subj and xnat_mapping_type == 'scan_type':
                    xnat_mapping_type = x['type']
                elif x['ID'] == scan_id and x['subject_label'] == subj and xnat_mapping_type == 'series_description':
                    xnat_mapping_type = x['series_description']
            print(xnat_mapping_type)
    else:
        print(
            "ERROR: The type of xnat map info (for eg. scan_type or series_description) is not given. Use BidsMapping Tool")
        sys.exit()

    data_type = sd_dict.get(xnat_mapping_type, "unknown_bids")
    if data_type == "unknown_bids":
        print((
            "WARNING: The type %s does not have a BIDS datatype mapping at default and project level. Use BidsMapping Tool" % xnat_mapping_type))

        # sys.exit()
    xnat_prov = yaml_create_json(XNAT, data_type, res_dir, scan_file, uri, project, xnat_mapping_type, sess,
                                 is_json_present,
                                 nii_file, json_file)
    sess_idx = "{0:0=2d}".format(sess_idx)
    subj_idx = "{0:0=2d}".format(subj_idx)
    bids_fname = yaml_bids_filename(XNAT, data_type, scan_id, subj, sess, project, scan_file, xnat_mapping_type,
                                    sess_idx, subj_idx)
    bids_fname_json = yaml_bids_filename(XNAT, data_type, scan_id, subj, sess, project, json_file, xnat_mapping_type,
                                         sess_idx, subj_idx)
    with open(os.path.join(res_dir, json_file), "w+") as f:
        json.dump(xnat_prov, f, indent=2)
    os.rename(os.path.join(res_dir, nii_file), os.path.join(res_dir, bids_fname))
    os.rename(os.path.join(res_dir, json_file), os.path.join(res_dir, bids_fname_json))
    bids_dir = os.path.join(res_dir, "BIDS_DATA")
    if not os.path.exists(bids_dir):
        os.makedirs(bids_dir)
    data_type_dir = os.path.join(bids_dir, "sub-" + subj_idx, "ses-" + sess_idx, data_type)
    if not os.path.exists(os.path.join(bids_dir, data_type_dir)):
        os.makedirs(os.path.join(bids_dir, data_type_dir))
    # for res in os.listdir(res_dir):
    #     if os.path.isfile(os.path.join(res_dir,res)):
    # print "Moving %s and %s" % (os.path.join(res_dir, nii_file), os.path.join(res_dir, json_file))
    shutil.move(os.path.join(res_dir, bids_fname), data_type_dir)
    shutil.move(os.path.join(res_dir, bids_fname_json), data_type_dir)


def yaml_bids_filename(XNAT, data_type, scan_id, subj, sess, project, scan_file, xnat_mapping_type, sess_idx, subj_idx):
    if data_type == "anat":
        bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + scan_id + '_' + 'T1w' + \
                     '.' + ".".join(scan_file.split('.')[1:])

        return bids_fname
    elif data_type == "func":
        tk_dict = sd_tasktype_mapping(XNAT, project)
        task_type = tk_dict.get(xnat_mapping_type)
        if task_type == None:
            print(('ERROR: Scan type %s does not have a BIDS tasktype mapping at default and project level ' \
                  'Use BidsMapping tool. Func folder not created' % xnat_mapping_type))
            # func_folder = os.path.join(bids_sess_path, data_type)
            # os.rmdir(func_folder)
            sys.exit()

        bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_task-' + task_type + '_acq-' + scan_id + '_run-01' \
                     + '_' + 'bold' + '.' + ".".join(scan_file.split('.')[1:])
        return bids_fname
    elif data_type == "dwi":
        if label == "BVEC":
            bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + scan_id + '_' + 'dwi' + '.' + 'bvec'

        elif label == "BVAL":
            bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + scan_id + '_' + 'dwi' + '.' + 'bval'

        else:
            bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + scan_id + '_' + 'dwi' + \
                         '.' + ".".join(scan_file.split('.')[1:])
        return bids_fname

    elif data_type == "fmap":
        bids_fname = "sub-" + subj_idx + '_' + "ses-" + sess_idx + '_acq-' + scan_id + '_bold' + \
                     '.' + ".".join(scan_file.split('.')[1:])
        return bids_fname


def yaml_create_json(XNAT, data_type, res_dir, scan_file, uri, project, xnat_mapping_type, sess, is_json_present,
                     nii_file,
                     json_file):
    if data_type != 'func':
        xnat_detail = {"XNATfilename": scan_file,
                       "XNATProvenance": uri}
        if not is_json_present:
            print('\t\t>No json sidecar. Created json sidecar with xnat info.')
            xnat_prov = xnat_detail
        else:
            # print os.path.join(res_dir, json_file)
            with open(os.path.join(res_dir, json_file), "r+") as f:
                print('\t\t>Json sidecar exists. Added xnat info.')
                xnat_prov = json.load(f)
                xnat_prov.update(xnat_detail)
                # file.seek(0)
                # json.dump(xnat_prov, f, indent=2)
                # print xnat_prov

    else:
        xnat_prov = yaml_func_json_sidecar(XNAT, data_type, res_dir, scan_file, uri, project, xnat_mapping_type,
                                           nii_file,
                                           is_json_present, sess, json_file)
        # print xnat_prov
    return xnat_prov


def yaml_func_json_sidecar(XNAT, data_type, res_dir, scan_file, uri, project, xnat_mapping_type, nii_file,
                           is_json_present,
                           sess, json_file):
    xnat_prov = None
    tr_dict = sd_tr_mapping(XNAT, project)
    TR_bidsmap = tr_dict.get(xnat_mapping_type)
    if TR_bidsmap == None:
        print(('\t\t>ERROR: Scan type %s does not have a TR mapping' % xnat_mapping_type))
        # func_folder = os.path.dirname(bids_res_path)
        # os.rmdir(func_folder)
        sys.exit()
    TR_bidsmap = round((float(TR_bidsmap)), 3)
    tk_dict = sd_tasktype_mapping(XNAT, project)
    task_type = tk_dict.get(xnat_mapping_type)
    img = nib.load(os.path.join(res_dir, nii_file))
    units = img.header.get_xyzt_units()[1]
    if units != 'sec':
        print("\t\t>ERROR: the units in nifti header is not secs")
        func_folder = os.path.dirname(bids_res_path)
        os.rmdir(func_folder)
        sys.exit()
    TR_nifti = round((img.header['pixdim'][4]), 3)
    if not is_json_present:
        xnat_prov = {"XNATfilename": scan_file,
                     "XNATProvenance": uri,
                     "TaskName": task_type}
        if TR_nifti == TR_bidsmap:
            print((
                '\t\t>No existing json. TR %.3f sec in BIDS mapping and NIFTI header. Using TR %.3f sec in nifti header ' \
                'for scan file %s in session %s. ' % (TR_bidsmap, TR_bidsmap, scan_file, sess)))
            xnat_prov["RepetitionTime"] = TR_nifti
        else:
            print((
                '\t\t>No existing json. WARNING: The TR is %.3f sec in project level BIDS mapping, which does not match the TR of %.3f sec in NIFTI header.\n  ' \
                '\t\tUPDATING NIFTI HEADER to match BIDS mapping TR %.3f sec for scan file %s in session %s.' \
                % (TR_bidsmap, TR_nifti, TR_bidsmap, scan_file, sess)))
            xnat_prov["RepetitionTime"] = TR_bidsmap
            img.header['pixdim'][4] = TR_bidsmap
            nib.save(img, os.path.join(res_dir, nii_file))
    else:
        with open(os.path.join(res_dir, json_file), "r+") as f:
            xnat_prov = json.load(f)
            TR_json = round((xnat_prov['RepetitionTime']), 3)
            xnat_detail = {"XNATfilename": scan_file,
                           "XNATProvenance": uri,
                           "TaskName": task_type}
            if TR_json != TR_bidsmap:
                print((
                    '\t\t>JSON sidecar exists. WARNING: TR is %.3f sec in project level BIDS mapping, which does not match the TR in JSON sidecar %.3f.\n ' \
                    '\t\tUPDATING JSON with TR %.3f sec in BIDS mapping and UPDATING NIFTI header for scan %s in session %s.' \
                    % (TR_bidsmap, TR_json, TR_bidsmap, scan_file, sess)))
                xnat_detail['RepetitionTime'] = TR_bidsmap
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
                    # tr_dict = {k.strip().replace('/', '_').replace(" ", "").replace(":", '_')
                    #: v for k, v in tr_dict.items()}
    else:
        print("\t\t>ERROR: no TR mapping at project level. Func folder not created")
        # func_folder = os.path.dirname(bids_res_path)
        # os.rmdir(func_folder)
        sys.exit()
    return tr_dict


def sd_datatype_mapping(XNAT, project):
    """
      Method to map scan type to task type for functional scans

      :return: mapping dict
    """
    sd_dict = {}
    # if OPTIONS.selectionScan:
    # project = OPTIONS.selectionScan.split('-')[0]
    # else:
    # project = OPTIONS.project
    if XNAT.select('/data/projects/' + project + '/resources/BIDS_datatype').exists():
        for res in XNAT.select('/data/projects/' + project + '/resources/BIDS_datatype/files').get():
            if res.endswith('.json'):
                with open(XNAT.select('/data/projects/' + project + '/resources/BIDS_datatype/files/' + res).get(),
                          "r+") as f:
                    datatype_mapping = json.load(f)
                    sd_dict = datatype_mapping[project]
                    print(('\t\t>Using BIDS datatype mapping in project level %s' % (project)))
                    # sd_dict = {k.strip().replace('/', '_').replace(" ", "").replace(":", '_')
                    #: v for k, v in sd_dict.items()}
    else:
        print(('\t\t>WARNING: No BIDS datatype mapping in project %s - using default mapping' % (project)))
        # LOGGER.info('WARNING: No BIDS datatype mapping in project %s - using default mapping' % (project))
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
     Method to map scan type to task type for functional scans

     :return: mapping dict
     """
    tk_dict = {}
    # project = OPTIONS.project
    if XNAT.select('/data/projects/' + project + '/resources/BIDS_tasktype').exists():
        for res in XNAT.select('/data/projects/' + project + '/resources/BIDS_tasktype/files').get():
            if res.endswith('.json'):
                with open(XNAT.select('/data/projects/' + project + '/resources/BIDS_tasktype/files/'
                                      + res).get(), "r+") as f:
                    datatype_mapping = json.load(f)
                    # print "\t\t>Using tasktype mapping in project level %s" % (project)
                    tk_dict = datatype_mapping[project]
                    # tk_dict = {k.strip().replace('/', '_').replace(" ", "").replace(":", '_')
                    #: v for k, v in tk_dict.items()}

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


def dataset_description_file(BIDS_DIR, XNAT, project):
    """
    Build BIDS dataset description json file

    :return: None
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
    dd_file = os.path.join(BIDS_DIR, project)
    if not os.path.exists(dd_file):
        os.makedirs(dd_file)
    with open(os.path.join(dd_file, 'dataset_description.json'), 'w+') as f:
        json.dump(dataset_description, f, indent=2)





