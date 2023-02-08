Quiffen
========

.. content

Quiffen is a Python package for parsing QIF (Quicken Interchange Format) files.

The package allows users to both read QIF files and interact with the contents, and also to create a QIF structure
and then output to either a QIF file, a CSV of transaction data or a pandas DataFrame.

QIF is an old file type, but has its merits because:

- It's standardised (apart from dates, but that can be dealt with)

  - Unlike CSVs, QIF files all follow the same format, so they don't require special attention when they come from
    different sources

- It's written in plain text

Features
--------

- Import QIF files and manipulate data
- Create QIF structures (support for Transactions, Investments, Accounts, Categories, Classes, Splits)
- Convert Qif objects to a number of different formats and export (pandas DataFrame, CSV, QIF file)

Usage
------

Here's an example parsing of a QIF file:

>>> from quiffen import Qif, QifDataType
>>> import decimal
>>> qif = Qif.parse('test.qif', day_first=False)
>>> qif.accounts
{'Quiffen Default Account': Account(name='Quiffen Default Account', desc='The default account created by Quiffen when no
other accounts were present')}
>>> acc = qif.accounts['Quiffen Default Account']
>>> acc.transactions
{'Bank': TransactionList(Transaction(date=datetime.datetime(2021, 2, 14, 0 , 0), amount=decimal.Decimal(150.0), ...), ...),
'Invst': TransactionList(...)}
>>> tr = acc.transactions['Bank'][0]
>>> print(tr)
Transaction:
    Date: 2020-02-14 00:00:00
    Amount: 67.5
    Payee: T-Mobile
    Category: Cell Phone
    Split Categories: ['Bills']
    Splits: 2 total split(s)
>>> qif.categories
{'Bills': Category(name='Bills), expense=True, hierarchy='Bills'}
>>> bills = qif.categories['Bills']
>>> print(bills.render_tree())
Bills (root)
└─ Cell Phone
>>> df = qif.to_dataframe(data_type=QifDataType.TRANSACTIONS)
>>> df.head()
        date  amount           payee  ...                           memo cleared check_number
0 2020-02-14    67.5        T-Mobile  ...                            NaN     NaN          NaN
1 2020-02-14    32.0  US Post Office  ...  money back for damaged parcel     NaN          NaN
2 2020-12-02   -10.0          Target  ...        two transactions, equal     NaN          NaN
3 2020-11-02   -25.0         Walmart  ...          non split transaction       X        123.0
4 2020-10-02  -100.0      Amazon.com  ...                   test order 1       *          NaN
...

And here's an example of creating a QIF structure and exporting to a QIF file:

>>> import quiffen
>>> from datetime import datetime
>>> qif = quiffen.Qif()
>>> acc = quiffen.Account(name='Personal Bank Account', desc='My personal bank account with Barclays.')
>>> qif.add_account(acc)
>>> groceries = quiffen.Category(name='Groceries')
>>> essentials = quiffen.Category(name='Essentials')
>>> groceries.add_child(essentials)
>>> qif.add_category(groceries)
>>> tr = quiffen.Transaction(date=datetime.now(), amount=150.0)
>>> acc.add_transaction(tr, header=quiffen.AccountType.BANK)
>>> qif.to_qif()  # If a path is provided, this will save the file too!
'!Type:Cat\nNGroceries\nETrue\nIFalse\n^\nNGroceries:Essentials\nETrue\nIFalse\n^\n!Account\nNPersonal Bank Account\nDMy
personal bank account with Barclays.\n^\n!Type:Bank\nD02/07/2021\nT150.0\n^\n'

Documentation
-------------

Documentation can be found at: https://quiffen.readthedocs.io/en/latest/

Installation
------------

Install Quiffen by running:

>>> pip install quiffen

Dependencies
------------

- `pandas <https://pypi.org/project/pandas/>`_ (optional) for exporting to DataFrames

  - The ``to_dataframe()`` method will not work without pandas installed.

To-Dos
------

- Add support for the ``MemorizedTransaction`` object present in QIF files.

Contribute
----------

GitHub pull requests welcome, though if you want to make a major change, please open an issue first for discussion.

- Issue Tracker: https://github.com/isaacharrisholt/quiffen/issues
- Source Code: https://github.com/isaacharrisholt/quiffen

Support
-------

If you are having issues, please let me know.

License
-------

The project is licensed under the GNU GPLv3 license.
