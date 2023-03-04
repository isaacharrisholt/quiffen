from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import root_validator, validator

from quiffen import utils
from quiffen.core.base import BaseModel, Field
from quiffen.core.category import (
    Category,
    add_categories_to_container,
    create_categories_from_hierarchy,
)
from quiffen.core.class_type import Class
from quiffen.core.investment import Investment
from quiffen.core.split import Split

logger = logging.getLogger(__name__)


class Transaction(BaseModel):
    """
    A class used to represent a transaction.

    Parameters
    ----------
    date : datetime
        Date transaction occurred. May or may not include timestamp.
    amount : decimal.Decimal
        The amount of the transaction. May be positive or negative.
    memo : str, default=None
        Also known as the reference. A string describing the purpose behind the
        transaction.
    cleared : str, default=None
        The cleared status of this transaction. See the QIF standards for valid
        values.
    payee : str, default=None
        The name of the payee on the other end of the transaction. The payee is
        the receiver of the money if amount is negative, else they are the
        sender of the money.
    payee_address : str, default=None
        The address of the aforementioned payee.
    category : Category, default=None
        The category object that represents the transaction.
    check_number : int, default=None
        The check number if the transaction relates to a check
    reimbursable_expense : bool, default=None
        Whether this transaction is flagged as a reimbursable business expense.
    small_business_expense : bool, default=None
        Whether this transaction is flagged as a small business expense.
    to_account : str, default=None
        The account the transaction was sent to, if applicable.
    first_payment_date : datetime.datetime, default=None
        If this transaction was completed over multiple days, the first payment
        date.
    loan_length : decimal.Decimal, default=None
        The length of the loan, if applicable.
    num_payments : int, default=None
        If this payment was split over multiple payments, the number of such
        payments.
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
        If this transaction has multiple categories (e.g. an Amazon purchase of
        an electrical item and a book), it can be split in QIF files to
        represent this. Each split has its own memo, category and amount. This
        parameter is a TransactionList containing the splits for this
        transaction.

    Examples
    --------
    Create a Transaction instance, then convert to a dict, ignoring the date.

    >>> import quiffen
    >>> import decimal
    >>> from datetime import datetime
    >>> cat = quiffen.Category('Finances')
    >>> tr = quiffen.Transaction(
    ...     date=datetime.now(),
    ...     amount=decimal.Decimal(150.60),
    ...     category=cat,
    ... )
    >>> tr
    Transaction(
        date=datetime.datetime(2021, 7, 5, 10, 45, 40, 48195),
        amount=150.6,
        category=Category(name='Finances',expense=True, hierarchy='Finances'),
    )
    >>> print(tr)
    Transaction:
        Date: 2021-07-05 10:45:40.048195
        Amount: 150.6
        Category: Finances
    >>> tr.to_dict(ignore=['date'], dictify_category=True)
    {
        'amount': 150.6,
        'category': {
            'name': 'Finances',
            'expense': True,
            'income': False,
            'hierarchy': 'Finances',
            'children': [],
        },
    }
    """

    date: datetime
    amount: Decimal
    memo: Optional[str] = None
    cleared: Optional[str] = None
    payee: Optional[str] = None
    payee_address: Optional[str] = None
    category: Optional[Category] = None
    check_number: Optional[Union[int, str]] = None
    reimbursable_expense: Optional[bool] = None
    small_business_expense: Optional[bool] = None
    to_account: Optional[str] = None
    first_payment_date: Optional[datetime] = None
    loan_length: Optional[Decimal] = None
    num_payments: Optional[int] = None
    periods_per_annum: Optional[int] = None
    interest_rate: Optional[Decimal] = None
    current_loan_balance: Optional[Decimal] = None
    original_loan_amount: Optional[Decimal] = None
    line_number: Optional[int] = None
    splits: List[Split] = []
    _split_categories: Dict[str, Category] = {}
    _last_split: Optional[Split] = None

    __CUSTOM_FIELDS: List[Field] = []  # type: ignore

    def __str__(self) -> str:
        properties = ""
        ignore = ["_last_split", "_is_split"]
        for object_property, value in self.__dict__.items():
            if value and object_property not in ignore:
                if object_property == "category":
                    properties += f"\n\tCategory: {value.name}"
                elif object_property == "_split_categories":
                    properties += f"\n\tSplit Categories: {list(value.keys())}"
                elif object_property == "splits":
                    properties += f"\n\tSplits: {len(value)}"
                else:
                    properties += (
                        f"\n\t"
                        f'{object_property.replace("_", " ").strip().title()}: '
                        f"{value}"
                    )

        return "Transaction:" + properties

    @root_validator(pre=True)
    def create_split_categories(cls, values: Dict[str, Any]) -> Dict:
        if splits := values.get("splits"):
            for split in splits:
                if split.category:
                    values["_split_categories"] = add_categories_to_container(
                        split.category,
                        values.get("_split_categories", {}),
                    )
            values["_last_split"] = splits[-1]
        return values

    @validator("splits")
    def check_split_percentages_and_amounts(
        cls,
        splits: List[Split],
        values: Dict[str, Any],
    ) -> List[Split]:
        total_percent = sum(split.percent for split in splits if split.percent)
        total_amount = sum(split.amount for split in splits if split.amount is not None)
        if total_percent - 100 > 0.01:
            raise ValueError("Split percentages cannot exceed 100% of the transaction")
        if abs(total_amount) - abs(values.get("amount", 0)) > 0.01:
            raise ValueError(
                "Split amounts cannot exceed the amount of the transaction"
            )
        return splits

    @property
    def split_categories(self) -> Dict[str, Category]:
        return self._split_categories

    @property
    def is_split(self) -> bool:
        """Returns True if the transaction is a split transaction, False
        otherwise."""
        return len(self.splits) > 0

    def add_split(self, split: Split) -> None:
        """Add a Split to Transaction."""
        if (
            split.percent
            and sum(s.percent for s in self.splits if s.percent is not None)
            + split.percent
            - 100
            > 0.01
        ):
            raise ValueError(
                "The sum of the split percentages cannot be greater than 100."
            )

        if split.amount:
            abs_sum_of_splits = abs(
                sum(s.amount for s in self.splits if s.amount is not None)
                + split.amount
            )
            if abs_sum_of_splits - abs(self.amount) > 0.01:
                raise ValueError(
                    "The sum of the split amounts cannot be greater than the "
                    "transaction amount."
                )

        self.splits.append(split)

    def remove_splits(self, **filters) -> List[Split]:
        """Remove splits from Transaction if they match a set of filters

        Takes filters as kwargs and removes splits that match all filters. If
        no filters are provided, all splits are removed.
        """
        if not filters:
            current_splits = self.splits.copy()
            self.splits = []
            return current_splits

        to_remove = []
        for split in self.splits:
            if all(getattr(split, attr) == value for attr, value in filters.items()):
                to_remove.append(split)

        self.splits = [split for split in self.splits if split not in to_remove]

        return to_remove

    @staticmethod
    def _create_class_from_category_string(
        category_string: str,
        classes: Dict[str, Class],
    ) -> Tuple[Optional[str], str, Dict[str, Class]]:
        if "/" in category_string:
            field_info, class_name = category_string.split("/")
            if class_name not in classes:
                classes[class_name] = Class(name=class_name)
            return class_name, field_info, classes
        return None, category_string, classes

    def to_qif(
        self,
        date_format: str = "%Y-%m-%d",
        classes: Optional[Dict[str, Class]] = None,
    ) -> str:
        """Converts a Transaction to a QIF string"""
        if classes is None:
            classes = {}

        qif = f"D{self.date.strftime(date_format)}\n"
        qif += f"T{self.amount}\n"
        if self.memo:
            qif += f"M{self.memo}\n"
        if self.cleared:
            qif += f"C{self.cleared}\n"
        if self.payee:
            qif += f"P{self.payee}\n"
        if self.payee_address:
            qif += f"A{self.payee_address}\n"
        if self.category:
            parent_class = None
            for cls in classes.values():
                for category in cls.categories:
                    if category.find_child(self.category.name):
                        parent_class = cls
                        break

            qif += f"L{self.category.hierarchy}"
            if parent_class:
                qif += f"/{parent_class.name}"
            qif += "\n"
        if self.check_number:
            qif += f"N{self.check_number}\n"
        if self.reimbursable_expense:
            qif += f"F{self.reimbursable_expense}\n"
        if self.to_account:
            qif += f"L[{self.to_account}]\n"
        if self.first_payment_date:
            qif += f"1{self.first_payment_date.strftime(date_format)}\n"
        if self.loan_length:
            qif += f"2{self.loan_length}\n"
        if self.num_payments:
            qif += f"3{self.num_payments}\n"
        if self.periods_per_annum:
            qif += f"4{self.periods_per_annum}\n"
        if self.interest_rate:
            qif += f"5{self.interest_rate}\n"
        if self.current_loan_balance:
            qif += f"6{self.current_loan_balance}\n"
        if self.original_loan_amount:
            qif += f"7{self.original_loan_amount}\n"
        if self.splits:
            for split in self.splits:
                qif += split.to_qif(date_format=date_format, classes=classes)

        qif += utils.convert_custom_fields_to_qif_string(
            self._get_custom_fields(),
            self,
        )

        return qif

    @classmethod
    def from_list(
        cls,
        lst: List[str],
        day_first: bool = False,
        line_number: Optional[int] = None,
    ) -> Tuple[Transaction, Dict[str, Class]]:
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the transaction.
        day_first : bool, default=False
             Whether the day or month comes first in the date.
        line_number : int, default=None
            The line number of the header line of the transaction in the QIF
            file.

        Returns
        -------
        Transaction
            A Transaction object created from the QIF strings.
        Dict[str, Class]
            A dictionary of Class objects created from the QIF strings.
        """
        kwargs: Dict[str, Any] = {}
        classes: Dict[str, Class] = {}
        splits: List[Split] = []
        current_split: Optional[Split] = None

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
            if found:
                continue

            if line_code == "S":
                _, field_info, classes = cls._create_class_from_category_string(
                    field_info,
                    classes,
                )

                split_category = create_categories_from_hierarchy(field_info)
                new_split = Split(category=split_category)
                splits.append(new_split)
                current_split = new_split
            elif line_code == "D":
                transaction_date = utils.parse_date(field_info, day_first)
                if not splits:
                    kwargs["date"] = transaction_date
                elif current_split:
                    current_split.date = transaction_date
            elif line_code == "E":
                if current_split is None:
                    logger.warning(
                        f"No split yet given for memo '{field_info}', skipping"
                    )
                else:
                    current_split.memo = field_info
            elif line_code in {"$", "£"}:
                if current_split:
                    current_split.amount = Decimal(field_info.replace(",", ""))
            elif line_code == "%":
                if current_split:
                    current_split.percent = Decimal(
                        field_info.split(" ")[0].replace("%", "")
                    )
            elif line_code in {"T", "U"}:
                amount = field_info.replace(",", "")
                if not splits:
                    kwargs["amount"] = amount
                elif current_split:
                    current_split.amount = Decimal(amount)
            elif line_code == "M":
                if not splits:
                    kwargs["memo"] = field_info
                elif current_split:
                    current_split.memo = field_info
            elif line_code == "C":
                if not splits:
                    kwargs["cleared"] = field_info
                elif current_split:
                    current_split.cleared = field_info
            elif line_code == "P":
                kwargs["payee"] = field_info
            elif line_code == "A":
                if not splits:
                    kwargs["payee_address"] = field_info
                elif current_split:
                    current_split.payee_address = field_info
            elif line_code == "L":
                (
                    class_name,
                    field_info,
                    classes,
                ) = cls._create_class_from_category_string(
                    field_info,
                    classes,
                )

                # 'L' can represent both categories and the 'to' transfer
                # account. Transfer accounts are denoted by [ ]
                if field_info.startswith("["):
                    if not splits:
                        kwargs["to_account"] = field_info[1:-1]
                    elif current_split:
                        current_split.to_account = field_info[1:-1]
                else:
                    category = create_categories_from_hierarchy(field_info)
                    category_root = category.traverse_up()[-1]
                    if not splits:
                        # If there's already a category, add the new category
                        # as a child
                        if "category" in kwargs:
                            category_root.set_parent(kwargs["category"])
                        kwargs["category"] = category
                    elif current_split:
                        category_root.set_parent(current_split.category)
                        current_split.category = category

                    if class_name:
                        classes[class_name].add_category(category)
            elif line_code == "N":
                if not splits:
                    kwargs["check_number"] = field_info
                elif current_split:
                    current_split.check_number = field_info
            elif line_code == "F":
                kwargs["reimbursable_expense"] = field_info or True
            elif line_code == "1":
                kwargs["first_payment_date"] = utils.parse_date(
                    field_info,
                    day_first,
                )
            elif line_code == "2":
                kwargs["loan_length"] = field_info.replace(",", "")
            elif line_code == "3":
                kwargs["num_payments"] = field_info.replace(",", "")
            elif line_code == "4":
                kwargs["periods_per_annum"] = field_info.replace(",", "")
            elif line_code == "5":
                kwargs["interest_rate"] = field_info.replace(",", "")
            elif line_code == "6":
                kwargs["current_loan_balance"] = field_info.replace(",", "")
            elif line_code == "7":
                kwargs["original_loan_amount"] = field_info.replace(",", "")
            else:
                raise ValueError(f"Unknown line code: {line_code}")

        if line_number is not None:
            kwargs["line_number"] = line_number

        # Set splits percentage if they don't already have one
        total = Decimal(kwargs.get("amount", 0))
        if splits and total:
            for split in splits:
                if split.percent is None and split.amount is not None:
                    split.percent = Decimal(round(split.amount / total * 100, 2))
                # Check if the split percentage is correct
                elif (
                    split.percent is not None
                    and split.amount is not None
                    and not (
                        Decimal(round(split.percent, 2))
                        == Decimal(
                            round(
                                split.amount / total * 100,
                                2,
                            )
                        )
                    )
                ):
                    logger.warning(
                        f"Split percentage ({split.percent}) does not match "
                        f"the split amount ({split.amount}) for transaction "
                        f"on line {line_number}."
                    )
        elif splits and not total:
            for split in splits:
                split.percent = None

        kwargs["splits"] = splits
        return cls(**kwargs), classes

    @classmethod
    def from_string(
        cls,
        string: str,
        separator: str = "\n",
        day_first: bool = False,
        line_number: Optional[int] = None,
    ) -> Tuple[Transaction, Dict[str, Class]]:
        """Return a class instance from a QIF string.

        Parameters
        ----------
        string : str
            String containing QIF information about the transaction.
        separator : str, default='\n'
            The separator between QIF fields.
        day_first : bool, default=False
             Whether the day or month comes first in the date.
        line_number : int, default=None
            The line number of the header line of the transaction in the QIF
            file.

        Returns
        -------
        Transaction
            A Transaction object created from the QIF strings.
        Dict[str, Class]
            A dictionary of classes created from the QIF strings.
        """
        lines = string.split(separator)
        return cls.from_list(lines, day_first, line_number)


TransactionLike = Union[Transaction, Investment, Split]
TransactionList = List[TransactionLike]
