# pylint: disable=redefined-outer-name
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from quiffen.core.account import Account
from quiffen.core.class_type import Class
from quiffen.core.category import Category
from quiffen.core.qif import Qif
from quiffen.core.transaction import Transaction


@pytest.fixture
def qif_file():
    return Path(__file__).parent / 'test_files' / 'test.qif'


def test_add_remove_account():
    qif = Qif()
    acc = Account(name='Test Account')
    qif.add_account(acc)

    assert qif == Qif(accounts={'Test Account': Account(name='Test Account')})

    qif.remove_account('Test Account')

    assert qif == Qif()


def test_add_remove_category():
    qif = Qif()
    cat = Category(name='Test')
    cat2 = Category(name='Test2', hierarchy='Test:Test2')
    cat.add_child(cat2)

    qif.add_category(cat)
    assert qif == Qif(categories={'Test': cat})

    qif.remove_category('Test')
    assert qif == Qif(categories={'Test2': cat2})

    qif.remove_category('Test2')
    assert qif == Qif()

    cat.add_child(cat2)
    qif.add_category(cat)
    qif.remove_category(cat.name, keep_children=False)
    assert qif == Qif()


def test_add_remove_class():
    qif = Qif()
    klass = Class(name='Test')

    qif.add_class(klass)
    assert qif == Qif(classes={'Test': Class(name='Test')})

    qif.remove_class('Test')
    assert qif == Qif()


def test_from_to_qif(qif_file):
    qif = Qif.parse(qif_file)
    test_file = qif_file.parent / 'test_output.qif'
    qif.to_qif(test_file)

    qif2 = Qif.parse(test_file)
    assert qif.accounts == qif2.accounts
    assert sorted(qif.categories) == sorted(qif2.categories)
    assert qif.classes == qif2.classes


def test_to_dicts():
    qif = Qif()
    acc = Account(name='Test Account')
    qif.add_account(acc)
    date_now = datetime.now()

    tr = Transaction(date=date_now, amount=Decimal(150))
    acc.last_header = 'Bank'
    acc.add_transaction(tr)

    tr_dicts = qif.to_dicts(data='transactions')
    assert tr_dicts == [{'date': date_now, 'amount': 150}]

    acc_dicts = qif.to_dicts(data='accounts')
    assert acc_dicts == [
        {
            'name': 'Test Account',
            'transactions': {'Bank': [{'date': date_now, 'amount': 150}]},
        },
    ]
