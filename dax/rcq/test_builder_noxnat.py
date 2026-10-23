'''Create task builder from duckdb and run update'''
import sys

import pandas as pd

from dax.rcq.builder_noxnat import TaskBuilderNoXnat, _fix_duckdb


if __name__ == '__main__':
	duckfile = sys.argv[1]
	yamldir = sys.argv[2]
	rootdir = sys.argv[3]

	_fix_duckdb(duckfile)

	builder = TaskBuilderNoXnat(duckfile, yamldir, rootdir)

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

	results = builder.update_all(only_session='180093a')

	#print(results)
