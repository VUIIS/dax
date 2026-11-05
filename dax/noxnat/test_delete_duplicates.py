import sys

import duckdb


if __name__ == '__main__':
	rootdir = sys.argv[1]
	filename = f'{rootdir}/db/dax.duckdb'

	with duckdb.connect(filename) as con:

		# Delete duplicate scans
		con.execute("""
			DELETE FROM scans
			WHERE rowid NOT IN (
  				SELECT first_value(rowid) OVER (
  					PARTITION BY PROJECT, SESSION, SCANID
    				ORDER BY rowid ASC
    			)
  				FROM scans
			);
		""")

		# Delete duplicate assessors
		con.execute("""
			DELETE FROM assessors
			WHERE rowid NOT IN (
				SELECT first_value(rowid) over (
					PARTITION BY PROJECT, PROCTYPE, INPUTS
					ORDER BY rowid ASC
 				)
  				FROM assessors
			);
		""")


	print('DONE!')
