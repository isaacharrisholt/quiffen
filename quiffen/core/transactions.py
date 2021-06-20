from datetime import datetime


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
        self.date = date
        self.amount = amount
        self.memo = memo
        self.payee = payee
        self.payee_address = payee_address
        self.category = category
        self.check_number = check_number
        self.flag = flag

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False

        return self.__dict__ == other.__dict__

    def __str__(self):
        properties = ''
        for object_property in self.__dict__:
            properties += f'\n    {object_property.replace("_", " ").title()}: {self.__dict__[object_property]}'

        return 'Transaction:' + properties

    def __repr__(self):
        properties = ''
        for object_property in self.__dict__:
            if self.__dict__[object_property] is not None:
                if object_property != 'date':
                    properties += f'{object_property}={self.__dict__[object_property]}, '
                else:
                    properties += f'{object_property}={repr(self.__dict__[object_property])}, '

        properties = properties.strip(', ')
        return f'Transaction({properties})'

    @staticmethod
    def _parse_date(date_string, day_first=True):
        # Parse a string date of an unknown format and return a datetime object.
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
