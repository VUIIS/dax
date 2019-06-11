from unittest import TestCase
from dax import utilities


class GroupbyToDictTest(TestCase):

    def test_find_with_pred(self):
        source = [{'a': 1, 'b': 2}, {'a': 2, 'b': 3}, {'a': 1, 'b': 4}]
        actual = utilities.find_with_pred(source, lambda x: x['a'] == 1)
        expected = {'a': 1, 'b': 2}
        self.assertDictEqual(actual, expected)

    def test_groupby_to_dict(self):
        source = [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}, {'a': 3, 'b': 1}, {'a': 4, 'b': 2}]

        actual = utilities.groupby_to_dict(source, lambda x: x['b'])
        expected = {
            1: [{'a': 1, 'b': 1}, {'a': 3, 'b': 1}],
            2: [{'a': 2, 'b': 2}, {'a': 4, 'b': 2}]
        }

        self.assertDictEqual(actual, expected)

    def test_groupby_to_dict_2(self):
        source = [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}, {'a': 3, 'b': 2}, {'a': 4, 'b': 1}]

        actual = utilities.groupby_to_dict(source, lambda x: x['b'])
        expected = {
            1: [{'a': 1, 'b': 1}, {'a': 4, 'b': 1}],
            2: [{'a': 2, 'b': 2}, {'a': 3, 'b': 2}]
        }

        self.assertDictEqual(actual, expected)

    def test_groupby_groupby_to_dict(self):
        source = [
            {'a': 1, 'b': 10, 'c': 100},
            {'a': 1, 'b': 11, 'c': 101},
            {'a': 1, 'b': 11, 'c': 102},
            {'a': 2, 'b': 12, 'c': 103},
            {'a': 1, 'b': 10, 'c': 104}
        ]
        actual = utilities.groupby_groupby_to_dict(source, lambda x: x['a'], lambda y: y['b'])
        expected = {
                1: {
                    10: [{'a': 1, 'b': 10, 'c': 100}, {'a': 1, 'b': 10, 'c': 104}],
                    11: [{'a': 1, 'b': 11, 'c': 101}, {'a': 1, 'b': 11, 'c': 102}]},
                2: {
                    12: [{'a': 2, 'b': 12, 'c': 103}]
                }
            }

        self.assertDictEqual(actual, expected)

    def test_strip_leading_and_trailing_spaces(self):
        tests = [
            ('', ''),
            (' ', ''),
            ('a', 'a'),
            (' a', 'a'),
            ('a ', 'a'),
            (' a ', 'a'),
            ('  a  ', 'a'),
            (' a , b ', 'a,b'),
        ]

        for t in tests:
            actual = utilities.strip_leading_and_trailing_spaces(t[0])
            self.assertEqual(actual, t[1])
