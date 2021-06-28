from datetime import datetime
from unittest import TestCase

from quiffen.core.accounts import Account
from quiffen.core.categories_classes import Category, Class
from quiffen.core.qif import Qif
from quiffen.core.transactions import Transaction


class TestQif(TestCase):

    def test_read_qif(self):
        data = Qif._read_qif('../test.qif')

        with open('../test.qif', 'r') as f:
            data2 = f.read()

        self.assertEqual(data, data2)

    def test_add_remove_account(self):
        qif = Qif()
        acc = Account(name='Test Account')
        qif.add_account(acc)

        self.assertEqual(qif, Qif(accounts={'Test Account': Account(name='Test Account')}))

        qif.remove_account('Test Account')

        self.assertEqual(qif, Qif())

    def test_add_remove_category(self):
        qif = Qif()
        cat = Category(name='Test')
        cat2 = Category(name='Test2', hierarchy='Test:Test2')
        cat.add_child(cat2)

        qif.add_category(cat)

        self.assertEqual(qif, Qif(categories={'Test': Category(name='Test')}))

        qif.remove_category('Test')
        self.assertEqual(qif, Qif(categories={'Test2': Category(name='Test2')}))

        qif.remove_category('Test2')
        self.assertEqual(qif, Qif())

        cat.add_child(cat2)
        qif.add_category(cat)
        qif.remove_category(cat.name, keep_children=False)
        self.assertEqual(qif, Qif())

    def test_add_remove_class(self):
        qif = Qif()
        klass = Class(name='Test')

        qif.add_class(klass)
        self.assertEqual(qif, Qif(classes={'Test': Class(name='Test')}))

        qif.remove_class('Test')
        self.assertEqual(qif, Qif())

    def test_from_to_qif(self):
        qif = Qif.parse('../test.qif')
        qif.to_qif('../test2.qif')

        qif2 = Qif.parse('../test2.qif')
        self.assertEqual(qif, qif2)

    def test_to_dicts(self):
        qif = Qif()
        acc = Account(name='Test Account')
        qif.add_account(acc)
        date_now = datetime.now()

        tr = Transaction(date=date_now, amount=150)
        acc.last_header = 'Bank'
        acc.add_transaction(tr)

        tr_dicts = qif.to_dicts(data='transactions')
        self.assertEqual(tr_dicts, [{'date': date_now, 'amount': 150}])

        acc_dicts = qif.to_dicts(data='accounts')
        self.assertEqual(acc_dicts, [
            {'name': 'Test Account', 'transactions': {'Bank': [{'date': date_now, 'amount': 150}]},
             'last_header': 'Bank'}])
