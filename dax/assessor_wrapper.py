# TODO BenM/assessor_of_assessor/pick this up later; it isn't required for the
# initial working solution
class ArtefactWrapper:

    @staticmethod
    def FromPath(intf, path):
        assessor = ArtefactWrapper()
        assessor._from_path(intf, path)

    @staticmethod
    def FromObject(object):
        assessor = ArtefactWrapper()
        assessor._from_object(object)

    def __init__(self):
        self.intf = None
        self.path = None
        self.artefact = None
        self.artefact_type = None
        self.xsitype = None

    def _from_path(self, intf, path):
        artefact = intf.select(path)
        artefact_type = intf.object_type_from_path(path)
        self.intf = intf
        self.path = path
        self.artefact = artefact
        self.artefact_type = artefact_type
        self.xsitype = artefact.attrs._get_datatype()

    def _from_object(self, artefact):
        intf = artefact._intf
        path = artefact._uri
        artefact_type = intf.object_type_from_path(path)
        self.intf = intf
        self.path = path
        self.artefact = artefact
        self.artefact_type = artefact_type
        self.xsitype = artefact.attrs._get_datatype()

    def exists(self):
        self.exists()

    def type(self):
        if self.artefact_type in ['scan', 'assessor']:
            return self.artefact_type
        else:
            return None

    def xsitype(self):
        return self.xsitype

    def get_attribute(self, attribute):
        return self.artefact.attrs.get(self.xsitype + '/' + attribute)

    def try_get_attribute(self, attribute, default):
        try:
            return self.artefact.attrs.get(self.xsitype + '/' + attribute)
        except IndexError:
            return default
