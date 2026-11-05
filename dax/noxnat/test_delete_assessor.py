'''sync database with filesystem'''
import os, sys, shutil
import glob

from dax.noxnat.database_noxnat import DatabaseNoXnat


if __name__ == '__main__':
	rootdir = sys.argv[1]
	assr = sys.argv[2]

	print(f'deleting {assr}')
	DatabaseNoXnat(f'{rootdir}/db/dax.duckdb').delete_assessor(assr)
