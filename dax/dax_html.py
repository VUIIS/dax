from dax.exports.export_html import save as save_html
from dax.noxnat.database_noxnat import DatabaseNoXnat
from dax.noxnat import load_stats


def save_html_noxnat(rootdir, filename, dbfile=None, projects=None, tabs=False, emojis=False):

    if projects:
        projects = projects.replace(' ','').split(',') or None

    if not dbfile:
        dbfile = f'{rootdir}/db/dax.duckdb'

    # Load data from database file
    data = DatabaseNoXnat(dbfile).load_data()

    print('loading stats')
    data['stats'] = load_stats(rootdir)

    # Save html file
    print(f'saving file:{filename}:{projects=}')
    save_html(data, filename, projects=projects, tabs=tabs, emojis=emojis)
