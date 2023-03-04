from __future__ import annotations

from typing import Any, Dict, List, Optional

from quiffen import utils
from quiffen.core.base import BaseModel, Field


class Security(BaseModel):
    """A class representing a security in a QIF file

    Parameters
    ----------
    name : str
        The name of the security
    symbol : str
        The symbol of the security
    type : str
        The type of the security
    goal : str
        The goal of the security
    line_number : int
        The line number of the security in the QIF file
    """

    name: Optional[str] = None
    symbol: Optional[str] = None
    type: Optional[str] = None
    goal: Optional[str] = None
    line_number: Optional[int] = None

    __CUSTOM_FIELDS: List[Field] = []  # type: ignore

    def __str__(self) -> str:
        return_str = "Security:"
        if self.name:
            return_str += f"\n\tName: {self.name}"
        if self.symbol:
            return_str += f"\n\tSymbol: {self.symbol}"
        if self.type:
            return_str += f"\n\tType: {self.type}"
        if self.goal:
            return_str += f"\n\tGoal: {self.goal}"

        return return_str

    def merge(self, other: Security) -> None:
        """Merge another security into this one.

        Parameters
        ----------
        other : Security
            The other security to merge into this one.
        """
        self.name = self.name or other.name
        self.symbol = self.symbol or other.symbol
        self.type = self.type or other.type
        self.goal = self.goal or other.goal

    def to_qif(self) -> str:
        """Converts a Security to a QIF string"""
        qif = "!Type:Security\n"

        if self.name:
            qif += f"N{self.name}\n"
        if self.symbol:
            qif += f"S{self.symbol}\n"
        if self.type:
            qif += f"T{self.type}\n"
        if self.goal:
            qif += f"G{self.goal}\n"

        qif += utils.convert_custom_fields_to_qif_string(
            self._get_custom_fields(),
            self,
        )

        return qif

    @classmethod
    def from_list(
        cls,
        lst: List[str],
        line_number: Optional[int] = None,
    ) -> Security:
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the transaction.
        line_number : int, default=None
            The line number of the header line of the transaction in the QIF
            file.

        Returns
        -------
        Security
            A class instance representing the security.
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

            if line_code == "N":
                kwargs["name"] = field_info
            elif line_code == "S":
                kwargs["symbol"] = field_info
            elif line_code == "T":
                kwargs["type"] = field_info
            elif line_code == "G":
                kwargs["goal"] = field_info
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
        line_number: Optional[int] = None,
    ) -> Security:
        """Return a class instance from a QIF string.

        Parameters
        ----------
        string : str
            String containing QIF information about the transaction.
        separator : str, default='\n'
            The separator between QIF fields.
        line_number : int, default=None
            The line number of the header line of the transaction in the QIF
            file.

        Returns
        -------
        Security
            A class instance representing the security.
        """
        return cls.from_list(
            lst=string.split(separator),
            line_number=line_number,
        )
