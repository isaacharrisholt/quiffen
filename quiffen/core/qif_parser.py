from quiffen.core.transactions import Transaction, TransactionList

try:
    import pandas as pd
    PANDAS_INSTALLED = True
except ModuleNotFoundError:
    PANDAS_INSTALLED = False


class QifParser:
    """
    The main class of the package. For parsing QIF files.

    Parameters
    ----------
    path : str
        Path to QIF file.
    day_first : bool
        Whether or not dates in QIF file are stored with the day first (UK) or month first (US)
    separator : str
        Separator used in QIF file.
    """
    def __init__(self, path, day_first=True, separator='\n'):
        self._path = path
        self._day_first = day_first
        self._separator = separator

        self._data, self._data_by_line = self._read_qif(self._path, self._separator)

        self._transactions = self._parse_transactions(self._data, self._separator, self._day_first)
        self._account_type = self._parse_account_type(self._data_by_line)

    def __eq__(self, other):
        return self.path == other.path

    def __str__(self):
        return f"""
QIF Parser:
    Path: {self._path}
    Day First: {self._day_first}
    Separator: {repr(self._separator)}
    No. Transactions: {len(self._transactions)}
    Account Type: {self._account_type}
"""

    def __repr__(self):
        return f'QifParser(path={repr(self._path)}, day_first={self._day_first}, separator={repr(self._separator)})'

    @property
    def path(self):
        return self._path

    @property
    def day_first(self):
        return self._day_first

    @property
    def separator(self):
        return self._separator

    @property
    def transactions(self):
        return self._transactions

    @transactions.setter
    def transactions(self, new_list):
        self._transactions = TransactionList(*new_list)

    @property
    def account_type(self):
        return self._account_type

    @staticmethod
    def _read_qif(path, separator):
        """Validate QIF file provided and return data."""
        if path[-3:].lower() != 'qif':
            raise FileNotFoundError(f'\'{path}\' does not point to a valid QIF file. Only .QIF file types are allowed')

        with open(path, 'r') as f:
            data = f.read()
            data_by_line = data.split(separator)

        return data, data_by_line

    @staticmethod
    def _parse_account_type(data_by_line):
        """Parse account type of QIF file."""
        for line in data_by_line:
            if '!Type:' in line:
                return line.replace('!Type:', '').strip('\n')

    @staticmethod
    def _parse_transactions(data, separator, day_first):
        """Parse transactions in QIF file."""
        data = data.split('^\n')
        return TransactionList(*[Transaction.from_string(datum, separator=separator, day_first=day_first)
                                 for datum in data if datum])

    def to_dicts(self, ignore=None):
        """Return a list of dict representations of transactions."""
        if ignore is None:
            ignore = []

        return [transaction.to_dict(ignore=ignore) for transaction in self._transactions]

    def to_csv(self, path, ignore=None):
        """Write a CSV file containing all transaction data."""
        if ignore is None:
            ignore = []

        properties = [key for key in self._transactions[0].__dict__.keys() if key.replace('_', '') not in ignore]

        with open(path, 'w') as f:
            f.write(','.join([property_name.strip('_').replace('_', ' ').title() for property_name in properties])
                    + '\n')

            for transaction in self._transactions:
                f.write(','.join([str(transaction.__dict__[property_name]) for property_name in properties]) + '\n')

    def to_dataframe(self, ignore=None):
        """Return a pandas DataFrame containing all transaction data."""
        if ignore is None:
            ignore = []

        if not PANDAS_INSTALLED:
            raise ModuleNotFoundError('The pandas module must be installed to use this method')
        return pd.DataFrame(self.to_dicts(ignore=ignore))
