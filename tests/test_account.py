from datetime import datetime
from decimal import Decimal

import pytest

from quiffen import Account, Transaction


def test_create_account():
    """Test creating an account"""
    account = Account(name='Test Account')
    assert account.name == 'Test Account'
    assert account.account_type is None
    assert account.desc is None
    assert account.balance is None
    assert not account.transactions
    assert account.date_at_balance is None
    assert account.credit_limit is None

    account2 = Account(
        name='Test Account',
        account_type='Bank',
        desc='Test Description',
        balance=100,
    )
    assert account2.name == 'Test Account'
    assert account2.account_type == 'Bank'
    assert account2.desc == 'Test Description'
    assert account2.balance == 100
    assert not account2.transactions

    account3 = Account(
        name='Test Account',
        account_type='Bank',
        desc='Test Description',
        balance=100,
        transactions={
            'Bank': [Transaction(date=datetime(2022, 2, 1), amount=0)],
        },
    )
    assert account3.name == 'Test Account'
    assert account3.account_type == 'Bank'
    assert account3.desc == 'Test Description'
    assert account3.balance == 100
    assert account3.transactions == {
        'Bank': [Transaction(date=datetime(2022, 2, 1), amount=Decimal(0))],
    }


def test_eq_success():
    """Test comparing two accounts for equality"""
    account1 = Account(name='Test Account')
    account2 = Account(name='Test Account')
    assert account1 == account2


def test_eq_failure():
    """Test comparing two accounts for equality"""
    account1 = Account(name='Test Account')
    account2 = Account(name='Test Account 2')
    assert account1 != account2

    account3 = Account(name='Test Account', account_type='CCard')
    account4 = Account(name='Test Account', account_type='Bank')
    assert account3 != account4


def test_add_transaction():
    """Test adding a transaction to an account"""
    account = Account(name='Test Account')
    transaction = Transaction(date=datetime(2022, 2, 1), amount=0)
    account.add_transaction(transaction, header='Bank')
    assert account.transactions == {
        'Bank': [Transaction(date=datetime(2022, 2, 1), amount=Decimal(0))],
    }


def test_str_method():
    """Test the string representation of an account"""
    account = Account(
        name='Test Account',
        account_type='Bank',
        desc='Test Description',
        balance=100,
        transactions={
            'Bank': [Transaction(date=datetime(2022, 2, 1), amount=0)],
        },
    )
    assert str(account) == (
        'Account:\n\tName: Test Account\n\tDesc: Test Description\n\t'
        'Account Type: Bank\n\tBalance: 100\n\tTransactions: 1'
    )

    account.add_transaction(
        Transaction(date=datetime(2022, 2, 1), amount=0),
        header='Bank',
    )
    assert str(account) == (
        'Account:\n\tName: Test Account\n\tDesc: Test Description\n\t'
        'Account Type: Bank\n\tBalance: 100\n\tTransactions: 2'
    )

    account.add_transaction(
        Transaction(date=datetime(2022, 2, 1), amount=0),
        header='CCard',
    )
    assert str(account) == (
        'Account:\n\tName: Test Account\n\tDesc: Test Description\n\t'
        'Account Type: Bank\n\tBalance: 100\n\tTransactions: 3'
    )


def test_add_transaction_invalid_header():
    """Test adding a transaction to an account with an invalid header"""
    account = Account(name='Test Account')
    transaction = Transaction(date=datetime(2022, 2, 1), amount=0)
    with pytest.raises(ValueError):
        account.add_transaction(transaction, header='Invalid')


def test_add_transaction_no_header():
    """Test adding a transaction to an account with no header"""
    account = Account(name='Test Account')
    transaction = Transaction(date=datetime(2022, 2, 1), amount=0)
    with pytest.raises(RuntimeError):
        account.add_transaction(transaction)


def test_merge():
    """Test merging two accounts"""
    account1 = Account(
        name='Test Account',
        account_type='Bank',
        balance=100,
        transactions={
            'Bank': [Transaction(date=datetime(2022, 2, 1), amount=0)],
        },
    )
    account2 = Account(
        name='Test Account',
        account_type='Bank',
        desc='Test Description',
        balance=100,
        transactions={
            'Bank': [Transaction(date=datetime(2022, 2, 1), amount=0)],
        },
    )
    account1.merge(account2)
    assert account1.name == 'Test Account'
    assert account1.desc == 'Test Description'
    assert account1.transactions == {
        'Bank': [
            Transaction(date=datetime(2022, 2, 1), amount=Decimal(0)),
            Transaction(date=datetime(2022, 2, 1), amount=Decimal(0)),
        ],
    }


def test_to_qif():
    """Test converting an account to QIF"""
    account = Account(
        name='Test Account',
        account_type='Bank',
        desc='Test Description',
        balance=100,
        transactions={
            'Bank': [Transaction(date=datetime(2022, 2, 1), amount=0)],
        },
    )
    account_qif = account.to_qif()
    print(repr(account_qif))
    assert account_qif == (
        '!Account\nNTest Account\nDTest Description\nTBank\n$100\n'
        '^\n!Type:Bank\nD2022-02-01\nT0\n'
    )


def test_from_list_no_custom_fields():
    """Test creating an account from a list of sections with no custom fields"""
    qif_list = [
        '!This should be ignored',
        'NTest Account',
        'DTest Description',
        'TCCard',
        'L1000',
        '$100',
        '/2022-02-01',
    ]
    account = Account.from_list(qif_list)
    assert account.name == 'Test Account'
    assert account.desc == 'Test Description'
    assert account.account_type == 'CCard'
    assert account.credit_limit == 1000
    assert account.balance == 100
    assert account.date_at_balance == datetime(2022, 2, 1)
    assert not account.transactions


def test_from_list_with_custom_fields():
    """Test creating an account from a list of sections with custom fields"""
    setattr(Account, '__CUSTOM_FIELDS', [])  # Reset custom fields
    qif_list = [
        '!This should be ignored',
        'NTest Account',
        'DTest Description',
        'TCCard',
        'L1000',
        '$100',
        '/2022-02-01',
        'XCustom field 1',
        'Y9238479',
        'DT2022-01-01T00:00:00.000001',
    ]

    # Add custom fields
    Account.add_custom_field(
        line_code='X',
        attr='custom_field_1',
        field_type=str,
    )
    Account.add_custom_field(
        line_code='Y',
        attr='custom_field_2',
        field_type=Decimal,
    )
    Account.add_custom_field(
        line_code='DT',  # Test multi-character line code
        attr='custom_field_3',
        field_type=datetime,
    )

    account = Account.from_list(qif_list)
    assert account.name == 'Test Account'
    assert account.desc == 'Test Description'
    assert account.account_type == 'CCard'
    assert account.credit_limit == 1000
    assert account.balance == 100
    assert account.date_at_balance == datetime(2022, 2, 1)
    assert not account.transactions
    assert account.custom_field_1 == 'Custom field 1'
    assert account.custom_field_2 == Decimal('9238479')
    assert account.custom_field_3 == datetime(2022, 1, 1, 0, 0, 0, 1)
    setattr(Account, '__CUSTOM_FIELDS', [])  # Reset custom fields


def test_from_list_with_unknown_line_code():
    """Test creating an account from a list of QIF strings with an unknown
    line code
    """
    qif_list = [
        '!This should be ignored',
        'NTest Account',
        'DTest Description',
        'TCCard',
        'L1000',
        '$100',
        '/2022-02-01',
        'ZInvalid field',
    ]

    with pytest.raises(ValueError):
        Account.from_list(qif_list)


def test_from_string_default_separator():
    """Test creating an account from a string with the default separator"""
    qif_string = (
        '!This should be ignored\n'
        'NTest Account\n'
        'DTest Description\n'
        'TCCard\n'
        'L1000\n'
        '$100\n'
        '/2022-02-01\n'
    )
    account = Account.from_string(qif_string)
    assert account.name == 'Test Account'
    assert account.desc == 'Test Description'
    assert account.account_type == 'CCard'
    assert account.credit_limit == 1000
    assert account.balance == 100
    assert account.date_at_balance == datetime(2022, 2, 1)
    assert not account.transactions


def test_from_string_custom_separator():
    """Test creating an account from a string with a custom separator"""
    qif_string = (
        '!This should be ignored---'
        'NTest Account---'
        'DTest Description---'
        'TCCard---'
        'L1000---'
        '$100---'
        '/2022-02-01---'
    )
    account = Account.from_string(qif_string, separator='---')
    assert account.name == 'Test Account'
    assert account.desc == 'Test Description'
    assert account.account_type == 'CCard'
    assert account.credit_limit == 1000
    assert account.balance == 100
    assert account.date_at_balance == datetime(2022, 2, 1)
    assert not account.transactions


def test_to_dict():
    """Test converting an account to a dictionary"""
    account = Account(name='Test Account')
    account_dict = account.to_dict()
    assert account_dict == {
        'name': 'Test Account',
        'desc': None,
        'account_type': None,
        'credit_limit': None,
        'balance': None,
        'date_at_balance': None,
        'transactions': {},
    }


def test_to_dict_with_ignore():
    """Test converting an account to a dictionary with ignored fields"""
    account = Account(name='Test Account')
    account_dict = account.to_dict(ignore=['name', 'desc'])
    assert account_dict == {
        'account_type': None,
        'credit_limit': None,
        'balance': None,
        'date_at_balance': None,
        'transactions': {},
    }
