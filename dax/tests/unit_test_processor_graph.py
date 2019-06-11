
from unittest import TestCase

from dax.processor_graph import ProcessorGraph
from dax import yaml_doc
from dax.tests import unit_test_common_processor_yamls as yamls
from dax.tests import unit_test_entity_common as common
from dax.processors import AutoProcessor


class TestLog:
    def __init__(self):
        self.warnings = list()

    def warning(self, message):
        self.warnings.append(message)

    def clear(self):
        self.warnings = list()


class ProcessorGraphUnitTests(TestCase):

    @staticmethod
    def __getabcdscenario():
        proc_a = yamls.generate_yaml(
            procname="Proc_A",
            scans=[{
            'name': 'scan1', 'types': 'T1',
            'resources': [
                {'type': 'NIFTI', 'name': 't1'}
            ]}
        ])
        proc_b = yamls.generate_yaml(
            procname="Proc_B",
            scans=[{
            'name': 'scan1', 'types': 'T1',
            'resources': [
                {'type': 'NIFTI', 'name': 't1'}
            ]
        }
        ])
        proc_c = yamls.generate_yaml(
            procname="Proc_C",
            assessors=[
            {
                'name': 'proc1', 'types': 'Proc_A_v1',
                'resources': [
                    {'type': 'SEG', 'name': 'proc_a'}
                ]
            },
            {
                'name': 'proc2', 'types': 'Proc_B_v1',
                'resources': [
                    {'type': 'SEG2', 'name': 'proc_b'}
                ]
            }
        ])
        proc_d = yamls.generate_yaml(
            procname="Proc_D",
            assessors=[
            {
                'name': 'proc1', 'types': 'Proc_C_v1',
                'resources': [
                    {'type': 'THING', 'name': 'proc_c'}
                ]
            },
            {
                'name': 'proc2', 'types': 'Proc_B_v1',
                'resources': [
                    {'type': 'SEG2', 'name': 'proc_b'}
                ]
            }
        ])

        return [
            ('Proc_A_v1', yaml_doc.YamlDoc().from_string(proc_a)),
            ('Proc_B_v1', yaml_doc.YamlDoc().from_string(proc_b)),
            ('Proc_C_v1', yaml_doc.YamlDoc().from_string(proc_c)),
            ('Proc_D_v1', yaml_doc.YamlDoc().from_string(proc_d))
        ]


    #def _getTestGraph1(self):



    def test_ordered_processors(self):
        log = TestLog()

        graph_description = {
            'a': [],
            'b': ['a'],
            'c': ['a'],
            'd': ['b'],
            'e': ['b', 'c'],
            'f': ['d', 'e']
        }
        actual = ProcessorGraph.order_from_inputs(graph_description, log)
        print(actual)


    def test_ordered_processors_has_cycle(self):
        log = TestLog()

        graph_description = {
            'a': [],
            'b': ['a', 'e'],
            'c': ['a'],
            'd': ['b'],
            'e': ['c', 'd'],
            'f': ['d', 'e']
        }
        actual = ProcessorGraph.order_from_inputs(graph_description, log)
        print(actual)

    def test_processor_inputs_from_sources(self):

        print((ProcessorGraph.processor_inputs_from_sources(
            ProcessorGraphUnitTests.__getabcdscenario()
        )))


    def test_ordering_from_sources(self):
        log = TestLog()
        print((ProcessorGraph.order_from_inputs(
            ProcessorGraph.processor_inputs_from_sources(
                ProcessorGraphUnitTests.__getabcdscenario()
            ),
            log
        )))

    def test_order_processors(self):
        yamldocs = [p[1] for p in ProcessorGraphUnitTests.__getabcdscenario()]
        processors = [AutoProcessor(common.FakeXnat, p) for p in yamldocs]
        log = TestLog()
        print((ProcessorGraph.order_processors(processors, log)))

    def test_order_processors_mocked(self):
        class TestProcessor:
            def __init__(self, name, inputs):
                self.name = name
                self.inputs = inputs

            def get_proctype(self):
                return self.name

            def get_assessor_input_types(self):
                return self.inputs

        log = TestLog()
        p = [
            TestProcessor('a', []),
            TestProcessor('b', []),
            TestProcessor('c', ['a', 'b']),
            TestProcessor(None, ['b']),
            TestProcessor('e', ['c', 'd']),
        ]

        actual = ProcessorGraph.order_processors(p, log)
        self.assertListEqual(
            actual, [p[0], p[1], p[2], p[4], p[3]]
        )
        self.assertListEqual(
            log.warnings,
            [
                'Unable to order all processors:',
                '  Unordered: e'
            ]
        )

        log = TestLog()
        p = [
            TestProcessor('a', []),
            TestProcessor('b', ['a', 'd']),
            TestProcessor('c', ['b']),
            TestProcessor('d', ['c']),
            TestProcessor('e', ['b'])
        ]

        actual = ProcessorGraph.order_processors(p, log)
        self.assertListEqual(
            actual,  [p[0], p[1], p[2], p[3], p[4]]
        )
        self.assertListEqual(
            log.warnings,
            [
                'Unable to order all processors:',
                '  Unordered: b, c, d, e',
                'Cyclic processor dependencies detected:',
                '  Cycle: d, c, b'
            ]
        )

        log = TestLog()
        p = [
            TestProcessor('a', []),
            TestProcessor('b', ['a', 'd']),
            TestProcessor('c', ['b']),
            TestProcessor('d', ['c']),
            TestProcessor('e', ['b', 'g']),
            TestProcessor('f', ['e']),
            TestProcessor('g', ['f']),
            TestProcessor('h', ['e'])
        ]

        actual = ProcessorGraph.order_processors(p, log)
        self.assertListEqual(
            actual,  [p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]]
        )
        self.assertListEqual(
            log.warnings,
            [
                'Unable to order all processors:',
                '  Unordered: b, c, d, e, f, g, h',
                'Cyclic processor dependencies detected:',
                '  Cycle: d, c, b',
                '  Cycle: g, f, e'
            ]
        )


    def test_tarjan(self):

        def impl(g, expected):
            actual = ProcessorGraph.tarjan(g)
            print(actual)
            self.assertListEqual(actual, expected)

        g = {
            'a': ['b', 'c'],
            'b': ['d'],
            'c': ['e'],
            'd': ['f'],
            'e': ['f'],
            'f': []
        }
        impl(g, [['f'], ['d'], ['b'], ['e'], ['c'], ['a']])

        g = {
            'a': ['b'],
            'b': ['c', 'e'],
            'c': ['d'],
            'd': ['b'],
            'e': []
        }
        impl(g, [['e'], ['d', 'c', 'b'], ['a']])

        g = {
            'a': ['b'],
            'b': ['c'],
            'c': ['a']
        }
        impl(g, [['c', 'b', 'a']])

        g = {
            'a': ['b'],
            'b': ['c', 'e'],
            'c': ['d'],
            'd': ['b'],
            'e': ['f', 'h'],
            'f': ['g'],
            'g': ['e'],
            'h': []
        }
        impl(g, [['h'], ['g', 'f', 'e'], ['d', 'c', 'b'], ['a']])
