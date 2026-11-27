import os, sys

from dax.noxnat.database_noxnat import DatabaseNoXnat

if __name__ == '__main__':
    rootdir = sys.argv[1]
    project = sys.argv[2]
    outdir = sys.argv[3]

    os.makedirs(outdir, exist_ok=False)

    db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')

    db._export_project_tsv(project, outdir)
