""" Trial Builder for DAX"""

import os, shutil
import logging
import tempfile

from dax.task import NeedInputsException, NoDataException
from dax.task import JOB_PENDING, JOB_RUNNING
from dax.task import NEED_INPUTS, NEED_TO_RUN, NO_DATA
from dax.processors import load_from_yaml, SgpProcessor
from .projectinfo import load_project_info
from .taskqueue import TaskQueue
from dax import validate


logger = logging.getLogger('dax')


PREFIX = 'TRIAL_'


class TrialBuilder(object):
    # Builds trial run of a processor on a project by creating assessor in XNAT and adding to queue in REDCap

    def __init__(self, projects_redcap, xnat, xnat_override=None):
        self._projects_rc = projects_redcap
        self._xnat = xnat
        self._queue = TaskQueue(projects_redcap)
        self._xnat_override = xnat_override

    def build(self, project, yaml_file, subject):
        logger.info(f'{project}:{yaml_file}:{subject}')

        try:
            validate.validate(yaml_file)
            logger.info('processor yaml is valid!')
        except Exception as err:
            logger.info(f'processor yanml is not valid!:{err}')
            raise Exception(f'Invalid yaml')

        with tempfile.TemporaryDirectory() as tmpdir:
            # Configure processor as "TRIAL" by making a temporary copy with prefix
            temp_file = os.path.join(tmpdir, PREFIX + os.path.basename(yaml_file))

            try:
                shutil.copy(yaml_file, temp_file)
            except Exception as err:
                raise Exception(f'error copying yaml file:{yaml_file}:{err}')

            # Load the processor object from yaml file
            logger.debug(f'loading processor from yaml:{temp_file}')
            try:
                processor = load_from_yaml(self._xnat, temp_file, job_template='~/job_template.txt')
            except Exception as err:
                logger.error(f'failed to load, cannot build:{temp_file}:{err}')
                raise Exception(f'failed to load processor from yaml:{err}')

            if not processor:
                logger.error(f'loading processor:{temp_file}')
                raise Exception(f'failed to load processor from yaml:{err}')

            # Load project info
            info = load_project_info(self._xnat, project)

            if isinstance(processor, SgpProcessor):
                if subject not in info['all_subjects']:
                    raise Exception(f'subject not found:{subject}')

                self._build_subject_trial(processor, subject, info)
            else:
                session  = subject
                if session not in info['all_sessions']:
                    raise Exception(f'session not found:{session}')

                self._build_session_trial(processor, session, info)

    def _build_session_trial(self, processor, session, project_info):
        # Get list of inputs sets (not yet matched with existing)
        inputsets = processor.parse_session_pd(session, project_info)

        for inputs in inputsets:
            if inputs == {}:
                # Blank inputs
                return

            # Get(create) assessor with given inputs and proc type
            (assr, info) = processor.get_assessor(
                session, inputs, project_info)

            if info['PROCSTATUS'] in [NEED_TO_RUN, NEED_INPUTS]:
                logger.info(f'building task:{info["ASSR"]}')
                (assr, info) = self._build_trial(assr, info, processor, project_info)
                logger.debug(f'{info}')
                logger.info(info['PROCSTATUS'])
            else:
                logger.info('already built:{}'.format(info['ASSR']))

    def _build_subject_trial(self, processor, subject, project_info):
        # Get list of inputs sets (not yet matched with existing)
        inputsets = processor.parse_subject(subject, project_info)

        for inputs in inputsets:
            if inputs == {}:
                # Blank inputs
                return

            # Get(creating if necessary) assessor with given inputs and proctype
            (assr, info) = processor.get_assessor(
                self._xnat, subject, inputs, project_info)

            if info['PROCSTATUS'] in [NEED_TO_RUN, NEED_INPUTS]:
                logger.info(f'building task:{info["ASSR"]}')
                (assr, info) = self._build_trial(assr, info, processor, project_info)
                logger.debug(f'assr after={info}')
                logger.info(info['PROCSTATUS'])
            else:
                logger.info('already built:{}'.format(info['ASSR']))

    def _build_trial(self, assr, info, processor, project_info):
        '''Build a task, create assessor in XNAT, add new record to redcap'''
        old_proc_status = info['PROCSTATUS']
        old_qc_status = info['QCSTATUS']

        try:
            var2val, inputlist = processor.build_var2val(
                assr,
                info,
                project_info)

            if self._xnat_override:
                # Replace the xnat host with the override so that
                # correct host is used to downlod the inputs
                for i in inputlist:
                    _old = self._xnat.host 
                    _new = self._xnat_override
                    i['fpath'] = i['fpath'].replace(_old, _new)

            self._queue._add_task(
                project_info['name'],
                info['ASSR'],
                inputlist,
                var2val,
                processor.walltime_str,
                processor.memreq_mb,
                processor.yaml_file,
                processor.user_inputs,
                custom=True
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
