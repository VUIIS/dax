import sys
import logging

import pandas as pd

from dax.noxnat.database_noxnat import DatabaseNoXnat


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
	d = DatabaseNoXnat(f'{sys.argv[1]}/db/dax.duckdb')

	updates = [{
		'ASSR': 'D3-x-180093-x-180093b-x-FS7_v1-x-2b669817',
		'PROCSTATUS': 'UNKNOWN',
		'TIMEUSED': 'NULL',
		'MEMUSED': '3g'
	}]

	d.update_tasks(updates)
