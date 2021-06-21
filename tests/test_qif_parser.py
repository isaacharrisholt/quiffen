from unittest import TestCase
from quiffen.core.qif_parser import QifParser


class TestQifParser(TestCase):
    def test__parse_transactions(self):
        self.fail()

    def test_to_dicts(self):
        self.fail()

    def test_to_csv(self):
        self.fail()

    def test_to_dataframe(self):
        self.fail()

    def test_properties(self):
        parser = QifParser('../test.qif')
        del parser.transactions
        print(parser.__dict__)
        print(parser.transactions[-1])
