
from unittest import TestCase

import StringIO
import yaml
import xml.etree.cElementTree as xmlet


from dax import XnatUtils
from dax.tests import unit_test_common_processor_yamls as yamls
from dax import AutoProcessor


# TODO: BenM/xnat refactor/ these sanity checks should be refactored into
# integration tests and performed on a test database that is explicitly
# setup / torn down within the scope of a test suite execution.
# Remove everything that doesn't make it into an integration test _before_
# the pull request back to vuiis/dax!

host = 'http://10.1.1.17'
proj_id = 'testproj1'
subj_id = 'subj1'
sess_id = 'sess1'
scan_id = '1'
assr_id = 'asr1'

class SanityChecks(TestCase):

    @staticmethod
    def __get_connection():
        return XnatUtils.get_interface(host=host)

    @staticmethod
    def __prep_project(intf):
        sess = intf.select_experiment(proj_id, subj_id, sess_id)
        print sess.exists()



    def test_interface_select_project(self):
        with SanityChecks.__get_connection() as intf:
            projobj = intf.select_project(proj_id)
            print(projobj)

    def test_interface_select_subject(self):
        with SanityChecks.__get_connection() as intf:
            subjobj = intf.select_subject(proj_id, subj_id)
            print(subjobj)

    def test_interface_select_session(self):
        with SanityChecks.__get_connection() as intf:
            sessobj = intf.select_experiment(proj_id, subj_id, sess_id)
            print(sessobj)

    def test_session_full_object(self):
        with SanityChecks.__get_connection() as intf:
            sessobj1 = intf.select_experiment(proj_id, subj_id, sess_id)
            sessobj2 = XnatUtils.CachedImageSession(intf, proj_id, subj_id, sess_id).full_object()
            self.assertEqual(sessobj1.label(), sessobj2.label())

    def test_scan_full_object(self):
        with SanityChecks.__get_connection() as intf:
            scanobj1 = intf.select_scan(proj_id, subj_id, sess_id, scan_id)
            csess = XnatUtils.CachedImageSession(intf, proj_id, subj_id, sess_id)
            cscan = filter(lambda x: x.label() == scan_id, csess.scans())[0]
            scanobj2 = cscan.full_object()
            self.assertEqual(scanobj1.label(), scanobj2.label())

    def test_assessor_full_object(self):
        with SanityChecks.__get_connection() as intf:
            assrobj1 = intf.select_assessor(proj_id, subj_id, sess_id, assr_id)
            csess = XnatUtils.CachedImageSession(intf, proj_id, subj_id, sess_id)
            cassr = filter(lambda x: x.label() == assr_id, csess.assessors())[0]
            assrobj2 = cassr.full_object()
            self.assertEqual(assrobj1.label(), assrobj2.label())

    def test_list_project_scans(self):
        with SanityChecks.__get_connection() as intf:
            print intf.get_project_scans(intf, proj_id)

    def test_processor_get_cmd(self):
        with SanityChecks.__get_connection() as intf:
            xnat = XnatUtils
            yaml_source = {
                'source_type': 'string',
                'source_id': 'unit test string',
                'document': yaml.load((StringIO.StringIO(yamls.scan_gif_parcellation_yaml)))
            }
            ap = AutoProcessor(xnat, yaml_source)
            assr = intf.select_assessor(proj_id, subj_id, sess_id, assr_id)
            print(ap.get_cmds(assr, 'ajobdir'))

    def test_list_project_scans(self):
        with SanityChecks.__get_connection() as intf:
            scans = intf.get_project_scans(proj_id, False)
            print(len(scans))


    def test_sanity_check_element_tree(self):
        xmltext = """
            <xnat:a xmlns:xnat="xnat">
                <xnat:out>
                    <xnat:file id='x'>
                        <nugget>Hi</nugget>
                    </xnat:file>
                    <xnat:file id='y'></xnat:file>
                </xnat:out>
                <xnat:out>
                    <xnat:file id='z'></xnat:file>
                    <xnat:file id='w'></xnat:file>
                </xnat:out>
             </xnat:a>
             """

        tree = xmlet.fromstring(xmltext)
        print tree
        print 'find "xnat:out":', tree.find('xnat:out', {'xnat':'xnat'})
        print 'find "xnat:file":', tree.find('xnat:file', {'xnat':'xnat'})
        print 'find "xnat:out->xnat:file":', tree.find('xnat:out', {'xnat':'xnat'}).find('xnat:file', {'xnat':'xnat'})
        print 'find "xnat:out/xnat:file":', tree.find('xnat:out/xnat:file', {'xnat':'xnat'})
        print 'find "xnat:out/xnat:file/nugget":', tree.find('xnat:out/xnat:file/nugget', {'xnat':'xnat'})
        print 'findall "xnat:out/xnat:file":', tree.findall('xnat:out/xnat:file', {'xnat':'xnat'})



    def test_xnat_get_cached_image_session(self):
        with XnatUtils.get_interface(host=host) as intf:

            cisess = XnatUtils.CachedImageSession(intf, proj_id, subj_id, sess_id)
            print(cisess)
            print(cisess.info())
            for ciscan in cisess.scans():
                print(ciscan.info())
                scanobj = ciscan.full_object()
                print(scanobj)
            for ciassr in cisess.assessors():
                print(ciassr.info())
                for cirsrc in ciassr.out_resources():
                    print(cirsrc.info())
                    asrinfo = ciassr.info()
                    rsrcobj = intf.select_assessor_resource(asrinfo['project_id'],
                                                            asrinfo['subject_id'],
                                                            asrinfo['session_id'],
                                                            asrinfo['assessor_label'],
                                                            cirsrc.info()['label'])
                    print(rsrcobj)
            sessobj = cisess.full_object()
            print(sessobj)



    def test_assessor_out_resources(self):
        with XnatUtils.get_interface(host=host) as intf:
            cisess = XnatUtils.CachedImageSession(intf, proj_id, subj_id, sess_id)
            for asr in cisess.assessors():
                asrobj = intf.select_assessor(proj_id, subj_id, sess_id, asr.label())
                print(asrobj.out_resources())



    def test_xnat_get_full_object(self):
        with XnatUtils.get_interface(host=host) as intf:
            intf.connect()

            print(map(lambda x: x['name'], intf.get_projects()))

            print(map(lambda x: x['label'], intf.get_subjects(proj_id)))

            subj = intf.select(XnatUtils.InterfaceTemp.S_XPATH.format(project=proj_id, subject=subj_id))
            print(subj.label())
            print(subj.parent().label())


    def test_xnat_has_inputs(self):
        with XnatUtils.get_interface(host=host) as intf:
            intf.connect()

            SanityChecks.__prep_project(intf)
