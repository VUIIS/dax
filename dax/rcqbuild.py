""" Build tasks in from XNAT/REDCap."""
import logging
import re
import fnmatch
import json
import os
import tempfile

from dax.task import NeedInputsException, NoDataException
from dax.task import JOB_PENDING, JOB_RUNNING
from dax.task import NEED_INPUTS, NEED_TO_RUN, NO_DATA
from dax.processors import load_from_yaml, SgpProcessor
from dax.XnatUtils import decode_inputs

logger = logging.getLogger('dax.rcqbuild')

DONE_STATUSES = ['COMPLETE', 'JOB_FAILED', 'FAILED']

SUBDIRS = ['OUTLOG', 'PBS', 'PROCESSOR']


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


PROCESSING_RENAME = {
    'redcap_repeat_instance': 'ID',
    'processor_file': 'FILE',
    'processor_filter': 'FILTER',
    'processor_args': 'ARGS',
    'processing_complete': 'COMPLETE',
}


def update(rc, xnat, yamldir):
    """Update tasks."""
    f = rc.def_field
    projects = [x[f] for x in rc.export_records(fields=[f])]

    for p in projects:
        logger.debug(f'updating tasks:{p}')
        with tempfile.TemporaryDirectory() as tmpdir:
            _update_project(rc, xnat, p, yamldir, tmpdir)


def _update_project(projects_redcap, xnat, project, yamldir, tmpdir):
    project_data = {}
    protocols = _load_protocols(projects_redcap, project, yamldir, tmpdir)

    if len(protocols) == 0:
        logger.info('no processing protocols found')
        return

    project_data['name'] = project
    project_data['scans'] = _load_scan_data(xnat, project)
    project_data['assessors'] = _load_assr_data(xnat, project)
    project_data['sgp'] = _load_sgp_data(xnat, project)

    # Iterate processing protocols
    for i, row in enumerate(protocols):
        filepath = row['FILE']

        logger.info(f'file:{project}:{filepath}')

        user_inputs = row.get('ARGS', None)
        if user_inputs:
            logger.debug(f'overrides:{user_inputs}')
            rlist = user_inputs.strip().split('\r\n')
            rdict = {}
            for arg in rlist:
                try:
                    key, val = arg.split(':', 1)
                    rdict[key] = val.strip()
                except ValueError as e:
                    msg = f'invalid arguments:{project}:{filepath}:{arg}:{e}'
                    raise Exception(msg)

            user_inputs = rdict
            logger.debug(f'user_inputs:{user_inputs}')

        if row['FILTER']:
            include_filters = str(row['FILTER']).replace(' ', '').split(',')
        else:
            include_filters = []

        _build_processor(
            projects_redcap,
            xnat,
            filepath,
            user_inputs,
            project_data,
            include_filters)


def _load_protocols(projects_redcap, project, yamldir, tmpdir):
    protocols = []

    rec = projects_redcap.export_records(
        records=[project],
        forms=['processing'],
        fields=[projects_redcap.def_field])

    print(rec)

    rec = [x for x in rec if x['redcap_repeat_instrument'] == 'processing']

    # Only enabled processing
    rec = [x for x in rec if str(x['processing_complete']) == '2']

    for r in rec:
        # Initialize record with project
        d = {'PROJECT': r[projects_redcap.def_field]}

        # Find the yaml file
        if r['processor_yamlupload']:
            filepath = r['processor_yamlupload']
            filepath = _save_processor_file(
                projects_redcap,
                project,
                r['redcap_repeat_instance'],
                tmpdir)
        else:
            filepath = r['processor_file']

        if not os.path.isabs(filepath):
            # Prepend lib location
            filepath = os.path.join(yamldir, filepath)

        if not os.path.isfile(filepath):
            logger.debug(f'file not found:{filepath}')
            continue

        # Get renamed variables
        for k, v in PROCESSING_RENAME.items():
            d[v] = r.get(k, '')

        d['FILE'] = filepath
        d['TYPE'] = _get_proctype(d['FILE'])

        d['EDIT'] = 'edit'

        # Finally, add to our list
        protocols.append(d)

    return protocols


def _get_proctype(procfile):
    # Get just the filename without the directory path
    tmp = os.path.basename(procfile)

    # Split on periods and grab the 4th value from right,
    # thus allowing periods in the main processor name
    return tmp.rsplit('.')[-4]


def _save_processor_file(project, record_id, repeat_id, outdir):
    # Get the file contents from REDCap
    try:
        (cont, hdr) = project.export_file(
            record=record_id,
            field='processor_yamlupload',
            event=None,
            repeat_instance=repeat_id)

        if cont == '':
            raise Exception('error exporting file from REDCap')

    except Exception as err:
        logging.error(f'downloading file:{err}')
        return None

    # Save contents to local file
    filename = os.path.join(outdir, hdr['name'])
    try:
        with open(filename, 'wb') as f:
            f.write(cont)

        return filename
    except FileNotFoundError as err:
        logging.error(f'file not found:{filename}:{err}')
        return None


def _upload_task_processor_file(rc, record_id, repeat_id, filename):
    with open(filename, 'rb') as f:
        return rc.import_file(
            record=record_id,
            field='task_yamlupload',
            file_name=os.path.basename(filename),
            event=None,
            repeat_instance=repeat_id,
            file_object=f)


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
    uri = SCAN_URI
    uri += f'&project={project}'

    result = _get_result(xnat, uri)

    # Change from one row per resource to one row per scan
    scans = {}
    for r in result:
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

    for r in result:
        assessors.append(_assessor_info(r))

    return assessors


def _load_sgp_data(xnat, project):
    """Get assessor info from XNAT as list of dicts."""
    assessors = []
    uri = SGP_URI
    uri += f'&project={project}'

    logging.debug(f'get_result uri=:{uri}')
    result = _get_result(xnat, uri)

    for r in result:
        assessors.append(_sgp_info(r))

    return assessors


def _build_processor(
    rc,
    xnat,
    filepath,
    user_inputs,
    project_data,
    include_filters
):

    # Get lists of subjects/sessions for filtering
    all_sessions = list(set([x['SESSION'] for x in project_data.get('scans')]))
    all_subjects = list(set([x['SUBJECT'] for x in project_data.get('scans')]))

    # Load the processor
    processor = load_from_yaml(
        xnat,
        filepath,
        user_inputs=user_inputs,
        job_template='~/job_template.txt')

    if not processor:
        logger.error(f'loading processor:{filepath}')
        return

    if isinstance(processor, SgpProcessor):
        # Handle subject level processing

        # Get list of subjects to process
        if include_filters:
            include_subjects = _filter_labels(all_subjects, include_filters)
        else:
            include_subjects = all_subjects

        logger.debug(f'include subjects={include_subjects}')

        # Apply the processor to filtered sessions
        for subj in sorted(include_subjects):
            logger.debug(f'subject:{subj}')
            _build_subject_processor(rc, xnat, processor, subj, project_data)
    else:
        # Handle session level processing

        # Get list of sessions to process
        if include_filters:
            include_sessions = _filter_labels(all_sessions, include_filters)
        else:
            include_sessions = all_sessions

        logger.debug(f'include sessions={include_sessions}')

        # Apply the processor to filtered sessions
        for sess in sorted(include_sessions):
            _build_session_processor(rc, xnat, processor, sess, project_data)


def _build_session_processor(rc, xnat, processor, session, project_data):
    # Get list of inputs sets (not yet matched with existing)
    inputsets = processor.parse_session(session, project_data)

    logger.debug(f'{session}:{processor.name}')

    logger.debug(inputsets)
    for inputs in inputsets:
        if inputs == {}:
            # Blank inputs
            return

        # Get(create) assessor with given inputs and proc type
        (assr, info) = processor.get_assessor(session, inputs, project_data)

        if info['PROCSTATUS'] in [NEED_TO_RUN, NEED_INPUTS]:
            logger.debug('building task')
            (assr, info) = _build_task(
                rc, xnat, assr, info, processor, project_data)

            logger.debug(f'{info}')
            logger.debug(
                'status:{}:{}'.format(info['ASSR'], info['PROCSTATUS']))
        else:
            logger.debug('already built:{}'.format(info['ASSR']))


def _build_subject_processor(rc, xnat, processor, subject, project_data):
    logger.debug(f'{subject}:{processor.name}')
    # Get list of inputs sets (not yet matched with existing)
    inputsets = processor.parse_subject(subject, project_data)
    logger.debug(inputsets)

    for inputs in inputsets:

        if inputs == {}:
            # Blank inputs
            return

        # Get(create) assessor with given inputs and proc type
        (assr, info) = processor.get_assessor(subject, inputs, project_data)

        if info['PROCSTATUS'] in [NEED_TO_RUN, NEED_INPUTS]:
            logger.debug('building task')
            (assr, info) = _build_task(
                rc, xnat, assr, info, processor, project_data)

            logger.debug(f'assr after={info}')
        else:
            logger.debug('already built:{}'.format(info['ASSR']))


def _build_task(rc, xnat, assr, info, processor, project_data):
    '''Build a task, create assessor in XNAT, add new record to redcap queue'''
    old_proc_status = info['PROCSTATUS']
    old_qc_status = info['QCSTATUS']

    try:
        var2val, inputlist = processor.build_var2val(
            assr,
            info,
            project_data)

        _add_task(
            rc,
            project_data['name'],
            info['ASSR'],
            inputlist,
            var2val,
            processor.walltime_str,
            processor.memreq_mb,
            processor.yaml_file,
            processor.user_inputs
        )

        # Set new statuses to be updated
        new_proc_status = JOB_RUNNING
        new_qc_status = JOB_PENDING
    except NeedInputsException as e:
        new_proc_status = NEED_INPUTS
        new_qc_status = e.value
    except NoDataException as e:
        new_proc_status = NO_DATA
        new_qc_status = e.value

    # Update on xnat
    _xsitype = processor.xsitype.lower()
    if new_proc_status != old_proc_status:
        assr.attrs.set(f'{_xsitype}/procstatus', new_proc_status)
    if new_qc_status != old_qc_status:
        assr.attrs.set(f'{_xsitype}/validation/status', new_qc_status)

    # Update local info
    info['PROCSTATUS'] = new_proc_status
    info['QCSTATUS'] = new_qc_status

    return (assr, info)


def _add_task(
    rc,
    project,
    assr,
    inputlist,
    var2val,
    walltime,
    memreq,
    yamlfile,
    userinputs
):
    """Add a new task record ."""

    # Convert to string for storing
    var2val = json.dumps(var2val)
    inputlist = json.dumps(inputlist)

    # Try to match existing record
    task_id = _assessor_task_id(rc, project, assr)

    if not os.path.dirname(yamlfile):
        task_yamlfile = 'CUSTOM'
    else:
        task_yamlfile = os.path.basename(yamlfile)

    if task_id:
        # Update existing record
        try:
            record = {
                'main_name': project,
                'redcap_repeat_instrument': 'taskqueue',
                'redcap_repeat_instance': task_id,
                'task_status': 'QUEUED',
                'task_inputlist': inputlist,
                'task_var2val': var2val,
                'task_walltime': walltime,
                'task_memreq': memreq,
                'task_yamlfile': task_yamlfile,
                'task_userinputs': userinputs,
                'task_timeused': '',
                'task_memused': '',
            }
            response = rc.import_records([record])
            assert 'count' in response
            logger.debug('task record created')
        except AssertionError as err:
            logger.error(f'upload failed:{err}')
            return
    else:
        # Create a new record
        try:
            record = {
                'main_name': project,
                'redcap_repeat_instrument': 'taskqueue',
                'redcap_repeat_instance': 'new',
                'task_assessor': assr,
                'task_status': 'QUEUED',
                'task_inputlist': inputlist,
                'task_var2val': var2val,
                'task_walltime': walltime,
                'task_memreq': memreq,
                'task_yamlfile': task_yamlfile,
                'task_userinputs': userinputs,
            }
            response = rc.import_records([record])
            assert 'count' in response
            logger.debug('task record created')

        except AssertionError as err:
            logger.error(f'upload failed:{err}')
            return

    # If the file is not in yaml dir, we need to upload it to the task
    if task_yamlfile == 'CUSTOM':
        logger.debug(f'yaml not in shared library, uploading to task')
        if not task_id:
            # Try to match existing record
            task_id = _assessor_task_id(rc, project, assr)

        logger.debug(f'uploading file:{yamlfile}')
        _upload_task_processor_file(
            rc,
            project,
            yamlfile,
            repeat_id=task_id)


def _assessor_task_id(projects_redcap, project, assessor):
    task_id = None

    rec = projects_redcap.export_records(
        forms=['taskqueue'],
        records=[project],
        fields=[projects_redcap.def_field, 'task_assessor'])

    rec = [x for x in rec if x['redcap_repeat_instrument'] == 'taskqueue']
    rec = [x for x in rec if x['task_assessor'] == assessor]

    if len(rec) > 1:
        logger.warn(f'duplicate tasks for assessor, not good:{assessor}')
        task_id = rec[0]['redcap_repeat_instance']
    elif len(rec) == 1:
        task_id = rec[0]['redcap_repeat_instance']

    return task_id


def _filter_matches(match_input, match_filter):
    return re.match(fnmatch.translate(match_filter), match_input)


def _filter_labels(labels, filters):
    filtered_labels = []

    for f in filters:
        filtered_labels += [x for x in labels if _filter_matches(x, f)]

    return list(set(filtered_labels))
