from datetime import datetime
from decimal import Decimal

import pytest

from quiffen.core.security import Security


def test_create_security():
    """Test creating a security"""
    security = Security()
    assert security.name is None
    assert security.symbol is None
    assert security.type is None
    assert security.goal is None

    security2 = Security(name='Test Security', symbol='Test Symbol')
    assert security2.name == 'Test Security'
    assert security2.symbol == 'Test Symbol'
    assert security2.type is None
    assert security2.goal is None

    security3 = Security(
        name='Test Security',
        symbol='Test Symbol',
        type='Test Type',
        goal='Test Goal',
    )
    assert security3.name == 'Test Security'
    assert security3.symbol == 'Test Symbol'
    assert security3.type == 'Test Type'
    assert security3.goal == 'Test Goal'


def test_eq_success():
    """Test that two securities are equal"""
    security = Security(name='Test Security', symbol='Test Symbol')
    security2 = Security(name='Test Security', symbol='Test Symbol')
    assert security == security2


def test_eq_failure():
    """Test that two securities are not equal"""
    security = Security(name='Test Security', symbol='Test Symbol')
    security2 = Security(name='Test Security', symbol='Test Symbol2')
    assert security != security2


def test_str_method():
    """Test the string representation of a security"""
    security = Security(name='Test Security', symbol='Test Symbol')
    assert str(security) == (
        'Security:\n\tName: Test Security\n\tSymbol: Test Symbol'
    )

    security2 = Security(
        name='Test Security',
        symbol='Test Symbol',
        type='Test Type',
        goal='Test Goal',
    )
    assert str(security2) == (
        'Security:\n\t'
        'Name: Test Security\n\t'
        'Symbol: Test Symbol\n\t'
        'Type: Test Type\n\t'
        'Goal: Test Goal'
    )


def test_merge():
    """Test merging two securities"""
    security = Security(name='Test Security', symbol='Test Symbol')
    security2 = Security(
        name='Test Security 2',
        symbol='Test Symbol 2',
        type='Test Type',
        goal='Test Goal',
    )
    security.merge(security2)
    assert security.name == 'Test Security'
    assert security.symbol == 'Test Symbol'
    assert security.type == 'Test Type'
    assert security.goal == 'Test Goal'


def test_to_qif():
    """Test the to_qif method"""
    security = Security(name='Test Security', symbol='Test Symbol')
    assert security.to_qif() == (
        '!Type:Security\n'
        'NTest Security\n'
        'STest Symbol\n'
    )

    security2 = Security(
        name='Test Security',
        symbol='Test Symbol',
        type='Test Type',
        goal='Test Goal',
    )
    assert security2.to_qif() == (
        '!Type:Security\n'
        'NTest Security\n'
        'STest Symbol\n'
        'TTest Type\n'
        'GTest Goal\n'
    )


def test_from_list_no_custom_fields():
    """Test creating a security from a list with no custom fields"""
    qif_list = [
        'NTest Security',
        'STest Symbol',
        'TTest Type',
        'GTest Goal',
    ]
    security = Security.from_list(qif_list)
    assert security.name == 'Test Security'
    assert security.symbol == 'Test Symbol'
    assert security.type == 'Test Type'
    assert security.goal == 'Test Goal'


def test_from_list_with_custom_fields():
    """Test creating a security from a list with custom fields"""
    setattr(Security, '__CUSTOM_FIELDS', [])  # Reset custom fields
    qif_list = [
        'NTest Security',
        'STest Symbol',
        'TTest Type',
        'GTest Goal',
        'XCustom field 1',
        'Y9238479',
        'DT2022-01-01T00:00:00.000001',
    ]

    # Add custom fields
    Security.add_custom_field(
        line_code='X',
        attr='custom_field_1',
        field_type=str,
    )
    Security.add_custom_field(
        line_code='Y',
        attr='custom_field_2',
        field_type=Decimal,
    )
    Security.add_custom_field(
        line_code='DT',  # Test multi-character line code
        attr='custom_field_3',
        field_type=datetime,
    )

    security = Security.from_list(qif_list)
    assert security.name == 'Test Security'
    assert security.symbol == 'Test Symbol'
    assert security.type == 'Test Type'
    assert security.goal == 'Test Goal'
    assert security.custom_field_1 == 'Custom field 1'
    assert security.custom_field_2 == Decimal('9238479')
    assert security.custom_field_3 == datetime(2022, 1, 1, 0, 0, 0, 1)
    setattr(Security, '__CUSTOM_FIELDS', [])  # Reset custom fields


def test_from_list_with_unknown_line_code():
    """Test creating a security from a list with an unknown line code"""
    qif_list = [
        'NTest Security',
        'STest Symbol',
        'TTest Type',
        'GTest Goal',
        'ZInvalid field',
    ]

    with pytest.raises(ValueError):
        Security.from_list(qif_list)


def test_from_string_default_separator():
    """Test creating a security from a string with the default separator"""
    qif_string = (
        'NTest Security\n'
        'STest Symbol\n'
        'TTest Type\n'
        'GTest Goal\n'
    )
    security = Security.from_string(qif_string)
    assert security.name == 'Test Security'
    assert security.symbol == 'Test Symbol'
    assert security.type == 'Test Type'
    assert security.goal == 'Test Goal'


def test_from_string_custom_separator():
    """Test creating a security from a string with a custom separator"""
    qif_string = (
        'NTest Security---'
        'STest Symbol---'
        'TTest Type---'
        'GTest Goal---'
    )
    security = Security.from_string(qif_string, separator='---')
    assert security.name == 'Test Security'
    assert security.symbol == 'Test Symbol'
    assert security.type == 'Test Type'
    assert security.goal == 'Test Goal'


def test_to_dict():
    """Test the to_dict method"""
    security = Security(
        name='Test Security',
        symbol='Test Symbol',
        type='Test Type',
        goal='Test Goal',
    )
    assert security.to_dict() == {
        'name': 'Test Security',
        'symbol': 'Test Symbol',
        'type': 'Test Type',
        'goal': 'Test Goal',
        'line_number': None,
    }


def test_to_dict_with_ignore():
    """Test the to_dict method with ignored attributes"""
    security = Security(
        name='Test Security',
        symbol='Test Symbol',
        type='Test Type',
        goal='Test Goal',
    )
    assert security.to_dict(ignore=['type', 'line_number']) == {
        'name': 'Test Security',
        'symbol': 'Test Symbol',
        'goal': 'Test Goal',
    }
