
from unittest import TestCase

from dax.processor_graph import ProcessorGraph
from dax import yaml_doc
from dax.tests import unit_test_common_processor_yamls as yamls
from dax.tests import unit_test_entity_common as common
from dax.processors import AutoProcessor


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
                'name': 'proc1', 'types': 'Proc_A',
                'resources': [
                    {'type': 'SEG', 'name': 'proc_a'}
                ]
            },
            {
                'name': 'proc2', 'types': 'Proc_B',
                'resources': [
                    {'type': 'SEG2', 'name': 'proc_b'}
                ]
            }
        ])
        proc_d = yamls.generate_yaml(
            procname="Proc_D",
            assessors=[
            {
                'name': 'proc1', 'types': 'Proc_C',
                'resources': [
                    {'type': 'THING', 'name': 'proc_c'}
                ]
            },
            {
                'name': 'proc2', 'types': 'Proc_B',
                'resources': [
                    {'type': 'SEG2', 'name': 'proc_b'}
                ]
            }
        ])

        return [
            ('Proc_A', yaml_doc.YamlDoc().from_string(proc_a)),
            ('Proc_B', yaml_doc.YamlDoc().from_string(proc_b)),
            ('Proc_C', yaml_doc.YamlDoc().from_string(proc_c)),
            ('Proc_D', yaml_doc.YamlDoc().from_string(proc_d))
        ]


    def test_ordered_processors(self):
        graph_description = {
            'a': [],
            'b': ['a'],
            'c': ['a'],
            'd': ['b'],
            'e': ['b', 'c'],
            'f': ['d', 'e']
        }
        actual = ProcessorGraph.order_from_inputs(graph_description)
        print actual


    def test_ordered_processors_has_cycle(self):
        graph_description = {
            'a': [],
            'b': ['a', 'e'],
            'c': ['a'],
            'd': ['b'],
            'e': ['c', 'd'],
            'f': ['d', 'e']
        }
        actual = ProcessorGraph.order_from_inputs(graph_description)
        print actual


    def test_processor_inputs_from_sources(self):

        print ProcessorGraph.processor_inputs_from_sources(
            ProcessorGraphUnitTests.__getabcdscenario()
        )


    def test_ordering_from_sources(self):
        print ProcessorGraph.order_from_inputs(
            ProcessorGraph.processor_inputs_from_sources(
                ProcessorGraphUnitTests.__getabcdscenario()
            )
        )

    def test_order_processors(self):
        yamldocs = map(lambda p: p[1],
                       ProcessorGraphUnitTests.__getabcdscenario())
        processors = map(lambda p: AutoProcessor(common.FakeXnat, p), yamldocs)
        # processors = map(lambda p: AutoProcessor(p[1]),
        #                  ProcessorGraphUnitTests.__getabcdscenario())
        print ProcessorGraph.order_processors(processors)