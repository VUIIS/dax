# exporter function:
#
# inputs: 
#    -project info, table of scans, assessors, sgp
# outputs: 
#   -html file


import logging
from datetime import datetime
from pathlib import Path
import json
from importlib import resources

import pandas as pd
import numpy as np
from redcap import Project

from ..rcq.projectinfo import load_project_info
from .export_templates import *


logger = logging.getLogger('dax')


SUBJ_COLUMNS = ['ID', 'PROJECT', 'GROUP', 'AGE', 'SEX']

STATS_COLUMNS = [
    'ASSR', 'PROJECT', 'SUBJECT', 'SESSION', 'SESSTYPE', 'SITE', 'DATE', 'PROCTYPE'
]

ANALYSES_COLUMNS = [
    'PROJECT', 'ID', 'NAME', 'STATUS', 'REPORT', 'BATCH',
    'LOGFILE', 'COVARS', 'OUTPUT', 'PROCESSOR', 'SUBJECTS', 'NOTE'
]

PROCESSORS_COLUMNS = [
    'ID', 'PROJECT', 'TYPE', 'FILTER', 'ARGS'
]


class DaxExporter(object):

    def __init__(self, rc):
        self._redcap = rc

    def export(
        self,
        projects,
        xnat,
        filename
    ):
        data = self._load_data(xnat, projects)

        # Set emoji statuses on scans/assessors
        _set_emojis(data)

        data['timestamp'] = datetime.now().strftime("%I:%M:%S %p %Y-%m-%d ")
        data['qa'] = pd.concat([data['scans'], data['assessors']]).fillna(np.nan)
        data['qa'].DATE = pd.to_datetime(data['qa'].DATE).dt.date

        # Merge in subject columns
        data['qa'] = pd.merge(
            data['qa'],
            data['subjects'],
           left_on=('SUBJECT','PROJECT'),
            right_on=('ID','PROJECT'),
            how='left'
        ).drop(columns=['ID'])

        # Merge in stats columns
        data['stats'] = pd.merge(
            data['stats'],
            data['subjects'],
            left_on=('SUBJECT','PROJECT'),
            right_on=('ID', 'PROJECT'),
            how='left'
        ).drop(columns=['ID'])

        data['stats'] = data['stats'].replace('', np.nan).dropna(subset=['SESSTYPE'])
        data['stats'] = data['stats'].replace(r'^\s*$', np.nan, regex=True).replace(np.nan, '')
        data['stats'].DATE = pd.to_datetime(data['stats'].DATE).dt.date

        # Add processing type to list stats mapping
        data['proc2stats'] = _map_proc2stats(data['stats'])

        # Get map of projects to proc types
        data['proj2proctypes'] = _map_proj2proctypes(data['qa'])

        # Get map of projects to sess types
        data['proj2sesstypes'] = _map_proj2sesstypes(data['qa'])

        # Get map of projects to scan types
        data['proj2scantypes'] = _map_proj2scantypes(data['qa'])

        # Get html from ag grid data
        html_text = _to_html(data)

        # Write html to file
        logger.info(f'saving html:{filename}:{projects=}')
        _write_html(html_text, filename)

    def _load_project_data(self, xnat, project):
        info = load_project_info(xnat, project)
        info['stats'] = self._load_project_stats(project, pd.concat([
            pd.DataFrame(info['assessors']),
            pd.DataFrame(info['sgp'])
        ]))
        return info

    def _stats_redcap(self, project):
        def_field = self._redcap.def_field

        # get the project ID for the stats redcap for this project
        _fields = [def_field, 'project_stats']
        logger.debug(f'loading projects stats key from redcap')
        rec = self._redcap.export_records(records=[project], fields=_fields)
        rec = [x for x in rec if x[def_field] == project][0]
        key = rec['project_stats']

        logger.debug(f'loading redcap with key:{project}')
        return Project(self._redcap.url, key)


    def _load_project_stats(self, project, assessors, proctypes=None, sesstypes=None):
        df = pd.DataFrame(columns=['ASSR', 'PROCTYPE', 'SESSTYPE'])

        try:
            """Get the stats data from REDCap."""
            statsrc = self._stats_redcap(project)
            rec = statsrc.export_records(forms=['stats'])
        except:
            logger.info(f'failed to load stats project:{project}')
            return df

        # Filter out FS6 if found, old
        rec = [x for x in rec if 'FS6_v1' not in x['stats_assr']]

        # Filter out old FS7 if found
        rec = [x for x in rec if not x['stats_name'].startswith('fs7_')]

        # Make a dataframe of columns we need
        df = pd.DataFrame(rec,columns=['stats_assr', 'stats_name', 'stats_value'])
        df = df.drop_duplicates(subset=['stats_assr', 'stats_name'])

        # Pivot to row per assessor, col per stats_name, values as stats_value
        df = pd.pivot(
            df,
            index='stats_assr',
            values='stats_value',
            columns='stats_name')

        df = df.reset_index()

        # Filter out failed
        logger.debug(f'filtering out Failed assessors')
        assessors = assessors[~assessors.QCSTATUS.isin(['Failed'])]

        # Only keep some columns
        assessors = assessors[[
            'ASSR',
            'PROJECT',
            'SUBJECT',
            'SESSION',
            'SESSTYPE',
            'SITE',
            'DATE',
            'PROCTYPE'
        ]]

        # Merge with assessors
        df = pd.merge(assessors, df, left_on='ASSR', right_on='stats_assr')

        # Clean up
        df = df.drop(columns=['stats_assr'])
        df = df.dropna(axis=1, how='all')

        if df.empty:
            return pd.DataFrame(columns=['ASSR', 'PROCTYPE', 'SESSTYPE'])

        df = df.sort_values('ASSR')

        # Apply filters
        if proctypes:
            df = df[df.PROCTYPE.isin(proctypes)]

        if sesstypes:
            df = df[df.SESSTYPE.isin(sesstypes)]

        return df.to_dict('records')

    def _load_data(self, xnat, projects):
        infos = []
        info = {}
        data = {}

        for p in projects:
            logger.debug(f'loading project info:{p=}')
            infos.append(self._load_project_data(xnat, p))

        # Combine list of project info into a single info
        for i in infos:
            # Append each list by key
            for k in ['scans', 'assessors', 'sgp', 'stats']:
                info[k] = info.get(k, []) + i[k]

        # Create df versions
        data['subjects'] = pd.DataFrame(columns=SUBJ_COLUMNS)
        data['scans'] = pd.DataFrame(info['scans'])
        data['assessors'] = pd.DataFrame(info['assessors'])
        data['sgp'] = pd.DataFrame(info['sgp'])
        data['stats'] = pd.DataFrame(info['stats'])
        data['analyses'] = pd.DataFrame(columns=ANALYSES_COLUMNS+['INVESTIGATOR'])
        data['processors'] = pd.DataFrame([])

        return data


def _map_proc2stats(stats):
    proc2stats = {}

    for proc in stats.PROCTYPE.unique():
        # Get columns with values for this proctype, no blanks
        df = stats[stats.PROCTYPE == proc]
        df = df.replace(r'^\s*$', np.nan, regex=True)
        df = df.dropna(axis=1, how='all')
        proc2stats[proc] = [x for x in list(df.columns) if x not in STATS_COLUMNS]

    return proc2stats


def _map_proj2proctypes(qa):
    proj2types = {}

    for proj in qa.PROJECT.unique():
        # Get columns with values for this project
        _types = qa[qa.PROJECT == proj].PROCTYPE.unique()
        proj2types[proj] = sorted(list([str(x) for x in _types if str(x)]))

    return proj2types


def _map_proj2sesstypes(qa):
    proj2types = {}

    for proj in qa.PROJECT.unique():
        # Get columns with values for this project
        _types = qa[qa.PROJECT == proj].SESSTYPE.unique()
        proj2types[proj] = sorted(list([str(x) for x in _types if str(x)]))

    return proj2types


def _map_proj2scantypes(qa):
    proj2types = {}

    for proj in qa.PROJECT.unique():
        # Get columns with values for this project
        df = qa[qa.PROJECT == proj]
        proj2types[proj] = list(df.SCANTYPE.unique())

    return proj2types


def _set_emojis(data):
# set a single emoji status for assessors and scans
# scans maps from quality, assessors from PROCSTATUS/QCSTATUS

#  'COMPLETE,Failed': '',
#  'COMPLETE,NeedsEdits': '',
#  'COMPLETE,NeedsQA': '',
#  'COMPLETE,Passed': '',
#  'JOB_FAILED,LaunchFailed': '',
#  'JOB_RUNNING,JobPending': '',
#  'JOB_RUNNING,JobRunning': '',
#  'NEED_INPUTS,JobPending': '',
#  'NEED_INPUTS,NeedAssr': '',
#  'COMPLETE,NeedsEdits': '',
#  'NEED_INPUTS,No Resource': '',
#  'NEED_INPUTS,No Files': '',
#  'NEED_INPUTS,xxxxxxxxxxxxx': '',

    # scan status as single emoji
    df = data['scans']
    df['STATUS'] = df['QUALITY'].map({
        'usable': '✅',
        'unusable': '❌',
        'questionable': '🟡',
    }).fillna('?')

    # assessor status as single emoji
    df = data['assessors']

    # Handle a few specific procstatuses
    df['STATUS'] = df['PROCSTATUS'].map({
        'NEED_INPUTS': '🟡',
        'JOB_FAILED': '🟡',
    })

    # Otherwise use QCSTATUS
    df['STATUS'] = df['QCSTATUS'].map({
        'Passed': '✅',
        'Job Pending': '🔷',
        'Needs QA': '🟩',
        'Failed': '❌',
    }).fillna('?')


def _to_html(data):
    html_text = ''

    tabs = [
        {'label': 'qa', 'panel': _qa_panel(data),  'active': True},
        {'label': 'stats', 'panel': _stats_panel(data), 'active': False},
        #{'label': 'home', 'panel': _home_panel(data)},
        {'label': 'processors', 'panel': _processors_panel(data),  'active': False},
        {'label': 'analyses', 'panel': _analyses_panel(data),  'active': False},
    ]

    tab_buttons, tab_panels = _get_tabs(tabs)

    qa_data = _get_qa_data(data)

    stats_data = _get_stats_data(data)

    data_dict = _get_data_dict(data)

    grids = ''.join(_get_grids(data))

    buttons = ''.join(_get_buttons(data))

    # Insert tabs pieces into webpage
    html_text = main_html_template
    html_text = html_text.replace('TIMESTAMP', data['timestamp'])
    html_text = html_text.replace('TABBUTTONS', ''.join(tab_buttons))
    html_text = html_text.replace('TABPANELS', ''.join(tab_panels))
    html_text = html_text.replace('BUTTONJS', buttons)
    html_text = html_text.replace('GRIDJS', qa_data + stats_data + data_dict + grids)

    return html_text


def _qa_panel(data):
    panel = ''
    # date selector Start Date to End Date
    # radio button for autofilter
    # radio button for graphs
    # radio button for demographics
    # radio buttons: MR PET EEG
    # radio buttons: emojis for statuses
    # buttons for pivot select

    # Filters
    _projects = sorted(list(data['scans'].PROJECT.unique()))
    _proctypes = sorted(list(data['assessors'].PROCTYPE.unique()))
    _scantypes = sorted(list(data['scans'].SCANTYPE.unique()))
    _sesstypes = sorted(list(data['scans'].SESSTYPE.unique()))
    _dropdowns = ''.join([
        _csv_button('qa'),
        _dropdown_html('qa_projects', 'Projects', _projects),
        _dropdown_html('qa_sesstypes', 'Session Types', _sesstypes),
        _dropdown_html('qa_scantypes', 'Scan Types', _scantypes),
        _dropdown_html('qa_proctypes', 'Processing Types', _proctypes)
    ])

    # Graph
    panel += _top_row(_dropdowns, '', _graph('qa'))

    # Row count badge
    panel += _badge('qa_rowcount')

    # Pivot buttons
    panel += _qa_pivot_buttons()

    return panel


def _qa_pivot_buttons():
    buttons = []

    buttons.append(_pivot_button('qa_scans', 'SCANS'))
    buttons.append(_pivot_button('qa_assessors', 'ASSESSORS'))
    buttons.append(_pivot_button_active('qa_sessions', 'SESSIONS'))
    buttons.append(_pivot_button('qa_subjects', 'SUBJECTS'))
    buttons.append(_pivot_button('qa_projects', 'PROJECTS'))

    return pivot_bar_html_template.replace('PIVOTBUTTONS', ''.join(buttons))


def _stats_pivot_buttons():
    buttons = []

    buttons.append(_pivot_button_active('stats_assessors', 'ASSESSORS'))
    buttons.append(_pivot_button('stats_sessions', 'SESSIONS'))
    buttons.append(_pivot_button('stats_subjects', 'SUBJECTS'))

    return pivot_bar_html_template.replace('PIVOTBUTTONS', ''.join(buttons))


def _pivot_button(ident, label):
    return pivot_button_html_template.replace('ID', ident).replace('LABEL', label)


def _pivot_button_active(ident, label):
    return pivot_button_active_html_template.replace('ID', ident).replace('LABEL', label)


def _stats_groupby_buttons():
    buttons = []

    buttons.append(_groupby_button_active('stats_all', 'No Grouping'))
    buttons.append(_groupby_button('stats_project', 'By Project'))
    buttons.append(_groupby_button('stats_sesstype', 'By Session Type'))
    buttons.append(_groupby_button('stats_site', 'By Site'))

    return groupby_bar_html_template.replace('GROUPBYBUTTONS', ''.join(buttons))


def _groupby_button(ident, label):
    return groupby_button_html_template.replace('ID', ident).replace('LABEL', label)


def _groupby_button_active(ident, label):
    return groupby_button_active_html_template.replace('ID', ident).replace('LABEL', label)


def _csv_button(ident):
    return csv_button_html_template.replace('ID', ident)


def _processors_panel(data):
    panel = ''

    _projects = sorted(data['assessors'].PROJECT.unique())
    _dropdowns = ''.join([
        _csv_button('processors'),
        _dropdown_html('processors_projects', 'Projects', _projects)
    ])
    panel += _top_row(_dropdowns, '', _graph('processors'))

    # Row count badge
    panel += _badge('processors_rowcount')

    return panel


def _analyses_panel(data):
    panel = ''

    # Filters
    _projects = sorted(list(data['assessors'].PROJECT.unique()))
    _investigators = sorted(list(data['analyses'].INVESTIGATOR.unique()))
    _statuses = sorted(list(data['analyses'].STATUS.unique()))

    _dropdowns = ''.join([
        _csv_button('analyses'),
        _dropdown_html('analyses_projects', 'Projects', _projects),
        _dropdown_html('analyses_invest', 'Investigator', _investigators),
        _dropdown_html('analyses_status', 'Status', _statuses),
    ])

    panel += _top_row(_dropdowns, '', '')

    # Row count badge
    panel += _badge('analyses_rowcount')

    return panel


def _dropdown_html(ident, label, options):

    dropdown_options = [_dropdown_option(x) for x in options]
    dropdown_html = dropdown_html_template
    dropdown_html = dropdown_html.replace('ID', ident)
    dropdown_html = dropdown_html.replace('LABEL', label)
    dropdown_html = dropdown_html.replace('OPTIONS', ''.join(dropdown_options))

    return dropdown_html


def _dropdown_option(label):
    return dropdown_option_html_template.replace('LABEL', label).replace('VALUE', label)


def _top_row(filters, groupbys, graphs):
    top_row = top_row_html_template
    top_row = top_row.replace('FILTERS', filters)
    top_row = top_row.replace('GROUPBYS', groupbys)
    top_row = top_row.replace('GRAPHS', graphs)
    return top_row

def _graph(ident):
    return graph_html_template.replace('ID', ident)


def _badge(ident):
    return badge_html_template.replace('ID', ident)


def _stats_panel(data):
    # Tab buttons for pivot select: Assessors or Sessions or Subjects
    panel = ''

    # Filters and Graph in next row
    _projects = sorted(list(data['assessors'].PROJECT.unique()))
    _proctypes = sorted(list(data['stats'].PROCTYPE.unique()))
    _sesstypes = sorted(list(data['stats'].SESSTYPE.unique()))
    _measures = data['stats'].columns
    _dropdowns = ''.join([
        _csv_button('stats'),
        _dropdown_html('stats_projects', 'Projects', _projects),
        _dropdown_html('stats_sesstypes', 'Session Types', _sesstypes ),
        _dropdown_html('stats_proctypes', 'Processing Types', _proctypes),
        _dropdown_html('stats_measures', 'Measures', _measures),
        _dropdown_html('stats_xvariable', 'x-variable', _measures)])

    _groupbys = _stats_groupby_buttons()
    _graphs = ''.join([_graph('stats')])
    panel += _top_row(_dropdowns, _groupbys, _graphs)

    # Row count badge
    panel += _badge('stats_rowcount')

    # Pivot buttons
    panel += _stats_pivot_buttons()

    return panel


def _get_tabs(tabs):
    buttons = []
    panels = []

    for t in tabs:
        tab_label = t['label']
        tab_data = t['panel']
        tab_active = t['active']

        if tab_active:
            tab_button = tab_button_active_html_template
            tab_panel = tab_panel_active_html_template
        else:
            tab_button = tab_button_html_template
            tab_panel = tab_panel_html_template
    
        tab_button = tab_button.replace('ID', tab_label)
        tab_button = tab_button.replace('LABEL', tab_label)

        tab_panel = tab_panel.replace('ID', tab_label)
        tab_panel = tab_panel.replace('LABEL', tab_label)
        tab_panel = tab_panel.replace('PANEL', tab_data)

        buttons.append(tab_button)
        panels.append(tab_panel)

    return buttons, panels


def _get_qa_data(data):
    row_data = _records(data['qa'])
    col_defs = _coldefs(data['qa'])

    qa_data = qa_data_js_template
    qa_data = qa_data.replace('ROWS', json.dumps(row_data, default=str))
    qa_data = qa_data.replace('COLUMNS', json.dumps(col_defs, default=str))

    return qa_data


def _records(df):
    records = df.to_dict('records')
    records = [{k:v for k,v in r.items() if v} for r in records]
    return records


def _coldefs(df):
    return [{'field': c, 'headerName': c} for c in df.columns]


def _get_stats_data(data):
    row_data = _records(data['stats'])
    col_defs = _coldefs(data['stats'])
    stats_data = stats_data_js_template
    stats_data = stats_data.replace('ROWS', json.dumps(row_data, default=str))
    stats_data = stats_data.replace('COLUMNS', json.dumps(col_defs, default=str))

    return stats_data


def _get_data_dict(data):
    proc2stats = data['proc2stats']
    proj2proctypes = data['proj2proctypes']
    proj2sesstypes = data['proj2sesstypes']
    proj2scantypes = data['proj2scantypes']

    data_dict = data_dict_js_template
    data_dict = data_dict.replace('PROC2STATS', json.dumps(proc2stats, default=str))
    data_dict = data_dict.replace('PROJ2PROCTYPES', json.dumps(proj2proctypes, default=str))
    data_dict = data_dict.replace('PROJ2SESSTYPES', json.dumps(proj2sesstypes, default=str))
    data_dict = data_dict.replace('PROJ2SCANTYPES', json.dumps(proj2scantypes, default=str))

    return data_dict


def _get_grids(data):
    grids = []

    # QA initialize with no data loaded
    _label = 'qa'
    _data = []
    _defs = _coldefs(data['qa'])
    _defs = [];
    grids.append(_grid(_label, _data, _defs))

    # Stats initialize with no data loaded
    _label = 'stats'
    _data = []
    _defs = _coldefs(data['stats'])
    grids.append(_grid(_label, _data, _defs))

    # Analyses
    _label = 'analyses'
    _data = _records(data['analyses'])
    _defs = _coldefs(data['analyses'])
    _defs = _hide_columns(_defs, ANALYSES_COLUMNS)
    grids.append(_grid(_label, _data, _defs))

    # Processors
    _label = 'processors'
    _data = _records(data['processors'])
    _defs = _coldefs(data['processors'])
    _defs = _hide_columns(_defs, PROCESSORS_COLUMNS)
    grids.append(_grid(_label, _data, _defs))

    return grids


def _grid(label, rowdata, coldefs):
    grid_js = grid_js_template
    grid_js = grid_js.replace('ID', label)
    grid_js = grid_js.replace('ROWS', json.dumps(rowdata, default=str))
    grid_js = grid_js.replace('COLUMNS', json.dumps(coldefs, default=str))

    return grid_js


def _hide_columns(column_defs, show_columns):
    for i, c in enumerate(column_defs):
        if c['field'] not in show_columns:
            c['hide'] = True

    return column_defs


def _get_buttons(data):
    buttons = []

    # Add pre javascript
    buttons.append(_dashboard_pre_js())

    # Stats dropdowns
    buttons.append(_dropdown_js('stats_projects'))
    buttons.append(_dropdown_js('stats_sesstypes'))
    buttons.append(_dropdown_js('stats_proctypes'))
    buttons.append(_dropdown_js('stats_measures'))
    buttons.append(_dropdown_js('stats_xvariable'))

    # QA dropdowns
    buttons.append(_dropdown_js('qa_projects'))
    buttons.append(_dropdown_js('qa_proctypes'))
    buttons.append(_dropdown_js('qa_scantypes'))
    buttons.append(_dropdown_js('qa_sesstypes'))

    # Analyses dropdowns
    buttons.append(_dropdown_js('analyses_projects'))
    buttons.append(_dropdown_js('analyses_invest'))
    buttons.append(_dropdown_js('analyses_status'))

    # Processors dropdowns
    buttons.append(_dropdown_js('processors_projects'))

    # Add post javascript
    buttons.append(_dashboard_post_js())

    return buttons

def _dashboard_pre_js():
    return resources.read_text('dax.exports', 'assets/dashboard_pre.js')


def _dashboard_post_js():
    return resources.read_text('dax.exports', 'assets/dashboard_post.js')


def _dropdown_js(label):
    dropdown_js = dropdown_js_template
    dropdown_js = dropdown_js.replace('ID', label)

    return dropdown_js


def _write_html(html_text, filename):
    _path = Path(filename)
    _path.write_text(html_text, encoding="utf-8")
