'''Create task builder from duckdb and run update'''
import sys
import logging

import pandas as pd

from dax.noxnat.launcher_noxnat import TaskLauncherNoXnat

if __name__ == '__main__':

	if '--debug' in sys.argv:
		logging.basicConfig(level=logging.DEBUG)

	TaskLauncherNoXnat(sys.argv[1]).update()
