import os
import logging
import subprocess
from datetime import datetime

import pandas as pd
import yaml
import requests

from ..cluster import PBS
from ..lockfiles import lock_flagfile, unlock_flagfile
from ..utilities import parse_list
from .database_noxnat import DatabaseNoXnat
from ..XnatUtils import decode_inputs


# Current analyses are in settings/analyses.yaml

# Each record in yaml maps to a record in db. Any
# additional records in db are ignored. If no record
# exists in db, a new one is created (unless the 
# record is disabled in yaml).

# Each record in yaml maps to a subdir in 
# projects/PROJECT/ANALYSES. Each run is a subdir
# with OUTPUT timestamp.

# To run a complete analysis again, set STATUS in db
# to Q with dax rerun -p PROJECT -a ID or
# test_rerun.py PROJECT-ID

# When you queue an analysis, it clears the record in db
# for a new slurm job.


logger = logging.getLogger('dax')


DONE_STATUSES = ['COMPLETE', 'JOB_FAILED', 'READY', 'DEVEL']

COMPLETED_STATUSES = [
    'COMPLETED',
    'FAILED',
    'CANCELLED',
    'NODE_FAIL',
    'OUT_OF_MEMORY',
    'TIMEOUT'
]

QUEUED_STATUSES = ['QUEUED', 'Q']

ANALYSES_COLUMNS = [
    'ID', 
    'PROJECT',
    'LABEL',
    'OTHERPROJECTS',
    'PROCREPO',
    'INCLUDE', 
    'EXCLUDE'
]

CMDS_TEMPLATE = '''
REPO={repo}
INLIST={inputs}
CONTAINERPATH={container}
PRECONTAINERPATH={precontainer}
POSTCONTAINERPATH={postcontainer}
DSTDIR={dstdir}
{maincmd}

'''


SINGULARITY_BASEOPTS = (
    '-e '
    '--home $JOBDIR:$HOME '
    '--bind $REPODIR:/REPO '
    '--bind $INDIR:/INPUTS '
    '--bind $OUTDIR:/OUTPUTS '
    '--bind $JOBDIR:/tmp '
    '--bind $JOBDIR:/dev/shm '
)


class AnalysisLauncherNoXnat(object):

    def __init__(self, rootdir):
        self._rootdir = rootdir
        self._dbfile = f'{rootdir}/db/dax.duckdb'
        self._settings = f'{rootdir}/settings/analyses.yaml'
        self._job_template = f'{rootdir}/templates/project_job_template_noxnat.txt'
        self._projects_dir = f'{rootdir}/projects'
        self._db = DatabaseNoXnat(self._dbfile)
        self._flags_dir = f'{rootdir}/flagfiles'
        self._singularitys_dir = f'{rootdir}/singularitys'

    def queue_analysis(self, analysis_id):
        # Set status to queued and clear previous run
        self._set_analysis({          
            'ID': analysis_id,
            'STATUS': 'QUEUED',
            'SUBJECTS': '',
            'JOBID': '',
            'JOBNODE': '',
            'JOBSTARTTIME': '',
            'JOBENDTIME': '',
            'WALLTIME': '',
            'MEMREQ': '',
            'TIMEUSED': '',
            'MEMUSED': '',
            'OUTPUT': '',
        })

    def _set_analysis(self, analysis):
        return self._db.set_analysis(analysis)

    def load_processor_github(self, user, repo, version, subdir):
        """Export file from github."""
        base = 'https://raw.githubusercontent.com'
        filename = 'processor.yaml'

        if subdir:
            url = f'{base}/{user}/{repo}/{version}/processors/{subdir}/{filename}'
        else:
            url = f'{base}/{user}/{repo}/{version}/{filename}'

        logger.info(f'{url=}')

        # Get the file contents
        try:
            r = requests.get(url, allow_redirects=True)
            if r.content == '':
                raise Exception('error exporting file from github')
        except Exception as err:
            logger.error(f'downloading file:{err}')
            return None

        return yaml.safe_load(r.text)

    def _load_analyses(self, projects=None):
        filename = self._settings

        # Get the current analysis table from yaml
        logger.debug('loading current analysis records')
        try:
            # Load settings from yaml file
            with open(filename, 'r', encoding='utf-8') as f:
                _records = yaml.safe_load(f)
                df = pd.DataFrame(_records, columns=ANALYSES_COLUMNS, dtype=str).fillna('')

            # Load db records
            data = self._db.load_analyses()

            # Merge
            df = pd.merge(
                df,
                data,
                left_on=('ID'),
                right_on=('ID'),
                how='left'
            ).astype(str).fillna('')

            # Filter to only open jobs
            df = df[~df['STATUS'].isin(DONE_STATUSES)]

        except Exception as err:
            logger.error(f'failed to load analyses:{err}')
            return

        logger.debug(f'found {len(df)} open analysis records')

        return df.to_dict('records')

    def update(self, projects, launch_enabled=True, update_enabled=True):
        """Update analyses."""
        updates = []

        # Lock for updating
        os.makedirs(self._flags_dir, exist_ok=True)
        lock_file = f'{self._flags_dir}/rcq.pid'
        success = lock_flagfile(lock_file)
        if not success:
            # Failed to get lock
            logger.warn(f'failed to get lock:{lock_file}')
            return

        try:
            if update_enabled:
                self._update_running(projects=projects)
                self._update_completed(projects=projects)

            if launch_enabled:
                self._launch(projects=projects)

            logger.info('analyses update:DONE!')

        finally:
            # Delete the lock file
            logger.debug(f'deleting lock file:{lock_file}')
            unlock_flagfile(lock_file)

    def _update_running(self, projects=None):
        updates = []
        records = self._load_analyses(projects=projects)
        running_list = [x for x in records if x['STATUS'] == 'RUNNING']

        if not running_list:
            logger.debug('no running analyses to update')
            return

        logger.info(f'{len(running_list)} running analyses to update')
        logger.debug(running_list)

        # Update each record
        for i, cur in enumerate(running_list):
            status = cur['STATUS']
            instance = cur['ID']

            # check on running job
            logger.debug(f'{i}:{instance}:{status=}:checking on running job')
            cur_updates = get_updates(cur)
            if cur_updates:
                cur_updates.update({
                    'ID': instance,
                })

                # Add to redcap updates
                updates.append(cur_updates)
            else:
                logger.info(f'analysis still running:{instance}')

        if updates:
            # upload changes
            logger.debug(f'applying updating:{updates}')
            try:
                self._apply_updates_analyses(updates)
            except Exception as err:
                err = f'failed to apply changes:{err}'
                logger.error(err)

    def _update_completed(self, projects=None):
        updates = []
        records = self._load_analyses(projects=projects)
        completed_list = [x for x in records if x['STATUS'] in COMPLETED_STATUSES]

        if not completed_list:
            logger.debug('no completed analyses to update')
            return

        logger.info(f'{len(completed_list)} completed analyses to update')
        logger.debug(completed_list)

        # Update each record
        for i, cur in enumerate(completed_list):
            status = cur['STATUS']
            instance = cur['ID']

            # finish completed job
            logger.debug(f'{i}:{instance}:{status=}:handling complete job')

            # Get the output label
            label = cur.get('OUTPUT', None)
            if not label:
                logger.error('label not found, cannot finish')
                continue

            logger.debug(f'{label=}')

            # Finalize the status
            if status == 'COMPLETED':
                status = 'READY'
            elif status == 'FAILED':
                status = 'JOB_FAILED'
            elif status == 'CANCELLED':
                status = 'JOB_CANCELLED'

            # Add to updates
            updates.append({
                'ID': instance,
                'STATUS': status,
            })

        if updates:
            # upload changes
            logger.debug(f'applying updating:{updates}')
            try:
                self._apply_updates_analyses(updates)
            except Exception as err:
                err = f'failed to apply changes:{err}'
                logger.error(err)

    def _launch(self, projects=None):
        updates = []
        records = self._load_analyses(projects=projects)
        launch_list = [x for x in records if x['STATUS'] in QUEUED_STATUSES]

        if not launch_list:
            logger.debug('no queued analyses to update')
            return

        logger.info(f'{len(launch_list)} queued analyses to update')
        logger.debug(launch_list)

        # Launch jobs
        updates = []
        for i, cur in enumerate(launch_list):
            try:
                # Launch it!
                logger.debug(f'launch:{i}')
                jobid, label = self.launch_analysis(cur)

                # Check for success
                if jobid and label:
                    # Append to updates, clear existing info
                    updates.append({
                        'ID': cur['ID'],
                        'STATUS': 'RUNNING',
                        'JOBID': jobid,
                        'OUTPUT': label,
                        'JOBNODE': '',
                        'TIMEUSED': '',
                        'MEMUSED': '',
                        'JOBSTARTTIME': '',
                        'JOBENDTIME': '',
                    })
                else:
                    # Update with launch failed
                    updates.append({
                        'ID': cur['ID'],
                        'STATUS': 'LAUNCH_FAILED',
                        })
            except Exception as err:
                logger.error(err)
                import traceback
                traceback.print_exc()

                # Update with launch failed
                updates.append({
                    'ID': cur['ID'],
                    'STATUS': 'LAUNCH_FAILED',
                    'OUTPUT': str(err),
                    })

        if updates:
            # upload changes
            logger.info(f'updating db:{updates}')
            try:
                self._apply_updates_analyses(updates)
            except Exception as err:
                logger.error(f'failed to apply updates to db:{err}')

    def _apply_updates_analyses(self, updates):
        logger.debug(f'applying analyses updates to db:{updates}')
        self._db.update_analyses(updates)

    def get_info(self, project):
        data = self._db.load_data()
        info = {}

        # Scans
        scans = data['scans']
        scans = scans[scans.PROJECT == project]
        scans['full_path'] = \
            'projects/' + \
            scans['PROJECT'].astype(str) + \
            '/SCANS/' + \
            scans['SUBJECT'].astype(str) + '/' + \
            scans['SESSION'].astype(str) + '/' + \
            scans['SCANID'].astype(str) + '-x-' + \
            scans['SCANTYPE'].astype(str) + '-x-' + \
            scans['DESCRIP'].astype(str)

        # Convert to list of dicts instead of df
        info['scans'] = scans.to_dict('records')

        # Assessors
        _assrs = data['assessors']
        _assrs['full_path'] = \
            'projects/' + \
            _assrs['PROJECT'] + \
            '/ASSESSORS/' + \
            _assrs['SUBJECT'] + '/' + \
            _assrs['ASSR']

        # Decode inputs
        records = _assrs[_assrs.PROJECT == project].to_dict('records')
        print(len(records))

        for i, r in enumerate(records):
            inputs = r['INPUTS']
            if isinstance(inputs, str):
                try:
                    records[i]['INPUTS'] = decode_inputs(inputs)
                except Exception as err:
                    print(f'decode failed:{inputs}')
                    records[i]['INPUTS'] = {}
                    continue

        records = [x for x in records if x['INPUTS']]
        print(len(records))

        info['assessors'] = records

        info['name'] = project

        return info

    def label_analysis(self, analysis_id):
        analysis_datetime = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        analysis_label = f'{analysis_id}_{analysis_datetime}'
        return analysis_label

    def get_inputlist(self, analysis):
        inputlist = []

        spec = analysis['PROCESSOR']['inputs']['xnat']['subjects']

        proj = analysis['ID'].split('-')[0]

        projects = [proj]

        if analysis['OTHERPROJECTS']:
            projects.extend(parse_list(analysis['OTHERPROJECTS']))

        logger.info(f'get_inputlist:{projects=}')
        for project in projects:
            logger.info(f'get_inputlist:{project=}')
            info = self.get_info(project=project)

            subjects = analysis.get('SUBJECTS', None)
            if not subjects:
                # Get unique list of subjects from scans
                subjects = sorted(list(set([x['SUBJECT'] for x in info['scans']])))

            exclude = analysis.get('EXCLUDE', None)
            logger.debug(f'{exclude=}')

            if exclude:
                subjects = [x for x in subjects if x not in exclude]

            logger.debug(f'{subjects=}')

            logger.info(f'get_inputlist:{subjects=}')

            for subj in subjects:
                logger.info(f'get_inputlist:{subj=}')
                inputlist.extend(self.get_subject_inputs(spec, info, subj))


        # TODO: check for inputs on each subject?


        return inputlist

    def get_session_inputs(self, spec, info, subject, session):
        inputs = []

        # Get the scans for this session
        scans = [x for x in info['scans'] if x['SESSION'] == session]

        for scan_spec in spec.get('scans', []):
            logger.info(f'get_session_inputs:{scan_spec=}')

            logger.debug(f'scan_spec={scan_spec}')

            # Get list of resources to download from this scan
            resources = scan_spec.get('resources', [])

            # Check for nifti tag
            if 'nifti' in scan_spec:
                # Add a NIFTI resource using value as fdest
                resources.append({
                    'resource': 'NIFTI',
                    'fdest': scan_spec['nifti']
                })

            scan_types = parse_list(scan_spec['types'])

            logger.debug(f'scan_types={scan_types}')

            input_scans = [x for x in scans if x['SCANTYPE'] in scan_types]

            if len(input_scans) > 0 and scan_spec.get('keep_multis', 'all') != 'all':
                # Sort by id
                input_scans = sorted(input_scans, key=lambda x: x['SCANID'])
                num_scans = len(input_scans)

                # Apply keep_multis filter
                if scan_spec['keep_multis'] == 'first':
                    idx_multi = 1
                elif iv['keep_multis'] == 'last':
                    idx_multi = num_scans
                else:
                    try:
                        idx_multi = int(iv['keep_multis'])
                    except:
                        msg = 'keep_multis must be first, last, or index 1,2,3,...'
                        logger.error(msg)
                        raise Exception(msg)

                    if idx_multi > num_scans:
                        msg = f'{idx_multi} index exceeds found {num_scans}'
                        logger.error(msg)
                        raise Exception(msg)

                    # Get a list of only the requested scan
                    input_scans = [input_scans[idx_multi-1]]

            # Get the file inputs for each input scan
            for scan in input_scans:
                scanid = scan['SCANID']

                for res_spec in resources:
                    try:
                        res = res_spec['resource']
                    except (KeyError, ValueError) as err:
                        logger.error(f'reading resource:{err}')
                        continue

                    # Get the download destination subdir
                    ddest = f'{subject}/{session}/scans/{scanid}'
                    if res_spec.get('ddest', False):
                        ddest += '/' + res_spec.get('ddest')

                    if 'fdest' in res_spec:
                        _file = self._first_file(
                            info['name'],
                            subject,
                            session,
                            scan['SCANID'],
                            res
                        )
                        fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/scans/{scanid}/resources/{res}/files/{_file}'
                        inputs.append(self._input(
                            fpath,
                            'FILE',
                            res_spec.get('fdest', _file),
                            ddest,
                        ))
                    elif 'fmatch' in res_spec:
                        for fmatch in parse_list(res_spec['fmatch']):
                            fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/scans/{scan["SCANID"]}/resources/{res}/files/{fmatch}'
                            inputs.append(self._input(
                                fpath,
                                'FILE',
                                res_spec.get('fdest', fmatch),
                                ddest
                            ))
                    else:
                        # Download whole resource
                        fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/scans/{scan["SCANID"]}/resources/{res}/files'
                        inputs.append(self._input(
                            fpath,
                            'DIR',
                            None,
                            ddest
                        ))

        # Get the assessors for this session
        assessors = [x for x in info['assessors'] if x['SESSION'] == session]

        # Filter to only complete assessors
        logger.debug(f'found {len(assessors)} total assessors, filtering')
        assessors = [x for x in assessors if x['PROCSTATUS'] == 'COMPLETE']
        logger.debug(f'found {len(assessors)} complete assessors')

        for assr_spec in spec.get('assessors', []):
            logger.debug(f'assr_spec={assr_spec}')

            logger.info(f'get_session_inputs:{assr_spec=}')

            assr_types = parse_list(assr_spec['types'])

            logger.debug(f'assr_types={assr_types}')

            logger.info(f'get_session_inputs:{assr_types=}')

            for assr in [x for x in assessors if x['PROCTYPE'] in assr_types]:
                assrlabel = assr["ASSR"]

                logger.info(f'get_session_inputs:{assr=}')

                for res_spec in assr_spec['resources']:

                    # Get the download destination subdir
                    ddest = f'{subject}/{session}/assessors/{assrlabel}'
                    if res_spec.get('ddest', False):
                        ddest += '/' + res_spec.get('ddest')

                    try:
                        res = res_spec['resource']
                    except (KeyError, ValueError) as err:
                        logger.error(f'reading resource:{err}')
                        continue

                    if 'fmatch' in res_spec:
                        for fmatch in parse_list(res_spec['fmatch']):
                            fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/assessors/{assrlabel}/out/resources/{res}/files/{fmatch}'
                            inputs.append(self._input(
                                fpath,
                                'FILE',
                                res_spec.get('fdest', fmatch),
                                ddest))
                    else:
                        # whole resource
                        fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/assessors/{assrlabel}/out/resources/{res}/files'
                        inputs.append(self._input(
                            fpath,
                            'DIR',
                            None,
                            ddest))

        print(f'{inputs=}')

        return inputs

    def get_subject_inputs(self, spec, info, subject):
        inputs = []

        # subject-level assessors, aka sgp
        if spec.get('assessors', None):
            logger.debug(f'get sgp:{subject}')
            sgp_spec = spec.get('assessors')
            sgp = [x for x in info['sgp'] if x['SUBJECT'] == subject]

            # Filter to only complete
            logger.debug(f'found {len(sgp)} total sgp, filtering')
            sgp = [x for x in sgp if x['PROCSTATUS'] == 'COMPLETE']
            logger.debug(f'found {len(sgp)} complete sgp')

            for assr in sgp:
                assrlabel = assr['ASSR']

                for assr_spec in sgp_spec:
                    logger.debug(f'assr_spec={assr_spec}')
                    assr_types = parse_list(assr_spec['types'])
                    logger.debug(f'assr_types={assr_types}')

                    if assr['PROCTYPE'] not in assr_types:
                        logger.debug(
                            f'no match={assr["ASSR"]}:{assr["PROCTYPE"]}')
                        continue

                    for res_spec in assr_spec['resources']:

                        # Get the download destination subdir
                        ddest = f'{subject}/assessors/{assrlabel}'
                        if res_spec.get('ddest', False):
                            ddest += '/' + res_spec.get('ddest')

                        # Load the resource
                        try:
                            res = res_spec['resource']
                        except (KeyError, ValueError) as err:
                            logger.error(f'reading resource:{err}')
                            continue

                        if 'fmatch' in res_spec:
                            # Add each file
                            for fmatch in parse_list(res_spec['fmatch']):
                                fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{assrlabel}/resources/{res}/files/{fmatch}'
                                inputs.append(self._input(
                                    fpath,
                                    'FILE',
                                    res_spec.get('fdest', fmatch),
                                    ddest
                                ))
                        else:
                            # We want the whole resource as one download
                            fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{assrlabel}/resources/{res}/files'
                            inputs.append(self._input(
                                fpath,
                                'DIR',
                                None,
                                ddest))

        # Download the subjects sessions
        for sess_spec in spec.get('sessions', []):

            if sess_spec.get('select', '') == 'first-eeg':
                # only get the first eeg
                subj_eeg = [x for x in info['scans'] if (x['SUBJECT'] == subject and x['MODALITY'] == 'EEG')]
                if len(subj_eeg) < 1:
                    logger.debug('eeg not found')
                    return

                # Sort by date and get first
                first = sorted(subj_eeg, key=lambda x: x['DATE'])[0]

                # First session only
                sessions = [first['SESSION']]

            elif sess_spec.get('select', '') == 'first-mri':
                # only get the first mri
                subj_mris = [x for x in info['scans'] if (x['SUBJECT'] == subject and x['MODALITY'] == 'MR')]
                if len(subj_mris) < 1:
                    logger.debug('mri not found')
                    return

                # Sort by date and get first
                first = sorted(subj_mris, key=lambda x: x['DATE'])[0]

                # First session only
                sessions = [first['SESSION']]
            elif 'types' in sess_spec:
                # Find sessions matching types
                sess_types = parse_list(sess_spec['types'])
                sessions = [x['SESSION'] for x in info['scans'] if x['SUBJECT'] == subject and x['SESSTYPE'] in sess_types]
                sessions = list(set(sessions))
            else:
                # Use any and all sessions for this subject
                sessions = [x['SESSION'] for x in info['scans'] if x['SUBJECT'] == subject]
                sessions = list(set(sessions))

            # Append inputs for this spec
            for sess in sessions:
                logger.info(f'get_subject_inputs:{sess=}')
                inputs += self.get_session_inputs(
                    sess_spec,
                    info,
                    subject,
                    sess
                )

        return inputs

    def _input(self, fpath, ftype, fdest='', ddest=''):
        data = {
            'fpath': fpath,
            'ftype': ftype,
        }

        if fdest:
            data['fdest'] = fdest
        else:
            data['fdest'] = ''

        if ddest:
            data['ddest'] = ddest
        else:
            data['ddest'] = ''

        return data

    def _adir(self, label):
        proj = label.split('-')[0]
        return f'{self._projects_dir}/{proj}/ANALYSES/{label}'

    def launch_analysis(self, analysis):
        """Launch as SLURM Job, write batch and submit. Return job id."""
        imagedir = self._singularitys_dir
        processor = None

        if analysis.get('PROCREPO', False):
            # Load the yaml file contents from github
            logger.info(f'loading:{analysis["PROCREPO"]}')

            # limit split to allow multi-level subdirs
            p = analysis['PROCREPO'].replace(':', '/').split('/', 3)

            if len(p) == 4:
                subdir = p[3]
            elif len(p) == 3:
                subdir = None
            else:
                logger.error(f'failed to parse:{analysis["PROCREPO"]}')
                return None

            user = p[0]
            repo = p[1]
            version = p[2]

            logger.info(f'loading:{user=}:{repo=}:{version=}:{subdir=}')
            analysis['PROCESSOR'] = self.load_processor_github(
                user,
                repo,
                version,
                subdir=subdir
            )
            analysis['PROCREPO'] = f'https://github.com/{user}/{repo}/archive/refs/tags/{version}.tar.gz'
        elif analysis.get('PROCFILE', False):
            # Load the yaml file contents
            logger.debug(f'loading:{analysis["PROCFILE"]}')
            analysis['PROCESSOR'] = self.load_processor_file(analysis['PROCFILE'])
        else:
            raise Exception(f'cannot launch, no processor specified:{analysis}')

        # TODO: validate processor here and handle invalid
        # import validate
        # try:
        #    validate.validate_processor(processor)
        #    print('Valid!')
        #except Exception as err:
        #    print('Not valid!')
        #    print(err)

        processor = analysis['PROCESSOR']

        # Set subject list
        analysis['SUBJECTS'] = analysis['INCLUDE'].splitlines()
        analysis['EXCLUDE'] = [x.strip() for x in analysis['EXCLUDE'].split(',')]

        logger.debug(f'{analysis=}')

        # Set the memory
        memreq = analysis.get('MEMREQ', None)

        if not memreq:
            memreq = processor['requirements'].get('memory', None)

        if not memreq:
            memreq = '8G'

        # Set the walltime
        walltime = analysis.get('WALLTIME', None)

        if not walltime:
            walltime = processor['requirements'].get('walltime', None)

        if not walltime:
            walltime = '0-12'

        # Create and set the label for our new analysis
        analysis['LABEL'] = self.label_analysis(analysis['ID'])
        label = analysis['LABEL']
        _adir = self._adir(label)
        batch_file = f'{_adir}/{label}.slurm'
        log_file = f'{_adir}/{label}.txt'
        covar_file = f'{_adir}/{label}.csv'

        if analysis.get('COVARFILE', False):
            self.save_covariates_file(analysis, covar_file)

        # Build list of inputs
        inputlist = self.get_inputlist(analysis)

        # Get the job batch script template
        if not os.path.exists(self._job_template):
            logger.error('cannot find project job template')
            return

        # Set up containers
        for i, cur in enumerate(processor.get('containers', [])):
            # Get container path/filename
            cpath = cur['path']
            if not os.path.isabs(cpath) and imagedir:
                # Prepend singularity imagedir
                processor['containers'][i]['path'] = f'{imagedir}/{cpath}'

        cmds = self.get_cmds(inputlist, analysis)

        # Write the script
        logger.info(f'writing batch file:{batch_file}')

        batch = PBS(
            batch_file,
            log_file,
            cmds,
            walltime,
            mem_mb=memreq,
            ppn=1,
            env=None,
            email=None,
            email_options='FAIL',
            job_template=self._job_template,
            xnat_host='NOXNAT'
        )

        # Save to file
        batch.write()

        # Submit the saved file
        jobid, job_failed = batch.submit()
        logger.info(f'job submit results:{jobid}:{job_failed}')

        return jobid, label

    def get_cmds(self, input_list, analysis):
        # Get inputs text
        inputs = self.build_inputs_text(input_list)

        # Get main commands text
        maincmd = self.build_main_text(analysis)

        # Get the container path so it can optionally be pre-copied to /tmp
        container_path = analysis['PROCESSOR']['command']['container']
        pre_path = analysis['PROCESSOR'].get('pre', {}).get('container', None)
        post_path = analysis['PROCESSOR'].get('post', {}).get('container', None)
        logger.info(f'{container_path=}')

        # Append other paths
        cmd = CMDS_TEMPLATE.format(
            inputs=inputs,
            repo=analysis['PROCREPO'],
            container=container_path,
            precontainer=pre_path,
            postcontainer=post_path,
            dstdir=self._adir(analysis['LABEL']),
            maincmd=maincmd
        )

        return [cmd]

    def build_inputs_text(self, inputs):
        txt = '(\n'

        for cur in inputs:
            cur['fpath'] = requests.utils.quote(cur['fpath'], safe=":/")
            txt += '{fdest},{ftype},{fpath},{ddest}\n'.format(**cur)

        txt += ')\n\n'

        return txt

    def build_main_text(self, analysis):
        pre = ''
        post = ''
        txt = ''

        # Get the pre command that runs before main
        if analysis['PROCESSOR'].get('pre', False):
            pre = self.build_command(analysis, 'pre') + ' && '

        # Get the post command that runs after main
        if analysis['PROCESSOR'].get('post', False):
            post = ' && ' + self.build_command(analysis, 'post')

        # Build and append the commands
        txt += 'MAINCMD="'
        txt += pre + self.build_command(analysis, 'command') + post

        # Finish with a newline
        txt += '\"\n'

        # Return the whole command lines
        return txt

    def build_command(self, analysis, name):
        txt = ''

        command = analysis['PROCESSOR'][name]

        # Use the container name to get the path
        command['container'] = self.get_container_path(
            analysis['PROCESSOR']['containers'],
            command['container'])

        # Build and append the post command
        if 'type' not in command:
            err = 'command type not set'
            logger.error(err)
            raise Exception(err)

        if analysis['PROCESSOR'].get('jobdir', '') == 'shared':
            shared = True
        else:
            shared = False

        var2val = analysis['PROCESSOR']['inputs'].get('vars', {})

        if command['type'] == 'singularity_run':
            txt = self.build_singularity_cmd('run', command, var2val, shared)

        elif command['type'] == 'singularity_exec':
            txt = self.build_singularity_cmd('exec', command, var2val, shared)

        else:
            err = 'invalid command type: {}'.format(command['type'])
            logger.error(err)
            raise Exception(err)

        return txt

    def build_singularity_cmd(self, runexec, command, var2val={}, shared=False):

        if 'container' not in command:
            err = 'singularity modes require a container to be set'
            logger.error(err)
            raise Exception(err)

        if runexec not in ['run', 'exec']:
            err = f'singularity mode {runexec} not known'
            logger.error(err)
            raise Exception(err)

        # Initialize command
        if 'opts' in command:
            # Get the user defined opts
            _opts = command['opts']
            # Prepend clean and contain
            _opts = f'--contain --cleanenv {_opts}'
            command_txt = f'singularity {runexec} {_opts}'
        else:
            command_txt = f'singularity {runexec} {SINGULARITY_BASEOPTS}'

        # Append extra options
        _extra = command.get('extraopts', None)
        if _extra:
            command_txt = '{} {}'.format(command_txt, _extra)

        # Append container name
        command_txt = '{} {}'.format(command_txt, command['container'])

        # Append arguments for the singularity entrypoint
        cargs = command.get('args', None)
        if cargs:
            # Unescape and then escape double quotes
            cargs = cargs.replace('\\"', '"').replace('"', '\\\"')
            command_txt = '{} {}'.format(command_txt, cargs)

        if var2val:
            command_txt = command_txt.format(**var2val)

        return command_txt

    def get_container_path(self, containers, name):
        cpath = None

        # Find the matching container
        for c in containers:
            if c['name'] == name:
                cpath = c['path']
                break

        return cpath


def get_updates(analysis):
    """Update information from local SLURM."""
    instance = analysis['ID']
    updates = {}

    if 'JOBID' not in analysis:
        logger.info(f'no jobid for analysis:{instance}')
        return

    jobid = analysis['JOBID']
    cmd = f'sacct -j {jobid}.batch --units G --noheader -p --format MaxRss,cputime,NodeList,Start,End,State'

    logger.debug(f'running command:{cmd}')

    try:
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode().strip()
    except subprocess.CalledProcessError:
        logger.info(f'error running command:{cmd}')
        return

    if not output:
        logger.debug(f'no output')
        return

    logger.debug(output)

    job_mem,job_time,job_node,job_start,job_end,job_state,_ = output.split('|')

    # only update usage if job is not still running
    if job_state == 'RUNNING':
        logger.debug(f'job still running:{instance}')
    else:
        if job_mem and job_mem != analysis.get('MEMUSED', ''):
            updates['MEMUSED'] = job_mem

        if job_time and job_time != analysis.get('TIMEUSED', ''):
            updates['TIMEUSED'] = job_time

    if job_node and job_node != analysis.get('JOBNODE', ''):
        updates['JOBNODE'] = job_node

    if job_start and job_start != analysis.get('JOBSTARTTIME', ''):
        updates['JOBSTARTTIME'] = job_start

    if job_end and job_end != analysis.get('JOBENDTIME', ''):
        updates['JOBENDTIME'] = job_end

    if job_state != analysis['STATUS']:
        logger.debug(f'changing status to:{job_state}')
        updates['STATUS'] = job_state

    return updates
