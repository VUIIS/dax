from unittest import TestCase

import copy

import StringIO
import yaml
import itertools

from dax.processor_parser import ProcessorParser
from dax.processors import AutoProcessor
from dax.tests import unit_test_entity_common as common
from dax.tests import unit_test_common_processor_yamls as yamls
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


sess_path = '/projects/{}/subjects/{}/experiments/{}'
scan_path = '/projects/{}/subjects/{}/experiments/{}/scans/{}'
assessor_path = '/projects/{}/subjects/{}/experiments/{}/assessors/{}'
scan_path_r = scan_path + '/resources/{}'
assessor_path_r = assessor_path + '/out/resources/{}'


class TestResource:

    def __init__(self, label, file_count):
        self.label_ = label
        self.file_count_ = file_count

    def label(self):
        return self.label_

    def file_count(self):
        return self.file_count_


class TestArtefact:

    def __init__(self):
        self.test_obj_type = None
        self.proj = None
        self.subj = None
        self.sess = None
        self.label_ = None
        self.artefact_type = None
        self.quality_ = None
        self.resources = None
        self.inputs = None

    def OldInit(self, test_obj_type, proj, subj, sess, label, artefact_type,
                quality, resources, inputs=None):
        self.test_obj_type = test_obj_type
        self.proj = proj
        self.subj = subj
        self.sess = sess
        self.label_ = label
        self.artefact_type = artefact_type
        self.quality_ = quality
        self.resources = [TestResource(r[0], r[1]) for r in resources]
        self.inputs = inputs
        return self


    def NewInit(self, proj, subj, sess, artefact):
        if artefact['category'] not in ['scan', 'assessor']:
            raise RuntimeError(
                'Artefact category must be one of scan or assessor')
        self.test_obj_type = artefact['category']
        self.proj = proj
        self.subj = subj
        self.sess = sess
        self.label_ = artefact['name']
        self.artefact_type = artefact['type']
        self.quality_ = artefact['quality']
        self.resources =\
            [TestResource(r.restype, len(r.files))
             for r in artefact['resources']]

        if artefact['category'] == 'assessor':
            self.inputs = artefact['artefacts']
        return self


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

    def __init__(self):
        self.scans_ = None
        self.assessors_ = None

    def OldInit(self, proj, subj, sess, scans, asrs):
        self.project_id_ = proj
        self.subject_id_ = subj
        self.session_id_ = sess
        self.scans_ = [
            TestArtefact().OldInit("scan", s[0], s[1], s[2], s[3], s[4], s[5], s[6])
            for s in scans]
        self.assessors_ = [
            TestArtefact().OldInit("assessor", a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7])
            for a in asrs]
        return self

    def NewInit(self, proj, subj, sess, artefacts):
        self.project_id_ = proj
        self.subject_id_ = subj
        self.session_id_ = sess
        self.scans_ = []
        self.assessors_ = []
        for a in artefacts:
            artefact = TestArtefact().NewInit(proj, subj, sess, a)
            if a['category'] == 'scan':
                self.scans_.append(artefact)
            else:
                self.assessors_.append(artefact)
        return self

    def scans(self):
        return self.scans_

    def assessors(self):
        return self.assessors_

    def project_id(self):
        return self.project_id_

    def subject_id(self):
        return self.subject_id_

    def session_id(self):
        return self.session_id_

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
    (proj, subj, sess, "21", "X3", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "22", "X3", "usable", copy.deepcopy(scan_files))
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
      - scan3:
        types: X3
        select: all
      - scan4:
        types: X4
        select: one
    assessors:
      - asr1:
        proctypes: proc1
        select: foreach(scan2)
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
  scan_nb: scan11
"""

class ArtefactResource:
    def __init__(self, restype, required, files):
        self.restype = restype
        self.required = required
        self.files = files

    def __repr__(self):
        return "{} ({}: {}, {}: {}, {}: {}".format(
            self.__class__.__name__,
            'restype', self.restype,
            'required', self.required,
            'files', self.files
        )


class YamlVariable:
    def __init__(self, restype, varname, required):
        self.restype = restype
        self.varname = varname
        self.required = required

    def __repr__(self):
        return "{} ({}: {}, {}: {}, {}: {})".format(
            self.__class__.__name__,
            'restype', self.restype,
            'varname', self.varname,
            'required', self.required
        )


class ProcessorTest(TestCase):

    def test_new_processor(self):
        yd = yaml_doc.YamlDoc().from_string(scan_gif_parcellation_yaml)
        ap = AutoProcessor(common.FakeXnat, yd)


class ProcessorParserUnitTests(TestCase):


    def test_processor_parser_experimental(self):
        print 'xnat_scan_contents =', xnat_scan_contents
        print 'xnat_assessor_contents =', xnat_assessor_contents
        csess = TestSession().OldInit(proj, subj, sess, xnat_scan_contents,
                                      xnat_assessor_contents)

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
                inputs, iteration_sources, iteration_map,
                filtered_artefacts_by_input)
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



    @staticmethod
    def __generate_test_matrix(headers, values):
        table_values = itertools.product(*values)
        table = map(lambda r: dict(itertools.izip(headers, r)), table_values)
        return table


    @staticmethod
    def __generate_yaml(entry):
        scans = []
        assessors = []
        for input in entry['yaml_inputs']:
            resources = []
            for r in input['resources']:
                resources.append({
                    'type': r.restype,
                    'name': r.varname,
                    'required': r.required
                })
            if input['category'] == 'scan':
                scans.append({
                    'name': input['label'],
                    'types': input['type'],
                    'select': input['select'],
                    'qc': input['needs_qc'],
                    'resources': resources
                })
            if input['category'] == 'assessor':
                assessors.append({
                    'name': input['label'],
                    'types': input['type'],
                    'select': input['select'],
                    'qc': input['needs_qc'],
                    'resources': resources
                })
        yaml_src = yamls.generate_yaml(scans=scans)
        return yaml_doc.YamlDoc().from_string(yaml_src)


    @staticmethod
    def __generate_one_scan_scenarios():
        artefact_headers = ['xsitype', 'category', 'name', 'quality', 'type',
                            'resources']
        artefact_xsitype = ['xnat:mrScanData']
        artefact_category = ['scan']
        artefact_name = ['1']
        artefact_quality = ['unusable', 'usable', 'preferred']
        artefact_type = ['T1', 'T2']
        artefact_resources = [
            [],
            [ArtefactResource('NIFTI', None, ['images.nii'])],
            [ArtefactResource('NIFTI', False, ['images.nii'])],
            [ArtefactResource('NIFTI', True, ['images.nii'])]
            #[('NIFTI', ['images.nii']), ('SNAPSHOTS', ['snapshot.jpg.gz', 'snapshot(1).jpg.gz'])]
        ]
        artefact_values = [artefact_xsitype, artefact_category, artefact_name,
                           artefact_quality, artefact_type, artefact_resources]
        artefact_matrix = ProcessorParserUnitTests.__generate_test_matrix(
            artefact_headers, artefact_values)
        artefact_matrix = map(lambda i: [i], artefact_matrix)

        yaml_headers = ['category', 'label', 'type', 'select', 'needs_qc',
                        'resources']
        yaml_categories = ['scan']
        yaml_labels = ['scan1']
        yaml_type = ['T1']
        yaml_select = [None, 'foreach']
        yaml_needs_qc = [None, False, True]
        yaml_resources = [[YamlVariable('NIFTI', 't1', None)],
                          [YamlVariable('NIFTI', 't1', False)],
                          [YamlVariable('NIFTI', 't1', True)]]
        yaml_elems = [yaml_categories, yaml_labels, yaml_type, yaml_select,
                      yaml_needs_qc, yaml_resources]
        yaml_matrix = ProcessorParserUnitTests.__generate_test_matrix(
            yaml_headers, yaml_elems
        )
        yaml_matrix = map(lambda i: [i], yaml_matrix)

        combined_headers = ['artefacts', 'yaml_inputs']
        combined_values = [artefact_matrix, yaml_matrix]
        combined_matrix = ProcessorParserUnitTests.__generate_test_matrix(
            combined_headers, combined_values
        )

        return combined_matrix


    @staticmethod
    def __create_mocked_xnat(scenario):
        pass



    def test_one_input(self):
        matrix = ProcessorParserUnitTests.__generate_one_scan_scenarios()

        for m in matrix:
            # print 'm[artefacts] =', m['artefacts']
            # print 'm[yaml_inputs] =', m['yaml_inputs']
            csess = TestSession().NewInit('proj1',
                                          'subj1',
                                          'sess1',
                                          m['artefacts'])


            yaml_source = ProcessorParserUnitTests.__generate_yaml(m)
            try:
                parser = ProcessorParser(yaml_source.contents)
                parser.parse_session(csess)
                print parser.assessor_parameter_map
            except ValueError as err:
                if err.message not in\
                    ['yaml processor is missing xnat keyword contents']:
                    raise
        print 'scenario count = ', len(matrix)