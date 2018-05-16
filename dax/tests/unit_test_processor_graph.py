
from unittest import TestCase

from dax.processor_graph import ProcessorGraph
from dax import yaml_doc
from dax.tests import unit_test_common_processor_yamls as yamls


class ProcessorGraphUnitTests(TestCase):

    def test_ordered_processors(self):
        graph_description = {
            'a': [],
            'b': ['a'],
            'c': ['a'],
            'd': ['b'],
            'e': ['b', 'c'],
            'f': ['d', 'e']
        }
        actual = ProcessorGraph.ordered_processors(graph_description)
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
        actual = ProcessorGraph.ordered_processors(graph_description)
        print actual


    def test_processor_inputs_from_sources(self):
        print yamls.proc_a
        ProcessorGraph.processor_inputs_from_sources([
            ('proc',
            yaml_doc.YamlDoc().from_string(yamls.proc_a))
        ])

