class Category:
    def __init__(self,
                 name: str,
                 desc: str = None,
                 tax_related: bool = None,
                 expense: bool = True,
                 income: bool = False,
                 budget_amount: float = None,
                 tax_schedule_info: str = None,
                 parent=None,
                 hierarchy: str = None):
        self._name = name
        self._desc = desc
        self._tax_related = tax_related
        self._expense = expense
        self._income = income
        self._budget_amount = budget_amount
        self._tax_schedule_info = tax_schedule_info
        self._parent = parent
        self._hierarchy = hierarchy
        self._children = []

    def __eq__(self, other):
        if not isinstance(other, Category):
            return False
        return self._name == other.name

    def __str__(self):
        return repr(self)

    def __repr__(self):
        properties = ''
        ignore = ['_children']
        for (object_property, value) in self.__dict__.items():
            if value and object_property not in ignore:
                properties += f'{object_property.strip("_")}={repr(value)}, '

        properties = properties.strip(', ')
        return f'Category({properties})'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = str(new_name)

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, new_desc):
        self._desc = str(new_desc)

    @property
    def tax_related(self):
        return self._tax_related

    @tax_related.setter
    def tax_related(self, new_bool):
        if isinstance(new_bool, str) and new_bool.lower() == 'false':
            self._tax_related = False
        else:
            self._tax_related = bool(new_bool)

    @property
    def expense(self):
        return self._expense

    @expense.setter
    def expense(self, new_bool):
        if isinstance(new_bool, str) and new_bool.lower() == 'false':
            self._expense = False
            self._income = True
        else:
            self._expense = bool(new_bool)
            self._income = not bool(new_bool)

    @property
    def income(self):
        return self._income

    @income.setter
    def income(self, new_bool):
        if isinstance(new_bool, str) and new_bool.lower() == 'false':
            self._income = False
            self._expense = True
        else:
            self._income = bool(new_bool)
            self._expense = not bool(new_bool)

    @property
    def budget_amount(self):
        return self._budget_amount

    @budget_amount.setter
    def budget_amount(self, new_amount):
        self._budget_amount = float(new_amount)

    @property
    def tax_schedule_info(self):
        return self._tax_schedule_info

    @tax_schedule_info.setter
    def tax_schedule_info(self, new_info):
        self._tax_schedule_info = str(new_info)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        if not isinstance(new_parent, (Category, type(None))):
            raise TypeError('New parent must be Category object')
        self._parent = new_parent
        if self._parent and self not in self._parent.children:
            new_parent.add_child(self)

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, new_children):
        # Check types
        for child in new_children:
            if not isinstance(child, (Category, type(None))):
                raise TypeError('Children must be Category objects')

        self._children = new_children

        # Update parent nodes
        for child in self._children:
            child.parent = self

    @property
    def hierarchy(self):
        return self._hierarchy

    @hierarchy.setter
    def hierarchy(self, new_hierarchy):
        if new_hierarchy.split(':')[-1] != self._name:
            raise RuntimeError('Invalid hierarchy. Must end with current category.')
        self._hierarchy = new_hierarchy

    @classmethod
    def from_list(cls, lst):
        """Return a category instance from a list"""
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

            if line_code == 'N':
                categories = field_info.split(':')
                kwargs['name'] = categories[-1]
                kwargs['hierarchy'] = field_info
            elif line_code == 'D':
                kwargs['desc'] = field_info
            elif line_code == 'T':
                if field_info.lower() == 'false':
                    kwargs['tax_related'] = False
                else:
                    kwargs['tax_related'] = True
            elif line_code == 'E':
                kwargs['expense'] = True
                kwargs['income'] = False
            elif line_code == 'I':
                kwargs['expense'] = False
                kwargs['income'] = True
            elif line_code == 'B':
                kwargs['budget_amount'] = float(field_info)
            elif line_code == 'R':
                kwargs['tax_schedule_info'] = field_info

        return cls(**kwargs)

    @classmethod
    def from_string(cls, string, separator='\n'):
        """Return a Category from a string"""
        property_list = string.split(separator)
        return cls.from_list(property_list)

    def add_child(self, child_category):
        """Add a child category to current category."""
        if not isinstance(child_category, Category):
            raise TypeError('Child must be of type Category')

        self._children.append(child_category)
        child_category = self._children[-1]

        if child_category.parent != self:
            child_category.parent = self

    def remove_child(self, child_category):
        """Remove a child category from current category"""
        child_category._parent = None
        self._children = [child for child in self._children if child is not child_category]

    def traverse_down(self):
        """Return a list of all children, grandchildren etc."""
        nodes_to_visit = [self]
        all_children = []
        while nodes_to_visit:
            current_node = nodes_to_visit.pop()
            all_children.append(current_node)
            nodes_to_visit.extend(current_node.children)
        return all_children

    def traverse_up(self):
        """Return a list of all parents, grandparents etc."""
        current_node = self
        all_parents = []
        while current_node._parent:
            all_parents.append(current_node._parent)
            current_node = current_node._parent
        return all_parents

    def render_tree(self, level=0):
        """Renders a tree-like structure for categories."""
        if not self._children:
            return self._name

        if self._parent is None:
            is_root_str = ' (root)'
        else:
            is_root_str = ''

        return self._name + f'{is_root_str}\n' + '\n'.join(['   ' * level + '└─ ' + child.render_tree(level + 1)
                                                            for child in self._children])

    def find_category(self, value):
        """Returns a node with a given name from the children of current node"""
        nodes_to_visit = [self]
        while nodes_to_visit:
            current_node = nodes_to_visit.pop()
            if current_node.name == value:
                return current_node
            nodes_to_visit.extend(current_node.children)
        raise KeyError(f'Node with name \'{value}\' not found')

    def to_dict(self, ignore=None):
        """Return a representation of the Category object as a dict"""
        if ignore is None:
            ignore = []

        res = {key.strip('_'): value for (key, value) in self.__dict__.items()
               if key.strip('_') not in ignore and value is not None}

        if self._children and 'children' not in ignore:
            res['children'] = [category.name for category in self._children]

        if self._parent and 'parent' not in ignore:
            res['parent'] = self._parent.name

        return res


class Class:
    """
    A class used to represent a QIF Class.

    Parameters
    ----------

    """
    def __init__(self,
                 name: str,
                 desc: str = None):
        self._name = name
        self._desc = desc

    def __eq__(self, other):
        return self._name == other.name

    def __str__(self):
        res = f'Class:\n    Name: {self._name}'
        if self._desc:
            res += f'\n    Description: {self._desc}'
        return res

    def __repr__(self):
        if self._desc:
            return f'Class(name={repr(self._name)}, desc={repr(self._desc)})'
        else:
            return f'Class(name={repr(self._name)})'

    @property
    def name(self):
        return self._name

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, new_desc):
        self._desc = str(new_desc)

    @classmethod
    def from_list(cls, lst):
        name = None
        desc = None

        for field in lst:
            field = field.replace('\n', '')

            if not field:
                continue
            line_code = field[0]

            try:
                field_info = field[1:]
            except KeyError:
                field_info = ''

            if line_code == 'N':
                name = field_info
            elif line_code == 'D':
                desc = field_info

        if not name:
            raise RuntimeError('No name specified for Class')

        return cls(name, desc)

    @classmethod
    def from_string(cls, string, separator='\n'):
        """Return a Class from a string"""
        property_list = string.split(separator)
        return cls.from_list(property_list)

    def to_dict(self, ignore=None):
        """Return a representation of the Class object as a dict"""
        if ignore is None:
            ignore = []

        return {key.strip('_'): value for (key, value) in self.__dict__.items()
                if key.strip('_') not in ignore and value is not None}
