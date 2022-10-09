from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from quiffen.core.accounts import Account
from quiffen.core.categories_classes import Category, Class
from quiffen.core.qif import Qif
from quiffen.core.transactions import Transaction


class TestParsing(TestCase):

    def test_parser_amends_01_qif(self):

        qif = Qif.parse('testqifs/parser-amends.01.qif')

        acc = qif.accounts['Quiffen Default Account']
        
        transactions = acc.transactions['Bank']

        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].date, datetime(2022,9,23))
        self.assertEqual(transactions[1].date, datetime(2022,9,8))
        self.assertEqual(transactions[0].amount,Decimal('-184.8'))
        self.assertEqual(transactions[1].amount,Decimal('-13.16'))

    def test_parser_amends_02_qif(self):

        qif = Qif.parse('testqifs/parser-amends.02.qif')

        acc = qif.accounts['Bank account']
        
        transactions = acc.transactions['Bank']

        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].date, datetime(2022,9,23))
        self.assertEqual(transactions[1].date, datetime(2022,9,8))
        self.assertEqual(transactions[0].amount,Decimal('-184.8'))
        self.assertEqual(transactions[1].amount,Decimal('-13.16'))

    def test_parser_amends_03_qif(self):

        qif = Qif.parse('testqifs/parser-amends.03.qif')

        acc = qif.accounts['Quiffen Default Account']
        
        transactions = acc.transactions['Bank']

        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].date, datetime(2022,9,23))
        self.assertEqual(transactions[1].date, datetime(2022,9,8))
        self.assertEqual(transactions[0].amount,Decimal('-184.8'))
        self.assertEqual(transactions[1].amount,Decimal('-13.16'))

