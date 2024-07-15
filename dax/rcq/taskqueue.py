""" Task Queue for DAX in REDCap."""

import os
import logging
import json

import pandas as pd

from dax import XnatUtils


logger = logging.getLogger('manager.rcq.taskqueue')


class TaskQueue(object):

    def __init__(self, projects_redcap):
        self._rc = projects_redcap

    def sync(self, xnat, projects):
        task_updates = []
        def_field = self._rc.def_field

        logger.info('loading taskqueue records from REDCap')
        rec = self._rc.export_records(
            records=projects,
            forms=['taskqueue'],
            fields=[def_field])

        # Filter to only uploading jobs
        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'taskqueue']
        rec = [x for x in rec if x['task_status'] in ['LOST', 'UPLOADING']]

        if len(rec) == 0:
            logger.info('no active tasks to update')
            return

        # Get projects with active tasks
        projects = list(set([x[def_field] for x in rec]))

        # Load assesssor data from XNAT as our current status
        logger.info(f'loading XNAT data:{projects}')
        assr_data = XnatUtils.load_assr_data(xnat, projects)
        sgp_data = XnatUtils.load_sgp_data(xnat, ','.join(projects))

        # Get updates
        logger.debug('updating each task')
        for i, t in enumerate(rec):
            assr = t['task_assessor']
            task_status = t['task_status']

            # Find the matching assessor for this task in XNAT data
            match_found = False
            for k, a in pd.concat([assr_data, sgp_data]).iterrows():
                if a.ASSR != assr:
                    continue

                match_found = True
                xnat_status = a.PROCSTATUS

                # We have a match, now check for updates
                if xnat_status == 'COMPLETE':
                    logger.debug(f'{i}:{assr}:COMPLETE')

                    # Apply complete from xnat to redcap
                    task_updates.append({
                        def_field: t[def_field],
                        'redcap_repeat_instrument': 'taskqueue',
                        'redcap_repeat_instance': t['redcap_repeat_instance'],
                        'task_status': 'COMPLETE',
                        'taskqueue_complete': '2'
                    })
                elif xnat_status == 'JOB_FAILED':
                    logger.debug(f'{i}:{assr}:JOB_FAILED')

                    # Apply from xnat to redcap
                    task_updates.append({
                        def_field: t[def_field],
                        'redcap_repeat_instrument': 'taskqueue',
                        'redcap_repeat_instance': t['redcap_repeat_instance'],
                        'task_status': 'JOB_FAILED',
                        'taskqueue_complete': '0'
                    })
                elif task_status == 'LOST':
                    logger.info(f'found lost job, setting to QUEUED:{assr}')

                    task_updates.append({
                        def_field: t[def_field],
                        'redcap_repeat_instrument': 'taskqueue',
                        'redcap_repeat_instance': t['redcap_repeat_instance'],
                        'task_status': 'QUEUED',
                        'task_jobid': '',
                        'task_jobnode': '',
                    })
                else:
                    logger.debug(f'{i}:{assr}:{task_status}')

                # we matched so we are done with this task
                break

            if not match_found:
                logger.debug(f'no match, set to DELETED:{assr}')
                task_updates.append({
                    def_field: t[def_field],
                    'redcap_repeat_instrument': 'taskqueue',
                    'redcap_repeat_instance': t['redcap_repeat_instance'],
                    'task_status': 'DELETED',
                })

        # Apply updates to REDCap
        logger.debug(f'updating {len(task_updates)} tasks')

        if task_updates:
            logger.debug(f'updating task info on redcap:{assr}:{task_updates}')
            self.apply_updates(task_updates)
        else:
            logger.debug(f'nothing to update')

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
            logger.warn(f'duplicate tasks for assessor, not good:{assessor}')
            task_id = rec[0]['redcap_repeat_instance']
        elif len(rec) == 1:
            task_id = rec[0]['redcap_repeat_instance']

        return task_id

    def current_tasks(self):
        return

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
