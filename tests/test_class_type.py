from datetime import datetime
from decimal import Decimal

import pytest

from quiffen import Category
from quiffen.core.class_type import Class


def test_create_class():
    """Test creating a class"""
    cls = Class(name='Test')
    assert cls.name == 'Test'
    assert cls.desc is None

    cls2 = Class(name='Test2', desc='Test Description')
    assert cls2.name == 'Test2'
    assert cls2.desc == 'Test Description'


def test_eq_success():
    """Test that two classes are equal"""
    cls = Class(name='Test')
    cls2 = Class(name='Test')
    assert cls == cls2


def test_eq_failure():
    """Test that two classes are not equal"""
    cls = Class(name='Test')
    cls2 = Class(name='Test2')
    assert cls != cls2


def test_str_method():
    """Test the string representation of a class"""
    cls = Class(name='Test')
    assert str(cls) == 'Class:\n\tName: Test\n\tCategories: 0'

    cls2 = Class(name='Test2', desc='Test Description')
    assert str(cls2) == (
        'Class:\n\t'
        'Name: Test2\n\t'
        'Description: Test Description\n\t'
        'Categories: 0'
    )


def test_to_dict():
    """Test the to_dict method"""
    cls = Class(name='Test')
    assert cls.to_dict() == {'name': 'Test', 'desc': None, 'categories': []}

    cls2 = Class(name='Test2', desc='Test Description')
    assert cls2.to_dict() == {
        'name': 'Test2',
        'desc': 'Test Description',
        'categories': [],
    }


def test_to_dict_with_ignore():
    """Test the to_dict method with ignore"""
    cls = Class(name='Test', desc='Test Description')
    assert cls.to_dict(ignore={'desc', 'categories'}) == {'name': 'Test'}


def test_add_category():
    """Test adding a category to a class"""
    cls = Class(name='Test')
    assert not cls.categories

    category = Category(name='Test Category')
    cls.add_category(category)
    assert cls.categories == [category]


def test_add_existing_category():
    """Test adding an existing category to a class"""
    cls = Class(name='Test')
    category = Category(name='Test Category')
    cls.add_category(category)
    assert cls.categories == [category]

    cls.add_category(category)
    assert cls.categories == [category]


def test_merge():
    """Test merging two classes"""
    category1 = Category(name='Category 1')
    category2 = Category(name='Category 2')
    cls = Class(name='Test', categories=[category1])
    cls2 = Class(name='Test2', desc='Test Description', categories=[category2])
    cls.merge(cls2)
    assert cls.name == 'Test'
    assert cls.desc == 'Test Description'
    assert cls.categories == [category1, category2]


def test_to_qif():
    """Test the to_qif method"""
    cls = Class(
        name='Test Class',
        desc='Test Description',
    )
    assert cls.to_qif() == '!Type:Class\nNTest Class\nDTest Description\n'


def test_from_list_no_custom_fields():
    """Test creating a class from a list of QIF strings"""
    qif_list = [
        'NTest',
        'DTest Description',
    ]
    cls = Class.from_list(qif_list)
    assert cls.name == 'Test'
    assert cls.desc == 'Test Description'


def test_from_list_with_custom_fields():
    """Test creating a class from a list of QIF strings"""
    setattr(Class, '__CUSTOM_FIELDS', [])  # Reset custom fields
    qif_list = [
        'NTest',
        'DTest Description',
        'XCustom field 1',
        'Y9238479',
        'DT2022-01-01T00:00:00.000001',
    ]

    # Add custom fields
    Class.add_custom_field(
        line_code='X',
        attr='custom_field_1',
        field_type=str,
    )
    Class.add_custom_field(
        line_code='Y',
        attr='custom_field_2',
        field_type=Decimal,
    )
    Class.add_custom_field(
        line_code='DT',  # Test multi-character line code
        attr='custom_field_3',
        field_type=datetime,
    )

    cls = Class.from_list(qif_list)
    assert cls.name == 'Test'
    assert cls.desc == 'Test Description'
    assert cls.custom_field_1 == 'Custom field 1'
    assert cls.custom_field_2 == Decimal('9238479')
    assert cls.custom_field_3 == datetime(2022, 1, 1, 0, 0, 0, 1)
    setattr(Class, '__CUSTOM_FIELDS', [])  # Reset custom fields


def test_from_list_with_unknown_line_code():
    """Test creating a class from a list of QIF strings with an unknown line
    code"""
    qif_list = [
        'NTest',
        'DTest Description',
        'ZCustom field 1',
    ]

    with pytest.raises(ValueError):
        Class.from_list(qif_list)


def test_from_string_default_separator():
    """Test creating a class from a QIF string"""
    qif_string = (
        'NTest\n'
        'DTest Description\n'
    )
    cls = Class.from_string(qif_string)
    assert cls.name == 'Test'
    assert cls.desc == 'Test Description'


def test_from_string_custom_separator():
    """Test creating a class from a QIF string with a custom separator"""
    qif_string = (
        'NTest---'
        'DTest Description---'
    )
    cls = Class.from_string(qif_string, separator='---')
    assert cls.name == 'Test'
    assert cls.desc == 'Test Description'
