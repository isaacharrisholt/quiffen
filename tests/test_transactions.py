from datetime import datetime
from decimal import Decimal

from quiffen.core.transactions import Split, Transaction
from quiffen.utils import parse_date


def test_equality():
    date_obj = parse_date('01/06/2021')
    trans1 = Transaction(date_obj, Decimal(150))
    trans2 = Transaction(date_obj, Decimal(150))
    assert trans1 == trans2

    date_obj1 = parse_date('01/06/2021')
    date_obj2 = parse_date('01/06/2021', False)
    trans1 = Transaction(date_obj1, Decimal(150))
    trans2 = Transaction(date_obj2, Decimal(150))
    assert trans1 != trans2


def test_str():
    date_obj = parse_date('01/06/2021')
    trans = Transaction(date_obj, Decimal(150))
    print(trans)


def test_repr():
    date_obj = parse_date('01/06/2021')
    trans = Transaction(date_obj, Decimal('-150.60'))
    print(repr(trans))


def test_parse_date():
    date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
    assert parse_date('01/06/2021') == date_obj

    date_obj = datetime.strptime('06/01/2021', '%m/%d/%Y')
    assert parse_date('06/01/2021', False) == date_obj

    date_obj = datetime.strptime('Jan 01 21', '%b %d %y')
    assert parse_date('Jan 01 21', False) == date_obj

    date_obj = datetime.strptime('01 Jan 21', '%d %b %y')
    assert parse_date('01 Jan 21') == date_obj


def test_from_list():
    lst = ['D01/06/2021', 'T-150.60', 'PMe', 'MMemo']
    date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
    tr, _, _ = Transaction.from_list(lst)
    assert tr == Transaction(
        date=date_obj,
        amount=Decimal('-150.60'),
        payee='Me',
        memo='Memo',
    )


def test_from_string():
    string = 'D01/06/2021\nT-150.60\nPMe\nMMemo'
    date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
    tr, _, _ = Transaction.from_string(string)
    assert tr == Transaction(
        date=date_obj,
        amount=Decimal('-150.60'),
        payee='Me',
        memo='Memo',
    )

    string = 'D01/06/2021_T-150.60_PMe_MMemo'
    date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
    tr, _, _ = Transaction.from_string(string, separator='_')
    assert tr == Transaction(
        date=date_obj,
        amount=Decimal('-150.60'),
        payee='Me',
        memo='Memo',
    )


def test_multiple_categories():
    lst = ['D01/06/2021', 'T-150.60', 'PMe', 'MMemo', 'LReptile', 'LLizard']
    _, categories, _ = Transaction.from_list(lst)
    assert categories['Reptile'].children[0].name == 'Lizard'


def test_add_remove_split():
    date_obj = datetime.strptime('01/06/2021', '%d/%m/%Y')
    tr = Transaction(date=date_obj, amount=Decimal(150.0), payee='Me')
    split = Split(amount=Decimal(50))
    assert not tr.is_split

    tr.add_split(split)
    assert tr.is_split

    tr.remove_split(amount=30)
    assert tr.is_split

    tr.remove_split(amount=50, date=date_obj)
    assert tr.is_split

    tr.remove_split(amount=50)
    assert not tr.is_split


def test_to_dict():
    date_obj = parse_date('01/06/2021')
    trans = Transaction(date_obj, Decimal(150))
    expected = {'date': date_obj, 'amount': 150}
    assert trans.to_dict() == expected
