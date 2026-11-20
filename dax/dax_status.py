from dax.noxnat.database_noxnat import DatabaseNoXnat


def show_status_noxnat(rootdir, projects=None, show_queue=False, show_assessors=False, show_analyses=False):

    dbfile = f'{rootdir}/db/dax.duckdb'

    # Load data from database file
    db = DatabaseNoXnat(dbfile)
    q = db.load_taskqueue()
    a = db.load_data()['assessors']
    g = db.load()['analyses']

    print(f'{projects=}')

    # TODO: show assr counts by project/proctype/status to show progress of processing

    if len(q) == 0:
        print('Nothing in the SLURM queue')
    else:
        # TODO: show queue counts by project/proctype/status
        q = q[q.PROCSTATUS != 'COMPLETE']
        print(f'{len(q)} jobs in the SLURM queue')
        print(q.PROCSTATUS.value_counts().to_string())

    if len(q) > 0 and show_queue:
        # Show the queue
        q = q[q.PROCSTATUS != 'COMPLETE']
        print(q[['ASSR', 'PROCSTATUS', 'JOBSTART', 'JOBEND']])

    if len(a) > 0 and show_assessors:
        # Get assessors
        print('show running assessors')

        # Show Some counts
        print(a.QCSTATUS.value_counts().to_string())
        print(a.PROCSTATUS.value_counts().to_string())

        # Show running statuses
        a = a[a.PROCSTATUS == 'JOB_RUNNING']
        print(a[['ASSR', 'PROCSTATUS']])

    if len(g) > 0 and show_analyses:
        print('show analyses')
        print(g)
