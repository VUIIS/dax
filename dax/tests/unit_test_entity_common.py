import dax.XnatUtils as XnatUtils

from unittest import TestCase


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



class TestAssessorObject:

    def __init__(self, label):
        self.label = label


    def info(self):
        return {'label': self.label}



class TestSessionObject:
    def __init__(self, project_id, subject_id, session):
        self.project_id_ = project_id
        self.subject_id_ = subject_id
        session_id = session['ID']
        self.session_id_ = session_id
        self.scan_objects_ = {
            s['ID']: TestScanObject(project_id, subject_id, self, s)
            for s in session['scans']
        }
        self.assessor_objects_ = {
            a['ID']: TestAssessorObject(project_id, subject_id, self, a)
            for a in session['assessors']
        }


    def project_id(self):
        return self.project_id_


    def subject_id(self):
        return self.subject_id_


    def session_id(self):
        return self.session_id_


    def session(self):
        return self


    def info(self):
        return {
            'project_id': self.project_id_,
            'subject_label': self.subject_id_,
            'session_label': self.session_id_
        }


    @staticmethod
    def entity_type():
        return 'session'


    def has_shared_project(self):
        return None


    def __getitem__(self, key):
        return self.scan_objects_[key]


    def assessors(self):
        return self.assessor_objects_.values()



class TestScanObject:

    def __init__(self, project_id, subject_id, session, scan, quality='usable'):
        self.project_id_ = project_id
        self.subject_id_ = subject_id
        self.session_ = session
        scan_id = scan['ID']
        self.scan_id_ = scan_id
        self.resource_objects_ = {
            r['label']: TestResourceObject(
                project_id, subject_id, session.session_id(), scan_id, r)
            for r in scan['resources']
        }
        self.quality_ = quality


    def project_id(self):
        return self.project_id_


    def subject_id(self):
        return self.subject_id_


    def session_id(self):
        return self.session_.session_id()


    def scan_id(self):
        return self.scan_id_


    def session(self):
        return self.session_


    def info(self):
        return {
            'project_id': self.project_id_,
            'subject_label': self.subject_id_,
            'session_label': self.session_.session_id(),
            'scan_label': self.scan_id_,
            'quality': self.quality_
        }


    @staticmethod
    def entity_type():
        return 'scan'


    def get_resources(self):
        return self.resource_objects_.values()


    def __getitem__(self, key):
        return self.resource_objects_[key]



class TestAssessorObject:

    def __init__(self, project_id, subject_id, session, assessor, qcstatus='usable'):
        self.project_id_ = project_id
        self.subject_id_ = subject_id
        self.session_ = session
        assessor_id = assessor['ID']
        self.assessor_id_ = assessor_id
        self.label_ = assessor['label']
        self.resource_objects_ = {
            r['label']: TestResourceObject(
                project_id, subject_id, session.session_id(), assessor_id, r)
            for r in assessor['resources']
        }
        self.proctypes_ = assessor['proctypes']
        self.qcstatus_ = qcstatus
        self.procstatus_ = assessor['procstatus']


    def project_id(self):
        return self.project_id_


    def subject_id(self):
        return self.subject_id_


    def session_id(self):
        return self.session_.session_id()


    def assessor_id(self):
        return self.assessor_id_


    def session(self):
        return self.session_


    def info(self):
        return {
            'project_id': self.project_id_,
            'subject_label': self.subject_id_,
            'session_label': self.session_.session_id(),
            'label': self.label_,
            'proctype': self.proctypes_,
            'qcstatus': self.qcstatus_,
            'procstatus': 'NEED_TO_RUN'
        }


    def get_resources(self):
        return self.resource_objects_.values()


    @staticmethod
    def entity_type():
        return 'assessor'


    def __getitem__(self, key):
        return self.resource_objects_[key]



class TestResourceObject:
    def __init__(self, project_id, subject_id, session_id, scan_id, values):
        self.project_id_ = project_id
        self.subject_id_ = subject_id
        self.session_id_ = session_id
        self.scan_id_ = scan_id
        self.values_ = values


    def project_id(self):
        return self.project_id_


    def subject_id(self):
        return self.subject_id_


    def session_id(self):
        return self.session_id_


    def scan_id(self):
        return self.scan_id_


    def __getitem__(self, key):
        return self.values_[key]



class TestObjectsTest(TestCase):

    def test_make_repo(self):
        t = TestSessionObject(
            'proj1', 'subj1',
            brain_tiv_from_gif_xnat_contents['projects'][0]['subjects'][0]['sessions'][0])
        print(t['1'])



spider_tiv_from_gif = '/home/dax/Xnat-management/comic100_dax_config/pipelines/BrainTivFromGIF/v1.0.0/Spider_BrainTivFromGIF_v1_0_0.py'

scan_brain_tiv_from_gif_yaml = """
---
inputs:
  default:
    spider_path: /home/dax/Xnat-management/comic100_dax_config/pipelines/BrainTivFromGIF/v1.0.0/Spider_BrainTivFromGIF_v1_0_0.py
    working_dir: /scratch0/dax/
    nipype_exe: perform_brain_tiv_from_gif.py
  xnat:
    scans:
      - scan1:
        types: T1W,T1w,MPRAGE 
        resources:
          - resource: NIFTI
            varname: T1
    assessors:
      - assessor1:
        proctypes: GIF_Parcellation_v3
        resources:
          - resource: SEG
            varname: seg
            required: True
command: python {spider_path} --exe {nipype_exe} --seg {seg}
attrs:
  suffix:
  xsitype: proc:genProcData
  walltime: 01:00:00
  memory: 4096
  ppn: 1
  env: /share/apps/cmic/NiftyPipe/v2.0/setup_v2.0.sh
  type: scan
  scan_nb: scan1 
"""


brain_tiv_from_gif_xnat_contents = {
    'projects': [{
        'ID': 'proj1',
        'subjects': [{
            'ID': 'subj1',
            'sessions': [{
                'ID': 'sess1',
                'scans': [{
                    'ID': '1',
                    'type': 'T1',
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
                    'label': 'proj1-x-subj1-x-sess1-x-1-proc1',
                    'proctypes': 'GIF_Parcellation_v3',
                    'procstatus': 'COMPLETE',
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
      - scan1:
        types: T1w,MPRAGE,T1,T1W,1946_3DT1
        resources:
          - resource: NIFTI
            varname: t1
      - scan2:
        types: 1946_MRAC_UTE
        resources:
          - resource: NIFTI
            varname: ute_echo2
      - scan3:
        types: 1946_MRAC_UTE_UMAP
        resources:
          - resource: DICOM
            varname: ute_umap
      - scan4:
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
