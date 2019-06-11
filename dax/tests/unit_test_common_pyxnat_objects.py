
# TODO BenM/assessor_of_assessor/pick this up later; it isn't required for the
# initial working solution

class TestPyxnatSession:
    def __init__(self, project, subject, session, scans, assessors):
        self.scans_ = scans
        self.assessors_ = assessors
        self.project = project
        self.subject = subject
        self.session = session

    def scans(self):
        return self.scans_

    def assessors(self):
        return self.assessors_


class TestAttrs:
    def __init__(self, properties):
        pass


class TestPyxnatScan:
    def __init__(self, project, subject, session, scanjson):
        self.scanjson = scanjson
        self.project = project
        self.subject = subject
        self.session = session
        uristr = '/data/project/{}/subjects/{}/experiments/{}/scans/{}'
        self._uri = uristr.format(project,
                                  subject,
                                  session,
                                  self.scanjson['label'])

    def id(self):
        return self.scanjson['id']

    def label(self):
        return self.scanjson['label']


class TestPyxnatAssessor:
    def __init__(self, project, subject, session, asrjson):
        self.asrjson = asrjson
        self.project = project
        self.subject = subject
        self.session = session
        uristr = '/data/project/{}/subjects/{}/experiments/{}/assessors/{}'
        self._uri = uristr.format(project,
                                  subject,
                                  session,
                                  self.asrjson['label'])

    def id(self):
        return self.asrjson['id']

    def label(self):
        return self.asrjson['label']

    def inputs(self):
        return self.asrjson['xsitype'] + '/' + self.asrjson['inputs']
