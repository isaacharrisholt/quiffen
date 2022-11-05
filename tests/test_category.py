# pylint: disable=redefined-outer-name,protected-access
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from quiffen.core.qif import Qif
from quiffen.core.category import (
    Category,
    CategoryType, add_categories_to_container,
    create_categories_from_hierarchy,
)


@pytest.fixture
def tree():
    """Return a tree of categories.

    Parent (root)
    └─ Child1
       └─ Grandchild1
       └─ Grandchild2
    └─ Child2
    """
    parent = Category(name='Parent')
    child1 = Category(name='Child1')
    child2 = Category(name='Child2')
    grandchild1 = Category(name='Grandchild1')
    grandchild2 = Category(name='Grandchild2')
    parent.add_child(child1)
    parent.add_child(child2)
    child1.add_child(grandchild1)
    child1.add_child(grandchild2)
    return parent, child1, child2, grandchild1, grandchild2


def test_create_category():
    """Test creating a category"""
    category = Category(name='Test')
    assert category.name == 'Test'
    assert category.parent is None
    assert not category.children
    assert category.hierarchy == 'Test'
    assert category.category_type == 'expense'


def test_eq_success():
    """Test equality"""
    category1 = Category(name='Test')
    category2 = Category(name='Test')
    assert category1 == category2

    parent1 = Category(name='Parent')
    parent2 = Category(name='Parent')
    child1 = Category(name='Child')
    child2 = child1.copy()
    parent1.add_child(child1)
    parent2.add_child(child2)
    assert parent1 == parent2


def test_eq_failure():
    """Test equality"""
    category1 = Category(name='Test1')
    category2 = Category(name='Test1', category_type='income')
    assert category1 != category2

    parent1 = Category(name='Parent')
    parent2 = Category(name='Parent')
    child = Category(name='Child')
    parent1.add_child(child)
    assert parent1 != parent2


def test_str_method():
    """Test the string method"""
    category = Category(
        name='Test',
        category_type=CategoryType.INCOME,
        desc='Test',
        children=[Category(name='Child 1'), Category(name='Child 2')],
    )
    assert str(category) == (
        'Category:\n\tName: Test\n\tDesc: Test\n\t'
        'Category Type: income\n\tHierarchy: Test\n\tChildren: 2'
    )


def test_refresh_hierarchy():
    """Test refreshing the hierarchy of a category"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    parent.add_child(child)
    child.name = 'New Name'
    parent._refresh_hierarchy()
    assert child.hierarchy == 'Parent:New Name'


def test_to_dict(tree):
    """Test converting a category to a dictionary"""
    parent, child1, child2, grandchild1, grandchild2 = tree
    assert parent.to_dict() == {
        'name': 'Parent',
        'category_type': 'expense',
        'children': ['Child1', 'Child2'],
        'hierarchy': 'Parent',
        'budget_amount': None,
        'desc': None,
        'parent': None,
        'tax_related': None,
        'tax_schedule_info': None,
    }
    assert child1.to_dict() == {
        'name': 'Child1',
        'category_type': 'expense',
        'children': ['Grandchild1', 'Grandchild2'],
        'hierarchy': 'Parent:Child1',
        'parent': 'Parent',
        'budget_amount': None,
        'desc': None,
        'tax_related': None,
        'tax_schedule_info': None,
    }
    assert child2.to_dict() == {
        'name': 'Child2',
        'category_type': 'expense',
        'children': [],
        'hierarchy': 'Parent:Child2',
        'parent': 'Parent',
        'budget_amount': None,
        'desc': None,
        'tax_related': None,
        'tax_schedule_info': None,
    }
    assert grandchild1.to_dict() == {
        'name': 'Grandchild1',
        'category_type': 'expense',
        'children': [],
        'hierarchy': 'Parent:Child1:Grandchild1',
        'parent': 'Child1',
        'budget_amount': None,
        'desc': None,
        'tax_related': None,
        'tax_schedule_info': None,
    }
    assert grandchild2.to_dict() == {
        'name': 'Grandchild2',
        'category_type': 'expense',
        'children': [],
        'hierarchy': 'Parent:Child1:Grandchild2',
        'parent': 'Child1',
        'budget_amount': None,
        'desc': None,
        'tax_related': None,
        'tax_schedule_info': None,
    }


def test_to_dict_with_ignore():
    """Test converting a category to a dictionary with ignored fields"""
    category = Category(name='Test')
    assert category.to_dict(ignore=['name']) == {
        'category_type': 'expense',
        'children': [],
        'hierarchy': 'Test',
        'budget_amount': None,
        'desc': None,
        'parent': None,
        'tax_related': None,
        'tax_schedule_info': None,
    }


def test_set_parent():
    """Test setting a parent category"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    child.set_parent(parent)
    assert child.parent == parent
    assert parent.children == [child]
    assert child.hierarchy == 'Parent:Child'


def test_set_parent_with_children():
    """Test setting a parent category that already has children"""
    parent = Category(name='Parent')
    child1 = Category(name='Child1')
    child2 = Category(name='Child2')
    child1.add_child(child2)
    child2.set_parent(parent)
    assert child1.parent is None
    assert child2.parent == parent
    assert parent.children == [child2]
    assert not child1.children
    assert not child2.children
    assert child1.hierarchy == 'Child1'
    assert child2.hierarchy == 'Parent:Child2'


def test_set_parent_to_self():
    """Test setting a category as its own parent raises a ValueError"""
    category = Category(name='Test')
    with pytest.raises(ValueError):
        category.set_parent(category)


def test_merge_single_level():
    """Test merging two categories, one level deep"""
    parent1 = Category(name='Parent')
    parent2 = Category(name='Parent')
    child1 = Category(name='Child1')
    child2 = Category(name='Child2')
    child3 = Category(name='Child3')
    parent1.add_child(child1)
    parent1.add_child(child2)
    parent2.add_child(child3)

    parent1.merge(parent2)

    assert sorted(parent1.children) == sorted([child1, child2, child3])
    assert child3.parent == parent1


def test_merge_multi_level():
    """Test merging two categories, multiple levels deep"""
    parent1 = Category(name='Parent')
    parent2 = Category(name='Parent')
    child1 = Category(name='Child1')
    child1_2 = Category(name='Child1')
    child2 = Category(name='Child2')
    grandchild1 = Category(name='Grandchild1')
    grandchild2 = Category(name='Grandchild2')
    grandchild3 = Category(name='Grandchild3')
    parent1.add_child(child1)
    parent1.add_child(child2)
    parent2.add_child(child1_2)
    parent2.add_child(child2)
    child1.add_child(grandchild1)
    child1_2.add_child(grandchild2)
    child2.add_child(grandchild3)

    parent1.merge(parent2)

    assert sorted(parent1.children) == sorted([child1, child2])
    assert sorted(child1.children) == sorted([grandchild1, grandchild2])
    assert sorted(child2.children) == sorted([grandchild3])
    assert grandchild1.parent == child1
    assert grandchild2.parent == child1
    assert grandchild3.parent == child2


def test_add_child():
    """Test adding a child category"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    parent.add_child(child)
    assert child.parent == parent
    assert parent.children == [child]
    assert child.hierarchy == 'Parent:Child'


def test_add_multiple_children():
    """Test adding multiple children to a category"""
    parent = Category(name='Parent')
    child1 = Category(name='Child1')
    child2 = Category(name='Child2')
    parent.add_child(child1)
    parent.add_child(child2)
    assert child1.parent == parent
    assert child2.parent == parent
    assert parent.children == [child1, child2]
    assert child1.hierarchy == 'Parent:Child1'
    assert child2.hierarchy == 'Parent:Child2'


def test_add_child_with_parent():
    """Test adding a child category that already has a parent"""
    parent1 = Category(name='Parent1')
    parent2 = Category(name='Parent2')
    child = Category(name='Child')
    parent1.add_child(child)
    parent2.add_child(child)
    assert child.parent == parent2
    assert not parent1.children
    assert parent2.children == [child]
    assert child.hierarchy == 'Parent2:Child'


def test_add_child_with_children():
    """Test adding a child category that already has children"""
    parent = Category(name='Parent')
    child1 = Category(name='Child1')
    child2 = Category(name='Child2')
    child3 = Category(name='Child3')
    child1.add_child(child2)
    parent.add_child(child1)
    parent.add_child(child3)
    assert child1.parent == parent
    assert child2.parent == child1
    assert child3.parent == parent
    assert parent.children == [child1, child3]
    assert child1.children == [child2]
    assert not child2.children
    assert child1.hierarchy == 'Parent:Child1'
    assert child2.hierarchy == 'Parent:Child1:Child2'
    assert child3.hierarchy == 'Parent:Child3'


def test_add_child_multiple_times():
    """Test adding a child category multiple times"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    parent.add_child(child)
    parent.add_child(child)
    assert child.parent == parent
    assert parent.children == [child]
    assert child.hierarchy == 'Parent:Child'


def test_add_child_multi_level():
    """Test adding a child to a category that has a parent"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    grandchild = Category(name='Grandchild')
    parent.add_child(child)
    child.add_child(grandchild)
    assert child.parent == parent
    assert grandchild.parent == child
    assert parent.children == [child]
    assert child.children == [grandchild]
    assert child.hierarchy == 'Parent:Child'
    assert grandchild.hierarchy == 'Parent:Child:Grandchild'


def test_add_self_as_child():
    """Test adding a category as its own child raises a ValueError"""
    category = Category(name='Test')
    with pytest.raises(ValueError):
        category.add_child(category)


def test_remove_child():
    """Test removing a child category"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    parent.add_child(child)
    parent.remove_child(child)
    assert child.parent is None
    assert not parent.children
    assert child.hierarchy == 'Child'
    assert parent.hierarchy == 'Parent'


def test_remove_child_with_children_without_keep():
    """Test removing a child category that has children"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    grandchild = Category(name='Grandchild')
    parent.add_child(child)
    child.add_child(grandchild)
    parent.remove_child(child)
    assert child.parent is None
    assert grandchild.parent == child
    assert not parent.children
    assert child.children == [grandchild]
    assert not grandchild.children
    assert child.hierarchy == 'Child'
    assert grandchild.hierarchy == 'Child:Grandchild'
    assert parent.hierarchy == 'Parent'


def test_remove_child_with_children_with_keep():
    """Test removing a child category that has children"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    grandchild = Category(name='Grandchild')
    parent.add_child(child)
    child.add_child(grandchild)
    parent.remove_child(child, keep_children=True)
    assert child.parent is None
    assert grandchild.parent == parent
    assert parent.children == [grandchild]
    assert not child.children
    assert not grandchild.children
    assert child.hierarchy == 'Child'
    assert grandchild.hierarchy == 'Parent:Grandchild'
    assert parent.hierarchy == 'Parent'


def test_remove_child_with_children_with_keep_multi_level():
    """Test removing a child category that has children"""
    parent = Category(name='Parent')
    child = Category(name='Child')
    grandchild = Category(name='Grandchild')
    great_grandchild = Category(name='GreatGrandchild')
    parent.add_child(child)
    child.add_child(grandchild)
    grandchild.add_child(great_grandchild)
    parent.remove_child(child, keep_children=True)
    assert child.parent is None
    assert grandchild.parent == parent
    assert great_grandchild.parent == grandchild
    assert parent.children == [grandchild]
    assert not child.children
    assert grandchild.children == [great_grandchild]
    assert not great_grandchild.children
    assert child.hierarchy == 'Child'
    assert grandchild.hierarchy == 'Parent:Grandchild'
    assert great_grandchild.hierarchy == 'Parent:Grandchild:GreatGrandchild'
    assert parent.hierarchy == 'Parent'


def test_render_tree(tree):
    """Test rendering a tree of categories"""
    parent, *_ = tree
    render = parent.render_tree()
    print(render)
    assert render == (
        "Parent (root)\n"
        "└─ Child1\n"
        "   └─ Grandchild1\n"
        "   └─ Grandchild2\n"
        "└─ Child2"
    )


def test_render_tree_no_tree():
    """Test rendering a tree of categories with no children"""
    root = Category(name='Parent')
    tree = root.render_tree()
    assert tree == 'Parent'


def test_traverse_down(tree):
    """Test traversing down a tree"""
    parent, child1, child2, grandchild1, grandchild2 = tree

    parent_traversal = parent.traverse_down()
    assert len(parent_traversal) == 5
    for node in (parent, child1, grandchild1, grandchild2, child2):
        assert node in parent_traversal

    child1_traversal = child1.traverse_down()
    assert len(child1_traversal) == 3
    for node in (child1, grandchild1, grandchild2):
        assert node in child1_traversal

    assert child2.traverse_down() == [child2]
    assert grandchild1.traverse_down() == [grandchild1]
    assert grandchild2.traverse_down() == [grandchild2]


def test_traverse_up(tree):
    """Test traversing up a tree"""
    parent, child1, child2, grandchild1, grandchild2 = tree

    parent_traversal = parent.traverse_up()
    assert len(parent_traversal) == 1
    assert parent in parent_traversal

    child1_traversal = child1.traverse_up()
    assert len(child1_traversal) == 2
    for node in (child1, parent):
        assert node in child1_traversal

    child2_traversal = child2.traverse_up()
    assert len(child2_traversal) == 2
    for node in (child2, parent):
        assert node in child2_traversal

    grandchild1_traversal = grandchild1.traverse_up()
    assert len(grandchild1_traversal) == 3
    for node in (grandchild1, child1, parent):
        assert node in grandchild1_traversal

    grandchild2_traversal = grandchild2.traverse_up()
    assert len(grandchild2_traversal) == 3
    for node in (grandchild2, child1, parent):
        assert node in grandchild2_traversal


def test_find_child(tree):
    """Test finding a child"""
    parent, child1, child2, grandchild1, grandchild2 = tree
    assert parent.find_child('Child1') == child1
    assert parent.find_child('Child2') == child2
    assert parent.find_child('Grandchild1') == grandchild1
    assert parent.find_child('Grandchild2') == grandchild2
    assert child1.find_child('Grandchild1') == grandchild1
    assert child1.find_child('Grandchild2') == grandchild2

    assert child2.find_child('Grandchild1') is None
    assert child2.find_child('Grandchild2') is None
    assert grandchild1.find_child('Grandchild1') is grandchild1
    assert grandchild1.find_child('Grandchild2') is None
    assert grandchild2.find_child('Grandchild1') is None
    assert grandchild2.find_child('Grandchild2') is grandchild2


def test_to_qif():
    """Test converting a category to a QIF category"""
    root = Category(name='Root')
    child = Category(name='Child')
    root.add_child(child)
    assert root.to_qif() == (  # Should show both root and child
        '!Type:Cat\nNRoot\nE\n^\n'
        '!Type:Cat\nNRoot:Child\nE\n'
    )
    assert child.to_qif() == '!Type:Cat\nNRoot:Child\nE\n'


def test_to_qif_with_custom_fields():
    """Test converting a category to a QIF category"""
    setattr(Category, '__CUSTOM_FIELDS', [])  # Reset custom fields
    root = Category(name='Root')
    child = Category(name='Child')
    root.add_child(child)

    # Add custom fields
    Category.add_custom_field(
        line_code='X',
        attr='custom_field_1',
        field_type=str,
    )
    Category.add_custom_field(
        line_code='Y',
        attr='custom_field_2',
        field_type=Decimal,
    )
    Category.add_custom_field(
        line_code='DT',  # Test multi-character line code
        attr='custom_field_3',
        field_type=datetime,
    )

    root.custom_field_1 = 'Custom field 1'
    root.custom_field_2 = Decimal('9238479')
    root.custom_field_3 = datetime(2022, 1, 1, 0, 0, 0, 1)
    child.custom_field_1 = 'Custom field 1'
    child.custom_field_2 = Decimal('9238479')
    child.custom_field_3 = datetime(2022, 1, 1, 0, 0, 0, 1)

    assert root.to_qif() == (  # Should show both root and child
        '!Type:Cat\n'
        'NRoot\n'
        'E\n'
        'DT2022-01-01 00:00:00.000001\n'
        'Y9238479\n'
        'XCustom field 1\n'
        '^\n'
        '!Type:Cat\n'
        'NRoot:Child\n'
        'E\n'
        'DT2022-01-01 00:00:00.000001\n'
        'Y9238479\n'
        'XCustom field 1\n'
    )
    assert child.to_qif() == (
        '!Type:Cat\n'
        'NRoot:Child\n'
        'E\n'
        'DT2022-01-01 00:00:00.000001\n'
        'Y9238479\n'
        'XCustom field 1\n'
    )
    setattr(Category, '__CUSTOM_FIELDS', [])  # Reset custom fields


def test_from_list_no_custom_fields():
    """Test creating a category from a list of QIF strings"""
    qif_list = [
        'NParent',
        'DSome category description',
        'E',
        'T',
        'B123.45',
        'RTax schedule info',
    ]
    category = Category.from_list(qif_list)
    assert category.name == 'Parent'
    assert category.desc == 'Some category description'
    assert category.category_type == 'expense'
    assert category.tax_schedule_info == 'Tax schedule info'
    assert category.budget_amount == Decimal('123.45')


def test_from_list_with_custom_fields():
    """Test creating a category from a list of QIF strings"""
    setattr(Category, '__CUSTOM_FIELDS', [])  # Reset custom fields
    qif_list = [
        'NParent',
        'DSome category description',
        'E',
        'T',
        'B123.45',
        'RTax schedule info',
        'XCustom field 1',
        'Y9238479',
        'DT2022-01-01T00:00:00.000001',
    ]

    # Add custom fields
    Category.add_custom_field(
        line_code='X',
        attr='custom_field_1',
        field_type=str,
    )
    Category.add_custom_field(
        line_code='Y',
        attr='custom_field_2',
        field_type=Decimal,
    )
    Category.add_custom_field(
        line_code='DT',  # Test multi-character line code
        attr='custom_field_3',
        field_type=datetime,
    )

    category = Category.from_list(qif_list)
    assert category.name == 'Parent'
    assert category.desc == 'Some category description'
    assert category.category_type == 'expense'
    assert category.tax_schedule_info == 'Tax schedule info'
    assert category.budget_amount == Decimal('123.45')
    assert category.custom_field_1 == 'Custom field 1'
    assert category.custom_field_2 == Decimal('9238479')
    assert category.custom_field_3 == datetime(2022, 1, 1, 0, 0, 0, 1)
    setattr(Category, '__CUSTOM_FIELDS', [])  # Reset custom fields


def test_from_list_with_unknown_line_code():
    """Test creating a category from a list of QIF strings with an unknown
    line code
    """
    qif_list = [
        'NParent',
        'DSome category description',
        'E',
        'T',
        'B123.45',
        'RTax schedule info',
        'ZInvalid field',
    ]

    with pytest.raises(ValueError):
        Category.from_list(qif_list)


def test_from_string_default_separator():
    """Test creating a category from a QIF string"""
    qif_string = (
        'NParent\n'
        'DSome category description\n'
        'E\n'
        'T\n'
        'B123.45\n'
        'RTax schedule info\n'
    )
    category = Category.from_string(qif_string)
    assert category.name == 'Parent'
    assert category.desc == 'Some category description'
    assert category.category_type == 'expense'
    assert category.tax_schedule_info == 'Tax schedule info'
    assert category.budget_amount == Decimal('123.45')


def test_from_string_custom_separator():
    """Test creating a category from a QIF string with a custom separator"""
    qif_string = (
        'NParent---'
        'DSome category description---'
        'E---'
        'T---'
        'B123.45---'
        'RTax schedule info---'
    )
    category = Category.from_string(qif_string, separator='---')
    assert category.name == 'Parent'
    assert category.desc == 'Some category description'
    assert category.category_type == 'expense'
    assert category.tax_schedule_info == 'Tax schedule info'
    assert category.budget_amount == Decimal('123.45')


def test_create_categories_from_hierarchy():
    """Test creating categories from a hierarchy string"""
    hierarchy = 'Parent:Child:Grandchild'
    grandchild = create_categories_from_hierarchy(hierarchy)
    assert grandchild.name == 'Grandchild'
    assert grandchild.parent.name == 'Child'
    assert grandchild.parent.parent.name == 'Parent'


def test_create_categories_from_hierarchy_single_category():
    """Test creating a single category from a hierarchy string"""
    hierarchy = 'Parent'
    parent = create_categories_from_hierarchy(hierarchy)
    assert parent == Category(name='Parent')


def test_add_categories_to_container_no_existing_categories_list():
    """Test that a category is added to an empty list of categories."""
    new_category = Category(name='New Category')
    categories = []
    add_categories_to_container(new_category, categories)
    assert categories == [new_category]


def test_add_categories_to_container_with_hierarchy_parent_not_in_list():
    """Test that a category is added to a list of categories with hierarchy."""
    child = Category(name='Child')
    child.set_parent(Category(name='Parent'))
    categories = []
    add_categories_to_container(child, categories)
    assert categories == [
        Category(name='Parent', children=[Category(name='Child')]),
    ]


def test_add_categories_to_container_with_hierarchy_parent_in_list():
    """Test that a category is added to a list of categories with hierarchy."""
    parent = Category(name='Parent')
    child = Category(name='Child')
    child.set_parent(parent)
    categories = [parent]
    add_categories_to_container(child, categories)
    assert categories == [Category(name='Parent', children=[child])]


def test_add_categories_to_container_with_existing_categories_list():
    """Test that a category is added to a filled list of categories."""
    new_category = Category(name='New Category')
    existing_category = Category(name='Existing Category')
    categories = [existing_category]
    add_categories_to_container(new_category, categories)
    assert categories == [existing_category, new_category]


def test_add_categories_to_container_with_hierarchy_existing_categories_list():
    """Test that a category is added to a filled list of categories."""
    child = Category(name='Child')
    child.set_parent(Category(name='Parent'))
    existing_category = Category(name='Existing Category')
    categories = [existing_category]
    add_categories_to_container(child, categories)
    assert categories == [
        existing_category,
        Category(name='Parent', children=[Category(name='Child')]),
    ]


def test_add_categories_to_container_complex_hierarchy_list():
    """Test that a complex category hierarchy is added to a list of
    categories."""
    plant = Category(name='Plant')
    tree = Category(name='Tree')
    tree.set_parent(plant)

    oak = Category(name='Oak')
    oak.set_parent(tree)
    oak_leaf = Category(name='Oak Leaf')
    oak_leaf.set_parent(oak)

    # Create separate list of categories with a root with the same name
    tree2 = Category(name='Tree')
    birch = Category(name='Birch')
    birch.set_parent(tree2)
    birch_leaf = Category(name='Birch Leaf')
    birch_leaf.set_parent(birch)

    categories = [plant]
    add_categories_to_container(birch_leaf, categories)

    assert len(categories) == 1
    plant_traversal = categories[0].traverse_down()
    assert plant_traversal == [oak_leaf, oak, birch_leaf, birch, tree, plant]

    plant_render = categories[0].render_tree()
    assert plant_render == (
        'Plant (root)\n'
        '└─ Tree\n'
        '   └─ Oak\n'
        '      └─ Oak Leaf\n'
        '   └─ Birch\n'
        '      └─ Birch Leaf'
    )


def test_add_categories_to_container_no_existing_categories_dict():
    """Test that a category is added to an empty dict of categories."""
    new_category = Category(name='New Category')
    categories = {}
    add_categories_to_container(new_category, categories)
    assert categories == {new_category.name: new_category}


def test_add_categories_to_container_with_hierarchy_parent_not_in_dict():
    """Test that a category is added to a dict of categories with hierarchy."""
    child = Category(name='Child')
    child.set_parent(Category(name='Parent'))
    categories = {}
    add_categories_to_container(child, categories)
    assert categories == {
        'Parent': Category(name='Parent', children=[Category(name='Child')]),
    }


def test_add_categories_to_container_with_hierarchy_parent_in_dict():
    """Test that a category is added to a dict of categories with hierarchy."""
    parent = Category(name='Parent')
    child = Category(name='Child')
    child.set_parent(parent)
    categories = {parent.name: parent}
    add_categories_to_container(child, categories)
    assert categories == {'Parent': Category(name='Parent', children=[child])}


def test_add_categories_to_container_with_existing_categories_dict():
    """Test that a category is added to a filled dict of categories."""
    new_category = Category(name='New Category')
    existing_category = Category(name='Existing Category')
    categories = {existing_category.name: existing_category}
    add_categories_to_container(new_category, categories)
    assert categories == {
        existing_category.name: existing_category,
        new_category.name: new_category,
    }


def test_add_categories_to_container_with_hierarchy_existing_categories_dict():
    """Test that a category is added to a filled dict of categories."""
    child = Category(name='Child')
    child.set_parent(Category(name='Parent'))
    existing_category = Category(name='Existing Category')
    categories = {existing_category.name: existing_category}
    add_categories_to_container(child, categories)
    assert categories == {
        existing_category.name: existing_category,
        'Parent': Category(name='Parent', children=[Category(name='Child')]),
    }


def test_add_categories_to_container_complex_hierarchy_dict():
    """Test that a complex category hierarchy is added to a dict of
    categories."""
    plant = Category(name='Plant')
    tree = Category(name='Tree')
    tree.set_parent(plant)

    oak = Category(name='Oak')
    oak.set_parent(tree)
    oak_leaf = Category(name='Oak Leaf')
    oak_leaf.set_parent(oak)

    # Create separate list of categories with a root with the same name
    tree2 = Category(name='Tree')
    birch = Category(name='Birch')
    birch.set_parent(tree2)
    birch_leaf = Category(name='Birch Leaf')
    birch_leaf.set_parent(birch)

    categories = {plant.name: plant}
    add_categories_to_container(birch_leaf, categories)

    assert len(categories) == 1
    plant_traversal = categories[plant.name].traverse_down()
    assert plant_traversal == [oak_leaf, oak, birch_leaf, birch, tree, plant]

    plant_render = categories[plant.name].render_tree()
    assert plant_render == (
        'Plant (root)\n'
        '└─ Tree\n'
        '   └─ Oak\n'
        '      └─ Oak Leaf\n'
        '   └─ Birch\n'
        '      └─ Birch Leaf'
    )


def test_categories_do_not_override_each_other():
    """Test that categories do not override each other

    Related to issue #23.
    https://github.com/isaacharrisholt/quiffen/issues/23
    """
    test_file = (
        Path(__file__).parent / 'test_files' / 'test_category_override.qif'
    )

    qif = Qif.parse(test_file)

    assert len(qif.categories) == 2

    assert sorted(qif.categories.keys()) == ['Everyday Expenses', 'Income']

    income = qif.categories['Income']
    assert income.name == 'Income'
    assert len(income.children) == 2
    assert sorted(c.name for c in income.children) == [
        'Available next month',
        'Available this month',
    ]

    everyday_expenses = qif.categories['Everyday Expenses']
    assert everyday_expenses.name == 'Everyday Expenses'
    assert len(everyday_expenses.children) == 2
    assert sorted(c.name for c in everyday_expenses.children) == [
        'Food Budget',
        'Gousto',
    ]
