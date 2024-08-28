""" rcq implements a job queue for DAX in REDCap. Launch and Finish."""

import os
import logging
import subprocess
from datetime import datetime

import yaml
import requests

from ..cluster import PBS, count_jobs
from ..lockfiles import lock_flagfile, unlock_flagfile
from .projectinfo import load_project_info
from ..utilities import get_this_instance, parse_list


# Handle analysis jobs that only need to be launched/updated, but not uploaded.
# The job will upload it's own output. On finish, we update job information on
# redcap and delete log and batch files from disk. No job information is stored
# on disk, no diskq, rcq.


logger = logging.getLogger('manager.rcq.analysislauncher')


DONE_STATUSES = ['COMPLETE', 'JOB_FAILED', 'READY', 'DEVEL']


CMDS_TEMPLATE = '''

ANALYSISID={analysis}
PROJECT={project}
REPO={repo}
VERSION={version}
INLIST={inputs}
XNATHOST={host}
XNATUSER={user}
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


class AnalysisLauncher(object):
    def __init__(self, xnat, projects_redcap, instance_settings):
        self._xnat = xnat
        self._projects_redcap = projects_redcap
        self._instance_settings = instance_settings
        self._resdir = self._instance_settings['main_resdir']
        self._rcqdir = f'{self._resdir}/RCQ'
        self._job_template = None

    def _get_job_template(self):
        if self._job_template is None:
            # Determine job template
            self._job_template = self._instance_settings.get(
                'main_projectjobtemplate', None)

        if self._job_template is None:
            #_job_template = instance_settings.get('jobtemplate', None)
            #job_template = f'{_job_template}/project_job_template.txt'
            self._job_template = os.path.expanduser(
                '~/project_job_template.txt')

        return self._job_template

    def load_processor_redcap(self, project, repeat_id):
        """Export file from REDCap."""

        # Get the file contents from REDCap
        try:
            (cont, hdr) = self._projects_redcap.export_file(
                record=project,
                field='analysis_processor',
                repeat_instance=repeat_id)

            if cont == '':
                raise Exception('error exporting file from REDCap')
        except Exception as err:
            logger.error(f'downloading file:{err}')
            return None

        return cont

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

    def save_covariates_file(self, analysis, output_file):
        """Export file from REDCap."""

        project = analysis['project']
        repeat_id = analysis['redcap_repeat_instance']

        # Get the file contents from REDCap
        try:
            (cont, hdr) = self._projects_redcap.export_file(
                record=project,
                field='analysis_covarfile',
                repeat_instance=repeat_id)

            if cont == '':
                raise Exception('error exporting file from REDCap')
        except Exception as err:
            logger.error(f'downloading file:{err}')
            return None

        # Save contents to local file
        try:
            with open(output_file, 'wb') as f:
                f.write(cont)

            return output_file
        except FileNotFoundError as err:
            logger.error(f'file not found:{output_file}:{err}')
            return None

    def update(self, projects, launch_enabled=True):
        """Update all analyses in projects_redcap."""
        launch_list = []
        updates = []
        def_field = self._projects_redcap.def_field
        projects_redcap = self._projects_redcap
        instance_settings = self._instance_settings

        # Lock rcq for updating
        lock_file = f'{self._resdir}/FlagFiles/rcq.pid'
        success = lock_flagfile(lock_file)
        if not success:
            # Failed to get lock
            logger.warn('failed to get lock:{}'.format(lock_file))
            return

        try:
            # Get the current analysis table
            logger.debug('loading current analysis records')
            try:
                rec = projects_redcap.export_records(
                    records=projects,
                    forms=['analyses'],
                    fields=[def_field])
            except Exception as err:
                logger.error(f'failed to load analyses:{err}')
                return

            rec = [x for x in rec if x['redcap_repeat_instrument'] == 'analyses']

            logger.debug(f'Found {len(rec)} analysis records')

            # Filter to only open jobs
            rec = [x for x in rec if x['analysis_status'] not in DONE_STATUSES]

            logger.debug(f'{len(rec)} analysis with open jobs')

            # Update each record
            for i, cur in enumerate(rec):
                project = cur[def_field]
                cur['project'] = project
                instance = cur['redcap_repeat_instance']
                status = cur['analysis_status']

                logger.debug(f'{i}:{project}:{instance}:{status}')

                if status in ['NEED_INPUTS', 'UPLOADING', 'READY', 'DEVEL']:
                    logger.debug(f'ignoring status={status}')
                    pass
                elif status == 'RUNNING':
                    # check on running job
                    logger.debug('checking on running job')
                    cur_updates = get_updates(cur)
                    if cur_updates:
                        cur_updates.update({
                            def_field: cur[def_field],
                            'redcap_repeat_instrument': 'analyses',
                            'redcap_repeat_instance': instance,
                        })

                        # Add to redcap updates
                        updates.append(cur_updates)
                elif status in ['COMPLETED', 'FAILED', 'CANCELLED']:
                    # finish completed job after being uploaded to xnat
                    logger.debug(f'handling complete, status={status}')

                    # Get the output label on xnat
                    label = cur.get('analysis_output', None)
                    if not label:
                        logger.error('label not found, cannot finish')
                        continue

                    logger.debug(f'{label=}')

                    # Upload slurm file to xnat
                    slurm_file = f'{self._rcqdir}/{label}.slurm'
                    if os.path.isfile(slurm_file):
                        logger.debug(f'upload slurm file:{slurm_file}')
                        self._upload_file(slurm_file, project, label)
                        os.remove(slurm_file)

                    # Upload log file to xnat
                    log_file = f'{self._rcqdir}/{label}.txt'
                    if os.path.isfile(log_file):
                        logger.debug(f'upload log file:{log_file}')
                        self._upload_file(log_file, project, label)
                        os.remove(log_file)

                    # Finalize the status from xnat
                    if status == 'COMPLETED':
                        status = 'READY'
                    elif status == 'FAILED':
                        status = 'JOB_FAILED'
                    elif status == 'CANCELLED':
                        status = 'JOB_CANCELLED'

                    # Add to redcap updates
                    updates.append({
                        def_field: cur[def_field],
                        'redcap_repeat_instrument': 'analyses',
                        'redcap_repeat_instance': instance,
                        'analysis_status': status,
                    })
                elif status == 'QUEUED' or status == 'Q':
                    logger.debug('adding queued job to launch list')
                    launch_list.append(cur)
                else:
                    logger.info(f'unknown status:{status}')
                    continue

            if updates:
                # upload changes
                logger.debug(f'updating redcap:{updates}')
                try:
                    projects_redcap.import_records(updates)
                except Exception as err:
                    err = 'connection to REDCap interrupted'
                    logger.error(err)

            if launch_enabled:

                # Make the rcq dir for slurm scripts and output logs
                try:
                    os.makedirs(self._rcqdir)
                except FileExistsError:
                    pass

                q_limit = int(instance_settings['main_queuelimit'])
                p_limit = int(instance_settings['main_queuelimit_pending'])
                u_limit = int(instance_settings['main_limit_pendinguploads'])

                # Launch jobs
                updates = []
                for i, cur in enumerate(launch_list):
                    launched, pending, uploads = count_jobs(self._resdir)
                    logger.info(f'Cluster:{launched}/{q_limit} total, {pending}/{p_limit} pending, {uploads}/{u_limit} uploads')

                    if launched >= q_limit:
                        logger.info(f'queue limit reached:{q_limit}')
                        break

                    if pending >= p_limit:
                        logger.info(f'pending limit reached:{p_limit}')
                        break

                    if uploads >= u_limit:
                        logger.info(f'upload limit reached:{u_limit}')
                        break

                    try:
                        # Launch it!
                        logger.debug(f'launch:{i}')
                        jobid, label = self.launch_analysis(cur)

                        # Check for success
                        if jobid and label:
                            # Append to updates for redcap, clear existing info
                            updates.append({
                                def_field: cur[def_field],
                                'redcap_repeat_instrument': 'analyses',
                                'redcap_repeat_instance': cur['redcap_repeat_instance'],
                                'analysis_status': 'RUNNING',
                                'analysis_jobid': jobid,
                                'analysis_output': label,
                                'analysis_jobnode': 'NULL',
                                'analysis_timeused': 'NULL',
                                'analysis_memused': 'NULL',
                                'analysis_jobstarttime': 'NULL',
                                'analysis_jobendtime': 'NULL',
                            })
                    except Exception as err:
                        logger.error(err)
                        import traceback
                        traceback.print_exc()

                if updates:
                    # upload changes
                    logger.info(f'updating redcap:{updates}')
                    try:
                        projects_redcap.import_records(updates)
                    except Exception as err:
                        err = 'connection to REDCap interrupted'
                        logger.error(err)
        finally:
            # Delete the lock file
            logger.debug(f'deleting lock file:{lock_file}')
            unlock_flagfile(lock_file)

    def _upload_file(self, filename, project, analysis_label):
        res_uri = f'/projects/{project}/resources/{analysis_label}'
        logger.info(f'upload:{filename}:{res_uri}')
        self._xnat.select(res_uri).file(os.path.basename(filename)).put(
            filename,
            overwrite=True,
            params={"event_reason": "analysis upload"})

    def get_info(self, project):
        return load_project_info(self._xnat, project)

    def label_analysis(self, analysis):
        project = analysis['project']
        analysis_id = str(analysis['redcap_repeat_instance']).zfill(3)
        analysis_datetime = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        analysis_label = f'{project}_A{analysis_id}_{analysis_datetime}'
        return analysis_label

    def get_inputlist(self, analysis):
        inputlist = []

        spec = analysis['processor']['inputs']['xnat']['subjects']

        projects = [analysis['project']]

        if analysis['analysis_otherprojects']:
            projects.extend(parse_list(analysis['analysis_otherprojects']))

        for project in projects:
            info = self.get_info(project=project)

            subjects = analysis.get('subjects', None)
            if not subjects:
                # Get unique list of subjects from scans
                subjects = sorted(list(set([x['SUBJECT'] for x in info['scans']])))

            for subj in subjects:
                inputlist.extend(self.get_subject_inputs(spec, info, subj))

        # Prepend xnat host to each input path
        for i, d in enumerate(inputlist):
            _fpath = inputlist[i]['fpath']
            inputlist[i]['fpath'] = f'{self._xnat.host}/{_fpath}'

        return inputlist

    def get_session_inputs(self, spec, info, subject, session):
        inputs = []

        # Get the scans for this session
        scans = [x for x in info['scans'] if x['SESSION'] == session]

        for scan_spec in spec.get('scans', []):
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

            assr_types = parse_list(assr_spec['types'])

            logger.debug(f'assr_types={assr_types}')

            for assr in [x for x in assessors if x['PROCTYPE'] in assr_types]:
                assrlabel = assr["ASSR"]

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

        return inputs

    def get_subject_inputs(self, spec, info, subject):
        inputs = []

        # subject-level assessors, aka sgp
        if spec.get('assessors', None):
            logger.debug(f'get sgp:{subject}')
            sgp_spec = spec.get('assessors')
            sgp = [x for x in info['sgp'] if x['SUBJECT'] == subject]

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

            if sess_spec.get('select', '') == 'first-mri':
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

    def _first_file(self, proj, subj, sess, scan, res):
        # Get name of the first file
        _files = self._xnat.select_scan_resource(
            proj, subj, sess, scan, res).files().get()
        return _files[0]

    def launch_analysis(self, analysis):
        """Launch as SLURM Job, write batch and submit. Return job id."""
        instance_settings = self._instance_settings

        if analysis['analysis_procrepo']:
            # Load the yaml file contents from github
            logger.info(f'loading:{analysis["analysis_procrepo"]}')
            p = analysis['analysis_procrepo'].replace(':', '/').split('/')
            if len(p) == 4:
                subdir = p[3]
            elif len(p) == 3:
                subdir = None
            else:
                logger.error(f'failed to parse:{analysis["analysis_procrepo"]}')
                return None

            user = p[0]
            repo = p[1]
            version = p[2]

            logger.info(f'loading:{user=}:{repo=}:{version=}:{subdir=}')

            analysis['processor'] = self.load_processor_github(
                user,
                repo,
                version,
                subdir=subdir
            )
            analysis['procrepo'] = f'https://github.com/{user}/{repo}/archive/refs/tags/{version}.tar.gz'
            analysis['procversion'] = version.replace('v', '')
        elif analysis['analysis_processor']:
            # Load the yaml file contents from REDCap
            logger.debug(f'loading:{analysis["analysis_processor"]}')
            analysis['processor'] = self.load_processor_redcap(
                analysis['project'],
                analysis['redcap_repeat_instance'])

        processor = analysis['processor']

        # Set subject list
        analysis['subjects'] = analysis['analysis_include'].splitlines()

        # Set the memory
        memreq = analysis.get('analysis_memreq', None)

        if not memreq:
            memreq = processor['requirements'].get('memory', None)

        if not memreq:
            memreq = '8G'

        # Set the walltime
        walltime = analysis.get('analysis_walltime', None)

        if walltime is None:
            walltime = processor['requirements'].get('walltime', None)

        if walltime is None:
            walltime = '0-12'

        # Create and set the label for our new analysis
        analysis['label'] = self.label_analysis(analysis)
        label = analysis['label']
        batch_file = f'{self._rcqdir}/{label}.slurm'
        log_file = f'{self._rcqdir}/{label}.txt'
        covar_file = f'{self._rcqdir}/{label}.csv'

        imagedir = instance_settings['main_singularityimagedir']
        xnat_host = instance_settings['main_xnathost']
        xnat_user = analysis.get('xnat_user', 'daxspider')

        if analysis.get('analysis_covarfile', False):
            self.save_covariates_file(analysis, covar_file)

        # Build list of inputs
        inputlist = self.get_inputlist(analysis)

        # Get the job batch script template
        job_template = self._get_job_template()
        if not os.path.exists(job_template):
            logger.error('cannot find project job template')
            return

        # Set up containers
        for i, cur in enumerate(processor.get('containers', [])):
            # Get container path/filename
            cpath = cur['path']
            if not os.path.isabs(cpath) and imagedir:
                # Prepend singularity imagedir
                processor['containers'][i]['path'] = f'{imagedir}/{cpath}'

        cmds = self.get_cmds(xnat_host, xnat_user, inputlist, analysis)

        # Write the script
        logger.info(f'writing batch file:{batch_file}')

        batch = PBS(
            batch_file,
            log_file,
            cmds,
            walltime,
            memreq,
            rungroup=instance_settings['main_rungroup'],
            xnat_host=xnat_host,
            job_template=job_template
        )

        # Save to file
        batch.write()

        # Submit the saved file
        jobid, job_failed = batch.submit()
        logger.info(f'job submit results:{jobid}:{job_failed}')

        return jobid, label

    def get_cmds(self, host, user, input_list, analysis):
        # Get inputs text
        inputs = self.build_inputs_text(input_list)

        # Get main commands text
        maincmd = self.build_main_text(analysis)

        # Append other paths
        cmd = CMDS_TEMPLATE.format(
            inputs=inputs,
            version=analysis['procversion'],
            host=host,
            user=user,
            project=analysis['project'],
            analysis=analysis['label'],
            repo=analysis['procrepo'],
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

    def build_dir_text(self, analysis):
        # Set shared jobdir
        txt = 'JOBDIR=$(mktemp -d "{}.XXXXXXXXX") || '.format(self._rcqdir)
        txt += '{ echo "mktemp failed"; exit 1; }\n'
        txt += 'INDIR=$JOBDIR/INPUTS\n'
        txt += 'OUTDIR=$JOBDIR/OUTPUTS\n'

        return txt

    def build_main_text(self, analysis):
        pre = ''
        post = ''
        txt = ''

        if analysis['processor'].get('jobdir', '') == 'shared':
            txt += self.build_dir_text(analysis)

        # Get the pre command that runs before main
        if analysis['processor'].get('pre', False):
            pre = self.build_command(analysis, 'pre') + ' && '

        # Get the post command that runs after main
        if analysis['processor'].get('post', False):
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

        command = analysis['processor'][name]

        # Use the container name to get the path
        command['container'] = self.get_container_path(
            analysis['processor']['containers'],
            command['container'])

        # Build and append the post command
        if 'type' not in command:
            err = 'command type not set'
            logger.error(err)
            raise Exception(err)

        if analysis['processor'].get('jobdir', '') == 'shared':
            shared = True
        else:
            shared = False

        if command['type'] == 'singularity_run':
            txt = self.build_singularity_cmd('run', command, shared)

        elif command['type'] == 'singularity_exec':
            txt = self.build_singularity_cmd('exec', command, shared)

        else:
            err = 'invalid command type: {}'.format(command['type'])
            logger.error(err)
            raise Exception(err)

        return txt

    def build_singularity_cmd(self, runexec, command, shared=False):

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

        if shared:
            _user, _host = get_this_instance().split('@')
            command_txt += f' -e --env USER={_user} --env HOSTNAME={_host} '
            command_txt += ' -B $HOME/.ssh:$HOME/.ssh'

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
    project = analysis['project']
    instance = analysis['redcap_repeat_instance']
    updates = {}

    if 'analysis_jobid' not in analysis:
        logger.info(f'no jobid for analysis:{project}:{instance}')
        return

    jobid = analysis['analysis_jobid']
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
        logger.debug(f'job still running:{project}:{instance}')
    else:
        if job_mem and job_mem != analysis.get('analysis_memused', ''):
            updates['analysis_memused'] = job_mem

        if job_time and job_time != analysis.get('analysis_timeused', ''):
            updates['analysis_timeused'] = job_time

    if job_node and job_node != analysis.get('analysis_jobnode', ''):
        updates['analysis_jobnode'] = job_node

    if job_start and job_start != analysis.get('analysis_jobstarttime', ''):
        updates['analysis_jobstarttime'] = job_start

    if job_end and job_end != analysis.get('analysis_jobendtime', ''):
        updates['analysis_jobendtime'] = job_end

    if job_state != analysis['analysis_status']:
        logger.debug(f'changing status to:{job_state}')
        updates['analysis_status'] = job_state

    return updates
