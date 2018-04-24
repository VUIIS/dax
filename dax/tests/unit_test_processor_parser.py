from unittest import TestCase

import copy

import StringIO
import yaml

from dax import processor_parser


class TestResource:

    def __init__(self, label, file_count):
        self.label_ = label
        self.file_count_ = file_count

    def label(self):
        return self.label_

    def file_count(self):
        return self.file_count_


class TestArtefact:

    def __init__(self, id, artefact_type, quality, resources):
        self.id_ = id
        self.artefact_type = artefact_type
        self.quality_ = quality
        self.resources = [TestResource(r[0], r[1]) for r in resources]

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


class TestSession:

    def __init__(self, scans, asrs):
        self.scans_ = [TestArtefact(s[0], s[1], s[2], s[3]) for s in scans]
        self.assessors_ = [TestArtefact(a[0], a[1], a[2], a[3]) for a in asrs]

    def scans(self):
        return self.scans_

    def assessors(self):
        return self.assessors_


scan_files = [('SNAPSHOTS', 2), ('NIFTI', 1)]

xnat_scan_contents = [
    ("1", "T1W", "usable", copy.deepcopy(scan_files)),
    ("2", "T1w", "unusable", copy.deepcopy(scan_files)),
    ("3", "T1", "usable", copy.deepcopy(scan_files)),
    ("4", "T1", "usable", copy.deepcopy(scan_files)),
    ("10", "FLAIR", "usable", copy.deepcopy(scan_files)),
    ("11", "FLAIR", "usable", copy.deepcopy(scan_files)),
]


asr_prefix = "proj1-x-subj1-x-sess1-x-"

asr_files = [
    ('LABELS', 1), ('PDF', 1), ('BIAS_COR', 1), ('PRIOR', 1), ('SEG', 1),
    ('STATS', 1), ('SNAPSHOTS', 2), ('OUTLOG', 1), ('PBS', 1)
]

xnat_assessor_contents = [
    (asr_prefix + "1-x-proc1", "proc1", "usable", copy.deepcopy(asr_files)),
    (asr_prefix + "2-x-proc1", "proc1", "usable", copy.deepcopy(asr_files))
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
        types: X1
        select: foreach
      - scan3:
        types: FLAIR
        select: foreach(scan1)
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
          - varname: seg
command: python {spider_path} --t1 {t1} --dbt {db} --exe {nipype_exe}
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

        # status, errors = processor_parser.has_inputs(inputs,
        #                                              artefacts,
        #                                              artefacts_by_input)

        filtered_artefacts_by_input =\
            processor_parser.filter_artefacts_by_quality(inputs,
                                                         artefacts,
                                                         artefacts_by_input)
        print "filter_artefacts_by_input =", filtered_artefacts_by_input

        commands =\
            processor_parser.generate_parameter_matrix(
                iteration_sources, iteration_map, filtered_artefacts_by_input)
        print "commands =", commands
