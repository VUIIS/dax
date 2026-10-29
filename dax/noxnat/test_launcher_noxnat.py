'''Create task builder from duckdb and run update'''
import sys
import logging

import pandas as pd

from dax.noxnat.launcher_noxnat import TaskLauncherNoXnat

if __name__ == '__main__':

	if '--debug' in sys.argv:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=logging.INFO)

	launcher = TaskLauncherNoXnat(sys.argv[1])
	launcher._set_plimit(500)
	launcher._set_qlimit(500)
	launcher._set_perlimit(100)
	launcher.update()

	if '-r' in sys.argv:
		print('retrying JOB_FAILED')
		launcher.retry_failed()
