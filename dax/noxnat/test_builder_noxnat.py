'''Create task builder from duckdb and run update'''
import sys
import logging

import pandas as pd

from dax.noxnat.builder_noxnat import TaskBuilderNoXnat


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
	rootdir = sys.argv[1]

	if True:
		from dax.noxnat.database_noxnat import DatabaseNoXnat
		DatabaseNoXnat(f'{rootdir}/db/dax.duckdb').fix_duckdb()

	builder = TaskBuilderNoXnat(rootdir)

	# Manually add a processor
	builder._data['processors'] = pd.concat(
		[builder._data['processors'],
		pd.DataFrame([{
			'PROJECT': 'D3',
			'FILE': 'FS7_v1.1.0.yaml',
			'FILTER': '',
			'ARGS': '',
		}])]
	)

	# Reload processing
	builder._build_projects = builder.projects_with_processing()

	# Run one session
	results = builder.update_all(only_session='180093b')

	print(f'{results=}')
