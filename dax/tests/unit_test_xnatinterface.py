
from unittest import TestCase


from dax import XnatUtils


class InterfaceTempUnitTests(TestCase):

    def unit_test_connection_strings(self):
        #positive tests
        self.assertEqual(
            XnatUtils.InterfaceTemp.P_XPATH.format(project='proj1'),
            '/project/proj1'
        )

        self.assertEqual(
            XnatUtils.InterfaceTemp.S_XPATH.format(project='proj1',
                                                   subject='subj1'),
            '/project/proj1/subject/subj1'
        )

        self.assertEqual(
            XnatUtils.InterfaceTemp.E_XPATH.format(project='proj1',
                                                   subject='subj1',
                                                   session='sess1'),
            '/project/proj1/subject/subj1/experiment/sess1'
        )

        self.assertEqual(
            XnatUtils.InterfaceTemp.C_XPATH.format(project='proj1',
                                                   subject='subj1',
                                                   session='sess1',
                                                   scan='scan1'),
            '/project/proj1/subject/subj1/experiment/sess1/scan/scan1'
        )

        self.assertEqual(
            XnatUtils.InterfaceTemp.CR_XPATH.format(project='proj1',
                                                    subject='subj1',
                                                    session='sess1',
                                                    scan='scan1',
                                                    resource='res1'),
            '/project/proj1/subject/subj1/experiment/sess1'
            '/scan/scan1/resource/res1'
        )

        self.assertEqual(
            XnatUtils.InterfaceTemp.A_XPATH.format(project='proj1',
                                                   subject='subj1',
                                                   session='sess1',
                                                   assessor='assr1'),
            '/project/proj1/subject/subj1/experiment/sess1/assessor/assr1'
        )

        self.assertEqual(
            XnatUtils.InterfaceTemp.AR_XPATH.format(project='proj1',
                                                    subject='subj1',
                                                    session='sess1',
                                                    assessor='assr1',
                                                    resource='res1'),
            '/project/proj1/subject/subj1/experiment/sess1'
            '/assessor/assr1/out/resource/res1'

        )
