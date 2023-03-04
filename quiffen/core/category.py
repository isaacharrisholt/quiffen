from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Union

from pydantic import validator

from quiffen import utils
from quiffen.core.base import BaseModel, Field


class CategoryType(str, Enum):
    """Enum representing the different types of categories in a QIF file."""

    EXPENSE = "expense"
    INCOME = "income"


class Category(BaseModel):
    """
    A node-like class used to represent a category. Can be built into trees to
    represent category families.

    Parameters
    ----------
    name : str
        The name of the category.
    desc : str, default=None
        The category's description.
    tax_related : bool, default=None
        Whether the category represents a tax related group of transactions.
    category_type : CategoryType, default='expense'
        The type of category. Can be either 'expense' or 'income'.
    budget_amount : decimal.Decimal, default=None
        The budget amount for this category.
    tax_schedule_info : str, default=None
        Information about the tax schedule for this category.
    children : list of Category
        A list of the category's children objects.
    parent : Category, default=None
        The parent category for this category.
    hierarchy : str, default=None
        The category hierarchy, separated by : characters.

    Examples
    --------
    Creating a category tree, then rendering it to console.

    >>> import quiffen
    >>> food = quiffen.Category(name='Food')
    >>> food
    Category(name='Food', expense=True, hierarchy='Food')
    >>> essentials = quiffen.Category(name='Essentials')
    >>> food.add_child(essentials)
    >>> pastas = quiffen.Category(name='Pastas')
    >>> essentials.add_child(pastas)
    >>> pastas.hierarchy
    'Food:Essentials:Pastas'
    >>> meat = quiffen.Category(name='Meat')
    >>> food.add_child(meat)
    >>> print(food.render_tree())
    Food (root)
    └─ Essentials
       └─ Pastas
    └─ Meat

    Removing a category from a tree by passing in the Category instance or the
    category name string.

    >>> print(food.render_tree())
    Food (root)
    └─ Essentials
       └─ Pastas
    └─ Meat
       └─ Chicken
    >>> meat
    Category(
        name='Meat',
        expense=True,
        parent=Category(name='Food', expense=True, hierarchy='Food'),
        hierarchy='Food:Meat',
    )
    >>> food.remove_child(meat, keep_children=True)
    >>> print(food.render_tree())
    Food (root)
    └─ Essentials
       └─ Pastas
    └─ Chicken
    >>> food.remove_child('Essentials')
    >>> print(food.render_tree())
    Food (root)
    └─ Chicken
    """

    name: str
    desc: Optional[str] = None
    tax_related: Optional[bool] = None
    category_type: CategoryType = CategoryType.EXPENSE
    budget_amount: Optional[Decimal] = None
    tax_schedule_info: Optional[str] = None
    hierarchy: Optional[str] = None
    children: List[Category] = []
    parent: Optional[Category] = None

    __CUSTOM_FIELDS: List[Field] = []  # type: ignore

    def __str__(self) -> str:
        properties = ""
        for object_property, value in self.__dict__.items():
            if value:
                if object_property == "parent":
                    properties += (
                        f'\n\tParent: {self.parent.name if self.parent else "None"}'
                    )
                elif object_property == "children":
                    properties += f"\n\tChildren: {len(self.children)}"
                elif object_property == "category_type":
                    properties += f"\n\tCategory Type: {value.value}"
                else:
                    properties += (
                        f"\n\t"
                        f'{object_property.replace("_", " ").strip().title()}: '
                        f"{value}"
                    )
        return "Category:" + properties

    def __lt__(self, other) -> bool:
        return self.name < other.name

    @validator("hierarchy", pre=True, always=True)
    def _set_hierarchy(cls, v: str, values) -> str:
        if not v:
            return values["name"]

        if values.get("parent", None) and v != values["name"]:
            raise ValueError("Hierarchy must match name if no parent is set.")

        if not v.endswith(values["name"]):
            raise ValueError("Hierarchy must end with name.", v, values["name"])

        return v

    def _refresh_hierarchy(self) -> None:
        """Refreshes the hierarchy of the current category and all its children
        recursively."""
        for child in self.children:
            child.hierarchy = (
                self.hierarchy + ":" + child.name if self.hierarchy else child.name
            )
            child._refresh_hierarchy()

    def dict(self, exclude: Optional[Iterable[str]] = None, **_) -> Dict[str, Any]:
        """Return a representation of the Category object as a dict.

        Overwrites pydantic.BaseModel.dict or else it will recurse infinitely
        when trying to serialize the parent and children attributes.

        Parameters
        ----------
        exclude : list of str
            A list of the object's attributes that should not be included in the
            resulting dict.
        """
        if exclude is None:
            exclude = []

        res = {
            key.strip("_"): value
            for (key, value) in self.__dict__.items()
            if key.strip("_") not in exclude
        }

        if self.children and "children" not in exclude:
            res["children"] = [category.name for category in self.children]

        if self.parent and "parent" not in exclude:
            res["parent"] = self.parent.name

        return res

    # This is kept for backwards compatibility
    def to_dict(
        self, ignore: Optional[Iterable[str]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Return a representation of the Category object as a dict.

        Parameters
        ----------
        ignore : iterable of str
            A list of the object's attributes that should not be included in the
            resulting dict.
        """
        return self.dict(exclude=ignore, **kwargs)

    def traverse_down(self) -> List[Category]:
        """Return a flat list of all children, grandchildren etc. of the
        current category.

        The list is ordered starting with the current category, then its
        children, then the children's children etc.
        """
        nodes_to_visit = [self]
        all_children = []
        while nodes_to_visit:
            current_node = nodes_to_visit.pop()
            all_children.append(current_node)
            nodes_to_visit.extend(current_node.children)
        return all_children

    def traverse_up(self: Category) -> List[Category]:
        """Return a list of all parents, grandparents etc. of the current
        category.

        The list is ordered from the current category to the root category.
        """
        current_node = self
        all_parents = [self]
        while current_node.parent:
            all_parents.append(current_node.parent)
            current_node = current_node.parent
        return all_parents

    def find_child(self, node_name: str) -> Union[Category, None]:
        """Returns a node with a given name from the children of current node.

        Will return None if no node with the given name is found. If the node
        being searched for is this node, it will return itself.

        Raises
        ------
        KeyError
            If the category cannot be found.
        """
        nodes_to_visit = [self]
        while nodes_to_visit:
            current_node = nodes_to_visit.pop()
            if current_node.name == node_name:
                return current_node
            nodes_to_visit.extend(current_node.children)
        return None

    def set_parent(self, parent: Union[Category, None]) -> None:
        """Sets the parent of the current category. Set to None to make this
        category a root category.

        Raises
        ------
        ValueError
            If the parent argument is this category.
        """
        if parent is self:
            raise ValueError("Cannot set parent to self.")

        if self.parent and self in self.parent.children:
            self.parent.children.remove(self)

        self.parent = parent

        if parent:
            parent.children.append(self)
            parent._refresh_hierarchy()
        else:
            self.hierarchy = self.name
            self._refresh_hierarchy()

    def add_child(self, child: Union[Category, str]) -> Category:
        """Adds a child category to the current category. Pass a string to
        create a new category with that name.

        Returns
        -------
        Category
            The newly added child category.
        """
        if isinstance(child, str):
            child = Category(name=child)
        child.set_parent(self)
        return child

    def set_children(self, children: Iterable[Category]) -> None:
        """Sets the children of the current category.

        Will remove all existing children and replace them with the new ones.
        """
        self.children = []
        for child in children:
            self.add_child(child)

    def remove_child(
        self,
        child: Union[Category, str],
        keep_children: bool = False,
    ) -> Category:
        """Remove a child category from the current category's hierarchy.

        Parameters
        ----------
        child : str or Category
            The Category object to be removed as a child or the string name of
            the category.
        keep_children : bool, default=False
            Whether the children of the removed category should be kept in the
            tree and moved up a level.

        Returns
        -------
        Category
            The removed category.

        Raises
        ------
        KeyError
            If the category cannot be found.
        """
        if isinstance(child, str):
            child_category = self.find_child(child)
        else:
            child_category = self.find_child(child.name)

        if not child_category:
            raise KeyError(f"Category '{child}' not found.")

        parent = child_category.parent

        if parent:
            new_children = [c for c in parent.children if c != child_category]
        else:
            new_children = []

        if keep_children:
            for grandchild in child_category.children:
                new_children.append(grandchild)

        if parent:
            parent.set_children(new_children)
        child_category.set_parent(None)
        return child_category

    def merge(self, other: Category) -> bool:
        """Recursively merge another category tree into this one.

        Will check through the entire tree for categories with the same name
        and merge them. If a category with the same name is found, the
        children of the other category will be added to the current category
        and the other category will be removed.

        Returns
        -------
        bool
            True if the merge was successful, False otherwise.
        """
        if other.name != self.name:
            for child in self.children:
                success = child.merge(other)
                if success:
                    return True
            return False
        else:
            for other_child in other.children:
                if this_child := self.find_child(other_child.name):
                    this_child.merge(other_child)
                else:
                    self.add_child(other_child)
            return True

    def render_tree(self, _level: int = 0) -> str:
        """Renders a tree-like structure for categories.

        Runs recursively, and uses ``_level`` to keep track of the indentation.
        """
        if not self.children:
            return self.name

        if self.parent is None:
            is_root_str = " (root)"
        else:
            is_root_str = ""

        return (
            self.name
            + f"{is_root_str}\n"
            + "\n".join(
                [
                    "   " * _level + "└─ " + child.render_tree(_level + 1)
                    for child in self.children
                ]
            )
        )

    def _to_qif_string(self) -> str:
        """Return a QIF representation of the individual Category object."""
        qif = f"!Type:Cat\nN{self.hierarchy}\n"

        if self.desc:
            qif += f"D{self.desc}\n"
        if self.tax_related is not None:
            qif += f"T{self.tax_related}\n"

        if self.category_type == CategoryType.INCOME:
            qif += "I\n"
        elif self.category_type == CategoryType.EXPENSE:
            qif += "E\n"

        if self.budget_amount:
            qif += f"B{self.budget_amount}\n"
        if self.tax_schedule_info:
            qif += f"R{self.tax_schedule_info}\n"

        qif += utils.convert_custom_fields_to_qif_string(
            self._get_custom_fields(),
            self,
        )

        return qif

    def to_qif(self) -> str:
        """Return a QIF representation of all the categories in the tree."""
        return "^\n".join([c._to_qif_string() for c in self.traverse_down()])

    @classmethod
    def from_list(cls, lst: List[str]) -> Category:
        """Return a Category instance from a list of QIF strings.

        Parameters
        ----------
        lst : list of str
            List of strings containing QIF information about the category.
        """
        kwargs: Dict[str, Any] = {}
        new_parent: Optional[Union[Category, None]] = None
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
                temp_cat = create_categories_from_hierarchy(field_info)
                kwargs["name"] = temp_cat.name
                kwargs["hierarchy"] = temp_cat.hierarchy
                new_parent = temp_cat.parent
                if new_parent:
                    new_parent.remove_child(temp_cat)
            elif line_code == "D":
                kwargs["desc"] = field_info
            elif line_code == "T":
                kwargs["tax_related"] = field_info or True
            elif line_code == "E":
                kwargs["category_type"] = CategoryType.EXPENSE
            elif line_code == "I":
                kwargs["category_type"] = CategoryType.INCOME
            elif line_code == "B":
                kwargs["budget_amount"] = field_info.replace(",", "")
            elif line_code == "R":
                kwargs["tax_schedule_info"] = field_info
            else:
                raise ValueError(f"Unknown line code: {line_code}")

        new_cat = cls(**kwargs)
        new_cat.set_parent(new_parent)
        return new_cat


ListOrDictOfCategories = Union[List[Category], Dict[str, Category]]


def create_categories_from_hierarchy(hierarchy: str) -> Category:
    """Create a Category instance from a QIF hierarchy string. Returns the
    lowest category of the hierarchy.
    """
    categories = hierarchy.split(":")
    root_category = Category(name=categories[0])
    current_category = root_category

    if len(categories) > 1:
        for category in categories[1:]:
            current_category = current_category.add_child(category)
    return current_category


def add_categories_to_container(
    new_category: Category,
    categories: ListOrDictOfCategories,
) -> ListOrDictOfCategories:
    """Add ``new_category`` to ``categories`` after first creating necessary
    hierarchy.

    If ``new_category`` already exists somewhere in ``categories``, it will
    be merged with the existing category.

    Parameters
    ----------
    new_category : Category
        The new category to be added to the iterable of categories.
    categories : List[Category] or Dict[str, Category]
        Iterable containing categories. If in a dict, Category objects are the
        values.

    Returns
    -------
    categories : List[Category] or Dict[str, Category]
        The new iterable, now containing ``new_category``
    """
    # Add categories in hierarchy
    categories_is_dict = isinstance(categories, dict)
    if new_category.hierarchy != new_category.name or new_category.children:
        # Get the root category in the chain
        root = new_category.traverse_up()[-1]

        iterator = categories.values() if categories_is_dict else categories

        # Check if the root category already exists in the categories container
        for category in iterator:
            category: Category  # Type hint
            success = category.merge(root)
            if success:
                break
        else:
            # If the category doesn't exist, add it to the categories container
            if categories_is_dict:
                categories[root.name] = root
            else:
                categories.append(root)
    else:
        if categories_is_dict:
            categories[new_category.name] = new_category
        else:
            categories.append(new_category)

    return categories
