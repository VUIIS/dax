import os, sys

from dax.noxnat.database_noxnat import DatabaseNoXnat

if __name__ == '__main__':
    rootdir = sys.argv[1]
    outdir = sys.argv[2]

    os.mkdirs(outdir, exist_ok=False)

    db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')

    db._export_tsv(outdir)
