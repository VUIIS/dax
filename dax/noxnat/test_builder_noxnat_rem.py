'''Create task builder from duckdb and run update'''
import sys
import logging

import pandas as pd

from dax.noxnat.builder_noxnat import TaskBuilderNoXnat


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
	rootdir = sys.argv[1]

	# Get a builder for this dax dir
	builder = TaskBuilderNoXnat(rootdir)

	# Manually add a processor to a project
	builder._data['processors'] = pd.concat(
		[builder._data['processors'],
		pd.DataFrame([{
			'PROJECT': 'REMBRANDT',
			'FILE': 'synbold_v1.3.2.yaml',
			'FILTER': '170006a',
			'ARGS': 'inputs.xnat.scans.scan_t1.types=T1\r\ninputs.xnat.scans.scan_fmri.types=fMRI_REST1',
		}])]
	)

	# Reload processing
	builder._build_projects = builder.projects_with_processing()

	# Run
	results = builder.update_all()

	print(f'{results=}')
