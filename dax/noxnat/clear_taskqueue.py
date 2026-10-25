import sys
import logging

import pandas as pd

from dax.noxnat.database_noxnat import DatabaseNoXnat


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
	DatabaseNoXnat(f'{sys.argv[1]}/db/dax.duckdb').clear_taskqueue()
