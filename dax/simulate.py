# Show set of assssors thar would exist after build but dont create anything new
# must iterate to get downstream assessors

# simulate function:
# inputs: 
#    -project info (no xnat/bids required), table of existing scans and assessors 
#    -processing protocols/processors
# outputs: 
#   -table of *new" assessors that would be created
#   -table of existing that was loaded
# then show counts of existing or something?

import os
import tempfile
import logging
from pprint import pprint

from .rcq.projectinfo import load_project_info
from .rcq.taskbuilder import PROCESSING_RENAME, _get_proctype, _filter_labels, save_processor_file
from .processors import load_from_yaml, SgpProcessor
from .validate import validate as validate_processor


logger = logging.getLogger('dax')


class DaxSimulator(object):

    def __init__(self, rc, yamldir):
        self._redcap = rc
        self._yamldir = yamldir

    def _sim_processor(self, xnat, filepath, user_inputs, info, include_filters, custom=False, only_session=None, only_subject=None):
        procp = []

        # Load the processor
        logger.debug(f'loading processor from yaml:{filepath}')
        try:
            processor = load_from_yaml(
                xnat,
                filepath,
                user_inputs=user_inputs,
                job_template='~/job_template.txt'
            )            

        except Exception as err:
            logger.info(f'failed to load, cannot build:{filepath}:{err}')
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

            if only_subject:
                if only_subject in include_subjects:
                    include_subjects = [only_subject]
                else:
                    include_subjects = []

            logger.debug(f'include subjects={include_subjects}')

            # Apply the processor to filtered sessions
            for subj in sorted(include_subjects):
                logger.debug(f'subject:{subj}')
                inputsets = self._sim_subject_processor(processor, subj, info, custom=custom)

                # Create list of potentials for this subject/processor
                subjp = []
                for i in inputsets:
                    subjp.append({'SUBJECT': subj, 'INPUTS': i})

                # Add to list for this processor across all subjects
                procp.extend(subjp)
        else:
            # Handle session level processing

            # Get list of sessions to process
            if include_filters:
                include_sessions = _filter_labels(
                    info['all_sessions'], include_filters)
            else:
                include_sessions = info['all_sessions']

            if only_session:
                if only_session in include_sessions:
                    include_sessions = [only_session]
                else:
                    include_sessions = []

            logger.debug(f'include sessions={include_sessions}')

            # Apply the processor to filtered sessions
            for sess in sorted(include_sessions):
                logger.debug(f'session:{sess}')
                inputsets = self._sim_session_processor(processor, sess, info, custom=custom)
                sessp = []
                for i in inputsets:
                    sessp.append({'SESSION': sess, 'INPUTS': i})

                procp.extend(sessp)

        return procp

    def _load_protocols(self, project, tmpdir, unverified=False):
        protocols = []
        def_field = self._redcap.def_field
        yamldir = self._yamldir

        rec = self._redcap.export_records(
            records=[project],
            forms=['processing'],
            fields=[def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'processing']

        if unverified:
            rec = [x for x in rec if str(x['processing_complete']) in ['1', '2']]
        else:
            # Only enabled processing
            rec = [x for x in rec if str(x['processing_complete']) == '2']

        for r in rec:
            # Initialize record with project
            d = {'PROJECT': r[def_field]}

            # Find the yaml file
            if r['processor_yamlupload']:
                filepath = r['processor_yamlupload']
                filepath = save_processor_file(
                    self._redcap,
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

    def _sim_session_processor(self, processor, session, project_info, custom=False):
        # Get all possible input combinations
        inputsets = processor.parse_session_pd(session, project_info)

        # Filter out existing
        inputsets = _find_session_novels(inputsets, session, processor.name, project_info)

        # Return list of potential new combinations
        return inputsets

    def _sim_subject_processor(self, processor, subject, project_info, custom=False):
        # Get all possible input combinations
        inputsets = processor.parse_subject(subject, project_info)

        # Filter out existing
        inputsets = _find_subject_novels(inputsets, subject, processor.name, project_info)

        # Return list of potential new combinations
        return inputsets

    def simulate(
        self,
        project,
        xnat,
        processor=None,
        only_subject=None,
        only_session=None,
        unverified=None,
    ):
        allp = []

        # Load project info
        logger.info(f'loading project info:{project=}')
        info = load_project_info(xnat, project)

        print(f'PROJECT INFO:{project=}')
        print(info['name'])
        print('scan count=', len(info['scans']))
        print('assr count=', len(info['assessors']))
        print('sgp count=', len(info['sgp']))
        print('session count=', len(info['all_sessions']))
        print('subject count=', len(info['all_subjects']))

        # Simulate build on processor(s) to get potential assessors
        with tempfile.TemporaryDirectory() as tmpdir:
            logger.debug(f'loading processing protocols:{project}')
            protocols = self._load_protocols(project, tmpdir, unverified=unverified)

            # TODO: Iterate while new potentials are found

            # Iterate processing protocols
            for i, row in enumerate(protocols):
                filepath = row['FILE']

                logger.debug(f'{project}:{filepath}')

                # Validate first
                try:
                    validate_processor(filepath)
                    logger.info(f'Validated:{filepath}')
                except Exception as err:
                    logger.error(f'processor failed to validate:{filepath}:{err}')
                    continue

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
                procp = self._sim_processor(
                    xnat,
                    filepath,
                    user_inputs,
                    info,
                    include_filters,
                    custom=row['CUSTOM'],
                    only_session=only_session,
                    only_subject=only_subject
                )

                # Set proc type
                for p in procp:
                    p['TYPE'] = row['TYPE']

                allp.extend(procp)

        # Display existing and potential assessors
        if allp:
            print('Potential new assessors from simulated build=')
            pprint(allp)
        else:
            print('No potential new assessors from simulated build.')


def _find_session_novels(inputsets, session, proctype, project_info):
    novels = []

    assrs = [x for x in project_info.get('assessors') \
        if x['SESSION'] == session and x['PROCTYPE'] == proctype]

    existing = [x['INPUTS'] for x in assrs]

    for i in inputsets:
        matches = [x for x in existing if x == i]
        if not matches:
            novels.append(i)

    return novels


def _find_subject_novels(inputsets, subject, proctype, project_info):
    novels = []

    assrs = [x for x in project_info.get('sgp') \
        if x['SUBJECT'] == subject and x['PROCTYPE'] == proctype]

    existing = [x['INPUTS'] for x in assrs]

    for i in inputsets:
        matches = [x for x in existing if x == i]
        if not matches:
            novels.append(i)

    return novels
