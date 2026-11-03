import sys
import tempfile

import webbrowser

from dax.noxnat.database_noxnat import DatabaseNoXnat
from dax.exports.export_html save as save_html

if __name__ == '__main__':
    rootdir = sys.argv[1]

    # Load data from database file
    data = DatabaseNoXnat(f'{sys.argv[1]}/db/dax.duckdb').load_data()

    with tempfile.TemporaryDirectory() as tmpdir:

        filename = f'{tmpdir}/dax.html'

        # Save html
        print(f'saving file:{filename}')
        save_html(data, filename)

        # Open html in browser
        print(f'opening file in browser:{filename}')
        webbrowser.open_new_tab(filename)
