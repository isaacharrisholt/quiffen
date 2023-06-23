from __future__ import annotations

import csv
import io
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from pydantic.types import FilePath

from quiffen import utils
from quiffen.core.account import Account, AccountType
from quiffen.core.base import BaseModel, Field
from quiffen.core.category import Category, add_categories_to_container
from quiffen.core.class_type import Class
from quiffen.core.investment import Investment
from quiffen.core.security import Security
from quiffen.core.transaction import Transaction

try:
    import pandas as pd

    PANDAS_INSTALLED = True
except ModuleNotFoundError:
    PANDAS_INSTALLED = False

VALID_TRANSACTION_ACCOUNT_TYPES = [
    "!type:cash",
    "!type:bank",
    "!type:ccard",
    "!type:otha",
    "!type:othl",
    "!type:invoice",
]


class QifDataType(str, Enum):
    """An Enum representing the different types of data that can be found in a
    Qif object."""

    TRANSACTIONS = "transactions"
    INVESTMENTS = "investments"
    CLASSES = "classes"
    CATEGORIES = "categories"
    ACCOUNTS = "accounts"
    SECURITIES = "securities"


class ParserException(Exception):
    pass


class Qif(BaseModel):
    """
    The main class of the package. For parsing QIF files.

    See the readme for usage examples.

    Parameters
    ----------
    accounts : dict, default=None
        A dict of accounts in the form {'Account Name': account_object}.
    categories : dict, default=None
        A dict of categories in the form {'Category Name': category_object}.
    classes : dict, default=None
        A dict of classes in the form {'Class Name': class_object}.
    """

    accounts: Dict[str, Account] = {}
    categories: Dict[str, Category] = {}
    classes: Dict[str, Class] = {}
    securities: Dict[str, Security] = {}

    __CUSTOM_FIELDS: List[Field] = []  # type: ignore

    def __str__(self) -> str:
        accounts_str = "\n".join(str(acc) for acc in self.accounts.values())
        categories_str = "\n".join(str(cat) for cat in self.categories.values())
        classes_str = "\n".join(str(cls) for cls in self.classes.values())
        securities_str = "\n".join(str(sec) for sec in self.securities.values())

        if not (accounts_str or categories_str or classes_str):
            return "Empty Qif object"

        return_str = "QIF\n===\n\n"

        if accounts_str:
            return_str += f"Accounts\n--------\n\n{accounts_str}\n\n"
        if categories_str:
            return_str += f"Categories\n----------\n\n{categories_str}\n\n"
        if classes_str:
            return_str += f"Classes\n-------\n\n{classes_str}\n\n"
        if securities_str:
            return_str += f"Securities\n----------\n\n{securities_str}\n\n"

        return return_str

    @classmethod
    def from_list(cls, lst: List[str]) -> Qif:
        raise NotImplementedError(
            "This method is not implemented for Qif objects. Use Qif.parse to "
            "parse a QIF file."
        )

    @classmethod
    def parse(
        cls,
        path: Union[FilePath, str],
        separator: str = "\n",
        day_first: bool = False,
        encoding: str = "utf-8",
    ) -> Qif:
        """Return a class instance from a QIF file.

        Parameters
        ----------
        path : Union[FilePath, str]
            The path to the QIF file.
        separator : str, default='\n'
            The line separator for the QIF file. This probably won't need
            changing.
        day_first : bool, default=False
            Whether the day or month comes first in the date.
        encoding : str, default='utf-8'
            The encoding of the QIF file.

        Returns
        -------
        Qif
            A Qif object containing all the data in the QIF file.
        """
        path = Path(path)
        if path.suffix.lower() != ".qif":
            raise ParserException("The file must be a QIF file.")

        if not path.exists():
            raise ParserException("The file does not exist.")

        data = path.read_text(encoding=encoding).strip().strip("\n")

        if not data:
            raise ParserException("The file is empty.")

        accounts: Dict[str, Account] = {}
        last_account = None
        categories: Dict[str, Category] = {}
        classes: Dict[str, Class] = {}
        securities: Dict[str, Security] = {}

        sections = data.split("^")
        last_header = None
        line_number = 1

        for section in sections:
            if not section:
                continue

            section_lines = section.split(separator)
            if not section_lines:
                continue

            # Allow for comments and blank lines at the top of sections
            for i, line in enumerate(section_lines):
                header_line = line
                if line.strip() and line[0] != "#":
                    line_number += i
                    section_lines = section_lines[i:]
                    break
            else:
                # Empty section
                continue

            if header_line[0] != "!":
                if not last_header:
                    raise ParserException(
                        f"Line {line_number}: " f"No header found before transactions."
                    )
                header_line = last_header

            last_header = header_line

            sanitised_section_lines = [
                line
                for line in section_lines
                if line.strip() and line.strip()[0] != "!"
            ]

            if not sanitised_section_lines:
                continue

            # Check for new categories and accounts first, otherwise it's a
            # transaction so a default account is created
            if "!Type:Cat" in header_line:
                # Section contains category information
                new_category = Category.from_list(sanitised_section_lines)
                categories = add_categories_to_container(  # type: ignore
                    new_category,
                    categories,
                )
            elif "!Type:Class" in header_line:
                new_class = Class.from_list(sanitised_section_lines)
                if new_class.name in classes:
                    classes[new_class.name].merge(new_class)
                else:
                    classes[new_class.name] = new_class
            elif "!Account" in header_line:
                new_account = Account.from_list(sanitised_section_lines)
                if new_account.name in accounts:
                    accounts[new_account.name].merge(new_account)
                else:
                    accounts[new_account.name] = new_account
                last_account = new_account.name
            elif "!Type:Invst" in header_line:
                # Investment
                new_investment = Investment.from_list(
                    sanitised_section_lines,
                    day_first=day_first,
                    line_number=line_number,
                )

                if last_account is None:
                    raise ParserException(
                        f"Line {line_number}: "
                        "No account found before investment. "
                        "This should not happen."
                    )

                accounts[last_account].add_transaction(
                    new_investment,
                    AccountType("Invst"),
                )
            elif "!Type:Security" in header_line:
                # Security
                new_security = Security.from_list(
                    sanitised_section_lines,
                    line_number=line_number,
                )
                if new_security.symbol is None:
                    raise ParserException(
                        f"Line {line_number}: " f"No symbol found for security."
                    )
                securities[new_security.symbol] = new_security
            elif "!Type" in header_line and not accounts:
                # Accounts is empty and there's a transaction, so create default
                # account to put transactions in
                default_account = Account(
                    name="Quiffen Default Account",
                    desc=(
                        "The default account created by Quiffen when no other "
                        "accounts were present"
                    ),
                )
                accounts[default_account.name] = default_account
                last_account = default_account.name

            if header_line.lower().replace(" ", "") in (
                VALID_TRANSACTION_ACCOUNT_TYPES
            ):
                # Other transaction type
                new_transaction, new_classes = Transaction.from_list(
                    sanitised_section_lines,
                    day_first=day_first,
                    line_number=line_number,
                )

                if last_account is None:
                    raise ParserException(
                        f"Line {line_number}: "
                        "No account found before transactions. "
                        "This should not happen."
                    )

                accounts[last_account].add_transaction(
                    new_transaction,
                    AccountType(header_line.split(":")[1].strip()),
                )

                if new_transaction.category:
                    root = new_transaction.category.traverse_up()[-1]
                    if root.name in categories:
                        categories[root.name].merge(root)
                    else:
                        categories[root.name] = root

                for class_name, new_class in new_classes.items():
                    if class_name in classes:
                        classes[class_name].merge(new_class)
                    else:
                        classes[class_name] = new_class

            line_number += len(section.split("\n"))

        return cls(
            accounts=accounts,
            categories=categories,
            classes=classes,
            securities=securities,
        )

    def add_account(self, new_account: Account) -> None:
        """Add a new account to the Qif object"""
        if new_account.name in self.accounts:
            self.accounts[new_account.name].merge(new_account)
        else:
            self.accounts[new_account.name] = new_account

    def remove_account(self, account_name: str) -> Account:
        """Remove an account from this Qif object"""
        try:
            return self.accounts.pop(account_name)
        except KeyError as e:
            raise KeyError(
                f'Account "{account_name}" does not exist in this Qif object.'
            ) from e

    def add_category(self, new_category: Category) -> None:
        """Add a new category to the Qif object"""
        self.categories = add_categories_to_container(  # type: ignore
            new_category,
            self.categories,
        )

    def remove_category(
        self,
        category_name: str,
        keep_children: bool = True,
    ) -> Category:
        """Remove a category from this Qif object"""
        try:
            category = self.categories.pop(category_name)
        except KeyError as e:
            raise KeyError(
                f'Category "{category_name}" does not exist in this Qif object.'
            ) from e

        if keep_children:
            print("Keeping children")
            for child in category.children:
                child.set_parent(None)
                self.add_category(child)

        return category

    def add_class(self, new_class: Class) -> None:
        """Add a new class to the Qif object"""
        if new_class.name in self.classes:
            self.classes[new_class.name].merge(new_class)
        else:
            self.classes[new_class.name] = new_class

    def remove_class(self, class_name: str) -> Class:
        """Remove a class from this Qif object"""
        try:
            return self.classes.pop(class_name)
        except KeyError as e:
            raise KeyError(
                f'Class "{class_name}" does not exist in this Qif object.'
            ) from e

    def add_security(self, new_security: Security) -> None:
        """Add a new security to the Qif object"""
        if not new_security.symbol:
            raise ValueError(
                "Cannot add a security without a symbol to the Qif object."
            )

        if new_security.symbol in self.securities:
            self.securities[new_security.symbol].merge(new_security)
        else:
            self.securities[new_security.symbol] = new_security

    def remove_security(self, security_symbol: str) -> Security:
        """Remove a security from this Qif object"""
        try:
            return self.securities.pop(security_symbol)
        except KeyError as e:
            raise KeyError(
                f'Security "{security_symbol}" does not exist in this Qif ' f"object."
            ) from e

    def to_qif(
        self,
        path: Optional[Union[FilePath, str, None]] = None,
        date_format: str = "%Y-%m-%d",
        encoding: str = "utf-8",
    ) -> str:
        """Convert the Qif object to a QIF file"""
        qif = ""

        if self.categories:
            qif += (
                "^\n".join(category.to_qif() for category in self.categories.values())
                + "^\n"
            )

        if self.classes:
            qif += "^\n".join(cls.to_qif() for cls in self.classes.values()) + "^\n"

        if self.accounts:
            qif += (
                "^\n".join(
                    account.to_qif(date_format=date_format, classes=self.classes)
                    for account in self.accounts.values()
                )
                + "^\n"
            )

        if path:
            Path(path).write_text(qif, encoding=encoding)

        return qif

    def _get_data_dicts(
        self,
        data_type: QifDataType = QifDataType.TRANSACTIONS,
        date_format: Optional[str] = "%Y-%m-%d",
        ignore: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Converts specified data from the Qif object to a list of dicts"""
        if ignore is None:
            ignore = []

        if data_type == QifDataType.TRANSACTIONS:
            data_dicts = []
            for account in self.accounts.values():
                for transaction_list in account.transactions.values():
                    data_dicts += [
                        transaction.to_dict(ignore=ignore)
                        for transaction in transaction_list
                        if not isinstance(transaction, Investment)
                    ]
        elif data_type == QifDataType.INVESTMENTS:
            data_dicts = []
            for account in self.accounts.values():
                for transaction_list in account.transactions.values():
                    data_dicts += [
                        transaction.to_dict(ignore=ignore)
                        for transaction in transaction_list
                        if isinstance(transaction, Investment)
                    ]
        elif data_type == QifDataType.ACCOUNTS:
            data_dicts = [
                account.to_dict(ignore=ignore) for account in self.accounts.values()
            ]
        elif data_type == QifDataType.CATEGORIES:
            data_dicts = [
                category.to_dict(ignore=ignore) for category in self.categories.values()
            ]
        elif data_type == QifDataType.CLASSES:
            data_dicts = [
                class_.to_dict(ignore=ignore) for class_ in self.classes.values()
            ]
        elif data_type == QifDataType.SECURITIES:
            data_dicts = [
                security.to_dict(ignore=ignore) for security in self.securities.values()
            ]
        else:
            raise ValueError(
                f"Invalid data_type: {data_type}. Must be one of "
                f"{list(QifDataType)}"
            )

        # Format and hide private fields
        return [  # type: ignore
            utils.apply_csv_formatting_to_container(
                {
                    k: v
                    for k, v in data_dict.items()
                    if not k.startswith("_") and k not in ignore
                },
                date_format=date_format,
            )
            for data_dict in data_dicts
        ]

    def to_csv(
        self,
        path: Optional[Union[FilePath, str, None]] = None,
        data_type: QifDataType = QifDataType.TRANSACTIONS,
        date_format: str = "%Y-%m-%d",
        ignore: Optional[List[str]] = None,
        delimiter: str = ",",
        quote_character: str = '"',
        encoding: str = "utf-8",
    ) -> str:
        """Convert part of the Qif object to a CSV file. The data_type
        parameter can be used to specify which part of the Qif object to
        convert to CSV. The default is to convert transactions.

        Parameters
        ----------
        path : Union[FilePath, str, None], optional
            The path to write the CSV file to, by default None
        data_type : QifDataType, optional
            The type of data to convert to CSV, by default
            QifDataType.TRANSACTIONS
        date_format : str, optional
            The date format to use when converting dates to strings, by
            default '%Y-%m-%d'
        ignore : List[str], optional
            A list of fields to ignore when converting to CSV, by default
            None
        delimiter : str, optional
            The delimiter to use when writing the CSV file, by default ','
        quote_character : str, optional
            The quote character to use when writing the CSV file, by
            default '"'
        encoding : str, default='utf-8'
            The encoding to use when writing the CSV file
        """
        if ignore is None:
            ignore = []

        data_dicts = self._get_data_dicts(
            data_type=data_type,
            date_format=date_format,
            ignore=ignore,
        )

        headers: Set[str] = set()
        for data_dict in data_dicts:
            headers.update(k for k in data_dict.keys())

        output = io.StringIO()

        writer = csv.DictWriter(
            output,
            fieldnames=headers,
            extrasaction="ignore",  # Ignore extra fields (e.g. private fields)
            dialect="unix",  # Use Unix line endings
            delimiter=delimiter,
            quotechar=quote_character,
        )
        writer.writeheader()
        for data_dict in data_dicts:
            writer.writerow(data_dict)

        return_value = output.getvalue()

        if path:
            Path(path).write_text(return_value, encoding=encoding)

        return return_value

    def to_dataframe(
        self,
        data_type: QifDataType = QifDataType.TRANSACTIONS,
        ignore: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Convert part of the Qif object to a Pandas DataFrame. The
        data_type parameter can be used to specify which part of the Qif
        object to convert to a DataFrame. The default is to convert
        transactions.

        Parameters
        ----------
        data_type : QifDataType, optional
            The type of data to convert to a DataFrame, by default
            QifDataType.TRANSACTIONS
        ignore : List[str], optional
            A list of fields to ignore when converting to a DataFrame, by
            default None

        Returns
        -------
        pd.DataFrame
            The data as a Pandas DataFrame
        """
        if not PANDAS_INSTALLED:
            raise ModuleNotFoundError(
                "The pandas module must be installed to use this method"
            )

        if ignore is None:
            ignore = []

        data_dicts = self._get_data_dicts(
            data_type=data_type,
            date_format=None,
            ignore=ignore,
        )

        return pd.DataFrame(data_dicts)
