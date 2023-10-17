from datetime import datetime
from decimal import Decimal

import pytest

from quiffen import Category, Class, Split, Transaction, TransactionConfig


def test_create_transaction():
    """Test creating a transaction"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=100,
    )
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 100
    assert transaction.check_number is None
    assert transaction.payee is None
    assert transaction.memo is None
    assert transaction.payee_address is None
    assert transaction.category is None
    assert not transaction.splits


def test_create_transaction_more_fields():
    """Test creating a transaction with more fields"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=100,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
    )
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 100
    assert transaction.check_number == 1
    assert transaction.payee == "Test Payee"
    assert transaction.memo == "Test Memo"
    assert transaction.payee_address == "Test Address"
    assert transaction.category is None
    assert not transaction.splits


def test_create_transaction_with_splits():
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=100,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100)],
    )
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 100
    assert transaction.check_number == 1
    assert transaction.payee == "Test Payee"
    assert transaction.memo == "Test Memo"
    assert transaction.payee_address == "Test Address"
    assert transaction.category == Category(name="Test Category")
    assert transaction.splits == [Split(amount=100)]


def test_create_transaction_with_splits_percent_too_high():
    """Test creating a transaction with splits where the percent is too high"""
    with pytest.raises(ValueError):
        Transaction(
            date=datetime(2022, 2, 1),
            amount=100,
            splits=[
                Split(amount=100, percent=50),
                Split(amount=200, percent=60),
            ],
        )


def test_split_overshoot_issue63():
    """
    test creating a transaction with overshoot but configured to have no exception
    """
    TransactionConfig.max_split_overshoot = 0.1
    Transaction(
        date=datetime(2022, 2, 1),
        amount=300,
        splits=[
            Split(amount=100, percent=50),
            Split(amount=200, percent=50.05),
        ],
    )
    pass


def test_create_transaction_with_splits_exactly_100_percent():
    """Test creating a transaction with splits where the percent is exactly 100.

    Relates to issue #39.
    https://github.com/isaacharrisholt/quiffen/issues/39
    """
    transaction_list = [
        "D12/1/22",
        "PPayee",
        "T5,382.39",
        "NDEP",
        "LSplit",
        "SCategory A",
        "$-120.83",
        "SCategory B",
        "$-2,100.96",
        "SCategory C",
        "$-729.15",
        "SCategory D",
        "$8,333.33",
    ]
    # Should not raise an error
    Transaction.from_list(transaction_list)


def test_create_transaction_with_splits_amount_too_high():
    """Test creating a transaction with splits where the amount is too high"""
    with pytest.raises(ValueError):
        Transaction(
            date=datetime(2022, 2, 1),
            amount=100,
            splits=[Split(amount=100), Split(amount=200)],
        )


def test_eq_success():
    """Test equality"""
    transaction1 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
    )
    transaction2 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
    )
    assert transaction1 == transaction2

    transaction3 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200)],
    )
    transaction4 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200)],
    )
    assert transaction3 == transaction4


def test_eq_failure():
    """Test inequality"""
    transaction1 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
    )
    transaction2 = Transaction(
        date=datetime(2022, 2, 2),
        amount=1000,
    )
    assert transaction1 != transaction2

    transaction3 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200)],
    )
    transaction4 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200), Split(amount=300)],
    )
    assert transaction3 != transaction4

    transaction5 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200)],
    )
    transaction5.splits[0].amount = 300
    assert transaction3 != transaction5

    transaction6 = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo 2",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200)],
    )
    assert transaction3 != transaction6


def test_str_method():
    """Test the string method"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200)],
    )
    assert str(transaction) == (
        "Transaction:\n\t"
        "Date: 2022-02-01 00:00:00\n\t"
        "Amount: 1000\n\t"
        "Memo: Test Memo\n\t"
        "Payee: Test Payee\n\t"
        "Payee Address: Test Address\n\t"
        "Category: Test Category\n\t"
        "Check Number: 1\n\t"
        "Splits: 2"
    )


def test_is_split():
    """Test the is_split property"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200)],
    )
    assert transaction.is_split

    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
    )
    assert not transaction.is_split


def test_add_split():
    """Test the add_split method"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
    )
    transaction.add_split(Split(amount=100))
    assert transaction.splits == [Split(amount=100)]
    transaction.add_split(Split(amount=200))
    assert transaction.splits == [Split(amount=100), Split(amount=200)]


def test_add_split_percent_too_high():
    """Test the add_split method where the sum of the percentages is too high"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100, percent=60)],
    )
    with pytest.raises(ValueError):
        transaction.add_split(Split(amount=100, percent=60))


def test_add_split_amount_too_high():
    """Test the add_split method where the sum of the amounts is too high"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100)],
    )
    with pytest.raises(ValueError):
        transaction.add_split(Split(amount=950))


def test_add_splits_exactly_100_percent():
    """Test adding splits that add up to 100 percent

    Relates to issue #39.
    https://github.com/isaacharrisholt/quiffen/issues/39
    """
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=Decimal("5382.39"),
    )

    splits = [
        Split(amount=Decimal("-121.83")),
        Split(amount=Decimal("-2101.96")),
        Split(amount=Decimal("-730.15")),
        Split(amount=Decimal("8332.33")),
    ]

    for split in splits:
        # Should not raise an error
        transaction.add_split(split)


def test_remove_splits_one_filter():
    """Test the remove_splits method with one filter"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200, memo="Test Memo")],
    )
    transaction.remove_splits(memo="Test Memo")
    assert transaction.splits == [Split(amount=100)]


def test_remove_splits_multiple_filters():
    """Test the remove_splits method with multiple filters"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=100, memo="Test Memo")],
    )
    transaction.remove_splits(memo="Test Memo", amount=100)
    assert transaction.splits == [Split(amount=100)]


def test_remove_splits_no_match():
    """Test the remove_splits method with no match"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=100, memo="Test Memo")],
    )
    transaction.remove_splits(memo="Test Memo", amount=100, check_number=1)
    assert transaction.splits == [
        Split(amount=100),
        Split(amount=100, memo="Test Memo"),
    ]


def test_remove_splits_no_filters():
    """Test the remove_splits method with no filters"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[Split(amount=100), Split(amount=200)],
    )
    transaction.remove_splits()
    assert not transaction.splits
    assert not transaction.is_split


def test_to_qif_no_splits_no_classes():
    """Test the to_qif method with no splits and no classes"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
    )
    print(repr(transaction.to_qif()))
    assert transaction.to_qif() == (
        "D2022-02-01\n"
        "T1000\n"
        "MTest Memo\n"
        "PTest Payee\n"
        "ATest Address\n"
        "LTest Category\n"
        "N1\n"
    )


def test_to_qif_no_split_with_class():
    """Test the to_qif method with no splits and a class"""
    parent = Category(name="Test Parent")
    child = Category(name="Test Child")
    parent.add_child(child)

    cls = Class(name="Test Class")
    cls.add_category(parent)

    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=child,
    )
    assert transaction.to_qif(classes={"Test Class": cls}) == (
        "D2022-02-01\n"
        "T1000\n"
        "MTest Memo\n"
        "PTest Payee\n"
        "ATest Address\n"
        "LTest Parent:Test Child/Test Class\n"
        "N1\n"
    )


def test_to_qif_with_splits_no_classes():
    """Test the to_qif method with splits and no classes"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=Category(name="Test Category"),
        splits=[
            Split(
                amount=100,
                memo="Test Memo",
                category=Category(name="Test Split Category"),
            ),
            Split(amount=200, memo="Test Memo 2"),
        ],
    )
    assert transaction.to_qif() == (
        "D2022-02-01\n"
        "T1000\n"
        "MTest Memo\n"
        "PTest Payee\n"
        "ATest Address\n"
        "LTest Category\n"
        "N1\n"
        "STest Split Category\n"
        "$100\n"
        "ETest Memo\n"
        "S\n"
        "$200\n"
        "ETest Memo 2\n"
    )


def test_to_qif_with_splits_with_classes():
    """Test the to_qif method with splits and classes"""
    parent = Category(name="Test Parent")
    child = Category(name="Test Child")
    parent.add_child(child)

    cls = Class(name="Test Class")
    cls.add_category(parent)

    split_category = Category(name="Test Split Category")
    cls.add_category(split_category)

    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        check_number=1,
        payee="Test Payee",
        memo="Test Memo",
        payee_address="Test Address",
        category=child,
        splits=[
            Split(
                amount=100,
                memo="Test Memo",
                category=Category(name="Test Split Category"),
            ),
            Split(amount=200, memo="Test Memo 2"),
        ],
    )
    assert transaction.to_qif(classes={"Test Class": cls}) == (
        "D2022-02-01\n"
        "T1000\n"
        "MTest Memo\n"
        "PTest Payee\n"
        "ATest Address\n"
        "LTest Parent:Test Child/Test Class\n"
        "N1\n"
        "STest Split Category/Test Class\n"
        "$100\n"
        "ETest Memo\n"
        "S\n"
        "$200\n"
        "ETest Memo 2\n"
    )


def test_from_list_no_splits_no_classes():
    """Test creating a transaction from a list of QIF strings"""
    qif_list = [
        "D2022-02-01",
        "T1000",
        "MTest Memo",
        "CTest Cleared",
        "PTest Payee",
        "ATest Address",
        "L[Test To Account]",  # Brackets denote to account
        "LTest Category",  # No brackets denote category
        "N1",
        "FFalse",
        "12022-03-01",  # First payment date
        "234",  # Loan length
        "312",  # Number of payments
        "42",  # Periods per year
        "51.23",  # Interest rate
        "61000",  # Current loan balance
        "710000",  # Original loan amount
    ]
    transaction, _ = Transaction.from_list(qif_list)
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 1000
    assert transaction.memo == "Test Memo"
    assert transaction.cleared == "Test Cleared"
    assert transaction.payee == "Test Payee"
    assert transaction.payee_address == "Test Address"
    assert transaction.to_account == "Test To Account"
    assert transaction.category == Category(name="Test Category")
    assert transaction.check_number == 1
    assert not transaction.is_split
    assert transaction.first_payment_date == datetime(2022, 3, 1)
    assert transaction.loan_length == 34
    assert transaction.num_payments == 12
    assert transaction.periods_per_annum == 2
    assert transaction.interest_rate == Decimal("1.23")
    assert transaction.current_loan_balance == 1000
    assert transaction.original_loan_amount == 10000


def test_from_list_no_split_with_class():
    """Test creating a transaction from a list of QIF strings with no splits but
    that does define a QIF class"""
    qif_list = [
        "D2022-02-01",
        "T1000",
        "L[Test To Account]",  # Brackets denote to account
        "LTest Category/Class Name",  # / denotes a class after the category
    ]
    transaction, classes = Transaction.from_list(qif_list)
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 1000
    assert transaction.to_account == "Test To Account"
    assert transaction.category == Category(name="Test Category")

    assert classes == {
        "Class Name": Class(
            name="Class Name",
            categories=[Category(name="Test Category")],
        ),
    }


def test_from_list_with_splits_no_classes():
    """Test creating a transaction from a list of QIF strings with splits"""
    qif_list = [
        "D2022-02-01",
        "T1000",
        "L[Test To Account]",  # Brackets denote to account
        "LTest Category",  # No brackets denote category
        "STest Split Category 1",
        "ETest Split Memo",
        "$100",
        "STest Split Category 2",
        "EMemo",
        "$100",
        "%10",
    ]
    transaction, _ = Transaction.from_list(qif_list)
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 1000
    assert transaction.to_account == "Test To Account"
    assert transaction.category == Category(name="Test Category")
    assert transaction.is_split
    assert transaction.splits == [
        Split(
            category=Category(name="Test Split Category 1"),
            memo="Test Split Memo",
            amount=100,
            percent=Decimal("10"),
        ),
        Split(
            category=Category(name="Test Split Category 2"),
            memo="Memo",
            amount=100,
            percent=Decimal("10"),
        ),
    ]


def test_from_list_with_splits_with_classes():
    """Test creating a transaction from a list of QIF strings with splits and
    classes"""
    qif_list = [
        "D2022-02-01",
        "T1000",
        "L[Test To Account]",  # Brackets denote to account
        "LTest Category",  # No brackets denote category
        "STest Split Category 1/Class Name",
        "ETest Split Memo",
        "T100",
        "STest Split Category 2/Class Name",
        "EMemo",
        "$100",
        "%10",
    ]
    transaction, classes = Transaction.from_list(qif_list)
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 1000
    assert transaction.to_account == "Test To Account"
    assert transaction.category == Category(name="Test Category")
    assert transaction.is_split
    assert transaction.splits == [
        Split(
            category=Category(name="Test Split Category 1"),
            memo="Test Split Memo",
            amount=100,
            percent=Decimal("10"),
        ),
        Split(
            category=Category(name="Test Split Category 2"),
            memo="Memo",
            amount=100,
            percent=Decimal("10"),
        ),
    ]

    assert classes == {
        "Class Name": Class(
            name="Class Name",
            categories=[
                Category(name="Test Split Category 1"),
                Category(name="Test Split Category 2"),
            ],
        ),
    }


def test_from_list_multiple_categories():
    """Test creating a transaction from a list of QIF strings with multiple
    categories"""
    qif_list = [
        "D2022-02-01",
        "T1000",
        "L[Test To Account]",  # Brackets denote to account
        "LTest Category 1",
        "LTest Category 2",
    ]
    transaction, _ = Transaction.from_list(qif_list)
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 1000
    assert transaction.to_account == "Test To Account"
    assert transaction.category.name == "Test Category 2"
    assert transaction.category.parent.name == "Test Category 1"


def test_from_string_default_separator():
    """Test creating a transaction from a string with the default separator"""
    qif_string = (
        "D2022-02-01\n"
        "T1000\n"
        "L[Test To Account]\n"  # Brackets denote to account
        "LTest Category"
    )
    transaction, _ = Transaction.from_string(qif_string)
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 1000
    assert transaction.to_account == "Test To Account"
    assert transaction.category == Category(name="Test Category")


def test_from_string_custom_separator():
    """Test creating a transaction from a string with a custom separator"""
    qif_string = (
        "D2022-02-01---"
        "T1000---"
        "L[Test To Account]---"  # Brackets denote to account
        "LTest Category"
    )
    transaction, _ = Transaction.from_string(qif_string, separator="---")
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 1000
    assert transaction.to_account == "Test To Account"
    assert transaction.category == Category(name="Test Category")


def test_to_dict():
    """Test converting a category to a dict"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        to_account="Test To Account",
        category=Category(name="Test Category"),
    )
    assert transaction.to_dict() == {
        "date": datetime(2022, 2, 1, 0, 0),
        "amount": Decimal("1000"),
        "memo": None,
        "cleared": None,
        "payee": None,
        "payee_address": None,
        "category": {
            "name": "Test Category",
            "desc": None,
            "tax_related": None,
            "category_type": "expense",
            "budget_amount": None,
            "tax_schedule_info": None,
            "hierarchy": "Test Category",
            "children": [],
            "parent": None,
        },
        "check_number": None,
        "reimbursable_expense": None,
        "small_business_expense": None,
        "to_account": "Test To Account",
        "first_payment_date": None,
        "loan_length": None,
        "num_payments": None,
        "periods_per_annum": None,
        "interest_rate": None,
        "current_loan_balance": None,
        "original_loan_amount": None,
        "line_number": None,
        "splits": [],
    }


def test_to_dict_with_ignore():
    """Test converting a category to a dict with ignored fields"""
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        to_account="Test To Account",
        category=Category(name="Test Category"),
    )
    assert transaction.to_dict(ignore=["to_account"]) == {
        "date": datetime(2022, 2, 1, 0, 0),
        "amount": Decimal("1000"),
        "memo": None,
        "cleared": None,
        "payee": None,
        "payee_address": None,
        "category": {
            "name": "Test Category",
            "desc": None,
            "tax_related": None,
            "category_type": "expense",
            "budget_amount": None,
            "tax_schedule_info": None,
            "hierarchy": "Test Category",
            "children": [],
            "parent": None,
        },
        "check_number": None,
        "reimbursable_expense": None,
        "small_business_expense": None,
        "first_payment_date": None,
        "loan_length": None,
        "num_payments": None,
        "periods_per_annum": None,
        "interest_rate": None,
        "current_loan_balance": None,
        "original_loan_amount": None,
        "line_number": None,
        "splits": [],
    }


def test_from_list_zero_value_with_splits():
    """Test creating a zero-value transaction from a list of QIF strings with
    splits

    Relates to issue #31.
    https://github.com/isaacharrisholt/quiffen/issues/31
    """
    qif_list = [
        "D2022-02-01",
        "T0",
        "L[Test To Account]",  # Brackets denote to account
        "LTest Category",  # No brackets denote category
        "STest Split Category 1",
        "ETest Split Memo",
        "T0",
        "STest Split Category 2",
        "EMemo",
        "$0",
    ]
    transaction, _ = Transaction.from_list(qif_list)
    assert transaction.date == datetime(2022, 2, 1)
    assert transaction.amount == 0
    assert transaction.to_account == "Test To Account"
    assert transaction.category == Category(name="Test Category")
    assert transaction.is_split
    assert transaction.splits == [
        Split(
            category=Category(name="Test Split Category 1"),
            memo="Test Split Memo",
            amount=0,
            percent=None,
        ),
        Split(
            category=Category(name="Test Split Category 2"),
            memo="Memo",
            amount=0,
            percent=None,
        ),
    ]


def test_check_number_allows_strings():
    """Test that the check number field allows strings

    Relates to issue #28.
    https://github.com/isaacharrisholt/quiffen/issues/28
    """
    transaction = Transaction(
        date=datetime(2022, 2, 1),
        amount=1000,
        to_account="Test To Account",
        category=Category(name="Test Category"),
        check_number="Transfer",
    )
    assert transaction.check_number == "Transfer"


def test_from_list_invalid_characters_in_amount_field():
    """Test that the amount field correctly parses out invalid
    characters (non-numeric).

    Relates to issue #56.
    https://github.com/isaacharrisholt/quiffen/issues/56
    """
    qif_list = [
        "D2022-02-01",
        "T$1,0ab£c00",
        "L[Test To Account]",  # Brackets denote to account
        "LTest Category 1",
        "LTest Category 2",
    ]
    transaction, _ = Transaction.from_list(qif_list)
    assert transaction.amount == 1000
