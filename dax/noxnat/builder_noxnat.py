""" Task Builder for DAX without XNAT, builds using duckdb data and local filesystem. 

Creates assessor with input artefacts in duckdb. 

Stops at NEEDS_RUN, ready for launch.

If any required files are missing, raises NEED_INPUTS.

Inputs is stored in database as a string, but should always be a dict after loaded
"""

import os
import logging
import json
from datetime import date
from uuid import uuid4

import duckdb

from ..rcq.taskbuilder import _filter_labels, _filter_matches, _get_proctype
from ..task import JOB_PENDING, JOB_RUNNING
from ..task import NEED_INPUTS, NEED_TO_RUN, NO_DATA, RERUN, REPROC_RES_SKIP_LIST
from ..task import NeedInputsException, NoDataException
from ..XnatUtils import decode_inputs
from .processors_noxnat import ProcessorNoXnat, load_from_yaml_noxnat
from .database_noxnat import DatabaseNoXnat


logger = logging.getLogger('dax')


# TODO: handle JOB_RUNNING in assessors with lost task in taskqueue


class TaskBuilderNoXnat(object):
    # Builds tasks and adds to queue

    def __init__(self, rootdir):
        self._rootdir = rootdir
        self._dbfile = f'{rootdir}/db/dax.duckdb'
        self._db = DatabaseNoXnat(self._dbfile)
        self._data = self._load_data()
        self._yamldir = f'{rootdir}/processors'
        self._singularitys_dir = f'{rootdir}/singularitys'
        self._logs_dir = f'{rootdir}/logs'
        self._scans_dir = f'{rootdir}/scans'
        self._assrs_dir = f'{rootdir}/assessors'
        self._flags_dir = f'{rootdir}/flagfiles'
        self._build_projects = self.projects_with_processing()

    def _load_data(self):
        return self._db.load_data()

    def _project_info(self, project):
        '''Extract project info from data'''
        info = {}

        # Scans
        scans = self._data['scans']
        scans = scans[scans.PROJECT == project]
        scans['full_path'] = 'scans/NIFTI/' + \
            scans['PROJECT'].astype(str) + '/' + \
            scans['SUBJECT'].astype(str) + '/' + \
            scans['SESSION'].astype(str) + '/' + \
            scans['SCANID'].astype(str) + '-x-' + \
            scans['SCANTYPE'].astype(str) + '-x-' + \
            scans['DESCRIP'].astype(str)

        # Convert to list of dicts instead of df
        info['scans'] = scans.to_dict('records')

        # Assessors
        _assrs = self._data['assessors']
        _assrs['full_path'] = \
            'asssessors/' + \
            _assrs['PROJECT'] + '/' + \
            #_assrs['SUBJECT'] + '/' + \
            _assrs['ASSR']

        # Decode inputs
        records = _assrs[_assrs.PROJECT == project].to_dict('records')
        for i, r in enumerate(records):
            inputs = r['INPUTS']
            if isinstance(inputs, str):
                try:
                    records[i]['INPUTS'] = decode_inputs(inputs)
                except Exception as err:
                    records[i]['INPUTS'] = {}
                    continue

        info['assessors'] = records

        # Quick access information
        info['all_sessions'] = list(set([x['SESSION'] for x in info['scans']]))
        info['all_subjects'] = list(set([x['SUBJECT'] for x in info['scans']]))
        info['name'] = project
        info['rootdir'] = self._rootdir

        return info

    def _project_protocols(self, project):
        protocols = []

        _protocols = self._data['processors']
        protocols =  _protocols[_protocols.PROJECT == project].to_dict('records')

        return protocols

    def update_all(self, only_session=None):
        results = []
        projects = self._build_projects

        logger.debug(f'update_all:{projects=}')

        for p in projects:
            logger.debug(f'update:{p=}')
            results.extend(self.update(p, only_session=only_session))

        return results

    def update(self, project, only_session=None, only_subject=None):
        results = []

        if project not in self._build_projects:
            logger.info(f'no processing protocols found:{project}')
            return results

        logger.debug(f'loading processing protocols:{project}')
        protocols = self._load_protocols(project)

        if len(protocols) == 0:
            logger.debug(f'no processing protocols found:{project}')
            return results

        info = self._project_info(project)

        # Iterate processing protocols
        for i, row in enumerate(protocols):
            filepath = row['FILE']

            logger.info(f'{project}:{filepath}')

            if row.get('ARGS', False):
                user_inputs = row.get('ARGS').replace('=', ':')
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

            if row.get('FILTER', ''):
                include_filters = row['FILTER'].replace(' ', '').split(',')
            else:
                include_filters = []

            custom = row.get('CUSTOM', False)

            logger.debug(f'building processor:{filepath}')
            cur_results = self._build_processor(
                filepath,
                user_inputs,
                info,
                include_filters,
                custom=custom,
                only_session=only_session,
                only_subject=only_subject)

            results.extend(cur_results)

        return results

    def update_session(self, project, session):
        return self.update(project, only_session=session)

    def update_subject(self, project, subject):
        return self.update(project, only_subject=subject)

    def build_projects(self):
        return self._build_projects

    def _build_processor(self, filepath, user_inputs, info, include_filters, custom=False, only_session=None, only_subject=None):
        # Get lists of subjects/sessions for filtering
        results = []

        try:
            processor = load_from_yaml_noxnat(
                filepath,
                user_inputs=user_inputs,
                job_template='~/job_template.txt')
        except Exception as err:
            logger.warn(f'failed to load, cannot build:{filepath}:{err}')
            return results

        if not processor:
            logger.error(f'loading processor:{filepath}')
            return results

        if False:
            # TBD: handle SGP
            # Handle subject level processing
            pass
        else:
            # Handle session level processing

            if include_filters:
                # Get list of sessions to process
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
                cur_results = self._build_session_processor(processor, sess, info, custom=custom)
                results.extend(cur_results)

        return results

    def projects_with_processing(self):
        projects = []

        _protocols = self._data['processors']
        if len(_protocols) > 0:
            projects = _protocols.PROJECT.unique()

        return projects

    def _load_protocols(self, project):
        protocols = []
        yamldir = self._yamldir

        for p in self._project_protocols(project):
            # Initialize record with project
            d = {'PROJECT': project}

            # Find the yaml file
            if p.get('CUSTOM', ''):
                _filename = p['FILE']
                filepath = f'{project}/{_filename}'
            else:
                filepath = p['FILE']

            if not os.path.isabs(filepath):
                # Prepend lib location
                filepath = os.path.join(yamldir, filepath)

            if not os.path.isfile(filepath):
                logger.info(f'file not found:{filepath}')
                continue

            d['FILE'] = filepath
            d['TYPE'] = _get_proctype(d['FILE'])

            d['EDIT'] = 'edit'

            d['FILTER'] = p['FILTER']
            d['ARGS'] = p['ARGS']

            # Finally, add to our list
            protocols.append(d)

        return protocols

    def _build_session_processor(self, processor, session, project_info, custom=False):
        results = []

        # Get list of inputs sets (not yet matched with existing)
        inputsets = processor.parse_session_pd(session, project_info)

        logger.debug(f'{session}:{processor.name}')

        logger.debug(inputsets)
        for inputs in inputsets:
            if inputs == {}:
                # Blank inputs
                return

            # Get(create) assessor with given inputs and proc type
            info = self.get_session_assessor(project_info, session, processor, inputs)
            if not info:
                raise Exception('failed to get new assessor')
                continue

            # Check for undo
            if info['QCSTATUS'] == RERUN:
                # Undo and set to run
                logger.info(f'TBD:undoing task{info["ASSR"]}')
                #self._undo_task(assr)
                #info['PROCSTATUS'] = NEED_TO_RUN

            if info['PROCSTATUS'] in [NEED_TO_RUN, NEED_INPUTS]:
                logger.info(f'building task:{info["ASSR"]}')
                try:
                    info = self._build_task(info, processor, project_info, custom=custom)
                except Exception as err:
                    logger.info(f'build_task failed:{err}')
                    continue

                logger.debug(f'{info}')
                logger.debug('status:{}:{}'.format(info['ASSR'], info['PROCSTATUS']))
            else:
                logger.debug('already built:{}'.format(info['ASSR']))

            results.append(info)

        return results

    def _build_task(self, info, processor, project_info, custom=False):
        '''Build a task'''
        old_proc_status = info['PROCSTATUS']
        old_qc_status = info['QCSTATUS']

        try:
            var2val, inputlist = processor.build_var2val(
                info,
                project_info)

            logger.debug(f'adding task to queue:{info['ASSR']}')
            self._add_task(
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
        except Exception as err:
            raise Exception(f'add task failed:{err}')

        # Update in database and locally
        # TODO:TBD batch db updates for whole project
        if new_proc_status != old_proc_status:
            self._update_assessor_procstatus(info['ASSR'], new_proc_status)
            info['PROCSTATUS'] = new_proc_status

        if new_qc_status != old_qc_status:
            self._update_assessor_qcstatus(info['ASSR'], new_qc_status)
            info['QCSTATUS'] = new_qc_status

        return info

    def get_session_assessor(self, project_info, session, processor, inputs):
        assessor = None

        # Try to match with existing
        assrs = project_info['assessors']
        assrs = [x for x in assrs if x['SESSION'] == session]
        assrs = [x for x in assrs if x['PROCTYPE'] == processor.proctype]
        for a in assrs:
            try:
                if self._compare_inputs(inputs, a['INPUTS']):
                    assessor = a
                    break
            except Exception as err:
                logger.debug('compare failed', err)
                continue

        if assessor:
            logger.debug('matches existing:{}'.format(assessor['ASSR']))
        else:
            logger.debug('no existing assessors found, creating a new one')

            # Create the assessor
            subject = self._subject_for_session(project_info, session)
            proctype = processor.proctype
            procversion = processor.procversion
            logger.debug(f'no match, creating session asssessor:{subject}:{session}:{proctype}')
            assessor = self.create_session_assessor(
                project_info['name'],
                subject,
                session,
                proctype,
                procversion,
                inputs
            )

            # Add to currently loaded data
            project_info['assessors'].append(assessor)
            logger.debug('created:{}'.format(assessor['ASSR']))

        return assessor

    def create_session_assessor(self, project, subject, session, proctype, procversion, inputs):
        assessor = {}
        guidchars = 8  # how many characters in the guid?
        today = str(date.today())

        # Get a unique ID
        count = 0
        max_count = 100
        while count < max_count:
            count += 1
            guid = str(uuid4())
            if True:
                #print(f'TOƒDO:check for existing:{guid=}')
                break

        if count == max_count:
            logger.error('failed to find unique ID, cannot create assessor!')
            raise AutoProcessorError()

        # Build the assessor attributes as key/value pairs
        assr_label = '-x-'.join([
            project,
            subject,
            session,
            proctype,
            guid[:guidchars]])

        # Create the assessor
        logger.info(f'creating session asssessor:{assr_label}')
        assessor = {
            'PROJECT': project,
            'SUBJECT': subject,
            'SESSION': session,
            'ASSR': assr_label,
            'QCSTATUS': JOB_PENDING,
            'PROCTYPE': proctype,
            'PROCVERSION': procversion,
            'PROCSTATUS': NEED_INPUTS,
            'INPUTS': inputs,
            'MEMREQ': '',
            'TIMEREQ': '',
            'JOBDATE': '',
            'TIMEUSED': '',
            'MEMUSED': '',
            'JOBNODE': '',
            #'QCDATE', 
            #'QCBY', 
            #'YAMLFILE', 
            #'USERINPUTS',
            #'FAILCOUNT', 
            #'SLURMFILE', 
            #'JOBSTARTTIME',
            #'JOBENDTIME', 
            #'NOTE_x',
            #'NOTE_y',
            #'full_path': f'/projects/{project}/subjects/{subject}/experiments/{session}/assessors/{assr_label}'
        }

        self._add_assessor(assessor)

        return assessor

    def _subject_for_session(self, project_info, session):       
        # Get the subject for this session
        scans = [x for x in project_info['scans'] if x['SESSION'] == session]
        subject = scans[0]['SUBJECT']
        return subject

    def _add_assessor(self, assessor):
        # Copy so we can edit
        _assessor = assessor.copy()

        # Encode inputs from dict to string
        _assessor['INPUTS'] = json.dumps(_assessor['INPUTS'])

        # Save edited assessor
        self._db.add_assessor(_assessor)

    def _compare_inputs(self, inputs1, inputs2):
        assert type(inputs1) == dict
        assert type(inputs2) == dict
        return inputs1 == inputs2

    def _update_assessor_procstatus(self, id, procstatus):
        self._db.update_assessor(id, 'PROCSTATUS', procstatus)

    def _update_assessor_qcstatus(self, id, qcstatus):
        self._db.update_assessor(id, 'QCSTATUS', qcstatus)

    def _set_task(self, task):
        self._db.set_task(task)

    def _add_task(
        self,
        project,
        assr,
        inputlist,
        var2val,
        walltime,
        memreq,
        yamlfile,
        userinputs,
        custom=False
    ):
        """Create or update task record"""

        # Convert to string for storing
        var2val = json.dumps(var2val)
        inputlist = json.dumps(inputlist)
        userinputs = json.dumps(userinputs)

        try:
            self._set_task({
                'ASSR': assr,
                'PROJECT': project,
                'PROCSTATUS': 'QUEUED',
                'INPUTLIST': inputlist,
                'VAR2VAL': var2val,
                'WALLTIME': walltime,
                'MEMREQ': memreq,
                'YAMLFILE': yamlfile,
                'USERINPUTS': userinputs,
                'TIMEUSED': '',
                'MEMUSED': ''
            })
        except Exception as err:
            raise Exception(f'set task failed:{err}')
