""" Task Queue for DAX in REDCap."""

import os
import logging
import json

import pandas as pd
import numpy as np

from ..assessor_utils import parse_full_assessor_name, is_sgp_assessor


logger = logging.getLogger('manager.rcq.taskqueue')


class TaskQueue(object):

    def __init__(self, projects_redcap):
        self._rc = projects_redcap

    def sync(self, xnat, projects):
        def_field = self._rc.def_field
        task_updates = []

        logger.info('loading taskqueue records from REDCap')
        rec = self._rc.export_records(
            records=projects,
            forms=['taskqueue'],
            fields=[def_field])

        # Filter
        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'taskqueue']
        launch_failed = [x for x in rec if x['task_status'] in ['LAUNCH_FAILED']]
        uploading = [x for x in rec if x['task_status'] in ['UPLOADING', 'LOST']]

        if len(launch_failed) == 0 and len(uploading) == 0:
            logger.info('no active tasks to sync between XNAT and REDCap')
            return

        if len(launch_failed) > 0:
            task_updates += self.sync_launch_failed(launch_failed, xnat)

        if len(uploading) > 0:
            task_updates += self.sync_uploading(uploading, xnat)

        # Apply updates to REDCap
        logger.info(f'updating {len(task_updates)} tasks')

        if task_updates:
            logger.info(f'updating task info on redcap:{task_updates}')
            self.apply_updates(task_updates)
        else:
            logger.info(f'nothing to update')

    def sync_uploading(self, tasks, xnat):
        def_field = self._rc.def_field
        updates = []

        # Get projects with active tasks
        projects = list(set([x[def_field] for x in tasks]))

        # Load assesssor data from XNAT as our current status
        logger.info(f'loading XNAT data:{projects}')
        status_df = _load_status(xnat, projects)

        # Get updates
        logger.debug('updating each task')
        for i, t in enumerate(tasks):
            assr = t['task_assessor']
            task_status = t['task_status']

            # Find the matching assessor for this task in XNAT data
            match_found = False
            for k, a in status_df.iterrows():
                if a.ASSR != assr:
                    continue

                match_found = True
                xnat_status = a.PROCSTATUS

                # We have a match, now check for updates
                if xnat_status == 'COMPLETE':
                    logger.info(f'{i}:{assr}:COMPLETE')

                    # Apply complete from xnat to redcap
                    updates.append({
                        def_field: t[def_field],
                        'redcap_repeat_instrument': 'taskqueue',
                        'redcap_repeat_instance': t['redcap_repeat_instance'],
                        'task_status': 'COMPLETE',
                        'taskqueue_complete': '2'
                    })
                elif xnat_status == 'JOB_FAILED':
                    logger.info(f'{i}:{assr}:JOB_FAILED')

                    # Apply from xnat to redcap
                    updates.append({
                        def_field: t[def_field],
                        'redcap_repeat_instrument': 'taskqueue',
                        'redcap_repeat_instance': t['redcap_repeat_instance'],
                        'task_status': 'JOB_FAILED',
                        'taskqueue_complete': '0'
                    })
                else:
                    logger.info(f'{i}:{assr}:{task_status}:{xnat_status}')

                # we matched so we are done with this task
                break

            if not match_found:
                logger.debug(f'no match, set to DELETED:{assr}')
                updates.append({
                    def_field: t[def_field],
                    'redcap_repeat_instrument': 'taskqueue',
                    'redcap_repeat_instance': t['redcap_repeat_instance'],
                    'task_status': 'DELETED',
                })

        return updates

    def sync_launch_failed(self, tasks, xnat):
        def_field = self._rc.def_field
        updates = []

        for i, t in enumerate(tasks):
            assr = t['task_assessor']
            task_status = t['task_status']

            logger.info(f'sync_launch_failed:{i}:{assr}:{task_status}')

            # Connect to the assessor on xnat, sgp or assr
            adict = parse_full_assessor_name(assr)
            if is_sgp_assessor(assr):
                xnat_assr = xnat.select_sgp_assessor(
                    adict['project_id'],
                    adict['subject_label'],
                    adict['label'])
            else:
                xnat_assr = xnat.select_assessor(
                    adict['project_id'],
                    adict['subject_label'],
                    adict['session_label'],
                    adict['label'])

            if not xnat_assr.exists():
                logger.info(f'{i}:{assr}:not found on XNAT')

                # Append update for REDCap
                updates.append({
                    def_field: t[def_field],
                    'redcap_repeat_instrument': 'taskqueue',
                    'redcap_repeat_instance': t['redcap_repeat_instance'],
                    'task_status': 'DELETED',
                    'taskqueue_complete': '0'
                })
                continue

            xsi_type = xnat_assr.datatype().lower()
            xnat_status = xnat_assr.attrs.get(f'{xsi_type}/procstatus')

            if task_status == 'LAUNCH_FAILED' and xnat_status == 'JOB_RUNNING':
                logger.info(f'{i}:{assr}:apply launch failed from REDCap to XNAT')

                # set XNAT statuses
                xnat_assr.attrs.set(f'{xsi_type}/procstatus', 'JOB_FAILED')
                xnat_assr.attrs.set(f'{xsi_type}/validation/status', 'Launch Failed')

                # Append update for REDCap
                updates.append({
                    def_field: t[def_field],
                    'redcap_repeat_instrument': 'taskqueue',
                    'redcap_repeat_instance': t['redcap_repeat_instance'],
                    'task_status': 'JOB_FAILED',
                    'taskqueue_complete': '0'
                })
            else:
                logger.info(f'{i}:{assr}:{task_status}:{xnat_status}')

        return updates

    def apply_updates(self, updates):
        try:
            self._rc.import_records(updates)
        except Exception as err:
            logger.error(err)

    def _assessor_task_id(self, project, assessor):
        task_id = None

        rec = self._rc.export_records(
            forms=['taskqueue'],
            records=[project],
            fields=[self._rc.def_field, 'task_assessor'])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'taskqueue']
        rec = [x for x in rec if x['task_assessor'] == assessor]

        if len(rec) > 1:
            logger.error(f'duplicate tasks for assessor, not good:{assessor}')
            task_id = rec[0]['redcap_repeat_instance']
        elif len(rec) == 1:
            task_id = rec[0]['redcap_repeat_instance']

        return task_id

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
        """Add a new task record ."""

        # Convert to string for storing
        var2val = json.dumps(var2val)
        inputlist = json.dumps(inputlist)
        userinputs = json.dumps(userinputs)
        def_field = self._rc.def_field

        # Try to match existing record
        task_id = self._assessor_task_id(project, assr)

        if custom:
            task_yamlfile = 'CUSTOM'
        else:
            task_yamlfile = os.path.basename(yamlfile)

        if task_id:
            # Update existing record
            try:
                record = {
                    def_field: project,
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
                response = self._rc.import_records([record])
                assert 'count' in response
                logger.debug('task record created')
            except AssertionError as err:
                logger.error(f'upload failed:{err}')
                return
        else:
            # Create a new record
            try:
                record = {
                    def_field: project,
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
                response = self._rc.import_records([record])
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
                task_id = self._assessor_task_id(project, assr)

            logger.debug(f'uploading file:{yamlfile}')
            self._upload_task_processor_file(
                project,
                task_id,
                yamlfile)

    def _upload_task_processor_file(self, record_id, repeat_id, filename):
        with open(filename, 'rb') as f:
            return self._rc.import_file(
                record=record_id,
                field='task_yamlupload',
                file_name=os.path.basename(filename),
                event=None,
                repeat_instance=repeat_id,
                file_object=f)


def _get_result(xnat, uri):
    json_data = json.loads(xnat._exec(uri, 'GET'), strict=False)
    return json_data['ResultSet']['Result']


def _load_status(xnat, projects):
    base_uri = '/REST/experiments?xsiType=xnat:imagesessiondata&columns=proc:genprocdata/label,proc:genprocdata/procstatus'
    sgp_uri = '/REST/subjects?xsiType=xnat:subjectdata&columns=proc:subjgenprocdata/label,proc:subjgenprocdata/procstatus'
    project_filter = ','.join(projects)

    # Main project
    uri = f'{base_uri}&project={project_filter}'
    result = _get_result(xnat, uri)

    # Shared project
    uri = f'{base_uri}&xnat:imagesessiondata/sharing/share/project={project_filter}'
    result += _get_result(xnat, uri)

    # Create dataframe with renamed columns
    dfa = pd.DataFrame(result).rename(columns={
        'proc:genprocdata/label': 'ASSR',
        'proc:genprocdata/procstatus': 'PROCSTATUS'
    })
    dfa = dfa[['ASSR', 'PROCSTATUS']]

    # SGP main project
    uri = f'{sgp_uri}&project={project_filter}'
    result = _get_result(xnat, uri)

    # SGP shared project
    uri = f'{sgp_uri}&xnat:subjectdata/sharing/share/project={project_filter}'
    result += _get_result(xnat, uri)

    if len(result) > 0:
        # Create dataframe with renamed columns
        dfs = pd.DataFrame(result).rename(columns={
            'proc:subjgenprocdata/label': 'ASSR',
            'proc:subjgenprocdata/procstatus': 'PROCSTATUS'
        })
        dfs = dfs[['ASSR', 'PROCSTATUS']]

        # Combine
        df = pd.concat([dfa, dfs])
    else:
        df = dfa

    # No Blanks
    df = df.replace('', np.nan).dropna(axis=0, how='any')

    return df
