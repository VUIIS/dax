import yamale
import os

from .errors import DaxError


def validate(filename):
    # TODO: match file to schema by loading yaml, check procyamlversion, etc

    # Load the schema
    try:
        schema_file = os.path.realpath(os.path.join(
            os.path.dirname(__file__), 'schema', 'processor.yaml'))

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
