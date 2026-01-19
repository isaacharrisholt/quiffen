# Note: this file is named class_type.py rather than class.py as class is a
# reserved word in Python.
from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from quiffen import utils
from quiffen.core.base import BaseModel, Field
from quiffen.core.category import Category


class ClassType(str, Enum):
    """Enum representing the different types of Tags in a QIF file."""

    EXPENSE = "expense"
    INCOME = "income"


class Class(BaseModel):
    """
    A class used to represent a QIF Class.

    Parameters
    ----------
    name : str
        The name of the class.
    desc : str, default=None
        The description of the class.
    """

    name: str
    desc: Optional[str] = None
    categories: list[Category] = []

    # If the Class is actually a Tag, then it can have a type
    # which is either I/E
    class_type: Optional[ClassType] = None

    # is_tag is true when this is a tag rather than a class
    is_tag: bool = False

    __CUSTOM_FIELDS: list[Field] = []  # type: ignore

    def __eq__(self, other) -> bool:
        if not isinstance(other, Class):
            return False
        return self.name == other.name

    def __str__(self) -> str:
        res = f"{'Tag' if self._istag() else 'Class'}:\n\tName: {self.name}"
        if self.desc:
            res += f"\n\tDescription: {self.desc}"
        if self.class_type:
            res += f"\n\tType: {self.class_type}"
        res += f"\n\tCategories: {len(self.categories)}"
        return res

    def add_category(self, new_category: Category) -> None:
        """Add a category to the class."""
        for category in self.categories:
            if category.merge(new_category):
                return

        self.categories.append(new_category)

    def merge(self, other: Class) -> None:
        """Merge another class' categories into this one. Name is not
        merged, and desc is only merged if this class has no desc.
        """
        self.desc = self.desc or other.desc
        for category in other.categories:
            self.add_category(category)

    def to_qif(self) -> str:
        """Return a QIF-formatted string of this class."""
        qif = "!Type:Tag\n" if self._istag() else "!Type:Class\n"
        qif += f"N{self.name}\n"
        if self.desc:
            qif += f"D{self.desc}\n"

        if self.class_type:
            if self.class_type == ClassType.INCOME:
                qif += "I\n"
            elif self.class_type == ClassType.EXPENSE:
                qif += "E\n"

        qif += utils.convert_custom_fields_to_qif_string(
            self._get_custom_fields(),
            self,
        )

        return qif

    @classmethod
    def from_list(cls, lst: list[str], is_tag: bool = False) -> Class:
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the QIF class.
        """
        kwargs: dict[str, Any] = {}
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

            if is_tag:
                kwargs["is_tag"] = True

            if line_code == "N":
                kwargs["name"] = field_info
            elif line_code == "D":
                kwargs["desc"] = field_info
            elif line_code == "E":
                kwargs["tag_type"] = ClassType.EXPENSE
                kwargs["is_tag"] = True
            elif line_code == "I":
                kwargs["tag_type"] = ClassType.INCOME
                kwargs["is_tag"] = True
            else:
                raise ValueError(f"Unknown line code: {line_code}")

        return cls(**kwargs)

    def _istag(self) -> bool:
        return self.is_tag or self.class_type
