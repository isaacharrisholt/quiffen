from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from quiffen import utils
from quiffen.core.base import BaseModel, Field


class Investment(BaseModel):
    """A class used to represent an investment.

    Acts almost identically to the Transaction class, but with a few different
    parameters and no splits.

    Parameters
    ----------
    date : datetime
        Date investment occurred. May or may not include timestamp.
    action : str, default=None
        The investment action (Buy, Sell, etc.)
    security : str, default=None
        The security name.
    price : Decimal, default=None
        The price of the security.
    quantity : Decimal, default=None
        The quantity of the security bought, sold, etc.
    cleared : str, default=None
        The cleared status of this investment. See the QIF standards for valid
        values.
    amount : Decimal, default=None
        The overall amount of this investment.
    memo : str, default=None
        Also known as the reference. A string describing the purpose behind the
        investment.
    first_line : str, default=None
        The first line of the investment.
    to_account : str, default=None
        The to account of the investment, if applicable.
    transfer_amount : Decimal, default=None
        The amount transferred for the investment.
    commission : Decimal, default=None
        The commission paid/received on the investment.
    line_number : int, default=None
        The line number of the investment in the QIF file.
    """

    date: datetime
    action: Optional[str] = None
    security: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    cleared: Optional[str] = None
    amount: Optional[Decimal] = None
    memo: Optional[str] = None
    first_line: Optional[str] = None
    to_account: Optional[str] = None
    transfer_amount: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    line_number: Optional[int] = None

    __CUSTOM_FIELDS: List[Field] = []  # type: ignore

    def __str__(self) -> str:
        properties = ""
        for object_property, value in self.__dict__.items():
            if value:
                properties += (
                    f"\n\t"
                    f'{object_property.replace("_", " ").strip().title()}: '
                    f"{value}"
                )

        return "Investment:" + properties

    def to_qif(
        self,
        date_format: str = "%Y-%m-%d",
        **_,  # To keep the same signature as Transaction.to_qif
    ) -> str:
        """Converts an Investment to a QIF string"""
        qif = f"D{self.date.strftime(date_format)}\n"

        if self.action:
            qif += f"N{self.action}\n"
        if self.security:
            qif += f"Y{self.security}\n"
        if self.price:
            qif += f"I{self.price}\n"
        if self.quantity:
            qif += f"Q{self.quantity}\n"
        if self.cleared:
            qif += f"C{self.cleared}\n"
        if self.amount:
            qif += f"T{self.amount}\n"
        if self.memo:
            qif += f"M{self.memo}\n"
        if self.first_line:
            qif += f"P{self.first_line}\n"
        if self.to_account:
            qif += f"L{self.to_account}\n"
        if self.transfer_amount:
            qif += f"${self.transfer_amount}\n"
        if self.commission:
            qif += f"O{self.commission}\n"

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
    ) -> Investment:
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the investment.
        day_first : bool, default=False
            Whether the day or month comes first in the date.
        line_number : int, default=None
            The line number of the header line of the investment in the QIF
            file.

        Returns
        -------
        Investment
            An Investment object created from the QIF strings.
        """
        kwargs: Dict[str, Any] = {}
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

            # Check the QIF line code for banking-related operations, then
            # append to kwargs.
            if line_code == "D":
                transaction_date = utils.parse_date(field_info, day_first)
                kwargs["date"] = transaction_date
            elif line_code == "N":
                kwargs["action"] = field_info
            elif line_code == "Y":
                kwargs["security"] = field_info
            elif line_code == "I":
                kwargs["price"] = field_info.replace(",", "")
            elif line_code == "Q":
                kwargs["quantity"] = field_info.replace(",", "")
            elif line_code == "C":
                kwargs["cleared"] = field_info
            elif line_code in {"T", "U"}:
                kwargs["amount"] = field_info.replace(",", "")
            elif line_code == "M":
                kwargs["memo"] = field_info
            elif line_code == "P":
                kwargs["first_line"] = field_info
            elif line_code == "L":
                kwargs["to_account"] = field_info
            elif line_code == "$":
                kwargs["transfer_amount"] = field_info.replace(",", "")
            elif line_code == "O":
                kwargs["commission"] = field_info.replace(",", "")
            else:
                raise ValueError(f"Unknown line code: {line_code}")

        if line_number is not None:
            kwargs["line_number"] = line_number

        return cls(**kwargs)

    @classmethod
    def from_string(
        cls,
        string: str,
        separator: str = "\n",
        day_first: bool = False,
        line_number: Optional[int] = None,
    ) -> Investment:
        """Return a class instance from a QIF string.

        Parameters
        ----------
        string : str
            String containing QIF information about the investment.
        separator : str, default='\n'
            The separator between QIF fields.
        day_first : bool, default=False
            Whether the day or month comes first in the date.
        line_number : int, default=None
            The line number of the header line of the investment in the QIF
            file.

        Returns
        -------
        Investment
            An Investment object created from the QIF string.
        """
        lst = string.split(separator)
        return cls.from_list(lst, day_first, line_number)
