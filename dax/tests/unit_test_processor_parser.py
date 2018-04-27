from unittest import TestCase

import copy

import StringIO
import yaml

from dax import processor_parser


# test matrix
# ===========

# select keywords
# . foreach, foreach(i), one, some(n), all, malformed
# resources
# . well-formed
#   . one, many
# . malformed
#   . none, duplicates (intra), duplicates (inter)
# . present / not present
# assessor statuses
# . all statuses



class TestResource:

    def __init__(self, label, file_count):
        self.label_ = label
        self.file_count_ = file_count

    def label(self):
        return self.label_

    def file_count(self):
        return self.file_count_


class TestArtefact:

    def __init__(self, id, artefact_type, quality, resources, inputs):
        self.id_ = id
        self.artefact_type = artefact_type
        self.quality_ = quality
        self.resources = [TestResource(r[0], r[1]) for r in resources]
        self.inputs = inputs

    def id(self):
        return self.id_

    def type(self):
        return self.artefact_type

    def quality(self):
        return self.quality_

    def usable(self):
        return self.quality() == 'usable'

    def unusable(self):
        return self.quality() == 'unusable'

    def get_resources(self):
        return self.resources

    def get_inputs(self):
        return self.inputs


class TestSession:

    def __init__(self, scans, asrs):
        self.scans_ = [TestArtefact(s[0], s[1], s[2], s[3], {}) for s in scans]
        self.assessors_ = [TestArtefact(a[0], a[1], a[2], a[3], a[4]) for a in asrs]

    def scans(self):
        return self.scans_

    def assessors(self):
        return self.assessors_


proj = 'proj1'
subj = 'subj1'
sess = 'sess1'

scan_files = [('SNAPSHOTS', 2), ('NIFTI', 1)]

xnat_scan_contents = [
    ("1", "T1W", "usable", copy.deepcopy(scan_files)),
    ("2", "T1w", "unusable", copy.deepcopy(scan_files)),
    ("3", "T1", "usable", copy.deepcopy(scan_files)),
    ("4", "T1", "usable", copy.deepcopy(scan_files)),
    ("10", "FLAIR", "usable", copy.deepcopy(scan_files)),
    ("11", "FLAIR", "usable", copy.deepcopy(scan_files)),
]


asr_prefix = '-x-'.join((proj, subj, sess, ''))

asr_files = [
    ('LABELS', 1), ('PDF', 1), ('BIAS_COR', 1), ('PRIOR', 1), ('SEG', 1),
    ('STATS', 1), ('SNAPSHOTS', 2), ('OUTLOG', 1), ('PBS', 1)
]

scan_path = 'xnat:/project/{}/subject/{}/experiment/{}/scan/{}'
assessor_path = 'xnat:/project/{}/subject/{}/experiment/{}/assessor/{}'
scan_path_r = scan_path + '/resource/{}'
assessor_path_r = assessor_path + '/resource/{}'

# xnat_assessor_inputs = {
#     'proc1-asr1': {
#         't1': scan_path_r.format(proj, subj, sess, '1', 'NIFTI')
#     },
#     'proc1-asr2': {
#         't1': scan_path_r.format(proj, subj, sess, '2', 'NIFTI')
#     },
#     'proc2-asr1': {
#         't1': scan_path_r.format(proj, subj, sess, '1', 'NIFTI'),
#         'fl': scan_path_r.format(proj, subj, sess, '11', 'NIFTI'),
#         'seg': assessor_path_r.format(proj, subj, sess, 'proc1-asr1', 'SEG')
#     }
# }
xnat_assessor_inputs = {
    'proc1-asr1': {'scan1': scan_path.format(proj, subj, sess, '1')},
    'proc1-asr2': {'scan1': scan_path.format(proj, subj, sess, '2')},
    'proc2-asr1': {
        'scan1': scan_path.format(proj, subj, sess, '1'),
        'scan2': scan_path.format(proj, subj, sess, '11'),
        'asr1': assessor_path.format(proj, subj, sess, 'proc1-asr1')
    }
}

xnat_assessor_contents = [
    ("proc1-asr1", "proc1", "usable", copy.deepcopy(asr_files), xnat_assessor_inputs['proc1-asr1']),
    ("proc1-asr2", "proc1", "usable", copy.deepcopy(asr_files), xnat_assessor_inputs['proc1-asr2']),
    ("proc2-asr1", "proc2", "usable", copy.deepcopy(asr_files), xnat_assessor_inputs['proc2-asr1'])
]



scan_gif_parcellation_yaml = """
---
inputs:
  default:
    spider_path: /home/dax/Xnat-management/comic100_dax_config/pipelines/GIF_parcellation/v3.0.0/Spider_GIF_Parcellation_v3_0_0.py
    working_dir: /scratch0/dax/
    nipype_exe: perform_gif_propagation.py
    db: /share/apps/cmic/GIF/db/db.xml
  xnat:
    scans:
      - scan1:
        types: T1w,MPRAGE,T1,T1W
        needs_qc: True
        resources:
          - resource: NIFTI
            varname: t1
      - scan2:
        types: FLAIR
        select: foreach
        resources:
          - resource: NIFTI
            varname: fl
      - scan4:
        types: X3
        select: one
      - scan5:
        types: X4
        select: some
      - scan6:
        types: X5
        select: some(3)
      - scan7:
        types: X6
        select: all
    assessors:
      - asr1:
        proctypes: proc1
        select: foreach(scan1)
        resources:
          - resource: SEG
            varname: seg
command: python {spider_path} --t1 {t1} --fl {fl} --seg {seg} --dbt {db} --exe {nipype_exe}
attrs:
  suffix:
  xsitype: proc:genProcData
  walltime: 24:00:00
  memory: 3850
  ppn: 4
  env: /share/apps/cmic/NiftyPipe/v2.0/setup_v2.0.sh
  type: scan
  scan_nb: scan1
"""


class MyTestCase(TestCase):

    def test_processor_parser1(self):
        csess = TestSession(xnat_scan_contents, xnat_assessor_contents)

        doc = yaml.load((StringIO.StringIO(scan_gif_parcellation_yaml)))

        inputs, inputs_by_type, iteration_sources, iteration_map =\
            processor_parser.parse_inputs(doc)
        print "inputs =", inputs
        print "inputs_by_type =", inputs_by_type
        print "iteration_sources =", iteration_sources
        print "iteration_map =", iteration_map

        artefacts = processor_parser.parse_artefacts(csess)
        print "artefacts =", artefacts

        artefacts_by_input =\
            processor_parser.map_artefacts_to_inputs(csess,
                                                     inputs,
                                                     inputs_by_type)
        print "artefacts_by_input =", artefacts_by_input

        filtered_artefacts_by_input =\
            processor_parser.filter_artefacts_by_quality(inputs,
                                                         artefacts,
                                                         artefacts_by_input)
        print "filter_artefacts_by_input =", filtered_artefacts_by_input

        parameter_matrix =\
            processor_parser.generate_parameter_matrix(
                iteration_sources, iteration_map, filtered_artefacts_by_input)
        print "parameter_matrix =", parameter_matrix

        assessor_parameter_map =\
            processor_parser.compare_to_existing(csess, 'proc2',
                                                 parameter_matrix)

        print "assessor_parameter_map = ", assessor_parameter_map