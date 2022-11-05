from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel

T = TypeVar('T')


class Field(PydanticBaseModel):
    line_code: str
    attr: str
    type: Type[T]

    def __eq__(self, other):
        return self.line_code == other.line_code

    # Include __lt__ method so that the Field objects can be sorted
    def __lt__(self, other):
        return (
            len(self.line_code) < len(other.line_code)
            or self.line_code < other.line_code
        )


# pylint: disable=too-few-public-methods
class BaseModel(PydanticBaseModel):
    class Config:
        extra = 'allow'

    __CUSTOM_FIELDS: List[Field] = []

    @classmethod
    def add_custom_field(cls, line_code: str, attr: str, field_type: Type[T]):
        """Add a custom field to the class for parsing from a QIF.

        Parameters
        ----------
        line_code : str
            The line code of the extra field.
        attr : str
            The attribute name of the extra field.
        field_type : str
            The type of the extra field.
        """
        lst = getattr(cls, '__CUSTOM_FIELDS', []).copy()

        new_field = Field(line_code=line_code, attr=attr, type=field_type)
        if new_field in lst:
            # Overwrite existing field if it exists
            lst = [field if field != new_field else new_field for field in lst]
        else:
            lst.append(new_field)

        setattr(cls, '__CUSTOM_FIELDS', lst)

    @classmethod
    def _get_custom_fields(cls) -> List[Field]:
        """Return a list of the custom fields for the class, reverse ordered by
        line code length."""
        return sorted(getattr(cls, '__CUSTOM_FIELDS', []), reverse=True)

    @classmethod
    @abstractmethod
    def from_list(cls, lst: List[str]) -> T:
        pass

    @classmethod
    def from_string(cls, string: str, separator: str = '\n') -> T:
        """Create a class instance from a string."""
        return cls.from_list(string.split(separator))

    def to_dict(self, ignore: Iterable[str] = None) -> Dict[str, Any]:
        """Convert the class instance to a dict."""
        if ignore is None:
            ignore = []
        return self.dict(exclude=set(ignore))
