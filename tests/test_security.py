from unittest import TestCase
from quiffen.core.security import Security
from quiffen.core.qif import Qif

class TestSecurity(TestCase):

    # exercise the Security class

    def test_equality(self):

        S1 = Security('Test','TEST','Stock','Growth')
        S2 = Security('Test','TEST','Stock','Growth')
        S3 = Security('Test','TEST','Stock','Other')

        self.assertEqual(S1,S2)
        self.assertNotEqual(S1,S3)

    def test_str(self):
        S1 = Security('Test','TEST','Stock','Growth')
        print(S1)

    def test_repr(self):
        S1 = Security('Test','TEST','Stock','Growth')
        print(repr(S1))

    def test_from_list(self):
        lst = ['NTest','STEST','TStock','GGrowth']
        Slst = Security.from_list(lst)
        S1 = Security('Test','TEST','Stock','Growth')
        self.assertEqual(S1,Slst)

    def test_from_string(self):
        S1 = Security('Test','TEST','Stock','Growth')
        string1 = 'NTest\nSTEST\nTStock\nGGrowth'
        string2 = 'NTest_STEST_TStock_GGrowth'

        Ss1 = Security.from_string(string1)
        Ss2 = Security.from_string(string2, separator='_')

        self.assertEqual(S1,Ss1)
        self.assertEqual(Ss1,Ss2)
    
    def test_to_dict(self):
        S1 = Security('Test','TEST','Stock','Growth')
        expected = {'name': 'Test', 'symbol': 'TEST', 'type':'Stock', 'goal':'Growth'}
        self.assertEqual(S1.to_dict(), expected)

class TestQifSecurity(TestCase):
    # read in the test qif and make sure it has what we think it should have

    def test_reader(self):
        qif = Qif.parse('testqifs/example-security-list.qif')
        self.assertEqual(len(qif.securities),3)
        self.assertEqual(qif.securities['Security1'].symbol,'USD0000')
        self.assertEqual(qif.securities['Security2'].symbol,'G002864')
        self.assertEqual(qif.securities['Security3'].symbol,'M039728')
        self.assertNotEqual(qif.securities['Security3'].symbol,'M039728xxxxxxx')
        self.assertEqual(qif.securities['Security3'].goal,'Growth')
        self.assertEqual(qif.securities['Security3'].type,'Stock')
        self.assertEqual(qif.securities['Security2'].goal,'Growth')
        self.assertEqual(qif.securities['Security2'].type,'Stock')
        self.assertEqual(qif.securities['Security1'].goal,'Growth')
        self.assertEqual(qif.securities['Security1'].type,'Stock')

    def test_from_to_qif(self):
        qif = Qif.parse('testqifs/example-security-list.qif')
        qif.to_qif('testqifs/example-security-list.write.qif')

        qif2 = Qif.parse('testqifs/example-security-list.write.qif')
        self.assertEqual(qif, qif2)
        self.assertEqual(len(qif2.securities),3)

    def test_add_remove_security(self):
        qif = Qif()
        security = Security(name='Test')

        qif.add_security(security)
        self.assertEqual(qif, Qif(securities={'Test': Security(name='Test')}))

        qif.remove_security('Test')
        self.assertEqual(qif, Qif())

    def test_to_dicts(self):
        qif = Qif()
        security = Security(name="Test")
        qif.add_security(security)

        sec_dict = qif.to_dicts(data='securities')
        self.assertEqual(sec_dict,[{'name': 'Test'}])
