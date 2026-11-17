import os
import glob
import logging


logger = logging.getLogger('dax')


def load_stats(rootdir):
	stats = []

	projects = [x for x in os.listdir(f'{rootdir}/projects') if not x.startswith('.')]

	for p in projects:
		logger.info(f'loading stats:project={p}')
		resources = glob.glob(f'{rootdir}/{p}/ASSESSORS/*/*/STATS')
		logger.info(f'found {len(resources)} STATS folders for project {p}')
		for r in resources:
			logger.info(f'loading resource:{r}')

	return stats


def load_processors(rootdir):
	return []


def load_analyses(rootdir):
	return []
