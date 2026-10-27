'''Create task builder from duckdb and run update'''
import sys
import logging

import pandas as pd

from dax.noxnat.builder_noxnat import TaskBuilderNoXnat
from dax.noxnat.database_noxnat import DatabaseNoXnat


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
	rootdir = sys.argv[1]

	if '-r' in sys.argv:
		print('reset taskqueue')
		db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')
		db._delete_taskqueue()
		db._add_taskqueue()

		print('reset running assessors')
		df = db.load_data()['assessors']
		df = df[df.PROCSTATUS == 'JOB_RUNNING']
		for i, a in df.iterrows():
			id = a['ASSR']
			print(f'reset:{i}:{id}')
			db.update_assessor(id, 'PROCSTATUS', 'NEED_INPUTS')

	# Get a builder for this dax dir
	builder = TaskBuilderNoXnat(rootdir)

	# Manually add a processor to a project
	builder._data['processors'] = pd.concat(
		[builder._data['processors'],
		pd.DataFrame([{
			'PROJECT': 'REMBRANDT',
			'FILE': 'synbold_v1.3.2.yaml',
			'FILTER': '17000*a',
			'ARGS': 'inputs.xnat.scans.scan_t1.types=T1\r\ninputs.xnat.scans.scan_fmri.types=fMRI_REST1',
		}])]
	)

	# Reload processing
	builder._build_projects = builder.projects_with_processing()

	# Run
	results = builder.update_all()

	if '-q' in sys.argv:
		print('show taskqueue')
		db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')
		q = db.load_taskqueue()
		print(q[['ASSR', 'PROCSTATUS', 'JOBSTART', 'JOBEND']])

	if '-a' in sys.argv:
		print('show running assessors')
		db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')
		a = db.load_data()['assessors']
		a = a[a.PROCSTATUS == 'JOB_RUNNING']
		print(a[['ASSR', 'PROCSTATUS']])
