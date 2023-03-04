import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from dateutil import parser
from pydantic import ValidationError, parse_obj_as

from quiffen.core.base import Field

ZERO_SEPARATED_DATE = re.compile(
    r"^(\d{2}|\d{4}|[a-zA-Z]+)0(\d{2}|[a-zA-Z]+)0(\d{2}|\d{4})$",
)


def parse_date(date_string: str, day_first: bool = False) -> datetime:
    """Parse a string date of an unknown format and return a datetime object.

    Parameters
    ----------
    date_string : str
        String containing date found in QIF file
    day_first : bool, default=False
        Whether the day comes first in the date (e.g. UK date) or after the
        month (e.g. US date)

    Returns
    -------
    datetime.datetime
        datetime object with the date data from the ``date_string`` parameter.

    Raises
    -------
    ValueError
        If the date cannot be parsed.
    """

    # QIF files sometimes use ' ' instead of a 0 or a ' instead of a /
    date_string = date_string.replace(" ", "0")
    date_string = date_string.replace("'", "/")

    # QIF files allow some really strange date formats, such as
    # %d0%B0%Y (e.g. 0100202022 for 2022-02-01)
    # This extends also to month-first dates. The following regex  checks
    # for this and converts it to a date string that can be parsed by
    # dateutil.parser
    date_search = ZERO_SEPARATED_DATE.search(date_string)

    if date_search:
        date_parts = date_search.groups()
        date_string = " ".join(date_parts)

    return parser.parse(date_string, dayfirst=day_first)


def parse_line_code_and_field_info(field: str) -> Tuple[str, str]:
    """Parse a QIF field into a line code and field info."""
    field = field.replace("\n", "")

    if not field:
        return "", ""
    line_code = field[0]

    if len(field) > 1:
        field_info = field[1:]
    else:
        field_info = ""

    return line_code, field_info


def add_custom_field_to_object_dict(
    field: str,  # Takes in the whole field to allow multi-character line codes
    custom_fields: List[Field],
    object_dict: Dict[str, Any],
) -> Tuple[Dict[str, Any], bool]:
    """Add custom QIF fields to a dict representing a Quiffen object based on
    the QIF file line.

    Returns
    -------
    object_dict : dict
        The object dict with the custom field added.
    found : bool
        Whether the custom field was found.
    """
    for custom_field in custom_fields:
        if field.startswith(custom_field.line_code):
            try:
                object_dict[custom_field.attr] = parse_obj_as(
                    custom_field.type,
                    field[len(custom_field.line_code) :],
                )
                return object_dict, True
            except ValidationError:
                return object_dict, False

    return object_dict, False


def convert_custom_fields_to_qif_string(
    custom_fields: List[Field],
    obj: Any,
) -> str:
    """Convert custom fields to a QIF string."""
    qif = ""
    for custom_field in custom_fields:
        if (attr := getattr(obj, custom_field.attr)) is not None:
            qif += f"{custom_field.line_code}{attr}\n"

    return qif


def apply_csv_formatting_to_scalar(
    obj: Any,
    date_format: Optional[str] = "%Y-%m-%d",
    stringify: bool = False,
) -> Any:
    """Apply CSV-friendly formatting to a scalar value"""
    if isinstance(obj, (datetime, date)) and date_format:
        return obj.strftime(date_format)
    elif isinstance(obj, Enum):
        return str(obj.value)
    elif isinstance(obj, Decimal):
        if obj % 1:
            return float(obj)
        return int(obj)
    elif stringify:
        return str(obj)

    return obj


def apply_csv_formatting_to_container(
    obj: Union[List[Any], Dict[Any, Any]],
    date_format: Optional[str] = "%Y-%m-%d",
) -> Union[List[Any], Dict[Any, Any], Any]:
    """Recursively apply CSV-friendly formatting to a container"""
    if isinstance(obj, list):
        return [apply_csv_formatting_to_container(item, date_format) for item in obj]
    elif isinstance(obj, dict):
        return {
            apply_csv_formatting_to_scalar(
                key,
                date_format,
                stringify=True,
            ): apply_csv_formatting_to_container(value, date_format)
            for key, value in obj.items()
        }
    else:
        return apply_csv_formatting_to_scalar(obj, date_format)
