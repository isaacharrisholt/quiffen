from abc import ABC
from datetime import datetime
import collections

from quiffen.utils import parse_date, create_categories
from quiffen.core.categories_classes import Category, Class


class Transaction:
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
    reimbursable_expense : bool
        Whether or not this transaction is flagged as a reimbursable business expense.
    """
    def __init__(self,
                 date: datetime,
                 amount: float,
                 memo: str = None,
                 cleared: str = None,
                 payee: str = None,
                 payee_address: str = None,
                 category: str = None,
                 check_number: int = None,
                 reimbursable_expense: bool = None,
                 small_business_expense: bool = None,
                 to_account: str = None,
                 first_payment_date: datetime = None,
                 loan_length: float = None,
                 num_payments: int = None,
                 periods_per_annum: int = None,
                 interest_rate: float = None,
                 current_loan_balance: float = None,
                 original_loan_amount: float = None,
                 splits: list = None
                 ):
        self._date = date
        self._amount = amount
        self._memo = memo
        self._cleared = cleared
        self._payee = payee
        self._payee_address = payee_address
        self._category = category
        self._check_number = check_number
        self._reimbursable_expense = reimbursable_expense
        self._small_business_expense = small_business_expense
        self._to_account = to_account
        self._first_payment_date = first_payment_date
        self._loan_length = loan_length
        self._num_payments = num_payments
        self._periods_per_annum = periods_per_annum
        self._interest_rate = interest_rate
        self._current_loan_balance = current_loan_balance
        self._original_loan_amount = original_loan_amount

        self._split_categories = {}

        if splits:
            self._assert_type(splits, Split)
            self._splits = splits
            self._is_split = True
            self._last_split = splits[-1]
            for split in splits:
                self._split_categories = create_categories(split.category, self._split_categories)
        else:
            self._splits = []
            self._is_split = False
            self._last_split = None

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False

        return self.__dict__ == other.__dict__

    def __str__(self):
        properties = ''
        for (object_property, value) in self.__dict__.items():
            if value:
                properties += f'\n    {object_property.strip("_").replace("_", " ").title()}: {value}'

        return 'Transaction:' + properties

    def __repr__(self):
        properties = ''
        for (object_property, value) in self.__dict__.items():
            if value:
                properties += f'{object_property.strip("_")}={repr(value)}, '

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
        self._assert_type([new_category], Category)
        self._category = new_category

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
    def reimbursable_expense(self):
        return self._reimbursable_expense

    @reimbursable_expense.setter
    def reimbursable_expense(self, new_flag):
        try:
            self._reimbursable_expense = bool(new_flag)
        except ValueError:
            raise TypeError('Flag must be a boolean')

    @property
    def small_business_expense(self):
        return self._small_business_expense

    @small_business_expense.setter
    def small_business_expense(self, new_flag):
        try:
            self._small_business_expense = bool(new_flag)
        except ValueError:
            raise TypeError('Flag must be a boolean')

    @property
    def to_account(self):
        return self._to_account

    @to_account.setter
    def to_account(self, new_account):
        self._to_account = str(new_account)

    @property
    def first_payment_date(self):
        return self._first_payment_date

    @first_payment_date.setter
    def first_payment_date(self, new_date):
        self._first_payment_date = parse_date(new_date)

    @property
    def loan_length(self):
        return self._loan_length

    @loan_length.setter
    def loan_length(self, new_length):
        self._loan_length = float(new_length)

    @property
    def num_payments(self):
        return self._num_payments

    @num_payments.setter
    def num_payments(self, new_num):
        self._num_payments = int(new_num)

    @property
    def periods_per_annum(self):
        return self._periods_per_annum

    @periods_per_annum.setter
    def periods_per_annum(self, new_num):
        self._periods_per_annum = int(new_num)

    @property
    def interest_rate(self):
        return self._interest_rate

    @interest_rate.setter
    def interest_rate(self, new_rate):
        self._interest_rate = float(new_rate)

    @property
    def current_loan_balance(self):
        return self._current_loan_balance

    @current_loan_balance.setter
    def current_loan_balance(self, new_balance):
        self._current_loan_balance = float(new_balance)

    @property
    def original_loan_amount(self):
        return self._original_loan_amount

    @original_loan_amount.setter
    def original_loan_amount(self, new_amount):
        self._original_loan_amount = float(new_amount)

    @property
    def splits(self):
        return self._splits

    @splits.setter
    def splits(self, new_splits):
        self._assert_type(new_splits, Split)
        self._splits = new_splits
        self.refresh_is_split()

    @property
    def is_split(self):
        return self._is_split

    def refresh_is_split(self):
        self._is_split = bool(self._splits)

    @property
    def last_split(self):
        return self._last_split

    @last_split.setter
    def last_split(self, new_split):
        self._assert_type([new_split], Split)
        self._last_split = new_split

    @property
    def split_categories(self):
        return self._split_categories

    @split_categories.setter
    def split_categories(self, new_split_categories):
        self._assert_type(new_split_categories, Category)
        self._split_categories = new_split_categories

    @classmethod
    def from_list(cls, lst, day_first=True):
        """Return a Transaction object from a list of properties as found in a QIF file."""
        kwargs = {}
        categories = {}
        classes = []
        splits = []
        current_split = None
        split_categories = {}
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
            if line_code == 'S':
                new_split = Split()
                category_name = field_info.split(':')[-1]
                new_category = Category(category_name)
                new_category.hierarchy = field_info
                split_categories = create_categories(new_category, split_categories)
                new_split.category = new_category
                splits.append(new_split)
                current_split = new_split
            elif line_code == 'D':
                transaction_date = parse_date(field_info, day_first)
                if not splits:
                    kwargs['date'] = transaction_date
                else:
                    current_split.date = transaction_date
            elif line_code == 'E':
                current_split.memo = field_info
            elif line_code == '$' or line_code == '£':
                current_split.amount = float(field_info)
            elif line_code == '%':
                current_split.percent = float(field_info.split(' ')[0].replace('%', ''))
            elif line_code == 'T' or line_code == 'U':
                if not splits:
                    kwargs['amount'] = float(field_info)
                else:
                    current_split.amount = float(field_info)
            elif line_code == 'M':
                if not splits:
                    kwargs['memo'] = field_info
                else:
                    current_split.memo = field_info
            elif line_code == 'C':
                if not splits:
                    kwargs['cleared'] = field_info
                else:
                    current_split.cleared = field_info
            elif line_code == 'P':
                kwargs['payee'] = field_info
            elif line_code == 'A':
                if not splits:
                    kwargs['payee_address'] = field_info
                else:
                    current_split.payee_address = field_info
            elif line_code == 'L':
                # 'L' can store classes, denoted by '/'
                if '/' in field_info:
                    field_info, class_name = field_info.split('/')[0], field_info.split('/')[1]
                    classes.append(Class(name=class_name))

                # 'L' can represent both categories and the 'to' transfer account
                # Transfer accounts are denoted by [ ] so check for those
                if field_info.startswith('['):
                    if not splits:
                        kwargs['to_account'] = field_info[1:-1]
                    else:
                        current_split.to_account = field_info[1:-1]
                else:
                    category_name = field_info.split(':')[-1]
                    new_category = Category(category_name)
                    new_category.hierarchy = field_info
                    categories = create_categories(new_category, categories)
                    if not splits:
                        kwargs['category'] = new_category
                    else:
                        current_split.category = new_category
            elif line_code == 'N':
                if not splits:
                    kwargs['check_number'] = int(field_info)
                else:
                    current_split.check_number = int(field_info)
            elif line_code == 'F':
                kwargs['reimbursable_expense'] = bool(field_info)
            elif line_code == '1':
                kwargs['first_payment_date'] = parse_date(field_info, day_first)
            elif line_code == '2':
                kwargs['loan_length'] = float(field_info)
            elif line_code == '3':
                kwargs['num_payments'] = int(field_info)
            elif line_code == '4':
                kwargs['periods_per_annum'] = int(field_info)
            elif line_code == '5':
                kwargs['interest_rate'] = float(field_info)
            elif line_code == '6':
                kwargs['current_loan_balance'] = float(field_info)
            elif line_code == '7':
                kwargs['original_loan_amount'] = float(field_info)

        categories.update({name: category for (name, category) in split_categories.items() if name not in categories})
        kwargs['splits'] = splits
        return cls(**kwargs), categories, classes

    @classmethod
    def from_string(cls, string, separator='\n', day_first=True):
        """Return a Transaction object from a string of properties separated by separator."""
        property_list = string.split(separator)
        return cls.from_list(property_list, day_first)

    @staticmethod
    def _assert_type(iterable, types):
        """Assert that all items in a given list are of specific types"""
        if isinstance(iterable, dict):
            for item in iterable.values():
                if not isinstance(item, types):
                    raise TypeError(f'\'{repr(item)} is not of type {types}')
        else:
            for item in iterable:
                if not isinstance(item, types):
                    raise TypeError(f'\'{repr(item)} is not of type {types}')

    def add_split(self, new_split):
        """Add a Split to Transaction"""
        if not isinstance(new_split, Split):
            raise TypeError('Must be a Split object')

        if new_split.percent and sum([split.percent for split in self._splits
                                      if split.percent]) + new_split.percent > 100:
            raise ValueError('Percentage sum of splits cannot add up to more than 100%')

        if new_split.amount and sum([split.amount for split in self._splits if split.amount]) > self._amount:
            raise ValueError('Splits amounts cannot sum to more than Transaction amount')

        self._splits.append(new_split)

    def remove_split(self, multiple=False, **kwargs):
        """Remove Split(s) from Transaction based on given kwargs"""
        kwargs = dict(kwargs)
        indices = []

        for (i, split) in enumerate(self._splits):
            found_split = False
            for (key, value) in kwargs.items():
                if split.__dict__.get(key) != value:
                    found_split = False
                    break
                found_split = True

            if found_split:
                indices.append(i)
                if not multiple:
                    break

        # Reverse so indices in list don't change as items get removed
        for idx in reversed(indices):
            self._splits.pop(idx)

    def to_dict(self, ignore=None, dictify_splits=True):
        """Return a dictionary representation of the Transaction instance."""
        if ignore is None:
            ignore = []

        res = {key.strip('_'): value for (key, value) in self.__dict__.items()
               if value and key.strip('_') not in ignore}

        if dictify_splits and 'splits' not in ignore and self._is_split:
            res['splits'] = [split.to_dict(ignore=ignore) for split in res['splits']]

        return res


class Split:
    """
    A class used to represent a split in a transaction.

    Parameters
    ----------

    """
    def __init__(self,
                 date: datetime = None,
                 amount: float = None,
                 memo: str = None,
                 cleared: str = None,
                 payee_address: str = None,
                 category: str = None,
                 to_account: str = None,
                 check_number: int = None,
                 percent: float = None
                 ):
        self._date = date
        self._amount = amount
        self._memo = memo
        self._cleared = cleared
        self._payee_address = payee_address
        self._category = category
        self._to_account = to_account
        self._check_number = check_number
        self._percent = percent

    def __eq__(self, other):
        if not isinstance(other, Split):
            return False
        return self.__dict__ == other.__dict__

    def __str__(self):
        properties = ''
        for (object_property, value) in self.__dict__.items():
            if value:
                properties += f'\n        {object_property.strip("_").replace("_", " ").title()}: {value}'

        return '\n    Split:' + properties

    def __repr__(self):
        properties = ''
        for (object_property, value) in self.__dict__.items():
            if value:
                properties += f'{object_property.strip("_")}={repr(value)}, '

        properties = properties.strip(', ')
        return f'Split({properties})'

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
    def cleared(self):
        return self._cleared

    @cleared.setter
    def cleared(self, new_val):
        self._cleared = str(new_val)

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
        if not isinstance(new_category, Category):
            raise TypeError('Must be a Category object')
        self._category = new_category

    @property
    def to_account(self):
        return self._to_account

    @to_account.setter
    def to_account(self, new_account):
        self._to_account = str(new_account)

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
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, new_percent):
        self._percent = float(new_percent)

    def to_dict(self, ignore=None):
        if ignore is None:
            ignore = []
        return {key.strip('_'): value for (key, value) in self.__dict__.items()
                if value is not None and key.strip('_') not in ignore}


class Investment:
    """
    A class used to represent an investment.

    Parameters
    ----------
    date : datetime
        Date transaction occurred. May not include timestamp.
    amount : float
        The amount of the transaction. May be positive or negative.
    memo : str
        Also known as the reference. A string describing the purpose behind the transaction.

    """
    def __init__(self,
                 date: datetime,
                 action: str = None,
                 security: str = None,
                 price: float = None,
                 quantity: float = None,
                 cleared: str = None,
                 amount: float = None,
                 memo: str = None,
                 first_line: str = None,
                 to_account: str = None,
                 transfer_amount: float = None,
                 commission: float = None
                 ):
        self._date = date
        self._action = action
        self._security = security
        self._price = price
        self._quantity = quantity
        self._cleared = cleared
        self._amount = amount
        self._memo = memo
        self._first_line = first_line
        self._to_account = to_account
        self._transfer_amount = transfer_amount
        self._commission = commission

    def __eq__(self, other):
        if not isinstance(other, Investment):
            return False

        return self.__dict__ == other.__dict__

    def __str__(self):
        properties = ''
        for (object_property, value) in self.__dict__.items():
            if value:
                properties += f'\n    {object_property.strip("_").replace("_", " ").title()}: {value}'

        return 'Investment:' + properties

    def __repr__(self):
        properties = ''
        for (object_property, value) in self.__dict__.items():
            if value is not None:
                properties += f'{object_property.strip("_")}={repr(value)}, '

        properties = properties.strip(', ')
        return f'Investment({properties})'

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, new_date):
        if not isinstance(new_date, datetime):
            raise TypeError(f'New date must be datetime object')
        self._date = new_date

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, new_action):
        self._action = str(new_action)

    @property
    def security(self):
        return self._security

    @security.setter
    def security(self, new_security):
        self._security = str(new_security)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, new_price):
        try:
            self._price = float(new_price)
        except ValueError:
            raise TypeError('Price can only be int or float')

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, new_quantity):
        try:
            self._quantity = float(new_quantity)
        except ValueError:
            raise TypeError('Quantity can only be int or float')

    @property
    def cleared(self):
        return self._cleared

    @cleared.setter
    def cleared(self, new_value):
        self._cleared = str(new_value)

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
    def first_line(self):
        return self._first_line

    @first_line.setter
    def first_line(self, new_first_line):
        self._first_line = str(new_first_line)

    @property
    def to_account(self):
        return self._to_account

    @to_account.setter
    def to_account(self, new_to_account):
        self._to_account = str(new_to_account)

    @property
    def transfer_amount(self):
        return self._transfer_amount

    @transfer_amount.setter
    def transfer_amount(self, new_transfer_amount):
        try:
            self._transfer_amount = float(new_transfer_amount)
        except ValueError:
            raise TypeError('Transfer amount can only be int or float')

    @property
    def commission(self):
        return self._commission

    @commission.setter
    def commission(self, new_commission):
        try:
            self._commission = float(new_commission)
        except ValueError:
            raise TypeError('Commission can only be int or float')

    @classmethod
    def from_list(cls, lst, day_first=True):
        """Return an Investment object from a list of properties as found in a QIF file."""
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
                transaction_date = parse_date(field_info, day_first)
                kwargs['date'] = transaction_date
            elif line_code == 'N':
                kwargs['action'] = field_info
            elif line_code == 'Y':
                kwargs['security'] = field_info
            elif line_code == 'I':
                kwargs['price'] = float(field_info)
            elif line_code == 'Q':
                kwargs['quantity'] = float(field_info)
            elif line_code == 'C':
                kwargs['cleared'] = field_info
            elif line_code == 'T' or line_code == 'U':
                kwargs['amount'] = float(field_info)
            elif line_code == 'M':
                kwargs['memo'] = field_info
            elif line_code == 'P':
                kwargs['first_line'] = field_info
            elif line_code == 'L':
                kwargs['to_account'] = field_info
            elif line_code == '$':
                kwargs['transfer_amount'] = float(field_info)
            elif line_code == 'O':
                kwargs['commission'] = float(field_info)

        return cls(**kwargs)

    @classmethod
    def from_string(cls, string, separator='\n', day_first=True):
        """Return an Investment object from a string of properties separated by separator."""
        property_list = string.split(separator)
        return cls.from_list(property_list, day_first)

    def to_dict(self, ignore=None):
        """Return a dictionary representation of the Investment instance."""
        if ignore is None:
            ignore = []
        return {key.strip('_'): value for (key, value) in self.__dict__.items()
                if value is not None and key.strip('_') not in ignore}


class TransactionList(collections.MutableSequence, ABC):
    """
    A class to store Transaction and Investment objects only in an ordered list.

    Parameters
    ----------
    args : Transaction(s)/Investment(s)
        Transactions/Investments to be put in the list.
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
        return f'TransactionList({", ".join([repr(item) for item in self._list])})'

    def insert(self, key, value):
        self._check_if_transaction(value)
        self.list.insert(key, value)

    @staticmethod
    def _check_if_transaction(item):
        """Check if a given item is an instance of the Transaction or Investment classes and raise an error if not"""
        if not isinstance(item, (Transaction, Investment)):
            raise TypeError(f'Only Transaction and Investment objects can be appended to a TransactionList')

    @property
    def list(self):
        return self._list

    @list.setter
    def list(self, new_list):
        for item in new_list:
            self._check_if_transaction(item)
        self._list = new_list
