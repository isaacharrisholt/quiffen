from datetime import datetime
from decimal import Decimal

from quiffen.core.transactions import Transaction, TransactionList
from quiffen.utils import parse_date

VALID_ACCOUNT_TYPES = [
    'Cash',
    'Bank',
    'CCard',
    'Oth A',
    'Oth L',
    'Invoice',
    'Invst'
]


class Account:
    """
    A class representing a QIF account.

    Attributes
    ----------
    transactions : dict
        A dict of header strings as keys and TransactionList objects as values.
    last_header : {None, 'Cash', 'Bank', 'CCard', 'Oth A', 'Oth L', 'Invoice', 'Invst'}
        The last transaction header used. This must be set before transactions can be added.

    Examples
    --------
    Creating an Account instance, then adding a transaction.

    >>> import quiffen
    >>> from datetime import datetime
    >>> acc = quiffen.Account(name='Example name', desc='Some description')
    >>> acc
    Account(name='Example name', desc='Some description')
    >>> tr = quiffen.Transaction(date=datetime.now(), amount=150.0)
    >>> acc.last_header = 'Bank'
    >>> acc.add_transaction(tr)
    >>> acc.transactions
    {'Bank': TransactionList(Transaction(date=datetime.datetime(2021, 7, 2, 18, 31, 47, 817025), amount=150.0))}

    Creating an account instance from a section list in a QIF file.

    >>> import quiffen
    >>> string = '!Account\\nNPersonal Bank Account\\nDMy Personal bank account with Barclays.\\n^\\n'
    >>> acc = quiffen.Account.from_string(string)
    >>> acc
    Account(name='Personal Bank Account', desc='My Personal bank account with Barclays.')
    """

    def __init__(self,
                 name: str,
                 desc: str = None,
                 account_type: str = None,
                 credit_limit: Decimal = None,
                 balance: Decimal = None,
                 date_at_balance: datetime = None
                 ):
        """Initialise an instance of the Account class.

        Parameters
        ----------
        name : str
            The name of the account.
        desc : str, default=None
            A description of the account.
        account_type : {None, 'Cash', 'Bank', 'CCard', 'Oth A', 'Oth L', 'Invoice', 'Invst'}
            The type of account specified in the QIF file. Relates to the type of transactions stored in the account,
            but not on a functional level.
        credit_limit : decimal.Decimal, default=None
            The credit limit on the account.
        balance : decimal.Decimal, default=None
            The balance in the account at `date_at_balance`.
        date_at_balance: datetime.datetime, default=None
            The date at which `balance` was recorded.
        """
        self._name = name
        self._desc = desc

        if account_type and account_type not in VALID_ACCOUNT_TYPES:
            raise ValueError(f'\'{account_type}\' is not a valid account type. Valid account types are '
                             f'{VALID_ACCOUNT_TYPES}')

        self._account_type = account_type
        self._credit_limit = credit_limit
        self._balance = balance
        self._date_at_balance = date_at_balance

        self._transactions = {}
        self._last_header = None

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return self._name == other.name

    def __str__(self):
        properties = ''
        ignore = ['_transactions', '_last_header']
        for (object_property, value) in self.__dict__.items():
            if value and object_property not in ignore:
                properties += f'\n    {object_property.strip("_").replace("_", " ").title()}: {value}'

        return 'Account:' + properties

    def __repr__(self):
        properties = ''
        ignore = ['_transactions', '_last_header']
        for (object_property, value) in self.__dict__.items():
            if value and object_property not in ignore:
                properties += f'{object_property.strip("_")}={repr(value)}, '

        properties = properties.strip(', ')
        return f'Account({properties})'

    @property
    def name(self):
        """"""
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = str(new_name)

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, new_desc):
        self._desc = str(new_desc)

    @property
    def account_type(self):
        return self._account_type

    @account_type.setter
    def account_type(self, new_type):
        if new_type not in VALID_ACCOUNT_TYPES:
            raise ValueError('Invalid account type')
        self._account_type = str(new_type)

    @property
    def credit_limit(self):
        return self._credit_limit

    @credit_limit.setter
    def credit_limit(self, new_limit):
        self._credit_limit = Decimal(new_limit)

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, new_balance):
        self._balance = Decimal(new_balance)

    @property
    def date_at_balance(self):
        return self._date_at_balance

    @date_at_balance.setter
    def date_at_balance(self, new_date):
        date = parse_date(new_date)
        self._date_at_balance = date

    @property
    def transactions(self):
        return self._transactions

    @transactions.setter
    def transactions(self, new_transactions):
        transactions = TransactionList(*new_transactions)
        self._transactions = transactions

    @property
    def last_header(self):
        return self._last_header

    @last_header.setter
    def last_header(self, new_header):
        if new_header not in VALID_ACCOUNT_TYPES:
            raise ValueError('Invalid header')
        self._last_header = str(new_header)

    @classmethod
    def from_list(cls, lst, day_first=True):
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the account.
        day_first : bool, default=True
             Whether the day or month comes first in the date.

        Returns
        -------
        Account
            An Account object created from the QIF strings.
        """
        kwargs = {}
        for field in lst:
            field = field.replace('\n', '')

            if not field:
                continue

            line_code = field[0]

            try:
                field_info = field[1:]
            except KeyError:
                field_info = ''

            # Check the QIF line code for banking-related operations, then append to kwargs.
            if line_code == '!':
                continue
            elif line_code == 'N':
                kwargs['name'] = field_info
            elif line_code == 'D':
                kwargs['desc'] = field_info
            elif line_code == 'T':
                kwargs['account_type'] = field_info
            elif line_code == 'L':
                kwargs['credit_limit'] = Decimal( field_info.replace(',', ''))
            elif line_code == '$' or line_code == '£':
                kwargs['balance'] = Decimal( field_info.replace(',', ''))
            elif line_code == '/':
                balance_date = parse_date(field_info, day_first)
                kwargs['date_at_balance'] = balance_date

        return cls(**kwargs)

    @classmethod
    def from_string(cls, string, separator='\n', day_first=True):
        """Return a class instance from a QIF file section string.

        Parameters
        ----------
        string : str
            The string containing the QIF-formatted data.
        separator : str, default='\n'
             The line separator for the QIF file. This probably won't need changing.
        day_first : bool, default=True
             Whether the day or month comes first in the date.

        Returns
        -------
        Account
            An Account object created from the QIF strings.
        """
        property_list = string.split(separator)
        return cls.from_list(property_list, day_first)

    def add_transaction(self, transaction, header=None):
        """Add a transaction to the dict of TransactionList objects.

        Parameters
        ----------
        transaction : Transaction or Investment
            The Transaction-type object to be added.
        header : {None, 'Cash', 'Bank', 'CCard', 'Oth A', 'Oth L', 'Invoice', 'Invst'}
             The header under which the transaction falls. Will be used as a key in the dict of transactions.

        Raises
        -------
        RuntimeError
            If there is no header provided, and no ``last_header`` set.
        """
        if not header and not self._last_header:
            raise RuntimeError('No header provided and no last header present')
        elif not header:
            header = self._last_header
        else:
            header = header.split(':')[-1]
            self._last_header = header

        if header not in self._transactions:
            self._transactions[header] = TransactionList()

        self._transactions[header].append(transaction)

    def to_dict(self, ignore=None, dictify_transactions=True, dictify_splits=True):
        """Return a dict object representing the Account.

        Parameters
        ----------
        ignore : list of str, default=None
             A list of strings of parameters that should be excluded from the dict.
        dictify_transactions : bool, default=True
             Whether the Transaction objects should be converted to dicts or left as they are.
        dictify_splits : bool, default=True
             Whether Splits within Transaction objects should be converted to dicts or left as they are.

        Returns
        -------
        dict
            A dict representing the Account object.
        """
        if ignore is None:
            ignore = []

        res = {key.strip('_'): value for (key, value) in self.__dict__.items()
               if value is not None and key.strip('_') not in ignore}

        if dictify_transactions and 'transactions' not in ignore:
            dicted_transactions = {}
            for (header, tl) in self._transactions.items():
                dict_list = [transaction.to_dict(ignore=ignore, dictify_splits=dictify_splits) for transaction in tl]
                dicted_transactions[header] = dict_list
            res['transactions'] = dicted_transactions

        return res
