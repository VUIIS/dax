""" Stores database in .duckdb file"""
import logging

import duckdb


logger = logging.getLogger('dax')


class DatabaseNoXnat(object):
    def __init__(self, filename):
        self._filename = filename

    def delete_bad_assessors(self):
        filename = self._filename

        with duckdb.connect(filename) as con:
            con.execute("""
                DELETE FROM assessors
                WHERE PROCSTATUS == 'NEED_INPUTS';
            """)

            con.execute("""
                DELETE FROM assessors
                WHERE PROCSTATUS == 'JOB_RUNNING';
            """)

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

    def clear_taskqueue(self):
        filename = self._filename

        with duckdb.connect(filename) as con:
            con.sql("DELETE FROM taskqueue")

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

    def _delete_taskqueue(self):
        filename = self._filename

        with duckdb.connect(filename) as con:
            con.sql("DROP TABLE taskqueue")

    def _add_taskqueue(self):
        filename = self._filename

        with duckdb.connect(filename) as con:
            con.execute("""
                CREATE TABLE taskqueue (
                    ASSR VARCHAR PRIMARY KEY,
                    JOBID VARCHAR,
                    JOBNODE VARCHAR,
                    JOBDATE VARCHAR,
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

    def update_tasks(self, updates):
        filename = self._filename
        key = 'ASSR'

        # Get all columns not key
        columns = list(dict.fromkeys(col for record in updates for col in record if col != key))
        if not columns:
            print('empty updates')
            return

        # Make (columns,present)
        value_columns = [item for c in columns for item in (c, f"{c}_present")]

        # Build values ? string
        values_query = ", ".join(
            "(" + ", ".join("?" for _ in range(1 + 2*len(columns))) + ")"
            for _ in updates
        )

        # Generate string of columns to update
        set_query = ", ".join(
            f"{c} = CASE WHEN v.{c}_present THEN v.{c} "
            f"ELSE a.{c} END"
            for c in columns
        )

        # Build full query
        table = 'taskqueue'
        full_query = f"""
            UPDATE {table} AS a
            SET {set_query}
            FROM (VALUES {values_query}) AS v 
                ({key}, {", ".join(value_columns)})
            WHERE a.{key} = v.{key}
        """

        # Get data rows to update
        data = []
        for u in updates:
            data.append(u[key])
            for c in columns:
                data.extend([u.get(c), c in u])

        # Apply batch of updates
        with duckdb.connect(filename) as con:
            con.execute(full_query, data)
