import logging
import json

from dax.XnatUtils import decode_inputs


logger = logging.getLogger('manager.rcq.projectinfo')

# The scan URI is a hacky way to get a row for each resource of a every
# scan including all modalities. Things go awry when we try to add any
# other columns.
SCAN_URI = '/REST/experiments?xsiType=xnat:imagesessiondata\
&columns=\
project,\
subject_label,\
session_label,\
session_type,\
xnat:imagesessiondata/note,\
xnat:imagesessiondata/date,\
tracer_name,\
xnat:imagesessiondata/acquisition_site,\
xnat:imagesessiondata/label,\
xnat:imagescandata/id,\
xnat:imagescandata/type,\
xnat:imagescandata/quality,\
xnat:imagescandata/frames,\
xnat:imagescandata/file/label'


# The scan URI is a hacky way to get a row for each assessor. We do
# not try to get a row per resource because that query takes too long.
# The column name is: proc:genprocdata/out/file/label
ASSR_URI = '/REST/experiments?xsiType=xnat:imagesessiondata\
&columns=\
project,\
subject_label,\
session_label,\
session_type,\
xnat:imagesessiondata/acquisition_site,\
xnat:imagesessiondata/note,\
xnat:imagesessiondata/date,\
xnat:imagesessiondata/label,\
proc:genprocdata/label,\
proc:genprocdata/procstatus,\
proc:genprocdata/proctype,\
proc:genprocdata/validation/status,\
proc:genprocdata/validation/date,\
proc:genprocdata/validation/validated_by,\
proc:genprocdata/jobstartdate,\
last_modified,\
proc:genprocdata/inputs'


SGP_URI = '/REST/subjects?xsiType=xnat:subjectdata\
&columns=\
project,\
label,\
proc:subjgenprocdata/label,\
proc:subjgenprocdata/date,\
proc:subjgenprocdata/procstatus,\
proc:subjgenprocdata/proctype,\
proc:subjgenprocdata/validation/status,\
proc:subjgenprocdata/inputs,\
last_modified'


SCAN_RENAME = {
    'project': 'PROJECT',
    'subject_label': 'SUBJECT',
    'session_label': 'SESSION',
    'session_type': 'SESSTYPE',
    'tracer_name': 'TRACER',
    'xnat:imagesessiondata/note': 'NOTE',
    'xnat:imagesessiondata/date': 'DATE',
    'xnat:imagesessiondata/acquisition_site': 'SITE',
    'xnat:imagescandata/id': 'SCANID',
    'xnat:imagescandata/type': 'SCANTYPE',
    'xnat:imagescandata/quality': 'QUALITY',
    'xsiType': 'XSITYPE',
    'xnat:imagescandata/file/label': 'RESOURCES',
    'xnat:imagescandata/frames': 'FRAMES',
}

ASSR_RENAME = {
    'project': 'PROJECT',
    'subject_label': 'SUBJECT',
    'session_label': 'SESSION',
    'session_type': 'SESSTYPE',
    'xnat:imagesessiondata/note': 'NOTE',
    'xnat:imagesessiondata/date': 'DATE',
    'xnat:imagesessiondata/acquisition_site': 'SITE',
    'proc:genprocdata/label': 'ASSR',
    'proc:genprocdata/procstatus': 'PROCSTATUS',
    'proc:genprocdata/proctype': 'PROCTYPE',
    'proc:genprocdata/jobstartdate': 'JOBDATE',
    'proc:genprocdata/validation/status': 'QCSTATUS',
    'proc:genprocdata/validation/date': 'QCDATE',
    'proc:genprocdata/validation/validated_by': 'QCBY',
    'xsiType': 'XSITYPE',
    'proc:genprocdata/inputs': 'INPUTS',
}

SGP_RENAME = {
    'project': 'PROJECT',
    'label': 'SUBJECT',
    'proc:subjgenprocdata/date': 'DATE',
    'proc:subjgenprocdata/label': 'ASSR',
    'proc:subjgenprocdata/procstatus': 'PROCSTATUS',
    'proc:subjgenprocdata/proctype': 'PROCTYPE',
    'proc:subjgenprocdata/validation/status': 'QCSTATUS',
    'proc:subjgenprocdata/inputs': 'INPUTS'}

XSI2MOD = {
    'xnat:eegSessionData': 'EEG',
    'xnat:mrSessionData': 'MR',
    'xnat:petSessionData': 'PET'}


def load_project_info(xnat, project):
    info = {}

    logger.info(f'loading project info from XNAT:{project}')

    info['name'] = project
    info['scans'] = _load_scan_data(xnat, project)
    info['assessors'] = _load_assr_data(xnat, project)
    info['sgp'] = _load_sgp_data(xnat, project)

    info['all_sessions'] = list(set([x['SESSION'] for x in info['scans']]))
    info['all_subjects'] = list(set([x['SUBJECT'] for x in info['scans']]))

    return info


def _get_result(xnat, uri):
    logger.debug(uri)
    json_data = json.loads(xnat._exec(uri, 'GET'), strict=False)
    return json_data['ResultSet']['Result']


def _scan_info(record):
    """Get scan info."""
    info = {}

    for k, v in SCAN_RENAME.items():
        info[v] = record[k]

    # set_modality
    info['MODALITY'] = XSI2MOD.get(info['XSITYPE'], 'UNK')

    # Get the full path
    _p = '/projects/{0}/subjects/{1}/experiments/{2}/scans/{3}'.format(
        info['PROJECT'],
        info['SUBJECT'],
        info['SESSION'],
        info['SCANID'])
    info['full_path'] = _p

    return info


def _assessor_info(record):
    """Get assessor info."""
    info = {}

    for k, v in ASSR_RENAME.items():
        info[v] = record[k]

    # Decode inputs into list
    info['INPUTS'] = decode_inputs(info['INPUTS'])

    # Get the full path
    _p = '/projects/{0}/subjects/{1}/experiments/{2}/assessors/{3}'.format(
        info['PROJECT'],
        info['SUBJECT'],
        info['SESSION'],
        info['ASSR'])
    info['full_path'] = _p

    # set_modality
    info['MODALITY'] = XSI2MOD.get(info['XSITYPE'], 'UNK')

    return info


def _sgp_info(record):
    """Get subject assessor info."""
    info = {}

    # Copy with new var names
    for k, v in SGP_RENAME.items():
        info[v] = record[k]

    info['XSITYPE'] = 'proc:subjgenprocdata'

    # Decode inputs into list
    info['INPUTS'] = decode_inputs(info['INPUTS'])

    # Get the full path
    _p = '/projects/{0}/subjects/{1}/assessors/{2}'.format(
        info['PROJECT'],
        info['SUBJECT'],
        info['ASSR'])
    info['full_path'] = _p

    return info


def _load_scan_data(xnat, project):
    # Get main project scans
    uri = SCAN_URI + f'&project={project}'
    result = _get_result(xnat, uri)

    # Append shared project scans
    uri = SCAN_URI + f'&xnat:imagesessiondata/sharing/share/project={project}'
    result += _get_result(xnat, uri)

    # Change from one row per resource to one row per scan
    scans = {}
    for r in result:
        # Force project to be requested not parent
        r['project'] = project

        k = (r['project'], r['session_label'], r['xnat:imagescandata/id'])
        if k in scans.keys():
            # Append to list of resources
            _resource = r['xnat:imagescandata/file/label']
            scans[k]['RESOURCES'] += ',' + _resource
        else:
            scans[k] = _scan_info(r)

    # Get just the values in a list
    scans = list(scans.values())

    return scans


def _load_assr_data(xnat, project):
    """Get assessor info from XNAT as list of dicts."""
    assessors = []
    uri = ASSR_URI
    uri += f'&project={project}'

    result = _get_result(xnat, uri)

    # Append shared project assessors
    uri = ASSR_URI + f'&xnat:imagesessiondata/sharing/share/project={project}'
    result += _get_result(xnat, uri)

    for r in result:
        # Force project to be requested not parent
        r['project'] = project
        assessors.append(_assessor_info(r))

    return assessors


def _load_sgp_data(xnat, project):
    """Get assessor info from XNAT as list of dicts."""
    assessors = []
    uri = SGP_URI
    uri += f'&project={project}'

    logger.debug(f'get_result uri=:{uri}')
    result = _get_result(xnat, uri)

    for r in result:
        assessors.append(_sgp_info(r))

    return assessors
