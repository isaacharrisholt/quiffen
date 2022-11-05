from datetime import datetime
from decimal import Decimal

from quiffen.core.investment import Investment


def test_create_investment():
    """Test creating an investment"""
    date = datetime(2022, 1, 1)
    investment = Investment(date=date)
    assert investment.action is None
    assert investment.security is None
    assert investment.price is None
    assert investment.memo is None
    assert investment.commission is None

    investment2 = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=10,
    )
    assert investment2.action == 'Buy'
    assert investment2.security == 'Test Security'
    assert investment2.price == 100
    assert investment2.memo == 'Test Memo'
    assert investment2.commission == 10


def test_eq_success():
    """Test that two investments are equal"""
    date = datetime(2022, 1, 1)
    investment = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=10,
    )
    investment2 = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=10,
    )
    assert investment == investment2


def test_eq_failure():
    """Test that two investments are not equal"""
    date = datetime(2022, 1, 1)
    investment = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=10,
    )
    investment2 = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=20,
    )
    assert investment != investment2


def test_str_method():
    """Test the string representation of an investment"""
    date = datetime(2022, 1, 1)
    investment = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=10,
    )
    assert str(investment) == (
        'Investment:\n\tDate: 2022-01-01 00:00:00\n\tAction: Buy\n\tSecurity: '
        'Test Security\n\tPrice: 100\n\tMemo: Test Memo\n\tCommission: 10'
    )


def test_to_qif():
    """Test the to_qif method"""
    date = datetime(2022, 1, 1)
    investment = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=10,
    )
    assert investment.to_qif() == (
        'D2022-01-01\nNBuy\nYTest Security\nI100\nMTest Memo\nO10\n'
    )


def test_to_dict():
    """Test the to_dict method"""
    date = datetime(2022, 1, 1)
    investment = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=10,
    )
    assert investment.to_dict() == {
        'date': date,
        'action': 'Buy',
        'security': 'Test Security',
        'price': Decimal('100'),
        'memo': 'Test Memo',
        'commission': Decimal('10'),
        'amount': None,
        'cleared': None,
        'first_line': None,
        'line_number': None,
        'quantity': None,
        'to_account': None,
        'transfer_amount': None,
    }


def test_to_dict_with_ignore():
    """Test the to_dict method with ignore"""
    date = datetime(2022, 1, 1)
    investment = Investment(
        date=date,
        action='Buy',
        security='Test Security',
        price=100,
        memo='Test Memo',
        commission=10,
    )
    assert investment.to_dict(ignore=['action', 'security']) == {
        'date': date,
        'price': Decimal('100'),
        'memo': 'Test Memo',
        'commission': Decimal('10'),
        'amount': None,
        'cleared': None,
        'first_line': None,
        'line_number': None,
        'quantity': None,
        'to_account': None,
        'transfer_amount': None,
    }


def test_from_list_no_custom_fields():
    """Test creating an investment from a list with no custom fields"""
    qif_list = [
        'D2022-01-01',
        'NBuy',
        'YTest Security',
        'I100',
        'MTest Memo',
        'O10',
    ]
    investment = Investment.from_list(qif_list)
    assert investment.date == datetime(2022, 1, 1)
    assert investment.action == 'Buy'
    assert investment.security == 'Test Security'
    assert investment.price == 100
    assert investment.memo == 'Test Memo'
    assert investment.commission == 10


def test_from_list_with_custom_fields():
    """Test creating an investment from a list with custom fields"""
    setattr(Investment, '__CUSTOM_FIELDS', [])  # Reset custom fields
    qif_list = [
        'D2022-01-01',
        'NBuy',
        'YTest Security',
        'I100',
        'MTest Memo',
        'O10',
        'XCustom field 1',
        'Y9238479',
        'DT2022-01-01T00:00:00.000001',
    ]

    # Add custom fields
    Investment.add_custom_field(
        line_code='X',
        attr='custom_field_1',
        field_type=str,
    )
    Investment.add_custom_field(
        line_code='Y',
        attr='custom_field_2',
        field_type=Decimal,
    )
    Investment.add_custom_field(
        line_code='DT',  # Test multi-character line code
        attr='custom_field_3',
        field_type=datetime,
    )

    investment = Investment.from_list(qif_list)
    assert investment.date == datetime(2022, 1, 1)
    assert investment.action == 'Buy'
    assert investment.security == 'Test Security'
    assert investment.price == 100
    assert investment.memo == 'Test Memo'
    assert investment.commission == 10
    assert investment.custom_field_1 == 'Custom field 1'
    assert investment.custom_field_2 == Decimal('9238479')
    assert investment.custom_field_3 == datetime(2022, 1, 1, 0, 0, 0, 1)
    setattr(Investment, '__CUSTOM_FIELDS', [])  # Reset custom fields
