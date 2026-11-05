'''sync database with filesystem'''
import os, sys
import glob

from dax.noxnat.database_noxnat import DatabaseNoXnat


if __name__ == '__main__':
	rootdir = sys.argv[1]

	# Get list of assessors in database
	db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')
	db_assessors = list(db.load_data()['assessors']['ASSR'])
	print(f'n={len(db_assessors)} assessors in database')

	# Get list of assessors in filesystem
	fs_assessors = glob.glob(f'{rootdir}/projects/REMBRANDT/ASSESSORS/*/*')
	print(f'n={len(fs_assessors)} assessors on filesystem')

	# Get list of assessors in filesystem not found in database
	delete_assessors = [x for x in fs_assessors if os.path.basename(x) not in db_assessors]
	print(f'n={len(delete_assessors)} to delete from filesystem')
	print(*delete_assessors, sep='\n')

	if '-d' in sys.argv:
		print('deleting files for assessors not found in database')

		# Delete each directory
		for i, a in enumerate(delete_assessors):
			print(f'{i}:deleting:{a}')
			shutil.rmtree(a)

	print('DONE!')
