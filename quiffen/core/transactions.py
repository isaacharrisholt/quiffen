from abc import ABC
from datetime import datetime
import collections


class Transaction(object):
    """
    A class used to represent a transaction.

    Parameters
    ----------
    date : datetime
        Date transaction occurred. May not include timestamp.
    amount : float
        The amount of the transaction. May be positive or negative.
    memo : str
        Also known as the reference. A string describing the purpose behind the transaction.
    payee : str
        The name of the payee on the other end of the transaction. The payee is the receiver of the money if amount is
        negative, else they are the sender of the money.
    payee_address : str
        The address of the aforementioned payee.
    category : str
        The category under which the transaction falls. E.g. 'groceries' or 'shopping'.
    check_number : int
        The check number if the transaction relates to a check
    flag : bool
        Whether or not this transaction is flagged as a reimbursable business expense.

    Notes
    -----
    In future updates, Transaction may become the parent class for other transaction types that can be stored in QIF
    files, such as BankTransaction, InvestmentTransaction or SplitTransaction.
    """
    def __init__(self,
                 date: datetime,
                 amount: float,
                 memo: str = None,
                 payee: str = None,
                 payee_address: str = None,
                 category: str = None,
                 check_number: int = None,
                 flag: bool = None
                 ):
        self._date = date
        self._amount = amount
        self._memo = memo
        self._payee = payee
        self._payee_address = payee_address
        self._category = category
        self._check_number = check_number
        self._flag = flag

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False

        return self.__dict__ == other.__dict__

    def __str__(self):
        properties = ''
        for object_property in self.__dict__:
            properties += f'\n    {object_property.strip("_").replace("_", " ").title()}: ' \
                          f'{self.__dict__[object_property]}'

        return 'Transaction:' + properties

    def __repr__(self):
        properties = ''
        for object_property in self.__dict__:
            if self.__dict__[object_property] is not None:
                properties += f'{object_property.strip("_")}={repr(self.__dict__[object_property])}, '

        properties = properties.strip(', ')
        return f'Transaction({properties})'

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, new_date):
        if not isinstance(new_date, datetime):
            raise TypeError(f'New date must be datetime object')
        self._date = new_date

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, new_amount):
        try:
            self._amount = float(new_amount)
        except ValueError:
            raise TypeError('Amount can only be int or float')

    @property
    def memo(self):
        return self._memo

    @memo.setter
    def memo(self, new_memo):
        self._memo = str(new_memo)

    @property
    def payee(self):
        return self._payee

    @payee.setter
    def payee(self, new_payee):
        self._payee = str(new_payee)

    @property
    def payee_address(self):
        return self._payee_address

    @payee_address.setter
    def payee_address(self, new_payee_address):
        self._payee_address = str(new_payee_address)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, new_category):
        self._category = str(new_category)

    @property
    def check_number(self):
        return self._check_number

    @check_number.setter
    def check_number(self, new_number):
        try:
            new_number = int(new_number)

            if new_number <= 0:
                raise ValueError
        except ValueError:
            raise TypeError('Check number must be a positive integer')

    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, new_flag):
        try:
            self._flag = bool(new_flag)
        except ValueError:
            raise TypeError('Flag must be a boolean')

    @staticmethod
    def _parse_date(date_string, day_first=True):
        """Parse a string date of an unknown format and return a datetime object."""
        day_first_patterns = ['%d/%m/%Y',
                              '%d-%m-%Y',
                              '%d/%m/%y',
                              '%d-%m-%y',
                              '%d %B %Y',
                              '%d %B %y',
                              '%d %b %Y',
                              '%d %b %y']

        month_first_patterns = ['%m/%d/%Y',
                                '%m-%d-%Y',
                                '%m/%d/%y',
                                '%m-%d-%y',
                                '%B %d %Y',
                                '%B %d %y',
                                '%b %d %Y',
                                '%b %d %y']

        if day_first:
            date_patterns = day_first_patterns + month_first_patterns
        else:
            date_patterns = month_first_patterns + day_first_patterns

        for pattern in date_patterns:
            try:
                return datetime.strptime(date_string, pattern)
            except ValueError:
                pass

        raise ValueError(f'Date string \'{date_string}\' is not in a recognised format.')

    @classmethod
    def from_list(cls, lst, day_first=True):
        """Return a class instance from a list of properties as found in a QIF file."""
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
            if line_code == 'D':
                transaction_date = cls._parse_date(field_info, day_first)
                kwargs['date'] = transaction_date
            elif line_code == 'T' or line_code == 'U':
                kwargs['amount'] = float(field_info)
            elif line_code == 'M':
                kwargs['memo'] = field_info
            elif line_code == 'P':
                kwargs['payee'] = field_info
            elif line_code == 'A':
                kwargs['payee_address'] = field_info
            elif line_code == 'L':
                kwargs['category'] = field_info
            elif line_code == 'L':
                kwargs['check_number'] = int(field_info)
            elif line_code == 'F':
                kwargs['flag'] = True

        return cls(**kwargs)

    @classmethod
    def from_string(cls, string, separator='\n', day_first=True):
        """Return a class instance from a string of properties separated by separator."""
        property_list = string.split(separator)
        return cls.from_list(property_list, day_first)

    def to_dict(self, ignore=None):
        """Return a dictionary representation of the Transaction instance."""
        if ignore is None:
            ignore = []
        return {key.strip('_'): value for (key, value) in self.__dict__.items()
                if value is not None and key.strip('_') not in ignore}


class TransactionList(collections.MutableSequence, ABC):
    """
    A class to store Transaction objects only in an ordered list.

    Parameters
    ----------
    args : Transaction(s)
        Transactions to be put in the list.
    """
    def __init__(self, *args):
        self._list = []
        self.extend(list(args))

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        return self._list[key]

    def __delitem__(self, key):
        del self._list[key]

    def __setitem__(self, key, value):
        self._check_if_transaction(value)
        self._list[key] = value

    def __str__(self):
        return str(self._list)

    def __repr__(self):
        return f'TransactionList({", ".join(self._list)})'

    def insert(self, key, value):
        self._check_if_transaction(value)
        self.list.insert(key, value)

    @staticmethod
    def _check_if_transaction(item):
        """Check if a given item is an instance of the Transaction class and raise an error if not"""
        if not isinstance(item, Transaction):
            raise TypeError(f'Only Transaction objects can be appended to a TransactionList')

    @property
    def list(self):
        return self._list

    @list.setter
    def list(self, new_list):
        for item in new_list:
            self._check_if_transaction(item)
        self._list = new_list
