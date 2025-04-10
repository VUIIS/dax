import os
import yaml

import yamale

from .errors import DaxError


def validate(filename):
    schema_file = None
    schema = None
    data = None
    contents = {}

    # Determine which schema should be used based on yaml contents
    try:
        with open(filename, 'r') as f:
            contents = yaml.safe_load(f)

        if contents.get('inputs', False).get('xnat', False).get('subjects', False):
            schema_file = os.path.realpath(os.path.join(
                os.path.dirname(__file__),
                'schema',
                'project_processor.yaml'))
        elif contents.get('inputs', False).get('xnat', False).get('sessions', False):
             schema_file = os.path.realpath(os.path.join(
                os.path.dirname(__file__),
                'schema',
                'subject_processor.yaml'))
        else:
            schema_file = os.path.realpath(os.path.join(
                os.path.dirname(__file__),
                'schema',
                'processor.yaml'))
    except Exception as err:
        raise Exception(f'failed to determine processor type of yaml, cannot validate.')

    # Load the schema
    try:
        schema = yamale.make_schema(schema_file)
    except Exception as err:
        raise DaxError('failed to read schema:{}:{}'.format(schema_file, err))

    # Load the file to be validated
    try:
        data = yamale.make_data(filename)
    except Exception as err:
        raise DaxError('failed to read file:{}:{}'.format(filename, err))

    # Validate data against the schema
    try:
        yamale.validate(schema, data)
    except ValueError as err:
        raise DaxError('validate failed:{}:{}'.format(schema_file, err))
