class Security:
    """
    A class used to represent a security.

    Behaves like the Investment class.
    """

    def __init__(self,
                name: str = None,
                symbol: str = None,
                type: str = None,
                goal: str = None,
                line_number: int = None
                ):
        """Initialise an instance of the Investment class.

        Parameters
        ----------
        name : str, default=None
            The name of the security
        symbol : str, default=None
            The symbol to be used for the security
        type : str, default=None
            The type of the security (e.g., share, bond, ...)
        goal : str, default=None
            Purpose of holding the security
        line_number : int, default=None
            The line number of the investment in the QIF file.
        """
        self._name = name
        self._symbol = symbol
        self._type = type
        self._goal = goal
        self._line_number = line_number

    def __eq__(self, other):
        if not isinstance(other, Security):
            return False

        return self.__dict__ == other.__dict__

    def __str__(self):
        properties = ''
        for (object_property, value) in self.__dict__.items():
            if value:
                properties += f'\n    {object_property.strip("_").replace("_", " ").title()}: {value}'

        return 'Security:' + properties

    def __repr__(self):
        properties = ''
        for (object_property, value) in self.__dict__.items():
            if value is not None:
                properties += f'{object_property.strip("_")}={repr(value)}, '

        properties = properties.strip(', ')
        return f'Security({properties})'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._date = str(new_name)

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol):
        self._symbol = str(new_symbol)

    @property
    def goal(self):
        return self._goal

    @goal.setter
    def goal(self, new_goal):
        self._goal = str(new_goal)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, new_type):
        self._type = str(new_type)

    @property
    def line_number(self):
        return self._line_number

    @classmethod
    def from_list(cls, lst, line_number=None):
        """Return a class instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the security.
        line_number : int, default=None
            The line number of the header line of the security in the QIF file.

        Returns
        -------
        Security
            A Security object created from the QIF strings.
        """
        kwargs = {}
        for field in lst:
            field = field.replace('\n', '')

            if not field:
                continue
            line_code = field[0]

            try:
                field_info = field[1:]
            except KeyError:
                field_info = ''

            # Check the QIF line code for security-related operations, then append to kwargs.
            if line_code == 'N':
                kwargs['name'] = field_info
            elif line_code == 'S':
                kwargs['symbol'] = field_info
            elif line_code == 'T':
                kwargs['type'] = field_info
            elif line_code == 'G':
                kwargs['goal'] = field_info

        if line_number is not None:
            kwargs['line_number'] = line_number

        return cls(**kwargs)

    @classmethod
    def from_string(cls, string, separator='\n', line_number=None):
        """Return a class instance from a QIF file section string.

        Parameters
        ----------
        string : str
            The string containing the QIF-formatted data.
        separator : str, default='\n'
             The line separator for the QIF file. This probably won't need changing.
        line_number : int, default=None
            The line number of the header line of the investment in the QIF file.

        Returns
        -------
        Security
            A Security object created from the QIF strings.
        """
        property_list = string.split(separator)
        return cls.from_list(property_list, line_number)

    def to_dict(self, ignore=None):
        """Return a dict object representing the Security.

        Parameters
        ----------
        ignore : list of str, default=None
             A list of strings of parameters that should be excluded from the dict.

        Returns
        -------
        dict
            A dict representing the Investment object.
        """

        if ignore is None:
            ignore = []

        res = {key.strip('_'): value for (key, value) in self.__dict__.items()
               if value is not None and key.strip('_') not in ignore}

        return res