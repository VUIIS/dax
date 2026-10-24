""" Stores database in .duckdb file"""
import logging

import duckdb


logger = logging.getLogger('dax')


class DatabaseNoXnat(object):
    def __init__(self, filename):
        self._filename = filename

    def load_data(self):
        data = {}
        filename = self._filename

        '''Load all tables from duckdb file as dict of df'''
        with duckdb.connect(filename) as con:
            table_names = (con.sql('SHOW ALL TABLES').df())['name'].tolist()
            for t in table_names:
                data[t] = con.sql(f"SELECT * FROM {t}").df()
                data[t] = data[t].fillna('')
        
        return data

    def load_taskqueue(self):
        filename = self._filename

        with duckdb.connect(filename) as con:
            df = con.sql(f"SELECT * FROM taskqueue").df()
            df.fillna('')
        
        return df

    def fix_duckdb(self):
        filename = self._filename
        logger.info(f'fix_duckdb:{filename}')

        data = self.load_data()

        if 'PROCVERSION' not in data['assessors'].columns:
            logger.debug('adding PROCVERSION column to assessors in duckdb')
            with duckdb.connect(filename) as con:
                con.sql('ALTER TABLE assessors ADD COLUMN PROCVERSION VARCHAR')

        # Check for task queue table, add if needed
        if 'taskqueue' not in data.keys():
            logger.debug('adding taskqueue table to duckdb')
            _add_taskqueue_duckdb(filename)

    def _add_taskqueue(self):
        filename = self._filename

        with duckdb.connect(filename) as con:
            con.execute("""
                CREATE TABLE taskqueue (
                    ASSR VARCHAR PRIMARY KEY,
                    PROJECT VARCHAR,
                    PROCSTATUS VARCHAR,
                    INPUTLIST VARCHAR,
                    VAR2VAL VARCHAR,
                    WALLTIME VARCHAR,
                    MEMREQ VARCHAR,
                    YAMLFILE VARCHAR,
                    USERINPUTS VARCHAR,
                    TIMEUSED VARCHAR,
                    MEMUSED VARCHAR
                    )
                """
            )

    def add_assessor(self, assessor):
        filename = self._filename
        assr = assessor['ASSR']
        logger.debug(f'adding assessor to duckdb:{assr}:{filename}')

        with duckdb.connect(filename) as con:
            con.execute("""
                INSERT INTO assessors 
                (
                    PROJECT,
                    ASSR,
                    SUBJECT,
                    SESSION,
                    QCSTATUS,
                    PROCTYPE,
                    PROCVERSION,
                    PROCSTATUS,
                    INPUTS
                )
                VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    assessor['PROJECT'],
                    assessor['ASSR'], 
                    assessor['SUBJECT'],
                    assessor['SESSION'],
                    assessor['QCSTATUS'], 
                    assessor['PROCTYPE'], 
                    assessor['PROCVERSION'], 
                    assessor['PROCSTATUS'], 
                    assessor['INPUTS']
                ]
            )

        logger.debug(f'assessor added to duckdb:{assr}')

    def set_task(self, task):
        filename = self._filename
        logger.debug(f'setting task in duckdb:{task}:{filename}')

        with duckdb.connect(filename) as con:
            con.execute("""
                INSERT OR REPLACE INTO taskqueue (
                    ASSR,
                    PROJECT,
                    PROCSTATUS,
                    INPUTLIST,
                    VAR2VAL,
                    WALLTIME,
                    MEMREQ,
                    YAMLFILE,
                    USERINPUTS
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    task['ASSR'],
                    task['PROJECT'],
                    task['PROCSTATUS'],
                    task['INPUTLIST'],
                    task['VAR2VAL'],
                    task['WALLTIME'],
                    task['MEMREQ'],
                    task['YAMLFILE'],
                    task['USERINPUTS'],  
                ]
            )

        logger.debug(f'task set in duckdb:{task}:{filename}')

    def update_assessor(self, id, field, value):
        filename = self._filename

        logger.debug(f'update assessor in duckdb:{filename=}:{id=}:{field=}:{value=}')

        query = f"""
            UPDATE assessors
            SET {field} = ?
            WHERE ASSR = ?
        """

        with duckdb.connect(filename) as con:
            con.execute(query, [value, id])
