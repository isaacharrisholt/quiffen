import decimal
from abc import ABC
from datetime import datetime
import collections.abc

from decimal import Decimal

from quiffen.utils import parse_date, create_categories
from quiffen.core.categories_classes import Category, Class


class TransactionList(collections.abc.MutableSequence, ABC):
    """
    A class to store Transaction-type objects only in an ordered list.

    Extends collections.MutableSequence, so all list operations will work on this class.

    Attributes
    ----------
    list : list
        The list of Transaction-type objects stored by the object.
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
        """Insert an object into the list at a specified key. Overrides the MutableSequence.insert() method.

        Parameters
        ----------
        key : int
            The key at which to insert ``value``.
        value : Transaction or Investment
            The Transaction-type object to be inserted into the list.
        """
        self._check_if_transaction(value)
        self.list.insert(key, value)

    @staticmethod
    def _check_if_transaction(item):
        # Check if a given item is an instance of the Transaction or Investment classes and raise an error if not.
        if not isinstance(item, (Transaction, Investment, Split)):
            raise TypeError(f'Only Transaction-type objects can be appended to a TransactionList')

    @property
    def list(self):
        return self._list

    @list.setter
    def list(self, new_list):
        for item in new_list:
            self._check_if_transaction(item)
        self._list = new_list


class Transaction:
    """
    A class used to represent a transaction.

    Attributes
    ----------
    is_split : bool
        Whether or not this transaction is split (see documentation on parameter ``splits``)
    split_categories : dict
        The categories of the splits for this transaction, if transaction ``is_split``.

    Examples
    --------
    Create a Transaction instance, then convert to a dict, ignoring the date.

    >>> import quiffen
    >>> import decimal
    >>> from datetime import datetime
    >>> cat = quiffen.Category('Finances')
    >>> tr = quiffen.Transaction(date=datetime.now(), amount=decimal.Decimal(150.60), category=cat)
    >>> tr
    Transaction(date=datetime.datetime(2021, 7, 5, 10, 45, 40, 48195), amount=150.6, category=Category(name='Finances',
    expense=True, hierarchy='Finances'))
    >>> print(tr)
    Transaction:
        Date: 2021-07-05 10:45:40.048195
        Amount: 150.6
        Category: Finances
    >>> tr.to_dict(ignore=['date'], dictify_category=True)
    {'amount': 150.6, 'category': {'name': 'Finances', 'expense': True, 'income': False, 'hierarchy': 'Finances',
    'children': []}}
    """

    def __init__(self,
                 date: datetime,
                 amount: Decimal,
                 memo: str = None,
                 cleared: str = None,
                 payee: str = None,
                 payee_address: str = None,
                 category: Category = None,
                 check_number: int = None,
                 reimbursable_expense: bool = None,
                 small_business_expense: bool = None,
                 to_account: str = None,
                 first_payment_date: datetime = None,
                 loan_length: Decimal = None,
                 num_payments: int = None,
                 periods_per_annum: int = None,
                 interest_rate: float = None,
                 current_loan_balance: float = None,
                 original_loan_amount: float = None,
                 line_number: int = None,
                 splits: TransactionList = None
                 ):
        """Initialise an instance of the Transaction class.

        Parameters
        ----------
        date : datetime
            Date transaction occurred. May or may not include timestamp.
        amount : decimal.Decimal
            The amount of the transaction. May be positive or negative.
        memo : str, default=None
            Also known as the reference. A string describing the purpose behind the transaction.
        cleared : str, default=None
            The cleared status of this transaction. See the QIF standards for valid values.
        payee : str, default=None
            The name of the payee on the other end of the transaction. The payee is the receiver of the money if amount is
            negative, else they are the sender of the money.
        payee_address : str, default=None
            The address of the aforementioned payee.
        category : Category, default=None
            The category object that represents the transaction.
        check_number : int, default=None
            The check number if the transaction relates to a check
        reimbursable_expense : bool, default=None
            Whether or not this transaction is flagged as a reimbursable business expense.
        small_business_expense : bool, default=None
            Whether or not this transaction is flagged as a small business expense.
        to_account : str, default=None
            The account the transaction was sent to, if applicable.
        first_payment_date : datetime.datetime, default=None
            If this transaction was completed over multiple days, the first payment date.
        loan_length : decimal.Decimal, default=None
            The length of the loan, if applicable.
        num_payments : int, default=None
            If this payment was split over multiple payments, the number of such payments.
        periods_per_annum : int, default=None
            The periods per annum for this transaction.
        interest_rate : decimal.Decimal, default=None
            The interest rate on this transaction.
        current_loan_balance : decimal.Decimal, default=None
            The current loan balance, if applicable.
        original_loan_amount : decimal.Decimal, default=None
            The original loan amount, if applicable.
        line_number : int, default=None
            The line number of the header line of the transaction in the QIF file.
        splits : TransactionList, default=None
            If this transaction has multiple categories (e.g. an Amazon purchase of an electrical item and a book), it
            can be split in QIF files to represent this. Each split has its own memo, category and amount.
            This parameter is a TransactionList containing the splits for this transaction.
        """
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
        self._line_number = line_number

        self._split_categories = {}

        if splits:
            self._assert_type(splits, Split)
            self._splits = TransactionList(*splits)
            self._is_split = True
            self._last_split = splits[-1]
            for split in splits:
                self._split_categories = create_categories(split.category, self._split_categories)
        else:
            self._splits = TransactionList()
            self._is_split = False
            self._last_split = None

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return self._date == other.date and self._amount == other.amount

    def __str__(self):
        properties = ''
        ignore = ['_last_split', '_is_split']
        for (object_property, value) in self.__dict__.items():
            if value and object_property not in ignore:
                if object_property == '_category':
                    properties += f'\n    Category: {value.name}'
                elif object_property == '_split_categories':
                    properties += f'\n    Split Categories: {[name for name in value]}'
                elif object_property == '_splits':
                    properties += f'\n    Splits: {len(value)} total split(s)'
                else:
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
            self._amount = Decimal(new_amount)
        except ValueError:
            raise TypeError('Amount can only be int, float or decimal.Decimal')

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
    def cleared(self, new_str):
        self._cleared = str(new_str)

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
        if isinstance(new_flag, str) and new_flag.lower() == 'false':
            self._reimbursable_expense = False
        else:
            self._reimbursable_expense = True

    @property
    def small_business_expense(self):
        return self._small_business_expense

    @small_business_expense.setter
    def small_business_expense(self, new_flag):
        if isinstance(new_flag, str) and new_flag.lower() == 'false':
            self._small_business_expense = False
        else:
            self._small_business_expense = True

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
        self._loan_length = Decimal(new_length)

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
        self._interest_rate = Decimal(new_rate)

    @property
    def current_loan_balance(self):
        return self._current_loan_balance

    @current_loan_balance.setter
    def current_loan_balance(self, new_balance):
        self._current_loan_balance = Decimal(new_balance)

    @property
    def original_loan_amount(self):
        return self._original_loan_amount

    @original_loan_amount.setter
    def original_loan_amount(self, new_amount):
        self._original_loan_amount = Decimal(new_amount)

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
    def split_categories(self):
        return self._split_categories

    @property
    def line_number(self):
        return self._line_number

    @classmethod
    def from_list(cls, lst, day_first=True, line_number=None):
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the transaction.
        day_first : bool, default=True
             Whether the day or month comes first in the date.
        line_number : int, default=None
            The line number of the header line of the transaction in the QIF file.

        Returns
        -------
        Transaction
            A Transaction object created from the QIF strings.
        """
        kwargs = {}
        categories = {}
        classes = []
        splits = TransactionList()
        current_split = None
        split_categories = {}
        last_category = None
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
                current_split.amount = Decimal(round(float(field_info.replace(',', '')), 2))
            elif line_code == '%':
                current_split.percent = Decimal(field_info.split(' ')[0].replace('%', ''))
            elif line_code == 'T' or line_code == 'U':
                amount = round(float(field_info.replace(',', '')), 2)
                if not splits:
                    kwargs['amount'] = Decimal(amount)
                else:
                    current_split.amount = Decimal(amount)
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

                    if last_category is None:
                        new_category.hierarchy = field_info
                        last_category = field_info
                    else:
                        new_category.hierarchy = f'{last_category}:{field_info}'
                        last_category = f'{last_category}:{field_info}'

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
                if field_info.lower() == 'false':
                    kwargs['reimbursable_expense'] = False
                else:
                    kwargs['reimbursable_expense'] = True
            elif line_code == '1':
                kwargs['first_payment_date'] = parse_date(field_info, day_first)
            elif line_code == '2':
                kwargs['loan_length'] = Decimal(round(float(field_info.replace(',', '')), 2))
            elif line_code == '3':
                kwargs['num_payments'] = int(field_info.replace(',', ''))
            elif line_code == '4':
                kwargs['periods_per_annum'] = int(field_info.replace(',', ''))
            elif line_code == '5':
                kwargs['interest_rate'] = Decimal(round(float(field_info.replace(',', '')), 2))
            elif line_code == '6':
                kwargs['current_loan_balance'] = Decimal(round(float(field_info.replace(',', '')), 2))
            elif line_code == '7':
                kwargs['original_loan_amount'] = Decimal(round(float(field_info.replace(',', '')), 2))

        if line_number is not None:
            kwargs['line_number'] = line_number

        # Set splits percentage if they don't already have one
        if splits:
            total_amount = kwargs['amount']
            for split in splits:
                if not split.percent:
                    split.percent = abs(split.amount / total_amount) * 100

        categories.update({name: category for (name, category) in split_categories.items() if name not in categories})
        kwargs['splits'] = splits
        return cls(**kwargs), categories, classes

    @classmethod
    def from_string(cls, string, separator='\n', day_first=True, line_number=None):
        """Return a class instance from a QIF file section string.

        Parameters
        ----------
        string : str
            The string containing the QIF-formatted data.
        separator : str, default='\n'
             The line separator for the QIF file. This probably won't need changing.
        day_first : bool, default=True
             Whether the day or month comes first in the date.
        line_number : int, default=None
            The line number of the header line of the transaction in the QIF file.

        Returns
        -------
        Transaction
            A Transaction object created from the QIF strings.
        """
        property_list = string.split(separator)
        return cls.from_list(property_list, day_first, line_number)

    @staticmethod
    def _assert_type(iterable, types):
        # Assert that all items in a given list are of specific types.
        if isinstance(iterable, dict):
            for item in iterable.values():
                if not isinstance(item, types):
                    raise TypeError(f'\'{repr(item)} is not of type {types}')
        else:
            for item in iterable:
                if not isinstance(item, types):
                    raise TypeError(f'\'{repr(item)} is not of type {types}')

    def add_split(self, new_split):
        """Add a Split to Transaction.

        Parameters
        ----------
        new_split : Split
            The Split object to be added.

        Raises
        -------
        TypeError
            If ``new_split`` is not a Split.
        ValueError
            If percentage sum of all splits added is greater than 100.
        ValueError
            If sum of split amounts is greater than overall transaction amount.
        """
        if not isinstance(new_split, Split):
            raise TypeError('Must be a Split object')

        if new_split.percent and sum([split.percent for split in self._splits
                                      if split.percent]) + new_split.percent > 100:
            raise ValueError('Percentage sum of splits cannot add up to more than 100%')

        if new_split.amount and abs(sum([split.amount for split in self._splits if split.amount])) > abs(self._amount):
            raise ValueError('Splits amounts cannot sum to more than Transaction amount')

        self._splits.append(new_split)
        self.refresh_is_split()

    def remove_split(self, multiple=False, **kwargs):
        """Remove Split(s) from Transaction if they match a set of kwargs.

        Parameters
        ----------
        multiple : bool, default=None
            Whether or not to remove multiple splits that match ``kwargs``.
        kwargs
            The keyword arguments to filter the splits by (e.g. amount=150 would only remove splits with amount=150)

        Raises
        -------
        RuntimeError
            If no kwargs are provided.
        """
        if not kwargs:
            raise RuntimeError('No kwargs provided')

        indices = []

        for (i, split) in enumerate(self._splits):
            found_split = False
            for (key, value) in kwargs.items():
                if not key.startswith('_'):
                    key = '_' + key
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
        self.refresh_is_split()

    def to_dict(self, ignore=None, dictify_splits=True, dictify_category=True):
        """Return a dict object representing the Transaction.

        Parameters
        ----------
        ignore : list of str, default=None
             A list of strings of parameters that should be excluded from the dict.
        dictify_splits : bool, default=True
             Whether Splits within Transaction objects should be converted to dicts or left as they are.
        dictify_category : bool, default=True
             Whether the Transaction's category should be converted to a dict or left as it is.

        Returns
        -------
        dict
            A dict representing the Transaction object.
        """
        if ignore is None:
            ignore = []

        res = {key.strip('_'): value for (key, value) in self.__dict__.items()
               if value and key.strip('_') not in ignore}

        if dictify_splits and 'splits' not in ignore and self._is_split:
            res['splits'] = [split.to_dict(ignore=ignore) for split in res['splits']]

        if dictify_category and 'category' not in ignore and self._category is not None:
            res['category'] = self._category.to_dict()

        return res


class Split:
    """
    A class used to represent a split in a transaction.

    Examples
    --------
    Adding Splits to a transaction to show that there were two categories that represent the transaction.

    >>> import quiffen
    >>> from datetime import datetime
    >>> tr = quiffen.Transaction(date=datetime.now(), amount=150.60)
    >>> beauty = quiffen.Category('Beauty')
    >>> electrical = quiffen.Category('Electrical')
    >>> splt1 = quiffen.Split(amount=50, category=beauty)
    >>> splt2 = quiffen.Split(amount=100.60, category=electrical)
    >>> tr.add_split(splt1)
    >>> tr.add_split(splt2)
    >>> print(tr)
    Transaction:
        Date: 2021-07-05 10:59:02.456190
        Amount: 150.6
        Splits: 2 total split(s)
    >>> print(tr.splits)
    [Split(amount=50, category=Category(name='Beauty', expense=True, hierarchy='Beauty')), Split(amount=100.6,
    category=Category(name='Electrical', expense=True, hierarchy='Electrical'))]
    >>> tr.remove_split(amount=50)
    >>> print(tr.splits)
    [Split(amount=100.6, category=Category(name='Electrical', expense=True, hierarchy='Electrical'))]
    """

    def __init__(self,
                 date: datetime = None,
                 amount: Decimal = None,
                 memo: str = None,
                 cleared: str = None,
                 payee_address: str = None,
                 category: Category = None,
                 to_account: str = None,
                 check_number: int = None,
                 percent: Decimal = None
                 ):
        """Initialise an instance of the Split class.

        Parameters
        ----------
        date : datetime, default=None
            The date of the split transaction.
        amount : decimal.Decimal, default=None
            The amount this of this split.
        memo : str, default=None
            The memo (reference) for this split.
        cleared : str, default=None
            The cleared status of this split. See the QIF standards for valid values.
        payee_address : str, default=None
            The address of the payee for this split.
        category : Category, default=None
            The Category object that represents the category this split falls under.
        to_account : str, default=None
            The to account for this split.
        check_number : int, default=None
            The check number if this transaction relates to a check.
        percent : decimal.Decimal, default=None
            The percentage value of this split compared to the overall transaction.
        """
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
                if object_property == '_category':
                    properties += f'\n        Category: {value.name}'
                else:
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
            self._amount = Decimal(new_amount)
        except ValueError:
            raise TypeError('Amount can only be int, float or Decimal')

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
        self._percent = Decimal(new_percent)

    def to_dict(self, ignore=None, dictify_category=True):
        """Return a dict object representing the Split.

        Parameters
        ----------
        ignore : list of str, default=None
             A list of strings of parameters that should be excluded from the dict.
        dictify_category : bool, default=True
             Whether the Split's category should be converted to a dict or left as it is.

        Returns
        -------
        dict
            A dict representing the Split object.
        """
        if ignore is None:
            ignore = []
        res = {key.strip('_'): value for (key, value) in self.__dict__.items()
               if value is not None and key.strip('_') not in ignore}

        if dictify_category and 'category' not in ignore and self._category is not None:
            res['category'] = self._category.to_dict()

        return res


class Investment:
    """
    A class used to represent an investment.

    Acts almost identically to the Transaction class, but with a few different parameters and no splits.
    """

    def __init__(self,
                 date: datetime,
                 action: str = None,
                 security: str = None,
                 price: Decimal = None,
                 quantity: Decimal = None,
                 cleared: str = None,
                 amount: Decimal = None,
                 memo: str = None,
                 first_line: str = None,
                 to_account: str = None,
                 transfer_amount: float = None,
                 commission: float = None,
                 line_number: int = None
                 ):
        """Initialise an instance of the Investment class.

        Parameters
        ----------
        date : datetime
            Date investment occurred. May or may not include timestamp.
        action : str, default=None
            The investment action (Buy, Sell, etc.)
        security : str, default=None
            The security name.
        price : decimal.Decimal, default=None
            The price of the security.
        quantity : decimal.Decimal, default=None
            The quantity of the security bought, sold, etc.
        cleared : str, default=None
            The cleared status of this investment. See the QIF standards for valid values.
        amount : decimal.Decimal, default=None
            The overall amount of this investment.
        memo : str, default=None
            Also known as the reference. A string describing the purpose behind the investment.
        first_line : str, default=None
            The first line of the investment.
        to_account : str, default=None
            The to account of the investment, if applicable.
        transfer_amount : decimal.Decimal, default=None
            The amount transferred for the investment.
        commission : decimal.Decimal, default=None
            The commission paid/received on the investment.
        line_number : int, default=None
            The line number of the investment in the QIF file.
        """
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
        self._line_number = line_number

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
            self._price = Decimal(new_price)
        except ValueError:
            raise TypeError('Price can only be int, float or decimal.Decimal')

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, new_quantity):
        try:
            self._quantity = Decimal(new_quantity)
        except ValueError:
            raise TypeError('Quantity can only be int, float or decimal.Decimal')

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
            self._amount = Decimal(new_amount)
        except ValueError:
            raise TypeError('Amount can only be int, float or decimal.Decimal')

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
            self._transfer_amount = Decimal(new_transfer_amount)
        except ValueError:
            raise TypeError('Transfer amount can only be int, float or decimal.Decimal')

    @property
    def commission(self):
        return self._commission

    @commission.setter
    def commission(self, new_commission):
        try:
            self._commission = Decimal(new_commission)
        except ValueError:
            raise TypeError('Commission can only be int, float or decimal.Decimal')

    @property
    def line_number(self):
        return self._line_number

    @classmethod
    def from_list(cls, lst, day_first=True, line_number=None):
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the investment.
        day_first : bool, default=True
            Whether the day or month comes first in the date.
        line_number : int, default=None
            The line number of the header line of the investment in the QIF file.

        Returns
        -------
        Investment
            An Investment object created from the QIF strings.
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
            if line_code == 'D':
                transaction_date = parse_date(field_info, day_first)
                kwargs['date'] = transaction_date
            elif line_code == 'N':
                kwargs['action'] = field_info
            elif line_code == 'Y':
                kwargs['security'] = field_info
            elif line_code == 'I':
                kwargs['price'] = Decimal(round(float(field_info.replace(',', '')), 2))
            elif line_code == 'Q':
                kwargs['quantity'] = Decimal(round(float(field_info.replace(',', '')), 2))
            elif line_code == 'C':
                kwargs['cleared'] = field_info
            elif line_code == 'T' or line_code == 'U':
                kwargs['amount'] = Decimal(round(float(field_info.replace(',', '')), 2))
            elif line_code == 'M':
                kwargs['memo'] = field_info
            elif line_code == 'P':
                kwargs['first_line'] = field_info
            elif line_code == 'L':
                kwargs['to_account'] = field_info
            elif line_code == '$':
                kwargs['transfer_amount'] = Decimal(round(float(field_info.replace(',', '')), 2))
            elif line_code == 'O':
                kwargs['commission'] = Decimal(round(float(field_info.replace(',', '')), 2))

        if line_number is not None:
            kwargs['line_number'] = line_number

        return cls(**kwargs)

    @classmethod
    def from_string(cls, string, separator='\n', day_first=True, line_number=None):
        """Return a class instance from a QIF file section string.

        Parameters
        ----------
        string : str
            The string containing the QIF-formatted data.
        separator : str, default='\n'
             The line separator for the QIF file. This probably won't need changing.
        day_first : bool, default=True
             Whether the day or month comes first in the date.
        line_number : int, default=None
            The line number of the header line of the investment in the QIF file.

        Returns
        -------
        Investment
            An Investment object created from the QIF strings.
        """
        property_list = string.split(separator)
        return cls.from_list(property_list, day_first, line_number)

    def to_dict(self, ignore=None):
        """Return a dict object representing the Transaction.

        Parameters
        ----------
        ignore : list of str, default=None
             A list of strings of parameters that should be excluded from the dict.

        Returns
        -------
        dict
            A dict representing the Investment object.
        """
        if ignore is None:
            ignore = []
        return {key.strip('_'): value for (key, value) in self.__dict__.items()
                if value is not None and key.strip('_') not in ignore}
