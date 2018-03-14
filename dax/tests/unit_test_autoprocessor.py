
from unittest import TestCase

import StringIO

import yaml

from dax.processors import AutoProcessor

from dax.tests import unit_test_entity_common as common



class AutoProcessorUnitTest(TestCase):

    def _make_yaml_source(self, resource):
        doc = yaml.load((StringIO.StringIO(resource)))
        yaml_source = {}
        yaml_source['source_type'] = 'string'
        yaml_source['source_id'] = 'unit test string'
        yaml_source['document'] = doc
        return yaml_source



    def _construct_session(self, name):
        return common.TestSessionObject(
            'proj1', 'subj1',
            common.xnat_contents[name]['projects'][0]['subjects'][0]['sessions'][0]
        )



    def test_scan_processor_construction(self):
        yaml_source = self._make_yaml_source(common.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

        yaml_source = self._make_yaml_source(common.git_pct_t1_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)



    def test_scan_assessor_get_assessor_name(self):
        tseo = self._construct_session('brain_tiv_from_gif')
        tsco = tseo['1']

        yaml_source = self._make_yaml_source(common.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

        actual = ap.get_assessor_name(tsco)
        self.assertEquals(actual, "proj1-x-subj1-x-sess1-x-1-x-BrainTivFromGIF_v1")


    def test_scan_assessor_get_assessor(self):
        tseo = self._construct_session('brain_tiv_from_gif')
        tsco = tseo['1']

        yaml_source = self._make_yaml_source(common.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

        actual = ap.get_assessor(tsco)
        self.assertEquals(actual, "proj1-x-subj1-x-sess1-x-1-x-BrainTivFromGIF_v1")



    def test_scan_assessor_has_inputs(self):
        tseo = self._construct_session('brain_tiv_from_gif')
        tsco = tseo['1']

        yaml_source = self._make_yaml_source(common.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

        ret, comment = ap.has_inputs(tsco)
        self.assertEqual(ret, 1)
