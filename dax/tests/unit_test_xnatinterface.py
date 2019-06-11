
from unittest import TestCase

import itertools


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

    def test_object_type_from_path(self):
        tests = [
            ('project/p1', 'project'),
            ('project/p1/subject/s1', 'subject'),
            ('project/p1/subject/s1/experiment/e1', 'experiment'),
            ('project/p1/subject/s1/experiment/e1/scan/sc1', 'scan'),
            ('project/p1/subject/s1/experiment/e1/assessor/as1', 'assessor'),
            ('project/p1/subject/s1/experiment/e1/scan/sc1/resource/r1',
             'resource'),
            ('project/p1/subject/s1/experiment/e1/assessor/as1/in/resource/r1',
             'resource'),
            ('project/p1/subject/s1/experiment/e1/assessor/as1/out/resource/r1',
             'resource'),
        ]

        prefix = ['', 'data/', 'xnat:/', '/', '/data/']
        postfix = ['', '/']

        for prepost in itertools.product(prefix, postfix):
            for t in tests:
                instr = prepost[0] + t[0] + prepost[1]
                print(('testing ', instr))
                self.assertEqual(
                    t[1],
                    XnatUtils.InterfaceTemp.object_type_from_path(instr),
                    'unexpected object type')
