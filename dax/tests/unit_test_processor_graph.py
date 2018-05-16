
from unittest import TestCase

from dax.processor_graph import ProcessorGraph


class ProcessorGraphUnitTests(TestCase):

    def test_ordered_processors(self):

        # graph_description = {
        #     'a': ['b', 'c'],
        #     'b': ['d', 'e'],
        #     'c': ['e'],
        #     'd': ['f'],
        #     'e': ['f'],
        #     'f': []
        # }
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
