import sys

import duckdb


if __name__ == '__main__':
	rootdir = sys.argv[1]
	filename = f'{rootdir}/db/dax.duckdb'

	with duckdb.connect(filename) as con:
		result = con.execute("""
			DELETE FROM scans
			WHERE rowid NOT IN (
  				SELECT first_value(rowid) OVER (
  					PARTITION BY PROJECT, SESSION, SCANID
    				ORDER BY rowid ASC
    			)
  				FROM scans
			);
		""")

		print(result)

	print('DONE!')
