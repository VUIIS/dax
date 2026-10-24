'''Create task builder from duckdb and run update'''
import sys
import logging

import pandas as pd

from dax.rcq.launcher_noxnat import TaskLauncherNoXnat


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
	rootdir = sys.argv[1]

	launcher = TaskLauncherNoXnat(rootdir)

	results = launcher.update()

	print(f'{results=}')
