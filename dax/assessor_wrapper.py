
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
        # self.xsitype =

    def _from_object(self, artefact):
        intf = artefact._intf
        path = artefact._uri
        artefact_type = intf.object_type_from_path(path)
        self.intf = intf
        self.path = path
        self.artefact = artefact
        self.artefact_type = artefact_type

    def exists(self):
        self.exists()

    def type(self):
        if self.artefact_type == 'scan':
            return self
