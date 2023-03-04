from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union

from quiffen import utils
from quiffen.core.base import BaseModel, Field
from quiffen.core.category import Category
from quiffen.core.class_type import Class


class Split(BaseModel):
    """
    A class used to represent a split in a transaction.


    Examples
    --------
    Adding Splits to a transaction to show that there were two categories that represent
    the transaction.

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
    [
        Split(
            amount=50,
            category=Category(name='Beauty', expense=True, hierarchy='Beauty'),
        ),
        Split(
            amount=100.6,
            category=Category(name='Electrical', expense=True, hierarchy='Electrical'),
        ),
    ]
    >>> tr.remove_splits(amount=50)
    [...]
    >>> print(tr.splits)
    [
        Split(
            amount=100.6,
            category=Category(name='Electrical', expense=True, hierarchy='Electrical'),
        ),
    ]
    """

    date: Optional[datetime] = None
    amount: Optional[Decimal] = None
    memo: Optional[str] = None
    cleared: Optional[str] = None
    category: Optional[Category] = None
    to_account: Optional[str] = None
    check_number: Optional[Union[int, str]] = None
    percent: Optional[Decimal] = None
    payee_address: Optional[str] = None

    __CUSTOM_FIELDS: List[Field] = []  # type: ignore

    def __str__(self) -> str:
        properties = ""
        for object_property, value in self.dict().items():
            if value:
                if object_property == "category":
                    properties += f'\n\t\tCategory: {value["name"]}'
                else:
                    properties += (
                        f"\n\t\t"
                        f'{object_property.replace("_", " ").strip().title()}'
                        f": {value}"
                    )

        return "\n\tSplit:" + properties

    def to_qif(
        self,
        date_format: str = "%Y-%m-%d",
        classes: Optional[Dict[str, Class]] = None,
    ) -> str:
        """Returns a QIF string representation of the split."""
        if classes is None:
            classes = {}

        qif = "S"

        if self.category:
            parent_class = None
            for cls in classes.values():
                for category in cls.categories:
                    if category.find_child(self.category.name):
                        parent_class = cls
                        break

            if self.category.hierarchy is not None:
                qif += self.category.hierarchy

            if parent_class:
                qif += f"/{parent_class.name}"

        qif += "\n"

        if self.date:
            qif += f"D{self.date.strftime(date_format)}\n"
        if self.amount:
            qif += f"${self.amount}\n"
        if self.memo:
            qif += f"E{self.memo}\n"
        if self.cleared:
            qif += f"C{self.cleared}\n"
        if self.to_account:
            qif += f"L[{self.to_account}]\n"
        if self.check_number:
            qif += f"N{self.check_number}\n"
        if self.percent:
            qif += f"%{self.percent}%\n"
        if self.payee_address:
            qif += f"A{self.payee_address}\n"

        qif += utils.convert_custom_fields_to_qif_string(
            self._get_custom_fields(),
            self,
        )

        return qif

    @classmethod
    def from_list(cls, lst: List[str]) -> Split:
        raise RuntimeError("Splits can only be created in the context of a transaction")
