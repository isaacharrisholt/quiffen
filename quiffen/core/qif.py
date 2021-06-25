from quiffen.core.transactions import Transaction, Investment, TransactionList
from quiffen.core.categories_classes import Category, Class
from quiffen.core.accounts import Account
from quiffen import utils

try:
    import pandas as pd
    PANDAS_INSTALLED = True
except ModuleNotFoundError:
    PANDAS_INSTALLED = False

VALID_TRANSACTION_ACCOUNT_TYPES = [
    '!Type:Cash',
    '!Type:Bank',
    '!Type:Ccard',
    '!Type:Oth A',
    '!Type:Oth L',
    '!Type:Invoice'
]


class ParserException(Exception):
    pass


class Qif:
    """
    The main class of the package. For parsing QIF files.

    Parameters
    ----------

    """
    def __init__(self,
                 accounts: dict = None,
                 categories: dict = None,
                 classes: list = None
                 ):
        self._assert_type(accounts, Account)
        self._assert_type(categories, Category)
        self._assert_type(classes, Class)

        self._accounts = accounts
        self._categories = categories
        self._classes = classes

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return f"""
QIF:
    Accounts: {[repr(account for account in self._accounts)]}
    Categories: {[repr(cat) for cat in self._categories]}
    Classes: {[repr(klass) for klass in self._classes]}
"""

    def __repr__(self):
        return f'Qif(accounts={[repr(account for account in self._accounts)]}, ' \
               f'day_first={[repr(cat) for cat in self._categories]}, ' \
               f'separator={[repr(klass) for klass in self._classes]})'

    @property
    def accounts(self):
        return self._accounts

    @accounts.setter
    def accounts(self, new_accounts):
        self._assert_type(new_accounts, Account)
        self._accounts = new_accounts

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, new_categories):
        self._assert_type(new_categories, Category)
        self._categories = new_categories

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, new_classes):
        self._assert_type(new_classes, Class)
        self._classes = new_classes

    @classmethod
    def parse(cls, filepath, separator='\n', day_first=True):
        data = cls._read_qif(filepath)

        accounts = {}
        last_account = None
        categories = {}
        classes = []

        sections = data.split('^\n')
        last_header = None

        for section in sections:
            if not section:
                continue

            header_line = section.split('\n')[0]
            if header_line is None:
                continue

            # Check for new categories and accounts first, as then we can be sure it's a transaction in case a default
            # account needs to be added
            if header_line[0] != '!':
                if last_header is None:
                    raise ParserException(f'Header \'{header_line}\' not recognised and no previous header supplied')
                header_line = last_header

            if '!Type:Cat' in header_line:
                # Section contains category information
                new_category = Category.from_string(section)
                categories = utils.create_categories(new_category, categories)
            elif '!Type:Class' in header_line:
                new_class = Class.from_string(section)
                classes.append(new_class)
            elif '!Account' in header_line:
                new_account = Account.from_string(section)
                accounts[new_account.name] = new_account
                last_account = new_account.name
            elif '!Type' in header_line and not accounts:
                # Accounts is empty and there's a transaction, so create default account to put transactions in
                default_account = Account(name='Quiffen Default Account',
                                          desc='The default account created by Quiffen when no other accounts were '
                                               'present')
                accounts[default_account.name] = default_account
                last_account = default_account.name
            elif '!Type:Invst' in header_line:
                # Investment
                new_investment = Investment.from_string(section, separator=separator, day_first=day_first)
                accounts[last_account].add_transaction(new_investment, 'Invst')
            elif header_line in VALID_TRANSACTION_ACCOUNT_TYPES:
                # Other transaction type
                new_transaction, new_categories, new_classes = Transaction.from_string(section, separator=separator,
                                                                                       day_first=day_first)
                accounts[last_account].add_transaction(new_transaction, header_line)
                categories.update(new_categories)
                classes.extend(new_classes)

            last_header = header_line

        return cls(accounts=accounts, categories=categories, classes=classes)

    @staticmethod
    def _assert_type(iterable, types):
        """Assert that all items in a list are of specific types"""
        if isinstance(iterable, dict):
            for item in iterable.values():
                if not isinstance(item, types):
                    raise TypeError(f'\'{repr(item)} is not of type {types}')
        else:
            for item in iterable:
                if not isinstance(item, types):
                    raise TypeError(f'\'{repr(item)} is not of type {types}')

    @staticmethod
    def _read_qif(path):
        """Validate QIF file provided and return data."""
        if path[-3:].lower() != 'qif':
            raise FileNotFoundError(f'\'{path}\' does not point to a valid QIF file. Only .QIF file types are allowed')

        with open(path, 'r') as f:
            data = f.read()
            if not data:
                raise ParserException('File is empty')

        return data

    def add_account(self, new_account):
        """Add a new account to the object"""
        self._assert_type([new_account], Account)
        self._accounts[new_account.name] = new_account

    def add_category(self, new_category):
        """Add a new category to the object"""
        self._assert_type([new_category], Category)
        self._categories[new_category.name] = new_category

    def add_class(self, new_class):
        """Add a new class to the object"""
        self._assert_type([new_class], Class)
        self._classes[new_class.name] = new_class

    def to_dicts(self, ignore=None, dictify_splits=True):
        """Return a list of dict representations of transactions."""
        if ignore is None:
            ignore = []

        res = {}

        return [transaction.to_dict(ignore=ignore) for transaction in self._transactions]

    def to_csv(self, path, ignore=None):
        """Write a CSV file containing all transaction data."""
        if ignore is None:
            ignore = []

        properties = [key for key in self._transactions[0].__dict__.keys() if key.replace('_', '') not in ignore]

        with open(path, 'w') as f:
            f.write(','.join([property_name.strip('_').replace('_', ' ').title() for property_name in properties])
                    + '\n')

            for transaction in self._transactions:
                f.write(','.join([str(transaction.__dict__[property_name]) for property_name in properties]) + '\n')

    def to_dataframe(self, ignore=None):
        """Return a pandas DataFrame containing all transaction data."""
        if ignore is None:
            ignore = []

        if not PANDAS_INSTALLED:
            raise ModuleNotFoundError('The pandas module must be installed to use this method')
        return pd.DataFrame(self.to_dicts(ignore=ignore))
