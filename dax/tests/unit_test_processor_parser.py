from unittest import TestCase

import copy

import StringIO
import yaml
import itertools

from dax.processor_parser import ProcessorParser
from dax.processors import AutoProcessor
from dax.tests import unit_test_entity_common as common
from dax import yaml_doc


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


sess_path = '/project/{}/subject/{}/experiment/{}'
scan_path = '/project/{}/subject/{}/experiment/{}/scan/{}'
assessor_path = '/project/{}/subject/{}/experiment/{}/assessor/{}'
scan_path_r = scan_path + '/resource/{}'
assessor_path_r = assessor_path + '/out/resource/{}'

class TestResource:

    def __init__(self, label, file_count):
        self.label_ = label
        self.file_count_ = file_count

    def label(self):
        return self.label_

    def file_count(self):
        return self.file_count_


class TestArtefact:

    def __init__(
            self, test_obj_type, proj, subj, sess, label, artefact_type,
            quality, resources, inputs = None):
        self.test_obj_type = test_obj_type
        self.proj = proj
        self.subj = subj
        self.sess = sess
        self.label_ = label
        self.artefact_type = artefact_type
        self.quality_ = quality
        self.resources = [TestResource(r[0], r[1]) for r in resources]
        self.inputs = inputs

    def label(self):
        return self.label_

    def full_path(self):
        if self.test_obj_type == 'scan':
            return scan_path.format(
                self.proj, self.subj, self.sess, self.label_)
        elif self.test_obj_type == 'assessor':
            return assessor_path.format(
                self.proj, self.subj, self.sess, self.label_)
        else:
            raise RuntimeError('invalid artefact type')

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


proj = 'proj1'
subj = 'subj1'
sess = 'sess1'


class TestSession:

    def __init__(self, scans, asrs):
        self.scans_ = [
            TestArtefact("scan", s[0], s[1], s[2], s[3], s[4], s[5], s[6])
            for s in scans]
        self.assessors_ = [
            TestArtefact("assessor", a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7])
            for a in asrs]

    def scans(self):
        return self.scans_

    def assessors(self):
        return self.assessors_

    def project_id(self):
        return proj

    def subject_id(self):
        return subj

    def session_id(self):
        return sess

    def full_path(self):
        sess_path.format(self.proj, self.subj, self.sess)


scan_files = [('SNAPSHOTS', 2), ('NIFTI', 1)]

xnat_scan_contents = [
    (proj, subj, sess, "1", "T1W", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "2", "T1w", "unusable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "3", "T1", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "4", "T1", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "10", "FLAIR", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "11", "FLAIR", "usable", copy.deepcopy(scan_files)),
]


asr_prefix = '-x-'.join((proj, subj, sess, ''))

asr_files = [
    ('LABELS', 1), ('PDF', 1), ('BIAS_COR', 1), ('PRIOR', 1), ('SEG', 1),
    ('STATS', 1), ('SNAPSHOTS', 2), ('OUTLOG', 1), ('PBS', 1)
]

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
    (proj, subj, sess, "proc1-asr1", "proc1", "usable", copy.deepcopy(asr_files), xnat_assessor_inputs['proc1-asr1']),
    (proj, subj, sess, "proc1-asr2", "proc1", "usable", copy.deepcopy(asr_files), xnat_assessor_inputs['proc1-asr2']),
    (proj, subj, sess, "proc2-asr1", "proc2", "usable", copy.deepcopy(asr_files), xnat_assessor_inputs['proc2-asr1'])
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

class ProcessorTest(TestCase):

    def test_new_processor(self):
        yd = yaml_doc.YamlDoc().from_string(scan_gif_parcellation_yaml)
        ap = AutoProcessor(common.FakeXnat, yd)


class MyTestCase(TestCase):

    def test_processor_parser1(self):
        csess = TestSession(xnat_scan_contents, xnat_assessor_contents)

        doc = yaml.load((StringIO.StringIO(scan_gif_parcellation_yaml)))

        inputs, inputs_by_type, iteration_sources, iteration_map =\
            ProcessorParser.parse_inputs(doc)
        print "inputs =", inputs
        print "inputs_by_type =", inputs_by_type
        print "iteration_sources =", iteration_sources
        print "iteration_map =", iteration_map

        artefacts = ProcessorParser.parse_artefacts(csess)
        print "artefacts =", artefacts

        artefacts_by_input = \
            ProcessorParser.map_artefacts_to_inputs(csess,
                                                    inputs,
                                                    inputs_by_type)
        print "artefacts_by_input =", artefacts_by_input

        variables_to_inputs = \
            ProcessorParser.parse_variables(inputs)
        print "variables_to_inputs =", variables_to_inputs

        filtered_artefacts_by_input = \
            ProcessorParser.filter_artefacts_by_quality(inputs,
                                                        artefacts,
                                                        artefacts_by_input)
        print "filter_artefacts_by_input =", filtered_artefacts_by_input

        parameter_matrix = \
            ProcessorParser.generate_parameter_matrix(
                iteration_sources, iteration_map, filtered_artefacts_by_input)
        print "parameter_matrix =", parameter_matrix

        assessor_parameter_map = \
            ProcessorParser.compare_to_existing(csess,
                                                'proc2',
                                                parameter_matrix)
        print "assessor_parameter_map = ", assessor_parameter_map

        commands = \
            ProcessorParser.generate_commands(csess,
                                              inputs,
                                              variables_to_inputs,
                                              parameter_matrix)
        print "commands = ", commands

        pp = ProcessorParser(doc)
