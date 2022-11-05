# pylint: disable=redefined-outer-name
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from quiffen import Investment, Transaction
from quiffen.core.account import Account, AccountType
from quiffen.core.category import Category
from quiffen.core.class_type import Class
from quiffen.core.qif import ParserException, Qif, QifDataType


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


# pylint: disable=protected-access
def test_get_data_dicts_transactions():
    """Test the get_data_dicts method with transactions"""
    qif = Qif()
    account = Account(name='Test Account')
    transaction = Transaction(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        payee='Test Payee',
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    account.set_header('Bank')
    account.add_transaction(transaction)
    qif.add_account(account)
    data_dicts = qif._get_data_dicts(data_type=QifDataType.TRANSACTIONS)

    assert len(data_dicts) == 1
    expected = transaction.to_dict()
    expected['date'] = '2019-01-01'  # Dates are converted to strings
    assert data_dicts[0] == expected


def test_get_data_dicts_transactions_with_date_format_and_ignore():
    """Test the get_data_dicts method with transactions and date format and
    ignore"""
    qif = Qif()
    account = Account(name='Test Account')
    transaction = Transaction(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        payee='Test Payee',
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    account.set_header('Bank')
    account.add_transaction(transaction)
    qif.add_account(account)
    data_dicts = qif._get_data_dicts(
        data_type=QifDataType.TRANSACTIONS,
        date_format='%d/%m/%Y',
        ignore=['payee', 'memo'],
    )

    assert len(data_dicts) == 1
    expected = transaction.to_dict()
    expected['date'] = '01/01/2019'  # Dates are converted to strings
    del expected['payee']
    del expected['memo']
    assert data_dicts[0] == expected


def test_get_data_dicts_categories():
    """Test the get_data_dicts method with categories"""
    qif = Qif()
    category = Category(name='Test Category')
    qif.add_category(category)
    data_dicts = qif._get_data_dicts(data_type=QifDataType.CATEGORIES)

    assert len(data_dicts) == 1
    assert data_dicts[0] == category.to_dict()


def test_get_data_dicts_classes():
    """Test the get_data_dicts method with classes"""
    qif = Qif()
    cls = Class(name='Test Class')
    qif.add_class(cls)
    data_dicts = qif._get_data_dicts(data_type=QifDataType.CLASSES)

    assert len(data_dicts) == 1
    assert data_dicts[0] == cls.to_dict()


def test_get_data_dicts_accounts():
    """Test the get_data_dicts method with accounts"""
    qif = Qif()
    account = Account(name='Test Account')
    account.set_header('Bank')
    qif.add_account(account)
    data_dicts = qif._get_data_dicts(data_type=QifDataType.ACCOUNTS)

    assert len(data_dicts) == 1
    expected = account.to_dict()
    del expected['_last_header']
    assert data_dicts[0] == expected


def test_get_data_dicts_investments():
    """Test the get_data_dicts method with investments"""
    qif = Qif()
    account = Account(name='Test Account')
    investment = Investment(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        security='Test Security',
        price=Decimal('10'),
    )
    account.set_header('Invst')
    account.add_transaction(investment)
    qif.add_account(account)
    data_dicts = qif._get_data_dicts(data_type=QifDataType.INVESTMENTS)

    assert len(data_dicts) == 1
    expected = investment.to_dict()
    expected['date'] = '2019-01-01'  # Dates are converted to strings
    assert data_dicts[0] == expected
# pylint: enable=protected-access


def test_to_csv_transactions():
    """Test the to_csv method with transactions"""
    qif = Qif()
    account = Account(name='Test Account')
    transaction = Transaction(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        payee='Test Payee',
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    account.set_header('Bank')
    account.add_transaction(transaction)
    qif.add_account(account)

    csv_file = Path(__file__).parent / 'test_files' / 'test_output.csv'
    qif.to_csv(path=csv_file, data_type=QifDataType.TRANSACTIONS)

    assert csv_file.exists()
    with csv_file.open() as f:
        reader = csv.DictReader(f)
        assert len(reader.fieldnames) == 20

        results = list(reader)
        assert len(results) == 1
        assert results[0]['date'] == '2019-01-01'
        assert results[0]['amount'] == '100'
        assert results[0]['payee'] == 'Test Payee'
        assert results[0]['memo'] == 'Test Memo'
        assert 'Test Category' in results[0]['category']
    csv_file.unlink()


def test_to_csv_categories():
    """Test the to_csv method with categories"""
    qif = Qif()
    category = Category(name='Test Category')
    qif.add_category(category)

    csv_file = Path(__file__).parent / 'test_files' / 'test_output.csv'
    qif.to_csv(path=csv_file, data_type=QifDataType.CATEGORIES)

    assert csv_file.exists()
    with csv_file.open() as f:
        reader = csv.DictReader(f)
        assert len(reader.fieldnames) == 9

        results = list(reader)
        assert len(results) == 1
        assert results[0]['name'] == 'Test Category'
    csv_file.unlink()


def test_to_csv_classes():
    """Test the to_csv method with classes"""
    qif = Qif()
    cls = Class(name='Test Class', desc='Test Description')
    qif.add_class(cls)

    csv_file = Path(__file__).parent / 'test_files' / 'test_output.csv'
    qif.to_csv(path=csv_file, data_type=QifDataType.CLASSES)

    assert csv_file.exists()
    with csv_file.open() as f:
        reader = csv.DictReader(f)
        assert len(reader.fieldnames) == 3

        results = list(reader)
        assert len(results) == 1
        assert results[0]['name'] == 'Test Class'
        assert results[0]['desc'] == 'Test Description'
    csv_file.unlink()


def test_to_csv_accounts():
    """Test the to_csv method with accounts"""
    qif = Qif()
    account = Account(name='Test Account', account_type='Bank')
    account.set_header('Bank')
    qif.add_account(account)

    csv_file = Path(__file__).parent / 'test_files' / 'test_output.csv'
    qif.to_csv(path=csv_file, data_type=QifDataType.ACCOUNTS)

    assert csv_file.exists()
    with csv_file.open() as f:
        reader = csv.DictReader(f)
        assert len(reader.fieldnames) == 7

        results = list(reader)
        assert len(results) == 1
        assert results[0]['name'] == 'Test Account'
        assert results[0]['account_type'] == 'Bank'
    csv_file.unlink()


def test_to_csv_investments():
    """Test the to_csv method with investments"""
    qif = Qif()
    account = Account(name='Test Account')
    investment = Investment(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        security='Test Security',
        price=Decimal('10'),
    )
    account.set_header('Invst')
    account.add_transaction(investment)
    qif.add_account(account)

    csv_file = Path(__file__).parent / 'test_files' / 'test_output.csv'
    qif.to_csv(path=csv_file, data_type=QifDataType.INVESTMENTS)

    assert csv_file.exists()
    with csv_file.open() as f:
        reader = csv.DictReader(f)
        assert len(reader.fieldnames) == 13

        results = list(reader)
        assert len(results) == 1
        assert results[0]['date'] == '2019-01-01'
        assert results[0]['amount'] == '100'
        assert results[0]['security'] == 'Test Security'
        assert results[0]['price'] == '10'
    csv_file.unlink()


def test_to_csv_transactions_with_date_format_and_ignore_list():
    """Test the to_csv method with transactions with date format and ignore"""
    qif = Qif()
    account = Account(name='Test Account')
    transaction = Transaction(
        date=datetime(2019, 2, 1),
        amount=Decimal('100'),
        payee='Test Payee',
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    account.set_header('Bank')
    account.add_transaction(transaction)
    qif.add_account(account)

    csv_file = Path(__file__).parent / 'test_files' / 'test_output.csv'
    qif.to_csv(
        path=csv_file,
        data_type=QifDataType.TRANSACTIONS,
        date_format='%m/%d/%Y',
        ignore=['payee'],
    )

    assert csv_file.exists()
    with csv_file.open() as f:
        reader = csv.DictReader(f)
        assert len(reader.fieldnames) == 19

        results = list(reader)
        assert len(results) == 1
        assert results[0]['date'] == '02/01/2019'
        assert results[0]['amount'] == '100'
        assert 'payee' not in results[0]
        assert results[0]['memo'] == 'Test Memo'
        assert 'Test Category' in results[0]['category']
    csv_file.unlink()


def test_to_csv_transactions_multiple():
    """Test the to_csv method with multiple transactions"""
    qif = Qif()
    account = Account(name='Test Account')
    transaction = Transaction(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        payee='Test Payee',
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    account.set_header('Bank')
    account.add_transaction(transaction)

    transaction2 = transaction.copy()
    transaction2.amount = Decimal('200')

    account.add_transaction(transaction2)
    qif.add_account(account)

    csv_file = Path(__file__).parent / 'test_files' / 'test_output.csv'
    qif.to_csv(path=csv_file, data_type=QifDataType.TRANSACTIONS)

    assert csv_file.exists()
    with csv_file.open() as f:
        reader = csv.DictReader(f)
        assert len(reader.fieldnames) == 20

        results = list(reader)
        assert len(results) == 2
        assert results[0]['date'] == '2019-01-01'
        assert results[0]['amount'] == '100'
        assert results[0]['payee'] == 'Test Payee'
        assert results[0]['memo'] == 'Test Memo'
        assert 'Test Category' in results[0]['category']
        assert results[1]['date'] == '2019-01-01'
        assert results[1]['amount'] == '200'
        assert results[1]['payee'] == 'Test Payee'
        assert results[1]['memo'] == 'Test Memo'
        assert 'Test Category' in results[1]['category']
    csv_file.unlink()


def test_to_dataframe_transactions():
    """Test the to_dataframe method with transactions"""
    qif = Qif()
    account = Account(name='Test Account')
    transaction = Transaction(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        payee='Test Payee',
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    account.set_header('Bank')
    account.add_transaction(transaction)
    qif.add_account(account)

    df = qif.to_dataframe(data_type=QifDataType.TRANSACTIONS)

    assert df.shape == (1, 20)
    assert df['date'][0] == '2019-01-01'
    assert df['amount'][0] == 100
    assert df['payee'][0] == 'Test Payee'
    assert df['memo'][0] == 'Test Memo'
    assert df['category'][0]['name'] == 'Test Category'


def test_to_dataframe_categories():
    """Test the to_dataframe method with categories"""
    qif = Qif()
    category = Category(name='Test Category')
    qif.add_category(category)

    df = qif.to_dataframe(data_type=QifDataType.CATEGORIES)

    assert df.shape == (1, 9)
    assert df['name'][0] == 'Test Category'
    assert df['parent'][0] is None


def test_to_dataframe_classes():
    """Test the to_dataframe method with classes"""
    qif = Qif()
    cls = Class(name='Test Class', desc='Test Description')
    qif.add_class(cls)

    df = qif.to_dataframe(data_type=QifDataType.CLASSES)

    assert df.shape == (1, 3)
    assert df['name'][0] == 'Test Class'
    assert df['desc'][0] == 'Test Description'


def test_to_dataframe_accounts():
    """Test the to_dataframe method with accounts"""
    qif = Qif()
    account = Account(name='Test Account', account_type='Bank')
    qif.add_account(account)

    df = qif.to_dataframe(data_type=QifDataType.ACCOUNTS)

    assert df.shape == (1, 7)
    assert df['name'][0] == 'Test Account'
    assert df['account_type'][0] == 'Bank'


def test_to_dataframe_investments():
    """Test the to_dataframe method with investments"""
    qif = Qif()
    account = Account(name='Test Account')
    investment = Investment(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        security='Test Security',
        price=Decimal('10'),
    )
    account.set_header('Invst')
    account.add_transaction(investment)
    qif.add_account(account)

    df = qif.to_dataframe(data_type=QifDataType.INVESTMENTS)

    assert df.shape == (1, 13)
    assert df['date'][0] == '2019-01-01'
    assert df['amount'][0] == 100
    assert df['security'][0] == 'Test Security'
    assert df['price'][0] == 10


def test_to_dataframe_transactions_with_date_format_and_ignore_list():
    """Test the to_dataframe method with transactions and date_format and
    ignore"""
    qif = Qif()
    account = Account(name='Test Account')
    transaction = Transaction(
        date=datetime(2019, 2, 1),
        amount=Decimal('100'),
        payee='Test Payee',
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    account.set_header('Bank')
    account.add_transaction(transaction)
    qif.add_account(account)

    df = qif.to_dataframe(
        data_type=QifDataType.TRANSACTIONS,
        date_format='%m/%d/%Y',
        ignore=['payee'],
    )

    assert df.shape == (1, 19)
    assert df['date'][0] == '02/01/2019'
    assert df['amount'][0] == 100
    assert 'payee' not in df.columns
    assert df['memo'][0] == 'Test Memo'
    assert df['category'][0]['name'] == 'Test Category'


def test_to_dataframe_transactions_multiple():
    """Test the to_dataframe method with multiple transactions"""
    qif = Qif()
    account = Account(name='Test Account')
    transaction = Transaction(
        date=datetime(2019, 1, 1),
        amount=Decimal('100'),
        payee='Test Payee',
        memo='Test Memo',
        category=Category(name='Test Category'),
    )
    account.set_header('Bank')
    account.add_transaction(transaction)

    transaction2 = transaction.copy()
    transaction2.amount = Decimal('200')

    account.add_transaction(transaction2)
    qif.add_account(account)

    df = qif.to_dataframe(data_type=QifDataType.TRANSACTIONS)

    assert df.shape == (2, 20)
    assert df['date'][0] == '2019-01-01'
    assert df['amount'][0] == 100
    assert df['payee'][0] == 'Test Payee'
    assert df['memo'][0] == 'Test Memo'
    assert df['category'][0]['name'] == 'Test Category'
    assert df['date'][1] == '2019-01-01'
    assert df['amount'][1] == 200
    assert df['payee'][1] == 'Test Payee'
    assert df['memo'][1] == 'Test Memo'
    assert df['category'][1]['name'] == 'Test Category'
