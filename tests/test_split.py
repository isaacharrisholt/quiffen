from datetime import datetime

from quiffen.core.split import Split
from quiffen.core.category import Category


def test_create_split():
    """Test creating a split"""
    split = Split()
    assert split.amount is None
    assert split.memo is None
    assert split.category is None

    split2 = Split(amount=100, memo='Test Memo')
    assert split2.amount == 100
    assert split2.memo == 'Test Memo'
    assert split2.category is None

    split3 = Split(
        amount=100,
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    assert split3.amount == 100
    assert split3.memo == 'Test Memo'
    assert split3.category.name == 'Test Category'


def test_eq_success():
    """Test that two splits are equal"""
    split = Split(amount=100, memo='Test Memo')
    split2 = Split(amount=100, memo='Test Memo')
    assert split == split2


def test_eq_failure():
    """Test that two splits are not equal"""
    split = Split(amount=100, memo='Test Memo')
    split2 = Split(amount=100, memo='Test Memo2')
    assert split != split2


def test_str_method():
    """Test the string representation of a split"""
    split = Split(amount=100, memo='Test Memo')
    assert str(split) == '\n\tSplit:\n\t\tAmount: 100\n\t\tMemo: Test Memo'

    split2 = Split(
        amount=100,
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    assert str(split2) == (
        '\n\tSplit:\n\t\t'
        'Amount: 100\n\t\t'
        'Memo: Test Memo\n\t\t'
        'Category: Test Category'
    )


def test_to_qif():
    """Test the to_qif method"""
    split = Split(amount=100, memo='Test Memo')
    assert split.to_qif() == (
        'S\n'
        '$100\n'
        'ETest Memo\n'
    )

    test_category = Category(name='Test Category')

    split2 = Split(
        amount=100,
        memo='Test Memo',
        category=test_category,
        date=datetime(2019, 1, 1),
        cleared='True',
        check_number=123,
        percent=50,
        to_account='Test Account',
        payee_address='Test Address',
    )
    assert split2.to_qif() == (
        'STest Category\n'
        'D2019-01-01\n'
        '$100\n'
        'ETest Memo\n'
        'CTrue\n'
        'L[Test Account]\n'
        'N123\n'
        '%50%\n'
        'ATest Address\n'
    )


def test_to_dict():
    """Test the to_dict method"""
    split = Split(amount=100, memo='Test Memo')
    assert split.to_dict() == {
        'amount': 100,
        'memo': 'Test Memo',
        'category': None,
        'check_number': None,
        'cleared': None,
        'date': None,
        'percent': None,
        'to_account': None,
        'payee_address': None,
    }

    test_category = Category(name='Test Category')

    split2 = Split(
        amount=100,
        memo='Test Memo',
        category=test_category,
    )
    assert split2.to_dict() == {
        'amount': 100,
        'memo': 'Test Memo',
        'category': test_category.to_dict(),
        'check_number': None,
        'cleared': None,
        'date': None,
        'percent': None,
        'to_account': None,
        'payee_address': None,
    }


def test_to_dict_with_ignore():
    """Test the to_dict method with ignore"""
    split = Split(amount=100, memo='Test Memo')
    assert split.to_dict(ignore={'memo'}) == {
        'amount': 100,
        'category': None,
        'check_number': None,
        'cleared': None,
        'date': None,
        'percent': None,
        'to_account': None,
        'payee_address': None,
    }

    test_category = Category(name='Test Category')

    split2 = Split(
        amount=100,
        memo='Test Memo',
        category=test_category,
    )
    assert split2.to_dict(ignore={'memo', 'category'}) == {
        'amount': 100,
        'check_number': None,
        'cleared': None,
        'date': None,
        'percent': None,
        'to_account': None,
        'payee_address': None,
    }
