from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List

from quiffen import utils
from quiffen.core.base import BaseModel, Field
from quiffen.core.class_type import Class
from quiffen.core.transaction import (
    TransactionLike,
    TransactionList,
)


class AccountType(str, Enum):
    CASH = 'Cash'
    BANK = 'Bank'
    CREDIT_CARD = 'CCard'
    OTH_A = 'Oth A'
    OTH_L = 'Oth L'
    INVOICE = 'Invoice'
    INVST = 'Invst'


class Account(BaseModel):
    # pylint: disable=line-too-long
    """
    A class representing a QIF account.

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
    # pylint: enable=line-too-long
    name: str
    desc: str = None
    account_type: AccountType = None
    credit_limit: Decimal = None
    balance: Decimal = None
    date_at_balance: datetime = None
    transactions: Dict[str, TransactionList] = {}
    _last_header: AccountType = None

    __CUSTOM_FIELDS: List[Field] = []

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return (
            self.name == other.name
            and self.account_type == other.account_type
        )

    def __str__(self):
        properties = ''
        ignore = ['_last_header']
        for (object_property, value) in self.__dict__.items():
            if value and object_property not in ignore:
                if object_property == 'transactions':
                    num_transactions = sum(
                        len(value[header]) for header in value
                    )
                    properties += f'\n\tTransactions: {num_transactions}'
                else:
                    properties += (
                        f'\n\t'
                        f'{object_property.replace("_", " ").strip().title()}: '
                        f'{value}'
                    )
        return 'Account:' + properties

    def add_transaction(
        self,
        transaction: TransactionLike,
        header: AccountType = None,
    ):
        """Add a transaction to the dict of TransactionList objects.

        Parameters
        ----------
        transaction : Transaction or Investment
            The Transaction-type object to be added.
        header : AccountType
             The header under which the transaction falls. Will be used as a key
             in the dict of transactions.

        Raises
        -------
        RuntimeError
            If there is no header provided, and no ``last_header`` set.
        """

        if not header and not self._last_header:
            raise RuntimeError('No header provided, and no last header set.')

        if not header:
            header = self._last_header
        else:
            try:
                header = AccountType(header.strip().split(':')[-1])
                self._last_header = header
            except ValueError as e:
                raise ValueError('Header must be a valid AccountType.') from e

        if header not in self.transactions:
            self.transactions[header] = []

        self.transactions[header].append(transaction)

    def merge(self, other: Account):
        """Merge another account into this one.

        Parameters
        ----------
        other : Account
            The other account to merge into this one.
        """
        self.desc = self.desc or other.desc
        self.account_type = self.account_type or other.account_type
        self.credit_limit = self.credit_limit or other.credit_limit
        self.balance = self.balance or other.balance
        self.date_at_balance = self.date_at_balance or other.date_at_balance

        for header in other.transactions:
            if header not in self.transactions:
                self.transactions[header] = []
            self.transactions[header].extend(other.transactions[header])

    def to_qif(
        self,
        date_format: str = '%Y-%m-%d',
        classes: Dict[str, Class] = None
    ) -> str:
        """Return a QIF-formatted string of this account.

        Returns
        -------
        str
            A QIF-formatted string of this account.
        """
        qif = '!Account\n'
        qif += f'N{self.name}\n'
        if self.desc:
            qif += f'D{self.desc}\n'
        if self.account_type:
            qif += f'T{self.account_type}\n'
        if self.credit_limit:
            qif += f'L{self.credit_limit}\n'
        if self.balance:
            qif += f'${self.balance}\n'
        if self.date_at_balance:
            qif += f'/{self.date_at_balance}\n'

        qif += utils.convert_custom_fields_to_qif_string(
            self._get_custom_fields(),
            self,
        )

        for header, header_transactions in self.transactions.items():
            qif += f'^\n!Type:{header}\n'
            qif += '^\n'.join(
                transaction.to_qif(
                    date_format=date_format,
                    classes=classes,
                ) for transaction in header_transactions
            )
        return qif

    @classmethod
    def from_list(cls, lst: List[str], day_first: bool = False) -> Account:
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
            line_code, field_info = utils.parse_line_code_and_field_info(field)
            if not line_code:
                continue

            # Check if current line is a custom field
            kwargs, found = utils.add_custom_field_to_object_dict(
                field=field,
                custom_fields=cls._get_custom_fields(),
                object_dict=kwargs,
            )
            if found or line_code == '!':
                continue

            if line_code == 'N':
                kwargs['name'] = field_info
            elif line_code == 'D':
                kwargs['desc'] = field_info
            elif line_code == 'T':
                kwargs['account_type'] = field_info
            elif line_code == 'L':
                kwargs['credit_limit'] = field_info.replace(',', '')
            elif line_code in {'$', '£'}:
                kwargs['balance'] = field_info.replace(',', '')
            elif line_code == '/':
                balance_date = utils.parse_date(field_info, day_first)
                kwargs['date_at_balance'] = balance_date
            else:
                raise ValueError(f'Unknown line code: {line_code}')

        return cls(**kwargs)