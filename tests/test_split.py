from datetime import datetime
from decimal import Decimal

from quiffen.core.category import Category
from quiffen.core.split import Split


def test_create_split():
    """Test creating a split"""
    split = Split()
    assert split.amount is None
    assert split.memo is None
    assert split.category is None

    split2 = Split(amount=Decimal(100), memo="Test Memo")
    assert split2.amount == 100
    assert split2.memo == "Test Memo"
    assert split2.category is None

    split3 = Split(
        amount=Decimal(100),
        memo="Test Memo",
        category=Category(name="Test Category"),
    )
    assert split3.amount == 100
    assert split3.memo == "Test Memo"
    assert split3.category is not None
    assert split3.category.name == "Test Category"


def test_eq_success():
    """Test that two splits are equal"""
    split = Split(amount=Decimal(100), memo="Test Memo")
    split2 = Split(amount=Decimal(100), memo="Test Memo")
    assert split == split2


def test_eq_failure():
    """Test that two splits are not equal"""
    split = Split(amount=Decimal(100), memo="Test Memo")
    split2 = Split(amount=Decimal(100), memo="Test Memo2")
    assert split != split2


def test_str_method():
    """Test the string representation of a split"""
    split = Split(amount=Decimal(100), memo="Test Memo")
    assert str(split) == "\n\tSplit:\n\t\tAmount: 100\n\t\tMemo: Test Memo"

    split2 = Split(
        amount=Decimal(100),
        memo="Test Memo",
        category=Category(name="Test Category"),
    )
    assert str(split2) == (
        "\n\tSplit:\n\t\tAmount: 100\n\t\tMemo: Test Memo\n\t\tCategory: Test Category"
    )


def test_to_qif():
    """Test the to_qif method"""
    split = Split(amount=Decimal(100), memo="Test Memo")
    assert split.to_qif() == ("S\nETest Memo\n$100\n")

    test_category = Category(name="Test Category")

    split2 = Split(
        amount=Decimal(100),
        memo="Test Memo",
        category=test_category,
        date=datetime(2019, 1, 1),
        cleared="True",
        check_number=123,
        percent=Decimal(50),
        to_account="Test Account",
        payee_address="Test Address",
    )
    assert split2.to_qif() == (
        "STest Category\n"
        "ETest Memo\n"
        "$100\n"
        "D2019-01-01\n"
        "CTrue\n"
        "L[Test Account]\n"
        "N123\n"
        "%50%\n"
        "ATest Address\n"
    )


def test_to_qif_zero_amount():
    """Test the to_qif method with a zero amount"""
    split = Split(amount=Decimal('0.00'), memo="Free Thing")
    assert split.to_qif() == ("S\nEFree Thing\n$0.00\n")
    split = Split(amount=Decimal(0), memo="Free Thing")
    assert split.to_qif() == ("S\nEFree Thing\n$0\n")
    split = Split(amount=None, memo="Free Thing")
    assert split.to_qif() == ("S\nEFree Thing\n")

    thing_category = Category(name="Things")

    split2 = Split(
        amount=0,
        memo="Thing 1",
        category=thing_category,
        date=datetime(2026, 1, 1),
        cleared="True",
        check_number=4321,
        percent=Decimal(75),
        to_account="Thing Account",
        payee_address="Thing Destination",
    )
    assert split2.to_qif() == (
        "SThings\n"
        "EThing 1\n"
        "$0\n"
        "D2026-01-01\n"
        "CTrue\n"
        "L[Thing Account]\n"
        "N4321\n"
        "%75%\n"
        "AThing Destination\n"
    )


def test_to_dict():
    """Test the to_dict method"""
    split = Split(amount=Decimal(100), memo="Test Memo")
    assert split.to_dict() == {
        "amount": 100,
        "memo": "Test Memo",
        "category": None,
        "check_number": None,
        "cleared": None,
        "date": None,
        "percent": None,
        "to_account": None,
        "payee_address": None,
    }

    test_category = Category(name="Test Category")

    split2 = Split(
        amount=Decimal(100),
        memo="Test Memo",
        category=test_category,
    )
    assert split2.to_dict() == {
        "amount": 100,
        "memo": "Test Memo",
        "category": test_category.to_dict(),
        "check_number": None,
        "cleared": None,
        "date": None,
        "percent": None,
        "to_account": None,
        "payee_address": None,
    }


def test_to_dict_zero_amount():
    """Test the to_dict method"""
    split = Split(amount=Decimal('0.00'), memo="Test Memo")
    assert split.to_dict() == {
        "date": None,
        "amount": Decimal('0.00'),
        "memo": "Test Memo",
        "cleared": None,
        "category": None,
        "to_account": None,
        "check_number": None,
        "percent": None,
        "payee_address": None,
    }

    test_category = Category(name="Thing Category")

    split2 = Split(
        amount=Decimal(0),
        memo="Thing 1",
        category=test_category,
    )
    assert split2.to_dict() == {
        "date": None,
        "amount": Decimal('0'),
        "memo": "Thing 1",
        "cleared": None,
        "category": test_category.to_dict(),
        "to_account": None,
        "check_number": None,
        "percent": None,
        "payee_address": None,
    }

    split3 = Split(
        memo="Thing 1",
        category=test_category,
    )
    assert split3.to_dict() == {
        "date": None,
        "amount": None,
        "memo": "Thing 1",
        "cleared": None,
        "category": test_category.to_dict(),
        "to_account": None,
        "check_number": None,
        "percent": None,
        "payee_address": None,
    }


def test_to_dict_with_ignore():
    """Test the to_dict method with ignore"""
    split = Split(amount=Decimal(100), memo="Test Memo")
    assert split.to_dict(ignore={"memo"}) == {
        "amount": 100,
        "category": None,
        "check_number": None,
        "cleared": None,
        "date": None,
        "percent": None,
        "to_account": None,
        "payee_address": None,
    }

    test_category = Category(name="Test Category")

    split2 = Split(
        amount=Decimal(100),
        memo="Test Memo",
        category=test_category,
    )
    assert split2.to_dict(ignore={"memo", "category"}) == {
        "amount": 100,
        "check_number": None,
        "cleared": None,
        "date": None,
        "percent": None,
        "to_account": None,
        "payee_address": None,
    }
