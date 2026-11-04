import sys
import webbrowser

from dax.noxnat.database_noxnat import DatabaseNoXnat
from dax.exports.export_html import save as save_html


if __name__ == '__main__':
    rootdir = sys.argv[1]    
    filename = sys.argv[2]
    projects = sys.argv[3].split(',')

    # Load data from database file
    data = DatabaseNoXnat(f'{sys.argv[1]}/db/dax.duckdb').load_data()

    # Save html file
    print(f'saving file:{filename}:{projects=}')
    save_html(data, filename, projects=projects)

    # Open html in firefox web browser
    try:
        firefox = webbrowser.get('firefox')
        print(f'opening file in browser:{filename}')
        firefox.open_new_tab(filename)
    except Exception:
        print('unable to open file in browser')
