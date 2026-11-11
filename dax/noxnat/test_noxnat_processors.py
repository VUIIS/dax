'''Create task builder from duckdb and run update'''
import sys
import logging
import yaml

import pandas as pd

from dax.noxnat.builder_noxnat import TaskBuilderNoXnat
from dax.noxnat.database_noxnat import DatabaseNoXnat
from dax.noxnat.launcher_noxnat import TaskLauncherNoXnat


if __name__ == '__main__':
    rootdir = sys.argv[1]
    yamlfile = sys.argv[2]

    if '--debug' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Make launcher
    launcher = TaskLauncherNoXnat(sys.argv[1])
    launcher._set_plimit(1000)
    launcher._set_qlimit(1000)
    launcher._set_perlimit(1000)

    # Database
    db = DatabaseNoXnat(f'{rootdir}/db/dax.duckdb')

    # Get a builder
    builder = TaskBuilderNoXnat(rootdir)

    # Load processors from yaml file
    with open(yamlfile, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Make into datafrme
    df = pd.DataFrame(data).astype(str).fillna('')
    builder._data['processors'] = pd.concat([builder._data['processors'], df])
    print(df)

    # Reload processing
    builder._build_projects = builder.projects_with_processing()

    if '-b' in sys.argv:
        # Run build update
        results = builder.update_all()

    if '-q' in sys.argv:
        print('show taskqueue')
        q = db.load_taskqueue()
        q = q[q.PROCSTATUS != 'COMPLETE']
        print(q[['ASSR', 'PROCSTATUS', 'JOBSTART', 'JOBEND']])

    if '-a' in sys.argv:
        print('show running assessors')
        a = db.load_data()['assessors']

        print(a.QCSTATUS.value_counts())
        print(a.PROCSTATUS.value_counts())
        
        a = a[a.PROCSTATUS == 'JOB_RUNNING']
        print(a[['ASSR', 'PROCSTATUS']])

    if '-l' in sys.argv:
        print('update taskqueue')
        launcher.update()

    if '-r' in sys.argv:
        print('retrying JOB_FAILED')
        launcher.retry_failed()
