import dax.XnatUtils as XnatUtils

from unittest import TestCase

from dax.task import (JOB_FAILED, JOB_RUNNING, JOB_PENDING, READY_TO_UPLOAD,
                   NEEDS_QA, RERUN, REPROC, FAILED_NEEDS_REPROC, BAD_QA_STATUS)

from . import unit_test_common_processor_yamls as processor_yamls

bad_qa_status = [JOB_PENDING, NEEDS_QA, REPROC, RERUN, FAILED_NEEDS_REPROC]


class FakeXnat:

    @staticmethod
    def placeholder():
        raise NotImplementedError()

    @staticmethod
    def get_proctype(spider, suffix=None):
        # TODO: ok to use XnatUtils method, at least until it is removed from XnatUtils, which should happen
        return XnatUtils.get_proctype(spider, suffix)

    @staticmethod
    def is_cscan_unusable(scan):
        return scan.info()['quality'] == 'unusable'

    @staticmethod
    def is_cscan_usable(scan):
        return scan.info()['quality'] == 'usable'

    @staticmethod
    def has_resource(scan, label):
        return XnatUtils.has_resource(scan, label)

    @staticmethod
    def get_good_cassr(csess, sp_types, needs_qc):
        return XnatUtils.get_good_cassr(csess, sp_types, needs_qc)


class TestResource:

    def __init__(self):
        self.thing = None

# class TestAssessorObject:
#
#     def __init__(self, label):
#         self.label = label
#
#
#     def info(self):
#         return {'label': self.label}


class TestProjectObject:
    def __init__(self, project_dict):
        project_id = project_dict['ID']
        self.project_id_ = project_id
        self.label_ = project_dict['label']
        self.subject_objects_ = {
            subj['ID']: TestSubjectObject(self, subj)
            for subj in project_dict['subjects']
        }

    def subjects(self):
        return self.subject_objects_

    def project_id(self):
        return self.project_id_

    def label(self):
        return self.label_


class TestSubjectObject:
    def __init__(self, project, subject_dict):
        self.project_ = project
        #self.project_id_ = project_id
        subject_id = subject_dict['ID']
        self.subject_id_ = subject_id
        self.label_ = subject_dict['label']
        self.session_objects_ = {
            sess['ID']: TestSessionObject(self, sess)
            for sess in subject_dict['sessions']
        }

    def sessions(self):
        return self.session_objects_

    def project_id(self):
        return self.project_.project_id()

    def subject_id(self):
        return self.subject_id_

    def parent(self):
        return self.project_

    def label(self):
        return self.label_


class TestSessionObject:
    def __init__(self, subject, session_dict):
        self.subject_ = subject
        session_id = session_dict['ID']
        self.session_id_ = session_id
        self.label_ = session_dict['label']
        self.scan_objects_ = {
            scan['ID']: TestScanObject(self, scan)
            for scan in session_dict['scans']
        }
        self.assessor_objects_ = {
            assr['ID']: TestAssessorObject(self, assr)
            for assr in session_dict['assessors']
        }

    def project_id(self):
        return self.subject_.project_id()

    def subject_id(self):
        return self.subject_.subject_id()

    def session_id(self):
        return self.session_id_

    def label(self):
        return self.label_

    def session(self):
        return self

    def parent(self):
        return self.subject_

    def info(self):
        return {
            'project_id': self.subject_.project_id(),
            'subject_label': self.subject_.subject_id(),
            'session_label': self.session_id_
        }

    @staticmethod
    def entity_type():
        return 'session'

    def has_shared_project(self):
        return None

    def scan_by_key(self, key):
        return self.scan_objects_[key]

    def assessor_by_key(self, key):
        return self.assessor_objects_[key]

    def scans(self):
        return self.scan_objects_

    def assessors(self):
        return self.assessor_objects_


class TestScanObject:

    def __init__(self, session, scan):
        self.quality_ = scan['quality']
        self.session_ = session
        scan_id = scan['ID']
        self.scan_id_ = scan_id
        self.resource_objects_ = {
            r['label']: TestResourceObject(self, r)
            for r in scan['resources']
        }
        self.type_ = scan['type']

    def project_id(self):
        return self.session_.project_id()

    def subject_id(self):
        return self.session_.subject_id()

    def session_id(self):
        return self.session_.session_id()

    def scan_id(self):
        return self.scan_id_

    def label(self):
        return self.scan_id_

    def type(self):
        return self.type_

    def session(self):
        return self.session_

    def parent(self):
        return self.session_

    def info(self):
        return {
            'ID': self.scan_id_,
            'project_id': self.session_.project_id(),
            'subject_label': self.session_.subject_id(),
            'session_label': self.session_.session_id(),
            'scan_label': self.scan_id_,
            'quality': self.quality_
        }

    @staticmethod
    def entity_type():
        return 'scan'

    def resources(self):
        return list(self.resource_objects_.values())

    def __getitem__(self, key):
        return self.resource_objects_[key]


class TestAssessorObject:

    def __init__(self, session, assessor_dict):
        self.session_ = session
        assessor_id = assessor_dict['ID']
        self.assessor_id_ = assessor_id
        self.label_ = assessor_dict['label']
        self.resource_objects_ = {
            r['label']: TestResourceObject(assessor_id, r)
            for r in assessor_dict['resources']
        }
        self.proctypes_ = assessor_dict['proctypes']
        self.qcstatus_ = assessor_dict['qcstatus']
        self.procstatus_ = assessor_dict['procstatus']

    def project_id(self):
        return self.session_.project_id()

    def subject_id(self):
        return self.session_.subject_id()

    def session_id(self):
        return self.session_.session_id()

    def assessor_id(self):
        return self.assessor_id_

    def label(self):
        return self.label_

    def type(self):
        return self.proctypes_

    def session(self):
        return self.session_

    def parent(self):
        return self.session_

    def info(self):
        return {
            'project_id': self.session_.project_id(),
            'subject_label': self.session_.subject_id(),
            'session_label': self.session_.session_id(),
            'label': self.label_,
            'proctype': self.proctypes_,
            'qcstatus': self.qcstatus_,
            'procstatus': self.procstatus_
        }

    def usable(self):
        return not self.qcstatus_ in bad_qa_status

    def unusable(self):
        return self.qcstatus_ in bad_qa_status

    def resources(self):
        return list(self.resource_objects_.values())

    @staticmethod
    def entity_type():
        return 'assessor'

    def __getitem__(self, key):
        return self.resource_objects_[key]


class TestResourceObject:
    def __init__(self, scan, resource_dict):
        self.scan_ = scan
        self.resource_dict_ = resource_dict

    def project_id(self):
        return self.scan_.project_id()

    def subject_id(self):
        return self.scan_.subject_id()

    def session_id(self):
        return self.scan_.session_id()

    def scan_id(self):
        return self.scan_.scan_id()

    def label(self):
        return self.resource_dict_['label']

    def __getitem__(self, key):
        return self.resource_dict_[key]


class TestObjectsTest(TestCase):

    def test_make_repo(self):
        # t = TestSessionObject(
        #     'proj1', 'subj1',
        #     brain_tiv_from_gif_xnat_contents['projects'][0]['subjects'][0]['sessions'][0])
        tp = TestProjectObject(brain_tiv_from_gif_xnat_contents['projects'][0])
        print((tp.label()))
        for tsb in tp.subjects().values():
            print(('', tsb.label()))
            for tse in tsb.sessions().values():
                print((' ', tse.label()))
                for tsc in tse.scans().values():
                    print(('  ', tsc.label()))
                for tas in tse.assessors().values():
                    print(('  ', tas.label()))


# second attempt; cut at xnatutils, assessorhandler and interfacetemp

# TODO: refactor calls to InterfaceTemp.select: move to methods on InterfaceTemp
# TODO: create FakeAssessorHandler
# TODO: create FakeXnatInterface


# class processor_yamls:
#     scan_gif_parcellation = processor_yamls.scan_gif_parcellation_yaml
#     scan_brain_tiv_from_gif = processor_yamls.scan_brain_tiv_from_gif_yaml


spider_tiv_from_gif = '/home/dax/Xnat-management/comic100_dax_config/pipelines/BrainTivFromGIF/v1.0.0/Spider_BrainTivFromGIF_v1_0_0.py'

brain_tiv_from_gif_xnat_contents = {
    'projects': [{
        'ID': 'proj1',
        'label': 'project 1',
        'subjects': [{
            'ID': 'subj1',
            'label': 'subject 1',
            'sessions': [{
                'ID': 'sess1',
                'label': 'session 1',
                'scans': [{
                    'ID': '1',
                    'type': 'T1',
                    'quality': 'usable',
                    'resources': [{
                        'label': 'SNAPSHOTS',
                        'file_count': 2
                    }, {
                        'label': 'NIFTI',
                        'file_count': 1
                    }]
                }, {
                    'ID': '2',
                    'type': 'T1',
                    'quality': 'usable',
                    'resources': [{
                        'label': 'SNAPSHOTS',
                        'file_count': 1
                    }, {
                        'label': 'NIFTI',
                        'file_count': 1
                    }]
                }],
                'assessors': [{
                    'ID': 'proc1',
                    'label': 'proj1-x-subj1-x-sess1-x-1-x-proc1',
                    'proctypes': 'GIF_Parcellation_v3',
                    'procstatus': 'COMPLETE',
                    'qcstatus': 'Passed QA',
                    # 'resources': [{
                    #     'label': 'PDF',
                    #     'file_count': 1
                    # }, {
                    #     'label': 'pBRAIN',
                    #     'file_count': 1
                    # }, {
                    #     'label': 'bBRAIN',
                    #     'file_count': 1
                    # }, {
                    #     'label': 'pTIV',
                    #     'file_count': 1
                    # }, {
                    #     'label': 'bTIV',
                    #     'file_count': 1
                    # }, {
                    #     'label': 'SNAPSHOTS',
                    #     'file_count': 2
                    # }, {
                    #     'label': 'PBS',
                    #     'file_count': 1
                    'resources': [{
                        'label': 'SEG',
                        'file_count': 1
                    }]
                }]
            }]
        }]
    }]
}

xnat_contents = {
    'brain_tiv_from_gif': brain_tiv_from_gif_xnat_contents
}

git_pct_t1_yaml = """
---
inputs:
  default:
    spider_path: /home/dax/Xnat-management/comic100_dax_config/pipelines/GIF_pCT/v1.0.0/Spider_GIF_pCT_v1_0_0.py
    working_dir: /scratch0/dax/
    nipype_exe: perform_gif_propagation.py
    db: /share/apps/cmic/GIF/1946_database_pCT/db_t1.xml
  xnat:
    scans:
      - name: scan1
        types: T1w,MPRAGE,T1,T1W,1946_3DT1
        resources:
          - resource: NIFTI
            varname: t1
      - name: scan2
        types: 1946_MRAC_UTE
        resources:
          - resource: NIFTI
            varname: ute_echo2
      - name: scan3
        types: 1946_MRAC_UTE_UMAP
        resources:
          - resource: DICOM
            varname: ute_umap
      - name: scan4
        types: RECON_PRR_NAC Images
        resources:
          - resource: DICOM
            varname: pet
command: python {spider_path} --t1_file {t1} --ute_echo2_file {ute_echo2} --ute_umap_dcm {ute_umap} --nac_pet_dcm {pet} --dbt {db} --working_dir {working_dir} --exe {nipype_exe}
attrs:
  suffix:
  xsitype: proc:genProcData
  walltime: 24:00:00
  memory: 3850
  ppn: 4
  env: /share/apps/cmic/NiftyPipe/pCT_only/setup_pCT_only.sh
  type: scan
  scan_nb: scan1
"""
