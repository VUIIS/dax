
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

host = ''
proj_id = ''
subj_id = ''
sess_id = ''
scan_id = ''
assr_id = ''

class SanityChecks(TestCase):

    @staticmethod
    def __get_connection():
        return XnatUtils.get_interface(host=host)

    def test_interface_select_project(self):
        with SanityChecks.__get_connection() as xnat:
            projobj = xnat.select_project(proj_id)
            print(projobj)

    def test_interface_select_subject(self):
        with SanityChecks.__get_connection() as xnat:
            subjobj = xnat.select_subject(proj_id, subj_id)
            print(subjobj)

    def test_interface_select_session(self):
        with SanityChecks.__get_connection() as xnat:
            sessobj = xnat.select_experiment(proj_id, subj_id, sess_id)
            print(sessobj)

    def test_session_full_object(self):
        with SanityChecks.__get_connection() as xnat:
            sessobj1 = xnat.select_experiment(proj_id, subj_id, sess_id)
            sessobj2 = XnatUtils.CachedImageSession(xnat, proj_id, subj_id, sess_id).full_object()
            self.assertEqual(sessobj1.label(), sessobj2.label())

    def test_scan_full_object(self):
        with SanityChecks.__get_connection() as xnat:
            scanobj1 = xnat.select_scan(proj_id, subj_id, sess_id, scan_id)
            csess = XnatUtils.CachedImageSession(xnat, proj_id, subj_id, sess_id)
            cscan = filter(lambda x: x.label() == scan_id, csess.scans())[0]
            scanobj2 = cscan.full_object()
            self.assertEqual(scanobj1.label(), scanobj2.label())

    def test_assessor_full_object(self):
        with SanityChecks.__get_connection() as xnat:
            assrobj1 = xnat.select_assessor(proj_id, subj_id, sess_id, assr_id)
            csess = XnatUtils.CachedImageSession(xnat, proj_id, subj_id, sess_id)
            cassr = filter(lambda x: x.label() == assr_id, csess.assessors())[0]
            assrobj2 = cassr.full_object()
            self.assertEqual(assrobj1.label(), assrobj2.label())

    def test_list_project_scans(self):
        with SanityChecks.__get_connection() as xnat:
            print xnat.get_project_scans(xnat, proj_id)

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
            scans = intf.get_project_scans(intf, proj_id, False)
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
        with XnatUtils.get_interface(host=host) as xnat:

            cisess = XnatUtils.CachedImageSession(xnat, proj_id, subj_id, sess_id)
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
                    rsrcobj = xnat.select_assessor_resource(asrinfo['project_id'],
                                                            asrinfo['subject_id'],
                                                            asrinfo['session_id'],
                                                            asrinfo['assessor_label'],
                                                            cirsrc.info()['label'])
                    print(rsrcobj)
            sessobj = cisess.full_object()
            print(sessobj)



    # def test_compare_cached_image_scan_with_select_image(self):
    #     with XnatUtils.get_interface(host="https://nimg1946.cs.ucl.ac.uk") as xnat:
    #
    #         proj_id = '1946'
    #         subj_id = '10015124'
    #         sess_id = '10015124_01_PETMR_20151203'
    #         cisess = XnatUtils.CachedImageSession(xnat, proj_id, subj_id, sess_id)
    #         for scan in cisess.scans():
    #             print(scan.label())
    #             scanobj = xnat.select_scan(proj_id, subj_id, sess_id, scan.label())
    #             print(scanobj)
    #             print(scanobj.get())
    #             print(list(scanobj.resources()))
    #             for r in scanobj.resources():
    #                 print(r)
    #                 for f in r.files():
    #                     print(f)
    #                     print(f.size())
    #                     print(f.content())
    #                     print(f.format())
    #                     try:
    #                         print("tags=", f.tags())
    #                     except AttributeError:
    #                         pass



    def test_assessor_out_resources(self):
        with XnatUtils.get_interface(host=host) as xnat:
            cisess = XnatUtils.CachedImageSession(xnat, proj_id, subj_id, sess_id)
            for assr in cisess.assessors():
                assrobj = xnat.select_assessor(proj_id, subj_id, sess_id, assr.label())
                print(assrobj.out_resources())



    def test_xnat_get_full_object(self):
        with XnatUtils.get_interface(host=host) as xnat:
            xnat.connect()

            print(map(lambda x: x['name'], xnat.get_projects()))

            print(map(lambda x: x['label'], xnat.get_subjects(proj_id)))

            #print(map(lambda x: x, xnat.select(XnatUtils.A_XPATH.format(project='1946', subject='nimg1946_S00175', session='nimg1946_E00981'))))

            subj = xnat.select(XnatUtils.InterfaceTemp.S_XPATH.format(project=proj_id, subject=subj_id))
            print(subj.label())
            print(subj.parent().label())

            # xpath = S_XPATH.format(project=obj_dict['project'],
            #                        subject=obj_dict['ID'])
        #xpath = A_XPATH.format(project=obj_dict['project'])