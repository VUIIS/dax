
from unittest import TestCase

import io
import json
import yaml
import xml.etree.cElementTree as xmlet
import os
import itertools
from dax import bin
from dax import dax_tools_utils


from dax import XnatUtils
from dax import assessor_utils
from dax.tests import unit_test_common_processor_yamls as yamls
from dax.tests.common_session_tools import SessionTools
from dax.yaml_doc import YamlDoc
from dax import AutoProcessor


# TODO: BenM/xnat refactor/ these sanity checks should be refactored into
# integration tests and performed on a test database that is explicitly
# setup / torn down within the scope of a test suite execution.
# Remove everything that doesn't make it into an integration test _before_
# the pull request back to vuiis/dax!

host165 = 'http://10.1.1.165'
host17 = 'http://10.1.1.17'
host = host17
proj_id = 'proj1'
subj_id = 'subj1'
sess_id = 'sess1'
scan_id = '1'
assr_id = 'asr1'

asrxsitype = 'proc:genProcData'
scanxsitype = 'xnat:mrScanData'

expstr = '/data/projects/{}/subjects/{}/experiments/{}'.format(
    proj_id, subj_id, sess_id)
scanstr = '/scans/{}'


# test dimensions:
#
# usable - processor:
# not set, false, true
#
# usable - scan / assessor:
# (unusable, questionable, usable, preferred), various
#
# types - scan / assessor:
# (1 type, several types), 1 type?
#
# needs qc - processor
# not set, false, true
#
# required - resource
# not set, false, true
#
#
# qc status - assessor
# JOB_PENDING, NEEDS_QA, GOOD, PASSED_QA, FAILED, BAD, POOR, RERUN, REPROC
# DONOTRUN, FAILED_NEEDS_REPROC, PASSED_EDITED_QA,
# OPEN_QA_LIST(RERUN, REPROC), BAD_QA_STATUS(FAILED, BAD, POOR, DONOTRUN)
#
# job status - assessor
# NO_DATA, NEED_TO_RUN, NEED_INPUTS, JOB_RUNNING, JOB_FAILED,
# READY_TO_UPLOAD, UPLOADING, COMPLETE, READY_TO_COMPLETE, DOES_NOT_EXIST,
# OPEN_STATUS_LIST(NEED_TO_RUN, UPLOADING, JOB_RUNNING, READY_TO_COMPLETE,
# JOB_FAILED), JOB_BUILT
#
# inputs
# no scans, 1 scan, n scans
# no assessors, 1 assessor, n assessors
# zero variables, one variable, n variables (from an input)
#
# select
# not set, foreach, foreach(other), one, some, all

t1_params = {
    'xsitype': scanxsitype,
    'type': "T1",
    'quality': "usable",
    'files': [
        ('NIFTI', ['images.nii']),
        ('SNAPSHOTS', ['snapshot.gif', 'snapshot(1).gif'])
    ]
}

t2_params = {
    'xsitype': scanxsitype,
    'type': "T2",
    'quality': "usable",
    'files': [
        ('NIFTI', ['images.nii']),
        ('SNAPSHOTS', ['snapshot.gif', 'snapshot(1).gif'])
    ]
}

flair_params = {
    'xsitype': scanxsitype,
    'type': "FLAIR",
    'quality': "usable",
    'files': [
        ('NIFTI', ['images.nii']),
        ('SNAPSHOTS', ['snapshot.gif', 'snapshot(1).gif'])
    ]
}

scan_presets = {
    't1': t1_params,
    't2': t2_params,
    'flair': flair_params
}


proc_x_params = {
    'xsitype': asrxsitype,
    'proctype': 'Proc_X_v1',
    'files': [
        ('SEG', ['seg.gz']),
    ]
}

assessor_presets = {
    'Proc_X_v1': proc_x_params
}


class ComponentTestBuild(TestCase):

    scan1_yaml = yamls.generate_yaml(
        scans=[
            {
                'name': 'scan1', 'types': 'T1', 'select': None, 'qc': None,
                'resources': [
                    {'type': 'NIFTI', 'name': 't1', 'required': None}
                ]
            }
        ]
    )

    @staticmethod
    def __generate_yamls(entries):
        yamldocs = []
        for e in entries:
            print(e)
            yamldocs.append(
                yamls.generate_yaml(
                    scans=[{
                        'name': 'scan1',
                        'types': 'T1',
                        'select': e['select'],
                        'qc': e['quality'],
                        'resources': [{
                            'type': 'NIFTI',
                            'name': 't1',
                            'required': e['required']
                        }]
                    }]
                )
            )

    @staticmethod
    def _setup_scans(session, scan_descriptors):
        for s, d in scan_descriptors:
            print((s, d))
            SessionTools.add_scan(session, s, scan_presets[d])

    @staticmethod
    def _setup_assessors(proj_id, subj_id, session):
        for i in range(1, 3):
            SessionTools.add_assessor(
                session, '{}-x-{}-x-{}-x-{}-x-Proc_X_v1'.format(
                    proj_id, subj_id, session.label(), i),
                assessor_presets['Proc_X_v1'],
                'no_inputs')

    def test_setup_old_assessors(self):
        intf = XnatUtils.get_interface(host)
        proj_id = 'proj1'
        subj_id = 'subj1'
        sess_ids = ['sess2', 'sess1']

        project = intf.select_project(proj_id)
        if not project.exists():
            self.assertTrue(False, 'proj1 should be pre-created for this test')

        subject = intf.select_subject(proj_id, subj_id)
        if not subject.exists():
            self.assertTrue(False, 'subj1 should be pre-created for this test')

        for s in sess_ids:
            session = intf.select_experiment(proj_id, subj_id, s)
            if not session.exists():
                self.assertTrue(
                    False, 'sess1 should be pre-created for this test')

            # delete and recreate scans
            scan_descriptors = [('1', 't1'), ('2', 't1'), ('11', 'flair')]
            ComponentTestBuild._setup_scans(session, scan_descriptors)

            # delete and recreate old assessors
            ComponentTestBuild._setup_assessors(proj_id, subj_id, session)

    def test_setup_session(self):
        proj_id = 'proj1'
        subj_id = 'subj1'
        sess_ids = ['sess1', 'sess2']
        intf = XnatUtils.get_interface(host=host)
        scan_descriptors = [
            ('1', 't1'), ('2', 't1'),
            ('11', 'flair'), ('12', 'flair'),
            ('21', 't2')]
        for sess_id in sess_ids:
            session = intf.select_experiment(proj_id, subj_id, sess_id)
            if not session.exists():
                self.assertTrue(False, "no such session")

            ComponentTestBuild._setup_scans(session, scan_descriptors)

    def test_clean_scans_from_test_session(self):
        proj_id = 'proj1'
        subj_id = 'subj1'
        sess_ids = ['sess1', 'sess2']
        # subj_id = 'subj2'
        # sess_ids = ['sess3', 'sess4']
        intf = XnatUtils.get_interface(host=host)
        for sess_id in sess_ids:
            session = intf.select_experiment(proj_id, subj_id, sess_id)
            if not session.exists():
                self.assertTrue(False, "no such session")

            for scn in session.scans():
                scn.delete()

    def test_clean_assessors_from_test_session(self):
        proj_id = 'proj1'
        subj_id = 'subj1'
        sess_ids = ['sess1', 'sess2']
        # subj_id = 'subj2'
        # sess_ids = ['sess3', 'sess4']
        intf = XnatUtils.get_interface(host=host)
        for sess_id in sess_ids:
            session = intf.select_experiment(proj_id, subj_id, sess_id)
            if not session.exists():
                self.assertTrue(False, "no such session")

            for asr in session.assessors():
                print((assessor_utils.full_label_from_assessor(asr)))
                asr.delete()

    # TODO: the text matrix that we run at the component level should be only
    # a small subset of the unit test processor parser test matrix
    def test_build_matrix(self):

        input_headers = ['xsitype', 'quality', 'type', 'files']
        input_xsitype = ['xnat:mrScanData']
        input_quality = ['unusable', 'usable', 'preferred']
        input_type = ['T1', 'T2']
        input_files = [
            [],
            [('NIFTI', ['images.nii'])],
            # [('NIFTI', ['images.nii']), ('SNAPSHOTS', ['snapshot.jpg.gz',
            # 'snapshot(1).jpg.gz'])]
        ]
        input_values = [input_xsitype, input_quality, input_type, input_files]
        input_table_values = itertools.product(*input_values)
        input_table = [[dict(zip(input_headers, r))] for r in input_table_values]

        headers = ['required', 'select', 'quality', 'inputs']
        required = [None, False, True]
        select = [None, 'foreach']
        quality = [None, False, True]
        input_fields = [[]] + [i for i in input_table]
        values = [required, select, quality, input_fields]
        table_values = itertools.product(*values)
        table = [dict(zip(headers, r)) for r in table_values]

        # generate the scan artefacts against which this is run
        for scans in input_table:
            for scan in scans:
                SessionTools.add_scan(None, 'scan1', scan)

        print((len(table)))

    def test_end_to_end_test(self):
        print((os.getcwd()))
        settings_location = os.getcwd()+'/settings/'
        processor_location = os.getcwd()+'/processors/'

        self.test_clean_assessors_from_test_session()

        self.test_setup_old_assessors()

        bin.build(
            settings_location + 'test.yaml',
            None,
            True,
            projects='proj1',
            sessions='sess1,sess2',
            mod_delta=None,
            proj_lastrun=None)

        bin.launch_jobs(
            settings_location + 'test.yaml',
            None,
            True,
            projects='proj1',
            sessions='sess1,sess2',
            writeonly=False,
            pbsdir=None,
            force_no_qsub=False)

        dax_tools_utils.upload_tasks(
            None,
            True,
            settings_location + 'test_upload.yaml',
            host=None,
            username=None,
            password=None,
            projects=None,
            suffix='',
            emailaddress=None)

        bin.update_tasks(
            settings_location + 'test.yaml',
            None,
            True,
            projects='proj1',
            sessions='sess1,sess2')

        dax_tools_utils.upload_tasks(
            None,
            True,
            settings_location + 'test_upload.yaml',
            host=None,
            username=None,
            password=None,
            projects=None,
            suffix='',
            emailaddress=None)
