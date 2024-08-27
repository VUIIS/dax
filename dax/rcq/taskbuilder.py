""" Task Builder for DAX in REDCap."""

import os
import logging
import re
import fnmatch
import tempfile


from dax.task import NeedInputsException, NoDataException
from dax.task import JOB_PENDING, JOB_RUNNING
from dax.task import NEED_INPUTS, NEED_TO_RUN, NO_DATA
from dax.processors import load_from_yaml, SgpProcessor
from .projectinfo import load_project_info
from .taskqueue import TaskQueue

logger = logging.getLogger('manager.rcq.taskbuilder')


PROCESSING_RENAME = {
    'redcap_repeat_instance': 'ID',
    'processor_file': 'FILE',
    'processor_filter': 'FILTER',
    'processor_args': 'ARGS',
    'processing_complete': 'COMPLETE',
}


class TaskBuilder(object):
    # Builds tasks and adds to queue in REDCap

    def __init__(self, projects_redcap, xnat, yamldir):
        self._projects_rc = projects_redcap
        self._xnat = xnat
        self._yamldir = yamldir
        self._queue = TaskQueue(projects_redcap)
        self._build_projects = self.projects_with_processing()

    def update(self, project):

        if project not in self._build_projects:
            logger.info(f'no processing protocols found:{project}')
            return

        with tempfile.TemporaryDirectory() as tmpdir:

            logger.debug(f'loading processing protools:{project}')
            protocols = self._load_protocols(project, tmpdir)

            if len(protocols) == 0:
                logger.debug(f'no processing protocols found:{project}')
                return

            info = load_project_info(self._xnat, project)

            # Iterate processing protocols
            for i, row in enumerate(protocols):
                filepath = row['FILE']

                logger.info(f'{project}:{filepath}')

                if row.get('ARGS', False):
                    user_inputs = row.get('ARGS')
                    logger.debug(f'overrides:{user_inputs}')
                    rlist = user_inputs.strip().split('\r\n')
                    rdict = {}
                    for arg in rlist:
                        try:
                            key, val = arg.split(':', 1)
                            rdict[key] = val.strip()
                        except ValueError as e:
                            msg = f'invalid arg:{project}:{filepath}:{arg}:{e}'
                            raise Exception(msg)

                    user_inputs = rdict
                    logger.debug(f'user_inputs:{user_inputs}')
                else:
                    user_inputs = None

                if row['FILTER']:
                    include_filters = row['FILTER'].replace(' ', '').split(',')
                else:
                    include_filters = []

                logger.debug(f'building processor:{filepath}')
                self._build_processor(
                    filepath,
                    user_inputs,
                    info,
                    include_filters,
                    custom=row['CUSTOM'])

    def build_projects(self):
        return self._build_projects

    def _build_processor(self, filepath, user_inputs, info, include_filters, custom=False):
        # Get lists of subjects/sessions for filtering

        # Load the processor
        logger.debug(f'loading processor from yaml:{filepath}')
        try:
            processor = load_from_yaml(
                self._xnat,
                filepath,
                user_inputs=user_inputs,
                job_template='~/job_template.txt')
        except Exception as err:
            logger.debug(f'failed to load, cannot build:{filepath}:{err}')
            return

        if not processor:
            logger.error(f'loading processor:{filepath}')
            return

        if isinstance(processor, SgpProcessor):
            # Handle subject level processing

            # Get list of subjects to process
            if include_filters:
                include_subjects = _filter_labels(
                    info['all_subjects'], include_filters)
            else:
                include_subjects = info['all_subjects']

            logger.debug(f'include subjects={include_subjects}')

            # Apply the processor to filtered sessions
            for subj in sorted(include_subjects):
                logger.debug(f'subject:{subj}')
                self._build_subject_processor(
                    processor, subj, info, custom=custom)
        else:
            # Handle session level processing

            # Get list of sessions to process
            if include_filters:
                include_sessions = _filter_labels(
                    info['all_sessions'], include_filters)
            else:
                include_sessions = info['all_sessions']

            logger.debug(f'include sessions={include_sessions}')

            # Apply the processor to filtered sessions
            for sess in sorted(include_sessions):
                self._build_session_processor(
                    processor, sess, info, custom=custom)

    def projects_with_processing(self):
        def_field = self._projects_rc.def_field

        rec = self._projects_rc.export_records(
            forms=['processing'],
            fields=[def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'processing']

        # Only enabled processing
        rec = [x for x in rec if str(x['processing_complete']) == '2']

        projects = list(set([x[def_field] for x in rec]))

        return projects

    def _load_protocols(self, project, tmpdir):
        protocols = []
        def_field = self._projects_rc.def_field
        yamldir = self._yamldir

        rec = self._projects_rc.export_records(
            records=[project],
            forms=['processing'],
            fields=[def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'processing']

        # Only enabled processing
        rec = [x for x in rec if str(x['processing_complete']) == '2']

        for r in rec:
            # Initialize record with project
            d = {'PROJECT': r[def_field]}

            # Find the yaml file
            if r['processor_yamlupload']:
                filepath = r['processor_yamlupload']
                filepath = self._save_processor_file(
                    project,
                    r['redcap_repeat_instance'],
                    tmpdir)
                d['CUSTOM'] = True
            else:
                filepath = r['processor_file']
                d['CUSTOM'] = False

            if not os.path.isabs(filepath):
                # Prepend lib location
                filepath = os.path.join(yamldir, filepath)

            if not os.path.isfile(filepath):
                logger.info(f'file not found:{filepath}')
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

    def _save_processor_file(self, project, repeat_id, outdir):
        # Get the file contents from REDCap
        try:
            (cont, hdr) = self._projects_rc.export_file(
                record=project,
                field='processor_yamlupload',
                repeat_instance=repeat_id)

            if cont == '':
                raise Exception('error exporting file from REDCap')

        except Exception as err:
            logger.error(f'downloading file:{err}')
            return None

        # Save contents to local file
        filename = os.path.join(outdir, hdr['name'])
        try:
            with open(filename, 'wb') as f:
                f.write(cont)

            return filename
        except FileNotFoundError as err:
            logger.error(f'file not found:{filename}:{err}')
            return None

    def _build_session_processor(self, processor, session, project_info, custom=False):
        # Get list of inputs sets (not yet matched with existing)
        inputsets = processor.parse_session_pd(session, project_info)

        logger.debug(f'{session}:{processor.name}')

        logger.debug(inputsets)
        for inputs in inputsets:
            if inputs == {}:
                # Blank inputs
                return

            # Get(create) assessor with given inputs and proc type
            (assr, info) = processor.get_assessor(
                session, inputs, project_info)

            if info['PROCSTATUS'] in [NEED_TO_RUN, NEED_INPUTS]:
                logger.debug('building task')
                (assr, info) = self._build_task(
                    assr, info, processor, project_info, custom=custom)

                logger.debug(f'{info}')
                logger.debug(
                    'status:{}:{}'.format(info['ASSR'], info['PROCSTATUS']))
            else:
                logger.debug('already built:{}'.format(info['ASSR']))

    def _build_subject_processor(self, processor, subject, project_info, custom=False):
        logger.debug(f'{subject}:{processor.name}')
        # Get list of inputs sets (not yet matched with existing)
        inputsets = processor.parse_subject(subject, project_info)
        logger.debug(inputsets)

        for inputs in inputsets:

            if inputs == {}:
                # Blank inputs
                return

            # Get(create) assessor with given inputs and proc type
            (assr, info) = processor.get_assessor(
                self._xnat, subject, inputs, project_info)

            if info['PROCSTATUS'] in [NEED_TO_RUN, NEED_INPUTS]:
                logger.debug('building task')
                (assr, info) = self._build_task(
                    assr, info, processor, project_info, custom=custom)

                logger.debug(f'assr after={info}')
            else:
                logger.debug('already built:{}'.format(info['ASSR']))

    def _build_task(self, assr, info, processor, project_info, custom=False):
        '''Build a task, create assessor in XNAT, add new record to redcap'''
        old_proc_status = info['PROCSTATUS']
        old_qc_status = info['QCSTATUS']

        try:
            var2val, inputlist = processor.build_var2val(
                assr,
                info,
                project_info)

            self._queue._add_task(
                project_info['name'],
                info['ASSR'],
                inputlist,
                var2val,
                processor.walltime_str,
                processor.memreq_mb,
                processor.yaml_file,
                processor.user_inputs,
                custom=custom
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


def _filter_matches(match_input, match_filter):
    return re.match(fnmatch.translate(match_filter), match_input)


def _filter_labels(labels, filters):
    filtered_labels = []

    for f in filters:
        filtered_labels += [x for x in labels if _filter_matches(x, f)]

    return list(set(filtered_labels))


def _get_proctype(procfile):
    # Get just the filename without the directory path
    tmp = os.path.basename(procfile)

    # Split on periods and grab the 4th value from right,
    # thus allowing periods in the main processor name
    return tmp.rsplit('.')[-4]
