""" Task Queue for DAX without XNAT."""

#import os
import logging
import json

#import pandas as pd
#import numpy as np

#from ..assessor_utils import parse_full_assessor_name, is_sgp_assessor


logger = logging.getLogger('dax')


class TaskQueueNoXnat(object):

    def __init__(self, data):
        self._data = data

    def sync(self, projects):
        task_updates = []

        # Filter
        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'taskqueue']
        launch_failed = [x for x in rec if x['task_status'] in ['LAUNCH_FAILED']]
        uploading = [x for x in rec if x['task_status'] in ['UPLOADING', 'LOST']]

        if len(uploading) > 0:
            task_updates += self.sync_uploading(uploading, xnat)

        # Apply updates to REDCap
        logger.info(f'updating {len(task_updates)} tasks')

        if task_updates:
            logger.info(f'updating task info on redcap:{task_updates}')
            self.apply_updates(task_updates)
        else:
            logger.info(f'nothing to update')

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
