

def save(data, filename):
    import duckdb

    # Connect to file and write each pandas dataframe as table
    with duckdb.connect(filename) as con:
        for t, df in data.items():
            con.execute(f'CREATE TABLE {t} AS SELECT * FROM df')
