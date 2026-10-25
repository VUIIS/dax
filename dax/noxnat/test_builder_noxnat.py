'''Create task builder from duckdb and run update'''
import sys
import logging

import pandas as pd

from dax.rcq.builder_noxnat import TaskBuilderNoXnat


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
	rootdir = sys.argv[1]

	if True:
		from dax.rcq.database_noxnat import DatabaseNoXnat
		DatabaseNoXnat(f'{rootdir}/db/dax.duckdb').fix_duckdb()

	builder = TaskBuilderNoXnat(rootdir)

	print('processors=', builder._data['processors'])

	builder._data['processors'] = pd.concat(
		[builder._data['processors'],
		pd.DataFrame([{
			'PROJECT': 'D3',
			'FILE': 'FS7_v1.1.0.yaml',
			'FILTER': '',
			'ARGS': '',
		}])]
	)

	builder._build_projects = builder.projects_with_processing()

	print(builder._data['processors'])

	results = builder.update_all(only_session='180093b')

	print(f'{results=}')
