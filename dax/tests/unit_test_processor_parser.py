from unittest import TestCase

import copy

import io
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
        self.resources_ = None
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
        self.resources_ = [TestResource(r[0], r[1]) for r in resources]
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
        self.resources_ =\
            [TestResource(r.restype, len(r.files))
             for r in artefact['resources']]

        if artefact['category'] == 'assessor':
            self.inputs = artefact['artefacts']
        return self

    def project_id(self):
        return self.proj

    def subject_id(self):
        return self.subj

    def session_id(self):
        return self.sess

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

    def resources(self):
        return self.resources_

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


asr_prefix = '-x-'.join((proj, subj, sess, ''))

asr_files = [
    ('LABELS', 1), ('PDF', 1), ('BIAS_COR', 1), ('PRIOR', 1), ('SEG', 1),
    ('STATS', 1), ('SNAPSHOTS', 2), ('OUTLOG', 1), ('PBS', 1)
]

# unit test 1
xnat_scan_contents_1 = [
    (proj, subj, sess, "1", "T1W", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "2", "T1w", "unusable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "3", "T1", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "4", "T1", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "11", "FLAIR", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "12", "FLAIR", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "21", "X3", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "22", "X3", "usable", copy.deepcopy(scan_files))
]

xnat_scan_contents_t1_no_fl_no_t2 = [
    (proj, subj, sess, '1', 'T1', 'usable', copy.deepcopy(scan_files)),
    (proj, subj, sess, '2', 'T1', 'usable', copy.deepcopy(scan_files))
]

xnat_scan_contents_no_t1_fl_no_t2 = [
    (proj, subj, sess, '11', 'T2', 'usable', copy.deepcopy(scan_files)),
    (proj, subj, sess, '12', 'T2', 'usable', copy.deepcopy(scan_files))
]

xnat_assessor_inputs_1 = {
    'proc1-asr1': {'scan1': scan_path.format(proj, subj, sess, '1')},
    'proc1-asr2': {'scan1': scan_path.format(proj, subj, sess, '2')},
    'proc2-asr1': {
        'scan1': scan_path.format(proj, subj, sess, '1'),
        'scan2': scan_path.format(proj, subj, sess, '11'),
        'scan3': [
                    scan_path.format(proj, subj, sess, '21'),
                    scan_path.format(proj, subj, sess, '22')
        ],
        'scan4': None,
        'asr1': assessor_path.format(proj, subj, sess, 'proc1-asr1')
    }
}

xnat_assessor_contents_1 = [
    (proj, subj, sess, "proc1-asr1", "proc1", "usable",
     copy.deepcopy(asr_files), xnat_assessor_inputs_1['proc1-asr1']),
    (proj, subj, sess, "proc1-asr2", "proc1", "usable",
     copy.deepcopy(asr_files), xnat_assessor_inputs_1['proc1-asr2']),
    (proj, subj, sess, "proc2-asr1", "proc2", "usable",
     copy.deepcopy(asr_files), xnat_assessor_inputs_1['proc2-asr1'])
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
      - name: scan1
        types: T1w,MPRAGE,T1,T1W
        needs_qc: True
        resources:
          - resource: NIFTI
            varname: t1
      - name: scan2
        types: FLAIR
        select: foreach
        resources:
          - resource: NIFTI
            varname: fl
      - name: scan3
        types: X3
        select: all
      - name: scan4
        types: X4
        select: one
    assessors:
      - name: asr1
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

# unit test 2

xnat_scan_contents_2 = [
    (proj, subj, sess, "1", "T1", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "2", "T1", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "11", "FLAIR", "usable", copy.deepcopy(scan_files)),
    (proj, subj, sess, "12", "FLAIR", "usable", copy.deepcopy(scan_files))
]

xnat_assessor_inputs_2 = {
    'proc1-asr1': {
        'scan1': scan_path.format(proj, subj, sess, '1'),
        'scan2': scan_path.format(proj, subj, sess, '11')
    },
    'proc1-asr2': {
        'scan1': scan_path.format(proj, subj, sess, '2'),
        'scan2': scan_path.format(proj, subj, sess, '12')
    }
}

xnat_assessor_contents_2 = [
    (proj, subj, sess, "proc1-asr1", "proc1", "usable",
     copy.deepcopy(asr_files), xnat_assessor_inputs_2['proc1-asr1']),
    (proj, subj, sess, "proc1-asr2", "proc1", "usable",
     copy.deepcopy(asr_files), xnat_assessor_inputs_2['proc1-asr2']),
]


processor_yaml_foreach_map = yamls.generate_yaml(
    'proc2',
    scans=[
        {
            'name': 'scanx', 'types': 'T1',
            'select': 'foreach',
            'resources': [
                {'type': 'NIFTI', 'name': 't1'}
            ]
        },
        {
            'name': 'scany', 'types': 'FLAIR',
            'select': 'foreach(scanx)',
            'resources': [
                {'type': 'NIFTI', 'name': 'fl'}
            ]
        },
    ],
    assessors=[]
)

processor_yaml_all = yamls.generate_yaml(
    'proc2',
    scans=[
        {
            'name': 'scanx', 'types': 'T1',
            'select': 'foreach',
            'resources': [
                {'type': 'NIFTI', 'name': 't1'}
            ]
        },
        {
            'name': 'scany', 'types': 'FLAIR',
            'select': 'all',
            'resources': [
                {'type': 'NIFTI', 'name': 'fl'}
            ]
        },
    ],
    assessors=[]
)

processor_yaml_2 = yamls.generate_yaml(
    'proc2',
    scans=[
        {
            'name': 'scan_t', 'types': 'T1',
            'select': 'from(asr1/scan1)',
            'resources': [
                {'type': 'NIFTI', 'name': 't1'}
            ]
        },
        {
            'name': 'scan_f', 'types': 'FLAIR',
            'select': 'from(asr1/scan2)',
            'resources': [
                {'type': 'NIFTI', 'name': 'fl'}
            ]
        }
    ],
    assessors=[{
        'name': 'asr1', 'types': 'proc1',
        'resources': [
            {'type': 'SEG', 'name': 'seg'}
        ]
    }]
)

processor_yaml_from_two_assessors = yamls.generate_yaml(
    'proc3',
    scans=[
        {
            'name': 'scan_t1', 'types': 'T1',
            'select': 'from(asr2/scan1)',
            'resources': [
                {'type': 'NIFTI', 'name': 't1'}
            ]
        },
        {
            'name': 'scan_f', 'types': 'FLAIR',
            'select': 'from(asr2/scan2)',
            'resources': [
                {'type': 'NIFTI', 'name': 'fl'}
            ]
        },
        {
            'name': 'scan_t2', 'types': 'T2',
            'select': 'from(asr1/scan1)',
            'resources': [
                {'type': 'NIFTI', 'name': 't2'}
            ]
        }
    ],
    assessors=[
        {
            'name': 'asr1', 'types': 'proc1',
            'resources': [
                {'type': 'SEG', 'name': 'seg1'}
            ]
        },
        {
            'name': 'asr2', 'types': 'proc2',
            'resources': [
                {'type': 'SEG', 'name': 'seg2'}
            ]
        }
    ]
)


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

    def __generate_scans(self, proj, subj, sess, scan_descriptors):
        contents = list()
        for s, d in scan_descriptors:
            contents.append(
                (proj, subj, sess, s, d, "usable", copy.deepcopy(scan_files))
            )
        return contents



    def __run_processor_parser_unit_tests(self,
                                          scan_contents,
                                          assessor_contents,
                                          processor_yaml,
                                          expected=None):

        csess = [TestSession().OldInit(proj, subj, sess, scan_contents,
                                      assessor_contents)]

        doc = yaml.load((io.StringIO(processor_yaml)))

        inputs, inputs_by_type, iteration_sources, iteration_map,\
            prior_session_count =\
            ProcessorParser.parse_inputs(doc)

        print(("inputs =", inputs))
        print(("inputs_by_type =", inputs_by_type))
        print(("iteration_sources =", iteration_sources))
        print(("iteration_map =", iteration_map))
        print(("prior_session_count =", prior_session_count))

        artefacts = ProcessorParser.parse_artefacts(csess)
        print(("artefacts =", artefacts))

        artefacts_by_input = \
            ProcessorParser.map_artefacts_to_inputs(csess, inputs, inputs_by_type)
        print(("artefacts_by_input =", artefacts_by_input))

        # variables_to_inputs = \
        #     ProcessorParser.parse_variables(inputs)
        # print "variables_to_inputs =", variables_to_inputs

        parameter_matrix = \
            ProcessorParser.generate_parameter_matrix(
                inputs, iteration_sources, iteration_map,
                artefacts, artefacts_by_input)
        print(("parameter_matrix =", parameter_matrix))

        assessor_parameter_map = \
            ProcessorParser.compare_to_existing(csess,
                                                'proc2',
                                                parameter_matrix)
        print(("assessor_parameter_map = ", assessor_parameter_map))

        if expected is None:
            self.assertTrue(False, 'No expected results provided: no test validation')
        else:
            for p in parameter_matrix:
                error = 'entry {} is not in expected; parameter matrix = {}, expected = {}'
                self.assertTrue(p in expected, error.format(p, parameter_matrix, expected))

    def test_processor_parser_experimental_1(self):
        expected = [
            {'scan4': None,
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr1',
             'scan1': '/projects/proj1/subjects/subj1/experiments/sess1/scans/1',
             'scan2': '/projects/proj1/subjects/subj1/experiments/sess1/scans/11',
             'scan3': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/21',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/22']},
            {'scan4': None,
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr2',
             'scan1': '/projects/proj1/subjects/subj1/experiments/sess1/scans/1',
             'scan2': '/projects/proj1/subjects/subj1/experiments/sess1/scans/12',
             'scan3': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/21',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/22']},
            {'scan4': None,
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr1',
             'scan1': '/projects/proj1/subjects/subj1/experiments/sess1/scans/2',
             'scan2': '/projects/proj1/subjects/subj1/experiments/sess1/scans/11',
             'scan3': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/21',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/22']},
            {'scan4': None,
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr2',
             'scan1': '/projects/proj1/subjects/subj1/experiments/sess1/scans/2',
             'scan2': '/projects/proj1/subjects/subj1/experiments/sess1/scans/12',
             'scan3': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/21',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/22']},
            {'scan4': None,
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr1',
             'scan1': '/projects/proj1/subjects/subj1/experiments/sess1/scans/3',
             'scan2': '/projects/proj1/subjects/subj1/experiments/sess1/scans/11',
             'scan3': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/21',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/22']},
            {'scan4': None,
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr2',
             'scan1': '/projects/proj1/subjects/subj1/experiments/sess1/scans/3',
             'scan2': '/projects/proj1/subjects/subj1/experiments/sess1/scans/12',
             'scan3': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/21',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/22']},
            {'scan4': None,
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr1',
             'scan1': '/projects/proj1/subjects/subj1/experiments/sess1/scans/4',
             'scan2': '/projects/proj1/subjects/subj1/experiments/sess1/scans/11',
             'scan3': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/21',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/22']},
            {'scan4': None,
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr2',
             'scan1': '/projects/proj1/subjects/subj1/experiments/sess1/scans/4',
             'scan2': '/projects/proj1/subjects/subj1/experiments/sess1/scans/12',
             'scan3': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/21',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/22']}
        ]

        self.__run_processor_parser_unit_tests(xnat_scan_contents_1,
                                               xnat_assessor_contents_1,
                                               scan_gif_parcellation_yaml,
                                               expected)


    def test_processor_parser_foreach_map(self):
        expected = [
            {'scanx': '/projects/proj1/subjects/subj1/experiments/sess1/scans/3',
             'scany': '/projects/proj1/subjects/subj1/experiments/sess1/scans/11'},
            {'scanx': '/projects/proj1/subjects/subj1/experiments/sess1/scans/4',
             'scany': '/projects/proj1/subjects/subj1/experiments/sess1/scans/12'}
        ]
        self.__run_processor_parser_unit_tests(xnat_scan_contents_1,
                                               xnat_assessor_contents_1,
                                               processor_yaml_foreach_map,
                                               expected)



    def test_processor_parser_foreach_map_no_fl(self):
        expected = [
            {}
        ]
        self.__run_processor_parser_unit_tests(xnat_scan_contents_t1_no_fl_no_t2,
                                               xnat_assessor_contents_1,
                                               processor_yaml_foreach_map,
                                               expected)



    def test_processor_parser_foreach_map_no_t1(self):
        expected = [
            {}
        ]
        self.__run_processor_parser_unit_tests(xnat_scan_contents_no_t1_fl_no_t2,
                                               xnat_assessor_contents_1,
                                               processor_yaml_foreach_map,
                                               expected)



    def test_processor_parser_all(self):
        expected = [
            {'scanx': '/projects/proj1/subjects/subj1/experiments/sess1/scans/1',
             'scany': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/11',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/12']},
            {'scanx': '/projects/proj1/subjects/subj1/experiments/sess1/scans/2',
             'scany': ['/projects/proj1/subjects/subj1/experiments/sess1/scans/11',
                       '/projects/proj1/subjects/subj1/experiments/sess1/scans/12']},
        ]
        scans = [('1', 'T1'), ('2', 'T1'), ('11', 'FLAIR'), ('12', 'FLAIR')]
        self.__run_processor_parser_unit_tests(
            self.__generate_scans('proj1', 'subj1', 'sess1', scans),
            [],
            processor_yaml_all,
            expected),


    def test_processor_parser_foreach_map(self):
        expected = [
            {'scanx': '/projects/proj1/subjects/subj1/experiments/sess1/scans/3',
             'scany': '/projects/proj1/subjects/subj1/experiments/sess1/scans/11'},
            {'scanx': '/projects/proj1/subjects/subj1/experiments/sess1/scans/4',
             'scany': '/projects/proj1/subjects/subj1/experiments/sess1/scans/12'}
        ]
        self.__run_processor_parser_unit_tests(xnat_scan_contents_1,
                                               xnat_assessor_contents_1,
                                               processor_yaml_foreach_map,
                                               expected)


    def test_processor_parser_experimental_2(self):
        expected = [
            {'scan_t': '/projects/proj1/subjects/subj1/experiments/sess1/scans/1',
             'scan_f': '/projects/proj1/subjects/subj1/experiments/sess1/scans/11',
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr1'},
            {'scan_t': '/projects/proj1/subjects/subj1/experiments/sess1/scans/2',
             'scan_f': '/projects/proj1/subjects/subj1/experiments/sess1/scans/12',
             'asr1': '/projects/proj1/subjects/subj1/experiments/sess1/assessors/proc1-asr2'}
        ]
        self.__run_processor_parser_unit_tests(xnat_scan_contents_2,
                                               xnat_assessor_contents_2,
                                               processor_yaml_2,
                                               expected)


    @staticmethod
    def __generate_test_matrix(headers, values):
        table_values = itertools.product(*values)
        table = [dict(zip(headers, r)) for r in table_values]
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
                    'select-session': input['select-session'],
                    'qc': input['needs_qc'],
                    'resources': resources
                })
            if input['category'] == 'assessor':
                assessors.append({
                    'name': input['label'],
                    'types': input['type'],
                    'select': input['select'],
                    'select-session': input['select-session'],
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
        artefact_matrix = [[i] for i in artefact_matrix]

        yaml_headers = ['category', 'label', 'type', 'select', 'select-session',
                        'needs_qc', 'resources']
        yaml_categories = ['scan']
        yaml_labels = ['scan1']
        yaml_type = ['T1']
        yaml_select = [None, 'foreach']
        yaml_select_session = [None, 'current', 'prior(1)']
        yaml_needs_qc = [None, False, True]
        yaml_resources = [[YamlVariable('NIFTI', 't1', None)],
                          [YamlVariable('NIFTI', 't1', False)],
                          [YamlVariable('NIFTI', 't1', True)]]
        yaml_elems = [yaml_categories, yaml_labels, yaml_type, yaml_select,
                      yaml_select_session, yaml_needs_qc, yaml_resources]
        yaml_matrix = ProcessorParserUnitTests.__generate_test_matrix(
            yaml_headers, yaml_elems
        )
        yaml_matrix = [[i] for i in yaml_matrix]

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
            csess = TestSession().NewInit('proj1',
                                          'subj1',
                                          'sess1',
                                          m['artefacts'])


            yaml_source = ProcessorParserUnitTests.__generate_yaml(m)
            try:
                parser = ProcessorParser(yaml_source.contents)
                parser.parse_session(csess)
                print((m, '->', parser.assessor_parameter_map))
            except ValueError as err:
                if err.message not in\
                    ['yaml processor is missing xnat keyword contents']:
                    raise
        print(('scenario count = ', len(matrix)))

    def test_check_valid_mode(self):
        input_category = 'scan'
        input_name = 'a_scan'
        keyword = 'select'
        valid_keywords = ['all', 'some']

        errors = ProcessorParser._check_valid_mode(
            input_category, input_name, keyword, valid_keywords,
            {'select': 'all'})
        self.assertEqual(errors, [])

        errors = ProcessorParser._check_valid_mode(
            input_category, input_name, keyword, valid_keywords,
            {'select': 'some'})
        self.assertEqual(errors, [])

        errors = ProcessorParser._check_valid_mode(
            input_category, input_name, keyword, valid_keywords,
            {'select': 'fish'})
        expected =\
            [("Error: scan 'a_scan': 'select' has an invalid value 'fish'. "
              "It must be one of 'all', 'some'")]
        self.assertEqual(errors, expected)

