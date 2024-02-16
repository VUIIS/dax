""" Update task status from XNAT to REDCap."""
import logging

import pandas as pd

from dax import XnatUtils

logger = logging.getLogger('dax.rcqsync')

DONE_STATUSES = ['COMPLETE', 'JOB_FAILED', 'FAILED']

SUBDIRS = ['OUTLOG', 'PBS', 'PROCESSOR']


# Find records in redcap quque that have staus of UPLOADING get updated status
# from xnat. If it's COMPLETE, set to complete. Ff it's is it JOB_FAILED, set
# to JOB_FAILED. Otherwise do nothing?


def update(projects_redcap):
    task_updates = []
    def_field = projects_redcap.def_field

    logger.debug('loading taskqueue records')
    rec = projects_redcap.export_records(
        forms=['taskqueue'],
        fields=[projects_redcap.def_field])

    # Filter to only uploading jobs
    rec = [x for x in rec if x['redcap_repeat_instrument'] == 'taskqueue']
    rec = [x for x in rec if x['task_status'] == 'UPLOADING']

    # Load assesssor data from XNAT as our current status
    logger.debug('loading XNAT data')
    projects = list(set([x[projects_redcap.def_field] for x in rec]))
    xnat = XnatUtils.get_interface()
    assr_data = XnatUtils.load_assr_data(xnat, projects)
    sgp_data = XnatUtils.load_sgp_data(xnat, ','.join(projects))

    # Get updates
    logger.debug('updating each task')
    for i, t in enumerate(rec):
        assr = t['task_assessor']

        # Find the matching assessor for this task in XNAT data
        match_found = False
        for k, a in pd.concat([assr_data, sgp_data]).iterrows():
            if a.ASSR != assr:
                continue

            match_found = True

            # We have a match, check for updates
            if a.PROCSTATUS == 'COMPLETE':
                logger.debug(f'{i}:{assr}:COMPLETE')

                task_updates.append({
                    def_field: t[def_field],
                    'redcap_repeat_instrument': 'taskqueue',
                    'redcap_repeat_instance': t['redcap_repeat_instance'],
                    'task_status': 'COMPLETE',
                })
            else:
                logger.debug(f'{i}:{assr}:UPLOADING')

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
        try:
            projects_redcap.import_records(task_updates)
        except Exception as err:
            logger.error(err)
    else:
        logger.debug(f'nothing to update')
