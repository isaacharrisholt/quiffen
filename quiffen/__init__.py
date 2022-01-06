"""
Quiffen is a Python package for parsing QIF (Quicken Interchange Format) files.

The package allows users to both read QIF files and interact with the contents, and also to create a QIF structure
and then output to either a QIF file, a CSV of transaction data or a pandas DataFrame.
"""
from quiffen.core.qif import Qif
from quiffen.core.transactions import Transaction, Investment, TransactionList, Split
from quiffen.core.accounts import Account
from quiffen.core.categories_classes import Category, Class


def init():
    import decimal
    context = decimal.Context(prec=2, rounding=decimal.ROUND_05UP)
    decimal.setcontext(context)


init()
