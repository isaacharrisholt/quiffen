# pylint: disable=redefined-outer-name
from pathlib import Path

import pytest

from quiffen.core.account import Account, AccountType
from quiffen.core.category import Category
from quiffen.core.class_type import Class
from quiffen.core.qif import ParserException, Qif


@pytest.fixture
def qif_file():
    return Path(__file__).parent / 'test_files' / 'test.qif'


@pytest.fixture
def empty_file():
    return Path(__file__).parent / 'test_files' / 'empty.qif'


@pytest.fixture
def txt_file():
    return Path(__file__).parent / 'test_files' / 'invalid.txt'


@pytest.fixture
def nonexistent_file():
    return Path(__file__).parent / 'test_files' / 'nonexistent.qif'


def test_create_qif():
    """Test creating a Qif instance"""
    qif = Qif()
    assert not qif.accounts
    assert not qif.classes
    assert not qif.categories


def test_eq_success_empty_qif():
    """Test that two Qif instances are equal when empty"""
    qif = Qif()
    qif2 = Qif()
    assert qif == qif2


def test_eq_success_with_accounts():
    """Test that two Qif instances are equal when they have accounts"""
    qif = Qif()
    qif.add_account(Account(name='Test Account'))
    qif2 = Qif()
    qif2.add_account(Account(name='Test Account'))
    assert qif == qif2


def test_eq_success_with_classes():
    """Test that two Qif instances are equal when they have classes"""
    qif = Qif()
    qif.add_class(Class(name='Test Class'))
    qif2 = Qif()
    qif2.add_class(Class(name='Test Class'))
    assert qif == qif2


def test_eq_success_with_categories():
    """Test that two Qif instances are equal when they have categories"""
    qif = Qif()
    qif.add_category(Category(name='Test Category'))
    qif2 = Qif()
    qif2.add_category(Category(name='Test Category'))
    assert qif == qif2


def test_eq_failure_with_accounts():
    """Test that two Qif instances are not equal when they have different
    accounts"""
    qif = Qif()
    qif.add_account(Account(name='Test Account'))
    qif2 = Qif()
    qif2.add_account(Account(name='Test Account 2'))
    assert qif != qif2


def test_eq_failure_with_categories():
    """Test that two Qif instances are not equal when they have different
    categories"""
    qif = Qif()
    qif.add_category(Category(name='Test Category'))
    qif2 = Qif()
    qif2.add_category(Category(name='Test Category 2'))
    assert qif != qif2


def test_eq_failure_with_classes():
    """Test that two Qif instances are not equal when they have different
    classes"""
    qif = Qif()
    qif.add_class(Class(name='Test Class'))
    qif2 = Qif()
    qif2.add_class(Class(name='Test Class 2'))
    assert qif != qif2


def test_str_method_empty_qif():
    """Test the string representation of an empty Qif instance"""
    qif = Qif()
    assert str(qif) == 'Empty Qif object'


def test_str_method_with_accounts():
    """Test the string representation of a Qif instance with accounts"""
    qif = Qif()
    qif.add_account(Account(name='Test Account'))
    assert str(qif) == (
        'QIF\n'
        '===\n\n'
        'Accounts\n'
        '--------\n\n'
        'Account:\n\t'
        'Name: Test Account\n\n'
    )


def test_str_method_with_categories():
    """Test the string representation of a Qif instance with categories"""
    qif = Qif()
    qif.add_category(Category(name='Test Category'))
    print(repr(str(qif)))
    assert str(qif) == (
        'QIF\n'
        '===\n\n'
        'Categories\n'
        '----------\n\n'
        'Category:\n\t'
        'Name: Test Category\n\t'
        'Category Type: expense\n\t'
        'Hierarchy: Test Category\n\n'
    )


def test_str_method_with_classes():
    """Test the string representation of a Qif instance with classes"""
    qif = Qif()
    qif.add_class(Class(name='Test Class'))
    assert str(qif) == (
        'QIF\n'
        '===\n\n'
        'Classes\n'
        '-------\n\n'
        'Class:\n\t'
        'Name: Test Class\n\t'
        'Categories: 0\n\n'
    )


def test_str_method_with_all():
    """Test the string representation of a Qif instance with all data"""
    qif = Qif()
    qif.add_account(Account(name='Test Account'))
    qif.add_class(Class(name='Test Class'))
    qif.add_category(Category(name='Test Category'))
    assert str(qif) == (
        'QIF\n'
        '===\n\n'
        'Accounts\n'
        '--------\n\n'
        'Account:\n\t'
        'Name: Test Account\n\n'
        'Categories\n'
        '----------\n\n'
        'Category:\n\t'
        'Name: Test Category\n\t'
        'Category Type: expense\n\t'
        'Hierarchy: Test Category\n\n'
        'Classes\n'
        '-------\n\n'
        'Class:\n\t'
        'Name: Test Class\n\t'
        'Categories: 0\n\n'
    )


def test_from_list():
    """Test that the from_list method raises a NotImplementedError"""
    qif = Qif()
    with pytest.raises(NotImplementedError):
        qif.from_list([])


def test_parse_works(qif_file):
    """Test parsing a QIF file"""
    Qif.parse(qif_file)


def test_parse_empty_file(empty_file):
    """Test parsing an empty QIF file"""
    with pytest.raises(ParserException):
        Qif.parse(empty_file)


def test_parse_non_qif_file(txt_file):
    """Test parsing a file that is not a QIF file"""
    with pytest.raises(ParserException):
        Qif.parse(txt_file)


def test_parse_nonexistent_file():
    """Test parsing a file that does not exist"""
    with pytest.raises(ParserException):
        Qif.parse('nonexistent_file.qif')


def test_parsed_accounts(qif_file):
    """Test that the accounts are parsed correctly"""
    qif = Qif.parse(qif_file)

    # Validate the account is the default account
    assert len(qif.accounts) == 1
    account_name = 'Quiffen Default Account'
    account = qif.accounts[account_name]

    assert account.name == account_name
    assert account.desc == (
        'The default account created by Quiffen when no other accounts were '
        'present'
    )


def test_parsed_transactions(qif_file):
    """Test that the transactions are parsed correctly"""
    qif = Qif.parse(qif_file)
    account = qif.accounts['Quiffen Default Account']

    # Validate the transactions
    transactions = account.transactions
    assert len(transactions) == 2

    # Validate bank transactions
    bank_transactions = transactions[AccountType.BANK]
    assert len(bank_transactions) == 6

    # Validate the investment transactions
    investment_transactions = transactions[AccountType.INVST]
    assert len(investment_transactions) == 1


def test_parsed_categories(qif_file):
    """Test that the categories are parsed correctly"""
    qif = Qif.parse(qif_file)

    # Validate categories
    assert len(qif.categories) == 4
    expected_categories = ['Bills', 'Food', 'Investments', 'Miscellaneous']
    assert sorted(qif.categories.keys()) == expected_categories

    # Validate bills category
    bills = qif.categories['Bills']
    assert len(bills.children) == 1
    assert bills.children[0].name == 'Cell Phone'
    assert bills.children[0].parent == bills

    # Validate food category
    food = qif.categories['Food']
    assert len(food.children) == 1
    assert food.children[0].name == 'Groceries'
    assert food.children[0].parent == food

    # Validate investments category
    investments = qif.categories['Investments']
    investment_child_categories = sorted(investments.children)
    assert len(investment_child_categories) == 2
    assert investment_child_categories[0].name == 'Bonds'
    assert investment_child_categories[0].parent == investments
    assert investment_child_categories[1].name == 'Stocks'
    assert investment_child_categories[1].parent == investments

    # Validate miscellaneous category
    miscellaneous = qif.categories['Miscellaneous']
    assert len(miscellaneous.children) == 0


def test_parsed_classes(qif_file):
    """Test that the classes are parsed correctly"""
    qif = Qif.parse(qif_file)

    # Validate classes
    assert len(qif.classes) == 2
    assert 'Test class' in qif.classes
    assert 'Test class 2' in qif.classes

    # Validate test class
    test_class = qif.classes['Test class']
    assert test_class.name == 'Test class'
    assert test_class.desc == (
        'This is just a class I added here for test purposes'
    )
    assert len(test_class.categories) == 1
    cell_phone = test_class.categories[0]
    assert cell_phone.name == 'Cell Phone'
    assert cell_phone.parent.name == 'Bills'

    # Validate test class 2
    test_class_2 = qif.classes['Test class 2']
    assert test_class_2.name == 'Test class 2'
    assert test_class_2.desc == (
        'This is just a class I added here for test purposes'
    )
    assert len(test_class_2.categories) == 0


def test_add_account():
    """Test adding an account"""
    qif = Qif()
    account = Account(name='Test Account')
    qif.add_account(account)
    assert len(qif.accounts) == 1
    assert qif.accounts['Test Account'] == account


def test_add_existing_account():
    """Test adding an account that already exists"""
    qif = Qif()
    account = Account(name='Test Account')
    account2 = Account(name='Test Account')
    qif.add_account(account)
    qif.add_account(account2)
    assert len(qif.accounts) == 1
    assert 'Test Account' in qif.accounts


def test_remove_account():
    """Test removing an account"""
    qif = Qif()
    account = Account(name='Test Account')
    qif.add_account(account)
    removed = qif.remove_account('Test Account')
    assert len(qif.accounts) == 0
    assert removed == account


def test_remove_nonexistent_account():
    """Test removing an account that does not exist"""
    qif = Qif()
    with pytest.raises(KeyError):
        qif.remove_account('Test Account')


def test_add_category():
    """Test adding a category"""
    qif = Qif()
    category = Category(name='Test Category')
    qif.add_category(category)
    assert len(qif.categories) == 1
    assert qif.categories['Test Category'] == category


def test_add_existing_category():
    """Test adding a category that already exists"""
    qif = Qif()
    category = Category(name='Test Category')
    category2 = Category(name='Test Category')
    qif.add_category(category)
    qif.add_category(category2)
    assert len(qif.categories) == 1
    assert 'Test Category' in qif.categories


def test_remove_category():
    """Test removing a category"""
    qif = Qif()
    category = Category(name='Test Category')
    qif.add_category(category)
    removed = qif.remove_category('Test Category')
    assert len(qif.categories) == 0
    assert removed == category


def test_remove_category_keep_children():
    """Test removing a category and keeping its children"""
    qif = Qif()
    category = Category(name='Test Category')
    child_category = Category(name='Child Category', parent=category)
    qif.add_category(category)
    qif.add_category(child_category)
    removed = qif.remove_category('Test Category', keep_children=True)
    assert len(qif.categories) == 1
    assert 'Child Category' in qif.categories
    assert removed == category


def test_remove_category_nonexistent_category():
    """Test removing a category that does not exist"""
    qif = Qif()
    with pytest.raises(KeyError):
        qif.remove_category('Test Category')


def test_add_class():
    """Test adding a class"""
    qif = Qif()
    cls = Class(name='Test Class')
    qif.add_class(cls)
    assert len(qif.classes) == 1
    assert qif.classes['Test Class'] == cls


def test_add_existing_class():
    """Test adding a class that already exists"""
    qif = Qif()
    cls = Class(name='Test Class')
    cls2 = Class(name='Test Class')
    qif.add_class(cls)
    qif.add_class(cls2)
    assert len(qif.classes) == 1
    assert 'Test Class' in qif.classes


def test_remove_class():
    """Test removing a class"""
    qif = Qif()
    cls = Class(name='Test Class')
    qif.add_class(cls)
    removed = qif.remove_class('Test Class')
    assert len(qif.classes) == 0
    assert removed == cls


def test_remove_nonexistent_class():
    """Test removing a class that does not exist"""
    qif = Qif()
    with pytest.raises(KeyError):
        qif.remove_class('Test Class')


def test_to_qif(qif_file):
    """Test the to_qif method

    The most important thing to test here is that the output contains all the
    data that was parsed from the input file.

    As such, the test file is parsed and then the output is compared to the
    original file.
    """
    qif = Qif.parse(qif_file)
    test_file = qif_file.parent / 'test_output.qif'
    qif.to_qif(test_file)

    resulting_qif = Qif.parse(test_file)
    assert qif.accounts == resulting_qif.accounts
    assert sorted(qif.categories) == sorted(resulting_qif.categories)
    assert qif.classes == resulting_qif.classes
    test_file.unlink()



# def test_to_dicts():
#     qif = Qif()
#     acc = Account(name='Test Account')
#     qif.add_account(acc)
#     date_now = datetime.now()
#
#     tr = Transaction(date=date_now, amount=Decimal(150))
#     acc.last_header = 'Bank'
#     acc.add_transaction(tr)
#
#     tr_dicts = qif.to_dicts(data='transactions')
#     assert tr_dicts == [{'date': date_now, 'amount': 150}]
#
#     acc_dicts = qif.to_dicts(data='accounts')
#     assert acc_dicts == [
#         {
#             'name': 'Test Account',
#             'transactions': {'Bank': [{'date': date_now, 'amount': 150}]},
#         },
#     ]
