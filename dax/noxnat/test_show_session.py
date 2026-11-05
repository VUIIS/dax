'''sync database with filesystem'''
import os, sys, shutil
import glob

from dax.noxnat.database_noxnat import DatabaseNoXnat


if __name__ == '__main__':
	rootdir = sys.argv[1]
	session = sys.argv[2]

	print(f'showing {session}')

	data = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb').load_data()

	scans = data['scans'][data['scans'].SESSION == session]
	print(scans)

	assessors = data['assessors'][data['assessors'].SESSION == session]
	print(assessors)
