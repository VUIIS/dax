""" rcq implements a job queue for DAX in REDCap. Launch and Finish."""

import os
import logging
import subprocess
import requests
from datetime import datetime

from ..cluster import PBS, count_jobs
from ..lockfiles import lock_flagfile, unlock_flagfile
from .projectinfo import load_project_info

# Handle analysis jobs that only need to be launched/updated, but not uploaded.
# The job will upload it's own output. On finish, we update job information on
# redcap and delete log and batch files from disk. No job information is stored
# on disk, no diskq, rcq.

logger = logging.getLogger('manager.rcq.analysislauncher')


DONE_STATUSES = ['COMPLETE', 'JOB_FAILED']


CMDS_TEMPLATE = '''


INLIST={inputs}
VERSION={version}
CONTAINERPATH={container}
XNATHOST={host}
XNATUSER={user}
PROJECT={project}
ANALYSISID={analysis}
REPO={repo}
MAINCMD={main}


'''


SINGULARITY_BASEOPTS = (
    '-e --env USER=$USER --env HOSTNAME=$HOSTNAME '
    '--home $JOBDIR:$HOME '
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
        self.resdir = self._instance_settings['main_resdir']

    def load_analysis(self, project, analysis_id, download=True):
        """Return analysis protocol record."""
        data = {
            'project': project,
            'id': analysis_id,
        }

        rec = self._projects_redcap.export_records(
            fields=[self._projects_redcap.def_field],
            forms=['analyses'],
            records=[project],
        )

        rec = [x for x in rec if str(x['redcap_repeat_instance']) == analysis_id]

        if rec['analysis_procrepo']:
            # Load the yaml file contents from github
            logger.debug(f'loading:{rec["analysis_procrepo"]}')
            user, repo, version = rec['analysis_procrepo'].replace(':', '/').split('/')
            data['processor'] = self.load_processor_github(user, repo, version)
            data['procrepo'] = rec['analysis_procrepo']
            data['procversion'] = version
        elif rec['analysis_processor']:
            # Load the yaml file contents from REDCap
            logger.debug(f'loading:{rec["analysis_processor"]}')
            data['processor'] = self.load_processor_redcap(
                project,
                rec['redcap_repeat_instance'])

        return data

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

    def load_processor_github(self, user, repo, version):
        """Export file from github."""

        base = 'https://raw.githubusercontent.com'
        filename = 'processor.yaml'

        # Get the file contents
        try:
            url = f'{base}/{user}/{repo}/{version}/{filename}'
            r = requests.get(url, allow_redirects=True)
            if r.content == '':
                raise Exception('error exporting file from github')
        except Exception as err:
            logger.error(f'downloading file:{err}')
            return None

        return r.content

    def update(self, projects, launch_enabled=True):
        """Update all analyses in projects_redcap."""
        launch_list = []
        updates = []
        resdir = self._instance_settings['main_resdir']
        def_field = self._projects_redcap.def_field
        projects_redcap = self._projects_redcap
        instance_settings = self._instance_settings

        # Try to lock
        lock_file = f'{resdir}/FlagFiles/rcq.pid'
        success = lock_flagfile(lock_file)
        if not success:
            # Failed to get lock
            logger.warn('failed to get lock:{}'.format(lock_file))
            return

        try:
            # Get the current analysis table
            logger.info('loading current analysis records')
            try:
                rec = projects_redcap.export_records(
                    records=projects,
                    forms=['analyses'],
                    fields=[def_field])
            except Exception as err:
                logger.error('failed to load analyses')
                return

            rec = [x for x in rec if x['redcap_repeat_instrument'] == 'analyses']

            logger.info(f'Found {len(rec)} analysis records')

            # Filter to only open jobs
            rec = [x for x in rec if x['analysis_status'] not in DONE_STATUSES]

            logger.info(f'{len(rec)} analysis with open jobs')

            # Update each record
            logger.info('updating each analysis')
            for i, cur in enumerate(rec):
                project = cur[def_field]
                instance = cur['redcap_repeat_instance']
                status = cur['analysis_status']

                label = f'{project}_{instance}'

                logger.info(f'{i}:{label}:{status}')

                if status in ['NEED_INPUTS', 'UPLOADING']:
                    logger.info(f'ignoring status={status}')
                    pass
                elif status == 'RUNNING':
                    # check on running job
                    logger.debug('checking on running job')
                    cur_updates = get_updates(cur)
                    if cur_updates:
                        cur_updates.update({
                            def_field: cur[def_field],
                            'redcap_repeat_instrument': 'analyses',
                            'redcap_repeat_instance': cur['redcap_repeat_instance'],
                        })

                        # Add to redcap updates
                        updates.append(cur_updates)
                elif status in ['COMPLETED', 'FAILED', 'CANCELLED']:
                    # finish completed job
                    logger.debug(f'setting to uploaded, status={status}')

                    # TODO: Delete the local files

                    # Add to redcap updates
                    updates.append({
                        def_field: cur[def_field],
                        'redcap_repeat_instrument': 'analyses',
                        'redcap_repeat_instance': cur['redcap_repeat_instance'],
                        'analysis_status': status,
                    })
                elif status == 'QUEUED':
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

            # TODO: sort or randomize list???

            if launch_enabled:
                q_limit = int(instance_settings['main_queuelimit'])
                p_limit = int(instance_settings['main_queuelimit_pending'])
                u_limit = int(instance_settings['main_limit_pendinguploads'])

                # Launch jobs
                updates = []
                for i, cur in enumerate(launch_list):
                    launched, pending, uploads = count_jobs(resdir)
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

                    project = cur[def_field]
                    instance = cur['redcap_repeat_instance']
                    label = f'{project}_{instance}'
                    outdir = f'{resdir}/{label}'

                    try:
                        os.makedirs(outdir)
                    except FileExistsError as err:
                        logger.error(f'cannot launch, existing:{outdir}:{err}')
                        continue

                    cur['outdir'] = outdir
                    cur['project'] = project

                    try:
                        logger.debug(f'launch:{i}:{label}')

                        # Launch it!
                        jobid = self.launch_analysis(cur)
                        if jobid:
                            updates.append({
                                def_field: cur[def_field],
                                'redcap_repeat_instrument': 'analyses',
                                'redcap_repeat_instance': cur['redcap_repeat_instance'],
                                'analysis_status': 'RUNNING',
                                'analysis_jobid': jobid,
                            })
                    except Exception as err:
                        logger.error(err)
                        import traceback
                        traceback.print_exc()

                if updates:
                    # upload changes
                    logger.debug(f'updating redcap:{updates}')
                    try:
                        projects_redcap.import_records(updates)
                    except Exception as err:
                        err = 'connection to REDCap interrupted'
                        logger.error(err)
        finally:
            # Delete the lock file
            logger.debug(f'deleting lock file:{lock_file}')
            unlock_flagfile(lock_file)

    def get_info(self, project):
        return load_project_info(self._xnat, project)

    def label_analysis(self, analysis):
        project = analysis['project']
        analysis_id = analysis['redcap_repeat_instance']
        analysis_datetime = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        analysis_label = f'{project}_{analysis_id}_{analysis_datetime}'
        return analysis_label

    def get_inputlist(self, analysis):
        inputlist = []

        # TODO: handle subjects from additional projects?

        project = analysis['project']
        spec = analysis['processor']['inputs']['xnat']['subjects']

        info = self.get_info(project=project)

        subjects = analysis.get('subjects', None)
        if subjects is None:
            # Get unique list of subjects from scans
            subjects = list(set([x['SUBJECT'] for x in info['scans']]))

        for subj in subjects:
            inputlist.extend(self.get_subject_inputs(spec, info, subj))

        # Prepend xnat host to each input
        inputlist = [f'{self._xnat.host}/{x}' for x in inputlist]
        print(f'{inputlist=}')

        return inputlist

    def get_session_inputs(self, spec, info, subject, session):
        inputs = []

        # Get the scans for this session
        scans = [x for x in info['scans'] if x['SESSION'] == session]

        for scan_spec in spec.get('scans', []):
            logger.debug(f'scan_spec={scan_spec}')

            scan_types = scan_spec['types'].split(',')

            logger.debug(f'scan_types={scan_types}')

            for scan in [x for x in scans if x['SCANTYPE'] in scan_types]:

                # Get list of resources to download from this scan
                resources = scan_spec.get('resources', [])

                # Check for nifti tag
                if 'nifti' in scan_spec:
                    # Add a NIFTI resource using value as fdest
                    resources.append({
                        'resource': 'NIFTI',
                        'fdest': scan_spec['nifti']
                    })

                for res_spec in resources:
                    try:
                        res = res_spec['resource']
                    except (KeyError, ValueError) as err:
                        logger.error(f'reading resource:{err}')
                        continue

                    if 'fdest' in res_spec:
                        _file = self._first_file(
                            info['name'],
                            subject,
                            session,
                            scan['SCANID'],
                            res
                        )
                        fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/scans/{scan["SCANID"]}/resources/{res}/files/{_file}'
                        inputs.append(self._input(
                            fpath,
                            'FILE'
                        ))
                    elif 'fmatch' in res_spec:
                        for fmatch in res_spec['fmatch'].split(','):
                            fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/scans/{scan["SCANID"]}/resources/{res}/files/{fmatch}'
                            inputs.append(self._input(
                                fpath,
                                'FILE'
                            ))
                    else:
                        # Download whole resource
                        fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/scans/{scan["SCANID"]}/resources/{res}/files'
                        inputs.append(self._input(
                            fpath,
                            'DIR'
                        ))

        # Get the assessors for this session
        assessors = [x for x in info['assessors'] if x['SESSION'] == session]

        for assr_spec in spec.get('assessors', []):
            logger.debug(f'assr_spec={assr_spec}')

            assr_types = assr_spec['types'].split(',')

            logger.debug(f'assr_types={assr_types}')

            for assr in [x for x in assessors if x['PROCTYPE'] in assr_types]:

                for res_spec in assr_spec['resources']:

                    try:
                        res = res_spec['resource']
                    except (KeyError, ValueError) as err:
                        logger.error(f'reading resource:{err}')
                        continue

                    if 'fmatch' in res_spec:
                        for fmatch in res_spec['fmatch'].split(','):
                            fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/assessors/{assr["ASSR"]}/out/resources/{res}/files/{fmatch}'
                            inputs.append(self._input(
                                fpath,
                                'FILE',
                                res_spec['fdest'],
                                res_spec['ddest']
                            ))
                    else:
                        # whole resource
                        fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{session}/assessors/{assr["ASSR"]}/out/resources/{res}/files'
                        inputs.append(self._input(
                            fpath,
                            'DIR',
                            res_spec['fdest'],
                            res_spec['ddest']))

        return inputs

    def get_subject_inputs(self, spec, info, subject):
        inputs = []

        # subject-level assessors, aka sgp
        if spec.get('assessors', None):
            logger.debug(f'get sgp:{subject}')
            sgp_spec = spec.get('assessors')
            sgp = [x for x in info['sgp'] if x['SUBJECT'] == subject]

            for assr in sgp:
                for assr_spec in sgp_spec:
                    logger.debug(f'assr_spec={assr_spec}')
                    assr_types = assr_spec['types'].split(',')
                    logger.debug(f'assr_types={assr_types}')

                    if assr['PROCTYPE'] not in assr_types:
                        logger.debug(
                            f'no match={assr["ASSR"]}:{assr["PROCTYPE"]}')
                        continue

                    for res_spec in assr_spec['resources']:

                        try:
                            res = res_spec['resource']
                        except (KeyError, ValueError) as err:
                            logger.error(f'reading resource:{err}')
                            continue

                        if 'fmatch' in res_spec:
                            # Add each file
                            for fmatch in res_spec['fmatch'].split(','):
                                fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{assr["ASSR"]}/resource/{res}/files/{fmatch}'
                                inputs.append(self._input(
                                    fpath,
                                    'FILE',
                                    res_spec['fdest'],
                                    res_spec['ddest']))
                        else:
                            # We want the whole resource as one download
                            fpath = f'data/projects/{info["name"]}/subjects/{subject}/experiments/{assr["ASSR"]}/resource/{res}/files'
                            inputs.append(self._input(
                                fpath,
                                'DIR',
                                res_spec['fdest'],
                                res_spec['ddest']))

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
            else:
                # Otherwise, find sessions matching types
                sess_types = sess_spec['types'].split(',')
                sessions = [x for x in info['scans'] if x['SUBJECT'] == subject and x['SESSTYPE'] in sess_types]
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

    def _input(self, fpath, ftype, fdest=None, ddest=None):
        data = {
            'fpath': fpath,
            'ftype': ftype,
        }

        if fdest:
            data['fdest'] = fdest

        if ddest:
            data['ddest'] = ddest

        return data

    def _first_file(self, garjus, proj, subj, sess, scan, res):
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
            user, repo, version = analysis['analysis_procrepo'].replace(
                ':', '/').split('/')
            analysis['processor'] = self.load_processor_github(
                user, repo, version)
            analysis['procrepo'] = analysis['analysis_procrepo']
            analysis['procversion'] = version
        elif analysis['analysis_processor']:
            # Load the yaml file contents from REDCap
            logger.debug(f'loading:{analysis["analysis_processor"]}')
            analysis['processor'] = self.load_processor_redcap(
                analysis['project'],
                analysis['redcap_repeat_instance'])

        # Create and set the label for our new analysis
        analysis['label'] = self.label_analysis(analysis)
        outdir = analysis['outdir']
        processor = analysis['processor']
        label = analysis['label']
        batch_file = f'{outdir}/PBS/{label}.slurm'
        log_file = f'{outdir}/OUTLOG/{label}.txt'

        imagedir = instance_settings['main_singularityimagedir']
        xnat_host = instance_settings['main_xnathost'],
        xnat_user = analysis.get('xnat_user', 'daxspider')

        # Build list of inputs
        inputlist = self.get_inputlist(analysis)

        # Determine job template
        job_template = instance_settings.get('main_projectjobtemplate', None)

        if job_template is None:
            _job_template = instance_settings.get('jobtemplate', None)
            job_template = f'{_job_template}/project_job_template.txt'

        if not os.path.exists(job_template):
            logger.error('cannot find project job template')
            return

        # Set up containers
        for i, cur in processor.get('containers', []):
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
            analysis.get('analysis_timereq', '0-8'),
            mem_mb=analysis.get('analysis_memreq', '8G'),
            rungroup=instance_settings['main_rungroup'],
            xnat_host=xnat_host,
            job_template=job_template
        )

        # Save to file
        batch.write()

        # Submit the saved file
        jobid, job_failed = batch.submit()
        logger.info(f'job submit results:{jobid}:{job_failed}')

        return jobid

    def get_cmds(self, host, user, input_list, analysis):
        # Get inputs text
        inputs = self.build_inputs_text(input_list)

        # Get main commands text
        main = self.build_main_text(analysis)

        # Append other paths
        cmd = CMDS_TEMPLATE.format(
            inputs=inputs,
            version=analysis['procversion'],
            container=analysis['processor']['containerpath'],
            host=host,
            user=user,
            project=analysis['project'],
            analysis=analysis['anlaysis_label'],
            repo=analysis['analysis_procrepo'],
            maincmd=main
        )

        return cmd

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
        txt = 'MAINCMD=\"'

        # Get the pre command that runs before main
        if analysis['processor']['pre']:
            pre = self.build_command(analysis, 'pre') + ' && '

        # Get the post command that runs after main
        if analysis['processor']['post']:
            post = ' && ' + self.build_command(analysis, 'post')

        # Build and append the commands
        txt += pre + self.build_command(analysis, 'command') + post

        # Finish with a newline
        txt += '\"\n'

        # Return the whole command lines
        return txt

    def build_command(self, analysis, name):
        txt = ''

        command = analysis['processor'][name]

        # Use the container name to get the path
        command['container'] = self.get_container_path(command['container'])

        # Build and append the post command
        if 'type' not in command:
            err = 'command type not set'
            logger.error(err)
            raise Exception(err)

        if command['type'] == 'singularity_run':
            txt = self.build_singularity_cmd('run', command)

        elif command['type'] == 'singularity_exec':
            txt = self.build_singularity_cmd('exec', command)

        else:
            err = 'invalid command type: {}'.format(command['type'])
            logger.error(err)
            raise Exception(err)

        return txt

    def build_singularity_cmd(self, runexec, command):

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
    label = analysis['analysis_label']
    updates = {}

    if 'analysis_jobid' not in analysis:
        logger.info(f'no jobid for analysis:{label}')
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
        logger.debug(f'job still running, not setting used:{label}')
    else:
        if job_mem and job_mem != analysis.get('analysis_memused', ''):
            updates['analysis_memused'] = job_mem

        if job_time and job_time != analysis.get('analysis_timeused', ''):
            updates['analysis_timeused'] = job_time

    if job_node and job_node != analysis.get('analysis_jobnode', ''):
        updates['analysis_jobnode'] = job_node

    if job_state != analysis['analysis_status']:
        logger.debug(f'changing status to:{job_state}')
        updates['analysis_status'] = job_state

    return updates
