
from unittest import TestCase


from dax import XnatUtils


class InterfaceTempUnitTests(TestCase):

    def unit_test_connection_strings(self):
        #positive tests
        XnatUtils.InterfaceTemp.P_XPATH.format(project='proj1')
        XnatUtils.InterfaceTemp.S_XPATH.format(project='proj1',
                                 subject='subj1')
        XnatUtils.InterfaceTemp.E_XPATH.format(project='proj1',
                                 subject='subj1',
                                 session='sess1')
        XnatUtils.InterfaceTemp.C_XPATH.format(project='proj1',
                                 subject='subj1',
                                 session='sess1',
                                 scan='scan1')
        XnatUtils.InterfaceTemp.A_XPATH.format(project='proj1',
                                 subject='subj1',
                                 session='sess1',
                                 assessor='assr1')
        XnatUtils.InterfaceTemp.AR_XPATH.format(project='proj1',
                                  subject='subj1',
                                  session='sess1',
                                  assessor='assr1',
                                  resource='resc1')
