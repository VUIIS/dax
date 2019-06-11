
from unittest import TestCase

import io

import yaml

from dax.processors import AutoProcessor

from dax.tests import unit_test_entity_common as common
from dax import XnatUtils
from dax import yaml_doc


class ConnectionStringUnitTest(TestCase):

    def test_a_xpath(self):
        print((XnatUtils.InterfaceTemp.A_XPATH.format(
            project='proj1', subject='subj1',
            session='sess1', assessor='assr1')))


class AutoProcessorUnitTest(TestCase):

    @staticmethod
    def _make_yaml_source(resource):
        return yaml_doc.YamlDoc().from_string(resource)

    def _construct_session(self, name):
        tpo = common.TestProjectObject(
            common.xnat_contents[name]['projects'][0]
        )
        return tpo.subjects()['subj1'].sessions()['sess1']

    def test_scan_processor_construction(self):
        yaml_source = self._make_yaml_source(
           common.processor_yamls.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

        yaml_source = self._make_yaml_source(common.git_pct_t1_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

    def test_test(self):
        print("hello world")

    def test_get_assessor_input_types(self):
        yaml_source = self._make_yaml_source(
            common.processor_yamls.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)
        print((ap.get_assessor_input_types()))

    # def test_scan_assessor_get_assessor_name(self):
    #     tseo = self._construct_session('brain_tiv_from_gif')
    #     tsco = tseo.scan_by_key('1')
    #
    #     yaml_source = self._make_yaml_source(
    #         common.processor_yamls.scan_brain_tiv_from_gif_yaml)
    #     ap = AutoProcessor(common.FakeXnat, yaml_source)
    #
    #     actual = ap.get_assessor_name(tsco)
    #     self.assertEquals(actual,
    #                       "proj1-x-subj1-x-sess1-x-1-x-BrainTivFromGIF_v1")

    # def test_scan_assessor_get_assessor(self):
    #     tseo = self._construct_session('brain_tiv_from_gif')
    #     tsco = tseo.scan_by_key('1')
    #
    #     yaml_source = self._make_yaml_source(
    #         common.processor_yamls.scan_brain_tiv_from_gif_yaml)
    #     ap = AutoProcessor(common.FakeXnat, yaml_source)
    #
    #     actual, name = ap.get_assessor(tsco)
    #     self.assertEquals(name,
    #                       "proj1-x-subj1-x-sess1-x-1-x-BrainTivFromGIF_v1")

    def test_scan_assessor_should_run(self):
        tseo = self._construct_session('brain_tiv_from_gif')
        tsco = tseo.scan_by_key('1')

        yaml_source = self._make_yaml_source(
            common.processor_yamls.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

        ret = ap.should_run(tseo.info())
        self.assertEqual(ret, 1)

    # TODO: BenM/asr_of_asr/this method needs to run off pyxnat assessor
    # objects, so create a mocked pyxnat assessor for this (and other) tests
    def test_scan_assessor_has_inputs(self):
        tseo = self._construct_session('brain_tiv_from_gif')
        tsco = tseo.scan_by_key('1')

        yaml_source = self._make_yaml_source(
            common.processor_yamls.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

        ret, comment = ap.has_inputs(tsco)
        self.assertEqual(ret, 1)

    def test_scan_assessor_build_cmds(self):
        tseo = self._construct_session('brain_tiv_from_gif')
        tsco = tseo.assessor_by_key('proc1')

        yaml_source = self._make_yaml_source(
            common.processor_yamls.scan_brain_tiv_from_gif_yaml)
        ap = AutoProcessor(common.FakeXnat, yaml_source)

        tsao = tseo.assessors()
        print(tsao)
        # TODO:BenM/assessor_of_assessor/we are passing an interface object
        # rather than a cached object. Fix and then re-enable
        cmds = ap.get_cmds(tsco, '/testdir')
        print(("cmds =", cmds))
