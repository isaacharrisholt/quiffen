from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from quiffen import utils
from quiffen.core.base import BaseModel, Field


class TagType(str, Enum):
    """Enum representing the different types of categories in a QIF file."""

    EXPENSE = "expense"
    INCOME = "income"


class Tag(BaseModel):
    """A class representing a tag (metadata) in a QIF file

    Parameters
    ----------
    name : str
        The name of the tag
    description : str
        The description of the tag
    tag_type : TagType, default=None
        The tag type which can be income
    goal : str
        The goal of the security
    line_number : int
        The line number of the security in the QIF file
    """

    name: str
    desc: Optional[str] = None
    tag_type: Optional[TagType] = None

    def __str__(self) -> str:
        return_str = "Tag:"
        return_str += f"\n\tName: {self.name}"
        if self.desc:
            return_str += f"\n\tDesc: {self.symbol}"
        if self.tag_type:
            return_str += f"\n\tType: {self.tag_type}"

        return return_str

    def __lt__(self, other: Tag) -> bool:
        return self.name < other.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return False
        return self.model_dump() == other.model_dump()

    def merge(self, other: Tag) -> None:
        """Merge another security into this one.

        Parameters
        ----------
        other : Security
            The other security to merge into this one.
        """
        self.name = self.name or other.name
        self.desc = self.desc or other.desc
        self.tag_type = self.tag_type or other.tag_type

    def to_qif(self) -> str:
        """Converts a Security to a QIF string"""
        qif = "!Type:Tag\n"

        qif += f"N{self.name}\n"
        if self.desc:
            qif += f"D{self.desc}\n"
        if self.tag_type:
            if self.tag_type == TagType.INCOME:
                qif += "I\n"
            elif self.category_type == TagType.EXPENSE:
                qif += "E\n"

        return qif

    @classmethod
    def from_list(cls, lst: list[str]) -> Tag:
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
        Tag
            A class instance representing the tag metadata.

        Raises
        ------
        KeyError
            If the name field cannot be found.
            If the field is unrecognized
        """
        kwargs: dict[str, Any] = {}

        found_name: bool = False
        for field in lst:
            line_code, field_info = utils.parse_line_code_and_field_info(field)
            if not line_code:
                continue

            if line_code == "N":
                kwargs["name"] = field_info
                found_name = True
            elif line_code == "D":
                kwargs["desc"] = field_info
            elif line_code == "E":
                kwargs["tag_type"] = TagType.EXPENSE
            elif line_code == "I":
                kwargs["tag_type"] = TagType.INCOME
            else:
                raise KeyError(f"Unknown line code: {line_code}")

        # if name is not present, throw
        if not found_name:
            raise KeyError(f"missing required field for Tag: 'name'")

        return cls(**kwargs)

    @classmethod
    def from_string(cls, string: str, separator: str = "\n") -> Tag:
        """Return a class instance from a QIF string.

        Parameters
        ----------
        string : str
            String containing QIF information about the transaction.
        separator : str, default='\n'
            The separator between QIF fields.

        Returns
        -------
        Security
            A class instance representing the security.
        """
        return cls.from_list(lst=string.split(separator))
