from datetime import datetime

import pytest

from quiffen import utils


@pytest.mark.parametrize(
    "date_pattern,day_first",
    [
        # Day first patterns
        ("%d/%m/%Y", True),
        ("%d-%m-%Y", True),
        ("%d/%m/%y", True),
        ("%d-%m-%y", True),
        ("%d0%B0%Y", True),
        ("%d0%B0%y", True),
        ("%d0%b0%Y", True),
        ("%d0%b0%y", True),
        # Month first patterns
        ("%m/%d/%Y", False),
        ("%m-%d-%Y", False),
        ("%m/%d/%y", False),
        ("%m-%d-%y", False),
        ("%B0%d0%Y", False),
        ("%B0%d0%y", False),
        ("%b0%d0%Y", False),
        ("%b0%d0%y", False),
        # Year first patterns
        ("%Y/%m/%d", False),
        ("%Y-%m-%d", False),
        ("%Y0%B0%d", False),
        ("%Y0%b0%d", False),
    ],
)
def test_parse_date(date_pattern, day_first):
    want = datetime(2022, 1, 2)
    input_string = want.strftime(date_pattern)
    got = utils.parse_date(input_string, day_first)
    assert got == want


@pytest.mark.parametrize(
    "field,expected_line_code,expected_field_info",
    [
        ("DDate\n\n", "D", "Date"),
        ("PPayee", "P", "Payee"),
        ("MMemo", "M", "Memo"),
        ("TAmount", "T", "Amount"),
        ("LCategory", "L", "Category"),
        ("SSplit", "S", "Split"),
        ("E", "E", ""),
        ("", "", ""),
    ],
)
def test_parse_line_code_and_field_info(
    field,
    expected_line_code,
    expected_field_info,
):
    line_code, field_info = utils.parse_line_code_and_field_info(field)
    assert line_code == expected_line_code
    assert field_info == expected_field_info


def test_apply_csv_formatting_scalar():
    assert utils.apply_csv_formatting_to_scalar("foo") == "foo"
    assert utils.apply_csv_formatting_to_scalar(123) == 123
    assert utils.apply_csv_formatting_to_scalar(123.45) == 123.45
    assert utils.apply_csv_formatting_to_scalar(123.0) == 123
    assert (
        utils.apply_csv_formatting_to_scalar(
            datetime(2022, 1, 2),
        )
        == "2022-01-02"
    )
    assert (
        utils.apply_csv_formatting_to_scalar(
            datetime(2022, 1, 2).date(),
        )
        == "2022-01-02"
    )


def test_apply_csv_formatting_to_container_list():
    assert utils.apply_csv_formatting_to_container(
        ["foo", 123, 123.45, 123.0, datetime(2022, 1, 2)],
    ) == ["foo", 123, 123.45, 123, "2022-01-02"]


def test_apply_csv_formatting_to_container_dict():
    assert utils.apply_csv_formatting_to_container(
        {
            "foo": 123,
            "bar": 123.45,
            "baz": 123.0,
            "qux": datetime(2022, 1, 2),
        },
    ) == {
        "foo": 123,
        "bar": 123.45,
        "baz": 123,
        "qux": "2022-01-02",
    }


def test_apply_csv_formatting_to_container_dict_with_dicts_and_lists():
    assert utils.apply_csv_formatting_to_container(
        {
            "foo": 123,
            "bar": 123.45,
            "baz": 123.0,
            "qux": datetime(2022, 1, 2),
            "quux": {
                "foo": 123,
                "bar": 123.45,
                "baz": 123.0,
                "qux": datetime(2022, 1, 2),
            },
            "quuz": [
                123,
                123.45,
                123.0,
                datetime(2022, 1, 2),
            ],
        },
    ) == {
        "foo": 123,
        "bar": 123.45,
        "baz": 123,
        "qux": "2022-01-02",
        "quux": {
            "foo": 123,
            "bar": 123.45,
            "baz": 123,
            "qux": "2022-01-02",
        },
        "quuz": [
            123,
            123.45,
            123,
            "2022-01-02",
        ],
    }
