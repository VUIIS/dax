
# TODO: BenM/general refactor/missing project requirement
import yaml
from io import StringIO

from . import utilities


# TODO: BenM/general refactor/document if this is staying
class YamlDoc:
    def __init__(self):
        self.source_type = None
        self.source_id = None
        self.contents = None

    def from_string(self, source):
        contents = yaml.load(
            (StringIO.StringIO(source)), Loader=yaml.FullLoader)
        self.source_type = "string"
        self.source_id = "string source"
        self.contents = contents
        return self

    def from_file(self, source):
        contents = utilities.read_yaml(source)
        self.source_type = "file"
        self.source_id = source
        self.contents = contents
        return self
