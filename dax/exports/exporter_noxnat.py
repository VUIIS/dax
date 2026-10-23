# exporter function for dax project without xnat:
#
# inputs: 
#    -project info, table of scans, assessors, sgp, etc from redcap
# outputs: 
#   -file


import logging

import pandas as pd
from redcap import Project

from . import export_duckdb
from . import export_html


logger = logging.getLogger('dax')


SUBJECTS_RENAME = {
    'project_id': 'PROJECT',
    'subject_id': 'ID',
    'subject_age': 'AGE',
    'subject_sex': 'SEX',
    'subject_group': 'GROUP',
}

SESSIONS_RENAME = {
    'project_id': 'PROJECT',
    'session_id': 'SESSION',
    'session_subject': 'SUBJECT',
    'session_site': 'SITE',
    'session_sesstype': 'SESSTYPE',
    'session_modality': 'MODALITY',
    'session_scanner': 'SCANNER',
    'session_tracer': 'TRACER',
    'session_note': 'NOTE'
}

SCANS_RENAME = {
    'project_id': 'PROJECT',
    'scan_id': 'SCANID',
    'scan_session':'SESSION',
    'scan_descrip': 'DESCRIP',
    'scan_scantype': 'SCANTYPE',
    'scan_quality': 'QUALITY',
    'scan_resources':'RESOURCES',
    'scan_duration': 'DURATION',
    'scan_tr': 'TR',
    'scan_frames': 'FRAMES',
    'scan_prfip': 'PRFIP',
    'scan_proop': 'PROOP',
    'scan_slicethickness': 'THICK',
    'scan_json': 'JSON',
    'scan_edat': 'EDAT',
}

ASSESSORS_RENAME = {
    'project_id': 'PROJECT',
    'assr_id': 'ASSR',
    'assr_subject': 'SUBJECT',
    'assr_session': 'SESSION',
    'assr_proctype': 'PROCTYPE',
    'assr_procversion': 'PROCVERSION',
    'assr_procstatus': 'PROCSTATUS',
    'assr_memreq': 'MEMREQ',
    'assr_timereq': 'TIMEREQ',
    'assr_jobdate': 'JOBDATE',
    'assr_inputs': 'INPUTS',
    'assr_timeused': 'TIMEUSED',
    'assr_memused': 'MEMUSED',
    'assr_jobnode': 'JOBNODE',
    'assr_qcstatus': 'QCSTATUS',
    'assr_qcdate': 'QCDATE',
    'assr_qcby': 'QCBY',
    'assr_yamlfile': 'YAMLFILE',
    'assr_userinputs': 'USERINPUTS', 
    'assr_failcount': 'FAILCOUNT', 
    'assr_slurmfile': 'SLURMFILE',
    'assr_jobstarttime': 'JOBSTARTTIME', 
    'assr_jobendtime': 'JOBENDTIME', 
    'assr_note': 'NOTE',
}

ANALYSES_RENAME = {
    'redcap_repeat_instance': 'ID',
    'analysis_name': 'NAME',
    'analysis_lead': 'INVESTIGATOR',
    'analysis_include': 'SUBJECTS',
    'analysis_processor': 'PROCESSOR',
    'analysis_input': 'INPUT',
    'analysis_output': 'OUTPUT',
    'analyses_complete': 'COMPLETE',
    'analysis_status': 'STATUS',
    'analysis_covars': 'COVARS',
    'analysis_notes': 'NOTES',
}

PROCESSORS_RENAME = {
    'redcap_repeat_instance': 'ID',
    'processor_file': 'FILE',
    'processor_filter': 'FILTER',
    'processor_args': 'ARGS',
    'processing_complete': 'COMPLETE',
}


class Exporter(object):

    def __init__(self, rc):
        # redcap connection to rc project for dax without xnat
        self._redcap = rc
        self._redcap_pid = None
        self.def_field = self._redcap.def_field

    def export_duckdb(
        self,
        projects,
        filename
    ):
        logger.info(f'loading data:{projects=}')
        data = self._load_data(projects)

        logger.info(f'saving duckdb:{filename}:{projects=}')
        export_duckdb.save(data, filename)

    def export_html(
        self,
        projects,
        filename
    ):
        logger.info(f'loading data:{projects=}')
        data = self._load_data(projects)

        logger.info(f'saving html:{filename}:{projects=}')
        export_html.save(data, filename)

    def redcap_pid(self):
        """Get the redcad project id"""
        if self._redcap_pid is None:
            self._redcap_pid = str(self._redcap.export_project_info().get('project_id'))

        return self._redcap_pid

    def get_link(self, instrument, project_id, repeat_id):
        url = self._redcap.url
        ver = self._redcap.redcap_version
        pid = self.redcap_pid()

        if url.endswith('/api/'):
            url = url[:-5]

        redcap_link = f'{url}/redcap_v{ver}/DataEntry/index.php?pid={pid}&page={instrument}&id={project_id}&instance={repeat_id}'

        return redcap_link

    def _load_subjects(self, projects):
        df = None

        logger.debug(f'loading subjects:{projects=}')

        rec = self._redcap.export_records(
            records=projects,
            forms=['subjects'],
            fields=[self.def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'subjects']

        # Get dataframe with renamed columns
        df = pd.DataFrame(rec).rename(columns=SUBJECTS_RENAME)[SUBJECTS_RENAME.values()]

        return df

    def _load_sessions(self, projects):
        df = None

        logger.debug(f'loading sessions:{projects=}')

        rec = self._redcap.export_records(
            records=projects,
            forms=['sessions'],
            fields=[self.def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'sessions']

        # Get dataframe with renamed columns
        df = pd.DataFrame(rec).rename(columns=SESSIONS_RENAME)[SESSIONS_RENAME.values()]

        if 'DATE' not in df.columns:
            df['DATE'] = ''

        return df

    def _load_stats(self, projects):
        df = None

        logger.debug(f'loading stats:{projects=}')

        rec = self._redcap.export_records(
            records=projects,
            forms=['stats'],
            fields=[self.def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'stats']

        # Make a dataframe of columns we need
        df = pd.DataFrame(rec, columns=['stats_assr', 'stats_name', 'stats_value'])
        df = df.drop_duplicates(subset=['stats_assr', 'stats_name'])

        # Pivot to row per assessor, col per stats_name, values as stats_value
        df = pd.pivot(
            df,
            index='stats_assr',
            values='stats_value',
            columns='stats_name').reset_index()

        return df

    def _load_scans(self, projects):
        df = None

        logger.debug(f'loading scans:{projects=}')

        rec = self._redcap.export_records(
            records=projects,
            forms=['scans'],
            fields=[self.def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'scans']

        # Get dataframe with renamed columns
        df = pd.DataFrame(rec).rename(columns=SCANS_RENAME)[SCANS_RENAME.values()]
        return df

    def _load_assessors(self, projects):
        df = None

        logger.debug(f'loading assessors:{projects=}')

        rec = self._redcap.export_records(
            records=projects,
            forms=['assessors'],
            fields=[self.def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'assessors']

        # Get dataframe with renamed columns
        df = pd.DataFrame(rec).rename(columns=ASSESSORS_RENAME)[ASSESSORS_RENAME.values()]

        return df

    def _load_analyses(self, projects):
        data = []

        logger.debug(f'analyses projects={projects}')

        rec = self._redcap.export_records(
            records=projects,
            forms=['analyses'],
            fields=[self.def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'analyses']

        # Apply hideshow
        rec = [x for x in rec if x['analysis_hideshow'] != '1']

        for r in rec:
            # Initialize record
            project_id = r[self.def_field]
            repeat_id = r['redcap_repeat_instance']
            link = self.get_link('analyses', project_id, repeat_id)
            d = {
                'PROJECT': project_id,
                'ID': repeat_id,
                'EDIT': link,
            }

            # Get renamed variables
            for k, v in ANALYSES_RENAME.items():
                d[v] = r.get(k, '')

            if r['analysis_procrepo']:
                d['PROCESSOR'] = r['analysis_procrepo']

            # Finally, add to our list
            data.append(d)

        return pd.DataFrame(data, columns=ANALYSES_RENAME.values())


    def _load_processors(self, projects):
        data = []

        rec = self._redcap.export_records(
            records=projects,
            forms=['processing'],
            fields=[self.def_field])

        rec = [x for x in rec if x['redcap_repeat_instrument'] == 'processing']

        # Only enabled processing
        rec = [x for x in rec if str(x['processing_complete']) == '2']

        for r in rec:
            # Initialize record with project
            project_id = r[self.def_field]
            repeat_id = r['redcap_repeat_instance']
            link = self.get_link('processing', project_id, repeat_id)
            d = {
                'PROJECT': project_id,
                'EDIT': link,
                'ID': repeat_id,
            }

            # Find the yaml file
            if r['processor_yamlupload']:
                filepath = r['processor_yamlupload']
            else:
                filepath = r['processor_file']

            # Get renamed variables
            for k, v in PROCESSING_RENAME.items():
                d[v] = r.get(k, '')

            d['FILE'] = filepath
            d['TYPE'] = _get_proctype(d['FILE'])

            # Finally, add to our list
            data.append(d)

        return pd.DataFrame(data, columns=PROCESSORS_RENAME.values())

    def _load_data(self, projects):
        data = {}

        # Load each data type
        data['subjects'] = self._load_subjects(projects)
        data['sessions'] = self._load_sessions(projects)
        data['scans'] = self._load_scans(projects)
        data['assessors'] = self._load_assessors(projects)
        data['stats'] = self._load_stats(projects)
        data['analyses'] = self._load_analyses(projects)
        data['processors'] = self._load_processors(projects)

        # Merge in session columns
        data['scans'] = pd.merge(
            data['scans'],
            data['sessions'],
            left_on=('SESSION','PROJECT'),
            right_on=('SESSION','PROJECT'),
            how='left'
        )
        data['assessors'] = pd.merge(
            data['assessors'],
            data['sessions'],
            left_on=('SESSION','PROJECT', 'SUBJECT'),
            right_on=('SESSION','PROJECT', 'SUBJECT'),
            how='left'
        )

        # Merge with notfailed assessors
        assessors = data['assessors']
        notfailed = assessors[~assessors.QCSTATUS.isin(['Failed'])]
        notfailed = notfailed[[
            'ASSR',
            'PROJECT',
            'SUBJECT',
            'SESSION',
            'SESSTYPE',
            'SITE',
            'DATE',
            'PROCTYPE'
        ]]
        data['stats'] = pd.merge(
            notfailed,
            data['stats'],
            left_on='ASSR',
            right_on='stats_assr'
        )

        # TODO: check for consistencies across data types, i.e. inputs deleted?

        #for k, df in data.items():
        #    print(k, len(df), df.columns)

        return data
