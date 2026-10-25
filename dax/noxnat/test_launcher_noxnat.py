'''Create task builder from duckdb and run update'''
import sys
import logging

import pandas as pd

from dax.rcq.launcher_noxnat import TaskLauncherNoXnat


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
	TaskLauncherNoXnat(sys.argv[1]).update()
