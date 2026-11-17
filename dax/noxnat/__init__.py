import os
import glob
import logging
import csv

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
			logger.debug(f'loading resource:{res}')
			assr = res.rsplit('/', 2)[1]
			_, subj, sess, proctype, _ = assr.split('-x-', 4)
			rec = {
				'ASSR': assr,
				'PROJECT': p,
				'SUBJECT': subj,
				'SESSION': sess,
				'SESSTYPE': '',
				'SITE': '',
				'DATE': '',
				'PROCTYPE': proctype,
				'resource': res
			}
			rec.update(_load_resource(res))
			records.append(rec)

	if len(records) > 0:
		stats = pd.DataFrame(records)
	else:
		stats = pd.DataFrame(columns=[
			'ASSR', 'PROJECT', 'SUBJECT', 'SESSION', 'SESSTYPE', 'SITE', 'DATE', 'PROCTYPE'
		])

	print(stats)

	return stats


def _load_resource(resource):
	data = {}

	'''Load key/value pairs from file'''
	for f in os.listdir(resource):
		logger.debug(f'loading file:{resource}/{f}')
		data.update(_load_stats_file(f'{resource}/{f}'))

	return data


def _load_stats_file(filename):

	# Read file to determine format
	lines = []
    with open(filename) as f:
        lines = f.readlines()

    # Redirect by file formatting
    if ('=' in lines[0]) or (len(lines) >= 3 and len(lines[0].split(',')) <= 3):
        return _load_stats_tall(filename)
    else:
        return _load_stats_wide(filename)


def _load_stats_wide(filename):
    data = {}

    with open(filename, newline='') as f:
        # Connect csv reader
        reader = csv.reader(f)

        # Load header from first line
        header = next(reader)

        # Read data from subsequent lines
        for line in reader:
            for i, v in enumerate(line):
                data[header[i]] = v

    return data


def _load_stats_tall(filename):
    data = {}
    rows = []

    try:
        with open(filename) as f:
            rows = f.readlines()

        if len(rows) == 1 and rows[0].startswith('excess_spikes') and 'spike_count' in rows[0]:
            _tmp = rows[0]
            rows[0] = _tmp.split('spike_count')[0]
            rows.append('spike_count' + _tmp.split('spike_count')[1])

        for r in rows:
            (k, v) = r.strip().replace('=', ',').split(',')
            data[k] = v
    except ValueError:
        logger.error(f'cannot load stats file:{filename}')
        return {}

    return data


def load_processors(rootdir):
	return []


def load_analyses(rootdir):
	return []
