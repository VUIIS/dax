
if __name__ == '__main__':
	rootdir = sys.argv[1]

	db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')
	db._delete_analyses()
	db._add_analyses()
