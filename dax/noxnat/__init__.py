import os
import glob
import logging

import pandas as pd


logger = logging.getLogger('dax')


def load_stats(rootdir):
	records = []
	stats = None
	projects = [x for x in os.listdir(f'{rootdir}/projects') if not x.startswith('.')]

	for p in projects:
		logger.info(f'loading stats:project={p}')
		resources = glob.glob(f'{rootdir}/projects/{p}/ASSESSORS/*/*/STATS')
		logger.info(f'found {len(resources)} STATS folders for project {p}')
		for res in resources:
			logger.info(f'loading resource:{res}')
			rec = _load_resource(res)
			rec['resource'] = res
			records.append(rec)

	if len(data) > 0:
		stats = pd.DataFrame(records)
	else:
		stats = pd.DataFrame(columns=[
			'ASSR', 'PROJECT', 'SUBJECT', 'SESSION', 'SESSTYPE', 'SITE', 'DATE', 'PROCTYPE'
		])

	return stats


def _load_resource(resource):
	data = {}

	'''Load key/value pairs from file'''
	for f in os.listdir(resource):
		logger.info(f'loading file:{resource}/{f}')
		data.update(_load_stats_file(f'{resource}/{f}'))

	return data


def _load_stats_file(filename):
	data = {'filename': filename}

	return data


def load_processors(rootdir):
	return []


def load_analyses(rootdir):
	return []
