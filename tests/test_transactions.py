from decimal import Decimal
from unittest import TestCase
from datetime import datetime

from quiffen.core.transactions import Transaction, Split
from quiffen.utils import parse_date


class TestTransaction(TestCase):
    def test_equality(self):
        date_obj = parse_date('01/06/2021')
        trans1 = Transaction(date_obj, Decimal(150))
        trans2 = Transaction(date_obj, Decimal(150))
        self.assertEqual(trans1, trans2)

        date_obj1 = parse_date('01/06/2021')
        date_obj2 = parse_date('01/06/2021', False)
        trans1 = Transaction(date_obj1, Decimal(150))
        trans2 = Transaction(date_obj2, Decimal(150))
        self.assertNotEqual(trans1, trans2)

    def test_str(self):
        date_obj = parse_date('01/06/2021')
        trans = Transaction(date_obj, Decimal(150))
        print(trans)

    def test_repr(self):
        date_obj = parse_date('01/06/2021')
        trans = Transaction(date_obj, Decimal('-150.60'))
        print(repr(trans))

    def test_parse_date(self):
        date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
        self.assertEqual(date_obj, parse_date('01/06/2021'))

        date_obj = datetime.strptime('06/01/2021', '%m/%d/%Y')
        self.assertEqual(date_obj, parse_date('06/01/2021', False))

        date_obj = datetime.strptime('Jan 01 21', '%b %d %y')
        self.assertEqual(date_obj, parse_date('Jan 01 21', False))

        date_obj = datetime.strptime('01 Jan 21', '%d %b %y')
        self.assertEqual(date_obj, parse_date('01 Jan 21'))

    def test_from_list(self):
        lst = ['D01/06/2021', 'T-150.60', 'PMe', 'MMemo']
        date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
        tr, _, _ = Transaction.from_list(lst)
        self.assertEqual(tr, Transaction(date=date_obj, amount=Decimal('-150.60'), payee='Me', memo='Memo'))

    def test_from_string(self):
        string = 'D01/06/2021\nT-150.60\nPMe\nMMemo'
        date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
        tr, _, _ = Transaction.from_string(string)
        self.assertEqual(tr, Transaction(date=date_obj, amount=Decimal('-150.60'), payee='Me', memo='Memo'))

        string = 'D01/06/2021_T-150.60_PMe_MMemo'
        date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
        tr, _, _ = Transaction.from_string(string, separator='_')
        self.assertEqual(tr, Transaction(date=date_obj, amount=Decimal('-150.60'), payee='Me', memo='Memo'))

    def test_multiple_categories(self):
        lst = ['D01/06/2021', 'T-150.60', 'PMe', 'MMemo', 'LReptile', 'LLizard']
        date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
        _, categories, _ = Transaction.from_list(lst)
        self.assertEqual(categories['Reptile'].children[0].name, 'Lizard')

    def test_add_remove_split(self):
        date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
        tr = Transaction(date=date_obj, amount=Decimal(150.0), payee='Me')
        split = Split(amount=Decimal(50))
        self.assertFalse(tr.is_split)

        tr.add_split(split)
        self.assertTrue(tr.is_split)

        tr.remove_split(amount=30)
        self.assertTrue(tr.is_split)

        tr.remove_split(amount=50, date=date_obj)
        self.assertTrue(tr.is_split)

        tr.remove_split(amount=50)
        self.assertFalse(tr.is_split)
    
    def test_to_dict(self):
        date_obj = parse_date('01/06/2021')
        trans = Transaction(date_obj, Decimal(150))
        expected = {'date': date_obj, 'amount': 150}
        self.assertEqual(trans.to_dict(), expected)
