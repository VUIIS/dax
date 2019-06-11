from unittest import TestCase

import json

from dax import XnatUtils
from dax import assessor_utils

from dax.tests import unit_test_entity_common as common


class XnatUtilsUnitTest(TestCase):

    def test_get_proctype(self):
        proctype, version = XnatUtils.get_proctype(common.spider_tiv_from_gif)
        self.assertEqual(proctype, 'BrainTivFromGIF_v1')
        self.assertEqual(version, '1.0.0')

    def test_get_assessor_inputs(self):
        class TestAssessor:
            class TestAttrs:

                def __init__(self, datatype, property):
                    self.datatype = datatype
                    self.property = property

                def get(self, name):
                    if name == self.datatype + '/' + self.property:
                        return json.dumps({'a': 'b'})
                    else:
                        raise IndexError("it's an index error")

            def __init__(self, datatype, property):
                self.attrs = TestAssessor.TestAttrs(datatype, property)
                self.datatype_ = datatype

            def datatype(self):
                return self.datatype_

        assr = TestAssessor('proc:genProcData', 'inputs')
        assr2 = TestAssessor('something', 'else')
        self.assertEqual(XnatUtils.get_assessor_inputs(assr), {'a': 'b'})
        self.assertEqual(XnatUtils.get_assessor_inputs(assr2), None)

    def test_create_full_assessor_name(self):
        test_entries = [
            ['proj1', 'subj1', 'sess1', '01234567-89ab-cdef-0123-456789abcdef']
        ]

        test_names = ['-x-'.join(t) for t in test_entries]

        for t in range(len(test_entries)):
            name = assessor_utils.full_label(*test_entries[t])
            self.assertEqual(test_names[t], name)
