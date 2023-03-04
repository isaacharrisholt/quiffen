# Note: this file is named class_type.py rather than class.py as class is a
# reserved word in Python.
from __future__ import annotations

from typing import Any, Dict, List, Optional

from quiffen import utils
from quiffen.core.base import BaseModel, Field
from quiffen.core.category import Category


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
    categories: List[Category] = []

    __CUSTOM_FIELDS: List[Field] = []  # type: ignore

    def __eq__(self, other) -> bool:
        if not isinstance(other, Class):
            return False
        return self.name == other.name

    def __str__(self) -> str:
        res = f"Class:\n\tName: {self.name}"
        if self.desc:
            res += f"\n\tDescription: {self.desc}"
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
        qif = "!Type:Class\n"
        qif += f"N{self.name}\n"
        if self.desc:
            qif += f"D{self.desc}\n"

        qif += utils.convert_custom_fields_to_qif_string(
            self._get_custom_fields(),
            self,
        )

        return qif

    @classmethod
    def from_list(cls, lst: List[str]) -> Class:
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the QIF class.
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
            elif line_code == "D":
                kwargs["desc"] = field_info
            else:
                raise ValueError(f"Unknown line code: {line_code}")

        return cls(**kwargs)
