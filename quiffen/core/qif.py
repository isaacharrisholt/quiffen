from quiffen import utils
from quiffen.core.accounts import Account
from quiffen.core.categories_classes import Category, Class
from quiffen.core.transactions import Transaction, Investment
from quiffen.core.security import Security

try:
    import pandas as pd

    PANDAS_INSTALLED = True
except ModuleNotFoundError:
    PANDAS_INSTALLED = False

VALID_TRANSACTION_ACCOUNT_TYPES = [
    '!type:cash',
    '!type:bank',
    '!type:ccard',
    '!type:oth a',
    '!type:oth l',
    '!type:invoice'
]


class ParserException(Exception):
    pass


class Qif:
    """
    The main class of the package. For parsing QIF files.

    See the readme for usage examples.

    """

    def __init__(self,
                 accounts: dict = None,
                 categories: dict = None,
                 classes: dict = None,
                 securities: dict = None
                 ):
        """Initialise an instance of the Qif class.

        Parameters
        ----------
        accounts : dict, default=None
            A dict of accounts in the form {'Account Name': account_object}.
        categories : dict, default=None
            A dict of categories in the form {'Category Name': category_object}.
        classes : dict, default=None
            A dict of classes in the form {'Class Name': class_object}.
        securities : dict, default=None
            A dict of securities in the form {'Security Name': security_object}.

        Raises
        ------
        TypeError
            If any provided arguments are the wrong type.
        """
        if accounts:
            self._assert_type(accounts, Account)
        else:
            accounts = {}

        if categories:
            self._assert_type(categories, Category)
        else:
            categories = {}

        if classes:
            self._assert_type(classes, Class)
        else:
            classes = {}

        if securities:
            self._assert_type(securities, Security)
        else:
            securities = {}

        self._accounts = accounts
        self._categories = categories
        self._classes = classes
        self._securities = securities

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        accounts = {name: repr(account) for (name, account) in self._accounts.items()}
        categories = {name: repr(cat) for (name, cat) in self._categories.items()}
        securities = {name: repr(security) for (name, security) in self._securities.items()}
        return f"""
QIF:
    Accounts: {accounts}
    Categories: {categories}
    Classes: {[repr(klass) for klass in self._classes]}
    Securities: {securities}
"""

    def __repr__(self):
        accounts = {name: repr(account) for (name, account) in self._accounts.items()}
        categories = {name: repr(cat) for (name, cat) in self._categories.items()}
        securities = {name: repr(security) for (name, security) in self._securities.items()}
        return f'Qif(accounts={accounts}, ' \
               f'categories={categories}, ' \
               f'classes={[repr(klass) for klass in self._classes]}, ' \
               f'securities={securities})'

    @property
    def accounts(self):
        return self._accounts

    @accounts.setter
    def accounts(self, new_accounts):
        self._assert_type(new_accounts, Account)
        self._accounts = new_accounts

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, new_categories):
        self._assert_type(new_categories, Category)
        self._categories = new_categories

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, new_classes):
        self._assert_type(new_classes, Class)
        self._classes = new_classes

    @property
    def securities(self):
        return self._securities

    @securities.setter
    def classes(self, new_securities):
        self._assert_type(new_securities, Security)
        self._securities = new_securities

    @classmethod
    def parse(cls, filepath, separator='\n', day_first=True):
        """Return a class instance from a QIF file.

        Parameters
        ----------
        filepath : str
            The path to the QIF file.
        separator : str, default='\n'
             The line separator for the QIF file. This probably won't need changing.
        day_first : bool, default=True
             Whether the day or month comes first in the date.

        Returns
        -------
        Qif
            A Qif object containing all the data in the QIF file.
        """
        data = cls._read_qif(filepath)

        accounts = {}
        last_account = None
        categories = {}
        classes = {}
        securities = {}

        sections = data.split('^\n')
        last_header = None
        line_number = 1

        for section in sections:
            if not section:
                continue

            header_line = section.split('\n')[0]
            if header_line is None:
                continue

            # Allow for comments and blank lines at the top of sections
            i = 0
            while True:
                if header_line.strip() != '':
                    if header_line[0] != '#':
                        break
                i += 1
                print(i, section.split('\n'))
                header_line = section.split('\n')[i]

            # Check for new categories and accounts first, as then we can be sure it's a transaction in case a default
            # account needs to be added
            if header_line[0] != '!':
                if last_header is None:
                    raise ParserException(f'Header \'{header_line}\' not recognised and no previous header supplied')
                header_line = last_header

            if '!Type:Cat' in header_line:
                # Section contains category information
                new_category = Category.from_string(section)
                categories = utils.create_categories(new_category, categories)
            elif '!Type:Class' in header_line:
                new_class = Class.from_string(section)
                classes[new_class.name] = new_class
            elif '!Type:Security' in header_line:
                new_security = Security.from_string(section)
                securities[new_security.name] = new_security
            elif '!Account' in header_line:
                new_account = Account.from_string(section)
                accounts[new_account.name] = new_account
                last_account = new_account.name
            elif '!Type' in header_line and not accounts:
                # Accounts is empty and there's a transaction, so create default account to put transactions in
                default_account = Account(name='Quiffen Default Account',
                                          desc='The default account created by Quiffen when no other accounts were '
                                               'present')
                accounts[default_account.name] = default_account
                last_account = default_account.name
            elif '!Type:Invst' in header_line:
                # Investment
                new_investment = Investment.from_string(section, separator=separator, day_first=day_first,
                                                        line_number=line_number)
                accounts[last_account].add_transaction(new_investment, 'Invst')
            elif header_line.lower().replace(' ', '') in VALID_TRANSACTION_ACCOUNT_TYPES:
                # Other transaction type
                new_transaction, new_categories, new_classes = Transaction.from_string(section, separator=separator,
                                                                                       day_first=day_first,
                                                                                       line_number=line_number)
                accounts[last_account].add_transaction(new_transaction, header_line.replace(' ', ''))
                categories.update(new_categories)
                classes.update(new_classes)

            last_header = header_line
            line_number += len(section.split('\n'))

        return cls(accounts=accounts, categories=categories, classes=classes, securities=securities)

    @staticmethod
    def _assert_type(iterable, types):
        # Assert that all items in an iterable are of specific types.
        if isinstance(iterable, dict):
            for item in iterable.values():
                if not isinstance(item, types):
                    raise TypeError(f'\'{repr(item)} is not of type {types}')
        else:
            for item in iterable:
                if not isinstance(item, types):
                    raise TypeError(f'\'{repr(item)} is not of type {types}')

    @staticmethod
    def _read_qif(path):
        # Validate QIF file provided and return data.
        if path[-3:].lower() != 'qif':
            raise FileNotFoundError(f'\'{path}\' does not point to a valid QIF file. Only .QIF file types are allowed')

        with open(path, 'r') as f:
            data = f.read().strip().strip('\n')
            if not data:
                raise ParserException('File is empty')

        return data

    def add_account(self, new_account):
        """Add a new account to the Qif object.

        Parameters
        ----------
        new_account : Account
            The Account to be added to the Qif.

        Raises
        ------
        TypeError
            If ``new_account`` is not an Account object.
        """
        self._assert_type([new_account], Account)
        self._accounts[new_account.name] = new_account

    def remove_account(self, account_name):
        """Remove an account from this Qif object.

        Parameters
        ----------
        account_name : str
            The name of the account.

        Returns
        -------
        Account
            The Account removed.
        """
        return self._accounts.pop(account_name)

    def add_category(self, new_category):
        """Add a new category to the object.

        Parameters
        ----------
        new_category : Category
            The Category to be added to the Qif.

        Raises
        ------
        TypeError
            If ``new_category`` is not a Category object.
        """
        self._assert_type([new_category], Category)
        self._categories[new_category.name] = new_category

    def remove_category(self, category_name, keep_children=True):
        """Remove a category from the Qif object.

        Parameters
        ----------
        category_name : str
            The name of the category to be removed.
        keep_children : bool, default=True
            Whether or not the children of the category will be kept (grandparent node will become the parent node).

        Returns
        -------
        Category
            The Category removed.
        """
        if category_name in self._categories:
            if keep_children:
                self._categories.update({category.name: category for category in
                                         self._categories[category_name].children})
            return self._categories.pop(category_name)

        categories_to_visit = list(self._categories.values())

        for category in categories_to_visit:
            if category.children:
                categories_to_visit.extend(category.children)
            if category.name == category_name:

                # Change children hierarchies
                children_to_visit = category.children
                for child in children_to_visit:
                    if child.children:
                        children_to_visit.extend(child)
                    if child.hierarchy:
                        child.hierarchy = child.hierarchy.replace(f'{category.name}:', '')
                    child.parent = category.parent

                parent = category.parent
                if parent is not None:
                    category_idx = parent.children.index(category)
                    parent.children.pop(category_idx)
                    parent.children.extend(category.children)
                    category.parent = None
                return category

    def add_class(self, new_class):
        """Add a new class to the object.

        Parameters
        ----------
        new_class : Class
            The Class to be added to the Qif.

        Raises
        ------
        TypeError
            If ``new_class`` is not a Class object.
        """
        self._assert_type([new_class], Class)
        self._classes[new_class.name] = new_class

    def remove_class(self, class_name):
        """Remove a class from the Qif object.

        Parameters
        ----------
        class_name : str
            The name of the Class to be removed.

        Returns
        -------
        Class
            The Class removed.
        """
        return self._classes.pop(class_name)

    def add_security(self, new_security):
        """Add a new Security to the object.

        Parameters
        ----------
        new_security : Security
            The Security to be added to the Qif.

        Raises
        ------
        TypeError
            If ``new_security`` is not a Security object.
        """
        self._assert_type([new_security], Security)
        self._securities[new_security.name] = new_security

    def remove_security(self, security_name):
        """Remove a Security from the Qif object.

        Parameters
        ----------
        security_name : str
            The name of the Security to be removed.

        Returns
        -------
        Security
            The Security removed.
        """
        return self._securities.pop(security_name)

    def to_qif(self, path=None, date_format='%d/%m/%Y'):
        """Write the Qif object to a QIF file and return the string.

        Parameters
        ----------
        path : str, default=None
            The path of the QIF file to be generated, if desired.
        date_format : str, default='%d/%m/%Y'
            The format of the date (using ``datetime`` verbs) to be input into the QIF file.

        Returns
        -------
        qif_data : str
            The string of QIF data.
        """
        qif_data = ''

        if self._classes:
            qif_data += '!Type:Class\n'
            for klass in self._classes.values():
                qif_data += f'N{klass.name}\n'
                if klass.desc:
                    qif_data += f'D{klass.desc}\n'
                qif_data += '^\n'

        if self._securities:
            securities_to_visit = list(self._securities.values())
            qif_data += '!Type:Security\n'
            for security in securities_to_visit:

                qif_data += f'N{security.name}\n' # must exist to get in .values()

                if security.symbol:
                    qif_data += f'S{security.symbol}\n'

                if security.type:
                    qif_data += f'T{security.type}\n'

                if security.goal:
                    qif_data += f'G{security.goal}\n'

                qif_data += '^\n'

        if self._categories:
            categories_to_visit = list(self._categories.values())
            qif_data += '!Type:Cat\n'
            for category in categories_to_visit:
                if category.children:
                    categories_to_visit.extend(category.children)

                qif_data += f'N{category.hierarchy}\n'

                if category.desc:
                    qif_data += f'D{category.desc}\n'

                if category.tax_related is not None:
                    qif_data += f'T{category.tax_related}\n'

                if category.expense is not None:
                    qif_data += f'E{category.expense}\n'

                if category.income is not None:
                    qif_data += f'I{category.income}\n'

                if category.budget_amount is not None:
                    qif_data += f'B{category.budget_amount}\n'

                if category.tax_schedule_info:
                    qif_data += f'R{category.tax_schedule_info}\n'

                qif_data += '^\n'

        if self._accounts:
            for account in self._accounts.values():
                qif_data += '!Account\n'

                qif_data += f'N{account.name}\n'

                if account.desc:
                    qif_data += f'D{account.desc}\n'

                if account.account_type:
                    qif_data += f'T{account.account_type}\n'

                if account.credit_limit is not None:
                    qif_data += f'L{account.credit_limit}\n'

                if account.balance is not None:
                    qif_data += f'${account.balance}\n'

                if account.date_at_balance:
                    qif_data += f'/{account.date_at_balance.strftime(date_format)}\n'

                qif_data += '^\n'

                for (header, transaction_list) in account.transactions.items():
                    qif_data += f'!Type:{header}\n'

                    for transaction in transaction_list:
                        qif_data += f'D{transaction.date.strftime(date_format)}\n'

                        if transaction.amount is not None:
                            qif_data += f'T{transaction.amount}\n'

                        if transaction.memo:
                            qif_data += f'M{transaction.memo}\n'

                        if transaction.cleared:
                            qif_data += f'C{transaction.cleared}\n'

                        if 'Invst' not in header:
                            if transaction.payee:
                                qif_data += f'P{transaction.payee}\n'

                            if transaction.payee_address:
                                qif_data += f'A{transaction.payee_address}\n'

                            if transaction.category:
                                qif_data += f'L{transaction.category.hierarchy}\n'

                            if transaction.to_account:
                                qif_data += f'L[{transaction.to_account}]\n'

                            if transaction.check_number is not None:
                                qif_data += f'N{transaction.check_number}\n'

                            if transaction.reimbursable_expense is not None:
                                qif_data += f'F{transaction.reimbursable_expense}\n'

                            if transaction.first_payment_date:
                                qif_data += f'1{transaction.first_payment_date.strftime(date_format)}\n'

                            if transaction.loan_length is not None:
                                qif_data += f'2{transaction.loan_length}\n'

                            if transaction.num_payments is not None:
                                qif_data += f'3{transaction.num_payments}\n'

                            if transaction.periods_per_annum is not None:
                                qif_data += f'4{transaction.periods_per_annum}\n'

                            if transaction.interest_rate is not None:
                                qif_data += f'5{transaction.interest_rate}\n'

                            if transaction.current_loan_balance is not None:
                                qif_data += f'6{transaction.current_loan_balance}\n'

                            if transaction.original_loan_amount is not None:
                                qif_data += f'7{transaction.original_loan_amount}\n'

                            if transaction.is_split:
                                for split in transaction.splits:
                                    if split.category:
                                        qif_data += f'S{split.category.hierarchy}\n'

                                    if split.date:
                                        qif_data += f'D{split.date.strftime(date_format)}\n'

                                    if split.amount is not None:
                                        qif_data += f'${split.amount}\n'

                                    if split.percent is not None:
                                        qif_data += f'%{split.percent}\n'

                                    if split.memo:
                                        qif_data += f'E{split.memo}\n'

                                    if split.cleared:
                                        qif_data += f'C{split.cleared}\n'

                                    if split.payee_address:
                                        qif_data += f'A{split.payee_address}\n'

                                    if split.to_account:
                                        qif_data += f'L[{split.to_account}]\n'

                                    if split.check_number is not None:
                                        qif_data += f'N{split.check_number}\n'

                        else:
                            if transaction.action:
                                qif_data += f'N{transaction.action}\n'

                            if transaction.security:
                                qif_data += f'Y{transaction.security}\n'

                            if transaction.price is not None:
                                qif_data += f'I{transaction.price}\n'

                            if transaction.quantity is not None:
                                qif_data += f'Q{transaction.quantity}\n'

                            if transaction.first_line:
                                qif_data += f'P{transaction.first_line}\n'

                            if transaction.to_account:
                                qif_data += f'L{transaction.to_account}\n'

                            if transaction.transfer_amount is not None:
                                qif_data += f'${transaction.transfer_amount}\n'

                            if transaction.commission is not None:
                                qif_data += f'O{transaction.commission}\n'

                        qif_data += '^\n'

        if path is not None:
            with open(path, 'w') as f:
                f.write(qif_data)

        return qif_data

    def to_dicts(self, data='transactions', ignore=None):
        """Return a list of dict representations of desired data.

        Parameters
        ----------
        data : {'transactions', 'investments', 'splits', 'accounts', 'categories', 'classes', 'securities'}
            The data type to be converted to dicts.
        ignore : list of str, default=None
             A list of strings of parameters that should be excluded from the dict.

        Returns
        -------
        list of dict
            A list of dict objects containing ``data`` specified.

        Raises
        ------
        RuntimeError
            If ``data`` is not a valid option.
        """
        if ignore is None:
            ignore = []

        data = data.lower()
        options = ['transactions', 'investments', 'splits', 'accounts', 'categories', 'classes', 'securities']

        if data not in options:
            raise RuntimeError(f'Can\'t get data for {data}. Valid options are:\n{", ".join(options)}')

        if data == 'transactions':
            transactions = []
            for account in self._accounts.values():
                for transaction_list in account.transactions.values():
                    for transaction in transaction_list:
                        if isinstance(transaction, Transaction):
                            transactions.append(transaction.to_dict(ignore=ignore))
            return transactions
        elif data == 'investments':
            investments = []
            for account in self._accounts.values():
                for transaction_list in account.transactions.values():
                    for transaction in transaction_list:
                        if isinstance(transaction, Investment):
                            investments.append(transaction.to_dict(ignore=ignore))
            return investments
        elif data == 'splits':
            splits = []
            for account in self._accounts.values():
                for transaction_list in account.transactions.values():
                    for transaction in transaction_list:
                        for split in transaction.splits:
                            splits.append(split.to_dict(ignore=ignore))
            return splits
        elif data == 'accounts':
            accounts = []
            for account in self._accounts.values():
                accounts.append(account.to_dict(ignore=ignore))
            return accounts
        elif data == 'categories':
            categories = []
            categories_to_visit = list(self._categories.values())

            for category in categories_to_visit:
                if category.children is not None:
                    categories_to_visit.extend(category.children)
                categories.append(category.to_dict(ignore=ignore))
            return categories
        elif data == 'classes':
            classes = []
            for klass in self._classes:
                classes.append(klass.to_dict(ignore=ignore))
            return classes
        elif data == 'securities':
            securities = []
            for security in self._securities.values():
                securities.append(security.to_dict(ignore=ignore))
            return securities

    def to_csv(self, path=None, data='transactions', ignore=None, separator=',', sub_separator=';',
               date_format='%d/%m/%Y'):
        """Write a CSV file containing desired data and return the string.

        Parameters
        ----------
        path : str, default=None
            The path of the CSV file to be created, if desired.
        data : {'transactions', 'investments', 'splits', 'accounts', 'categories', 'classes', 'securities'}
            The data type to be input into the CSV file.
        ignore : list of str, default=None
            A list of strings of parameters that should be excluded from the dict.
        separator : str, default=','
            The separator for the CSV file.
        sub_separator : str, default=';'
            The character to be used to replace ``separator`` if it appears in any strings.
        date_format : str, default='%d/%m/%Y'
            The format of the date (using ``datetime`` verbs) to be input into the QIF file.

        Returns
        -------
        csv_data : str
            A string containing the CSV data.

        Raises
        ------
        RuntimeError
            If ``data`` is not a valid option.
        ValueError
            If ``separator`` and ``sub_separator`` are present within each other.
        """
        if ignore is None:
            ignore = []

        data = data.lower()
        options = ['transactions', 'splits', 'investments', 'accounts', 'categories', 'classes', 'securities']

        if data not in options:
            raise RuntimeError(f'Can\'t get data for {data}. Valid options are:\n{", ".join(options)}')

        if separator in sub_separator or sub_separator in separator:
            raise ValueError('Separator and sub-separator cannot be equal or contain each other')

        csv_data = ''

        if data == 'transactions':
            headers = ['date', 'amount', 'memo', 'cleared', 'payee', 'payee_address', 'category', 'check_number',
                       'reimbursable_expense', 'small_business_expense', 'to_account', 'first_payment_date',
                       'loan_length', 'num_payments', 'periods_per_annum', 'interest_rate', 'current_loan_balance',
                       'original_loan_amount', 'is_split', 'splits']

            headers = [header for header in headers if header not in ignore]

            csv_data += separator.join(headers) + '\n'

            for account in self._accounts.values():
                for transaction_list in account.transactions.values():
                    for transaction in transaction_list:
                        if not isinstance(transaction, Transaction):
                            continue

                        this_line = ''
                        transaction_dict = transaction.to_dict()
                        for header in headers:
                            transaction_data = transaction_dict.get(header)

                            if transaction_data is not None:
                                if 'date' in header:
                                    this_line += transaction_data.strftime(date_format)
                                elif header == 'category':
                                    this_line += transaction_data['name']
                                elif header == 'splits':
                                    this_line += str(len(transaction_data))
                                else:
                                    this_line += str(transaction_data).replace(separator, sub_separator)

                            this_line += separator
                        this_line = this_line.strip(separator) + '\n'
                        csv_data += this_line
        elif data == 'splits':
            headers = ['date', 'amount', 'memo', 'cleared', 'payee_address', 'category', 'to_account', 'check_number',
                       'percent']

            headers = [header for header in headers if header not in ignore]

            csv_data += separator.join(headers) + '\n'

            for account in self._accounts.values():
                for transaction_list in account.transactions.values():
                    for transaction in transaction_list:
                        for split in transaction.splits:
                            this_line = ''
                            split_dict = split.to_dict()

                            for header in headers:
                                split_data = split_dict.get(header)

                                if split_data is not None:
                                    if 'date' in header:
                                        this_line += split_data.strftime(date_format)
                                    elif header == 'category':
                                        this_line += split_data['name']
                                    else:
                                        this_line += str(split_data).replace(separator, sub_separator)

                                this_line += separator
                            this_line = this_line.strip(separator) + '\n'
                            csv_data += this_line
        elif data == 'investments':
            headers = ['date', 'action', 'security', 'price', 'quantity', 'cleared', 'amount', 'memo', 'first_line',
                       'to_account', 'transfer_amount', 'commission']

            headers = [header for header in headers if header not in ignore]

            csv_data += separator.join(headers) + '\n'

            for account in self._accounts.values():
                for transaction_list in account.transactions.values():
                    for investment in transaction_list:
                        if not isinstance(investment, Investment):
                            continue

                        this_line = ''
                        investment_dict = investment.to_dict()
                        for header in headers:
                            investment_data = investment_dict.get(header)

                            if investment_data is not None:
                                if 'date' in header:
                                    this_line += investment_data.strftime(date_format)
                                elif header == 'category':
                                    this_line += investment_data['name']
                                elif header == 'splits':
                                    this_line += str(len(investment_data))
                                else:
                                    this_line += str(investment_data).replace(separator, sub_separator)

                            this_line += separator
                        this_line = this_line.strip(separator) + '\n'
                        csv_data += this_line
        elif data == 'accounts':
            headers = ['name', 'desc', 'account_type', 'credit_limit', 'balance', 'date_at_balance', 'transactions']

            headers = [header for header in headers if header not in ignore]

            csv_data += separator.join(headers) + '\n'

            for account in self._accounts.values():
                this_line = ''
                account_dict = account.to_dict()
                for header in headers:
                    account_data = account_dict.get(header)

                    if account_data is not None:
                        if header == 'date_at_balance':
                            this_line += account_data.strftime(date_format)
                        elif header == 'transactions':
                            this_line += str(len(account_data))
                        else:
                            this_line += str(account_data).replace(separator, sub_separator)

                    this_line += separator
                this_line = this_line.strip(separator) + '\n'
                csv_data += this_line
        elif data == 'categories':
            headers = ['name', 'desc', 'tax_related', 'expense', 'income', 'budget_amount', 'tax_schedule_info',
                       'parent', 'children']

            headers = [header for header in headers if header not in ignore]

            csv_data += separator.join(headers) + '\n'

            categories_to_visit = list(self._categories.values())
            for category in categories_to_visit:
                if category.children is not None:
                    categories_to_visit.extend(category.children)

                this_line = ''
                category_dict = category.to_dict()
                for header in headers:
                    category_data = category_dict.get(header)

                    if category_data is not None:
                        if header == 'children':
                            this_line += str(len(category_data))
                        else:
                            this_line += str(category_data).replace(separator, sub_separator)

                    this_line += separator
                this_line = this_line.strip(separator) + '\n'
                csv_data += this_line
        elif data == 'classes':
            headers = [header for header in ['name', 'desc'] if header not in ignore]

            csv_data += separator.join(headers) + '\n'

            for klass in self._classes:
                this_line = ''
                class_dict = klass.to_dict()
                for header in headers:
                    class_data = class_dict.get(header)

                    if class_data is not None:
                        this_line += str(class_data).replace(separator, sub_separator)

                    this_line += separator
                this_line = this_line.strip(separator) + '\n'
                csv_data += this_line

        elif data == 'securities':
            headers = [header for header in ['name','symbol','type','goal'] if header not in ignore]

            csv_data += separator.join(headers) + '\n'

            for security in self._securities:
                this_line = ''
                security_dict = security.to_dict()
                for header in headers:
                    security_data = security_dict.get(header)

                    if security_data is not None:
                        this_line += str(security_data).replace(separator, sub_separator)

                    this_line += separator

                this_line = this_line.strip(separator) + '\n'

                csv_data += this_line

        if path is not None:
            with open(path, 'w') as f:
                f.write(csv_data)

        return csv_data

    def to_dataframe(self, data='transactions', ignore=None):
        """Return a pandas DataFrame containing desired data.

        Parameters
        ----------
        data : {'transactions', 'investments', 'splits', 'accounts', 'categories', 'classes', 'securities'}
            The data type to be input into the CSV file.
        ignore : list of str, default=None
            A list of strings of parameters that should be excluded from the dict.

        Returns
        -------
        DataFrame
            A DataFrame containing he desired data.

        Raises
        ------
        ModuleNotFoundError
            If the pandas module is not installed.
        """
        if ignore is None:
            ignore = []

        if not PANDAS_INSTALLED:
            raise ModuleNotFoundError('The pandas module must be installed to use this method')

        return pd.DataFrame(self.to_dicts(data=data, ignore=ignore))
