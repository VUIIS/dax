from unittest import TestCase

from dax import XnatUtils

from dax.tests import unit_test_entity_common as common


class XnatUtilsUnitTest(TestCase):

    def test_get_proctype(self):
        proctype, version = XnatUtils.get_proctype(common.spider_tiv_from_gif)
        self.assertEqual(proctype, 'BrainTivFromGIF_v1')
        self.assertEqual(version, '1.0.0')
