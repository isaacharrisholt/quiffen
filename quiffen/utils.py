from datetime import datetime

from quiffen.core.categories_classes import Category


def parse_date(date_string, day_first=True):
    """Parse a string date of an unknown format and return a datetime object.

    Parameters
    ----------
    date_string : str
        String containing date found in QIF file
    day_first : bool, default=True
        Whether or not the day comes first in the date (e.g. UK date) or after the month (e.g. US date)

    Returns
    -------
    datetime.datetime
        datetime object with the date data from the ``date_string`` parameter.

    Raises
    -------
    ValueError
        If the date cannot be parsed.
    """
    day_first_patterns = ['%d/%m/%Y',
                          '%d-%m-%Y',
                          '%d/%m/%y',
                          '%d-%m-%y',
                          '%d0%B0%Y',  # 0 values instead of spaces for reasons explained below
                          '%d0%B0%y',
                          '%d0%b0%Y',
                          '%d0%b0%y']

    month_first_patterns = ['%m/%d/%Y',
                            '%m-%d-%Y',
                            '%m/%d/%y',
                            '%m-%d-%y',
                            '%B0%d0%Y',
                            '%B0%d0%y',
                            '%b0%d0%Y',
                            '%b0%d0%y']

    year_first_patterns = ['%Y/%m/%d',
                          '%Y-%m-%d',
                          '%y/%m/%d',
                          '%y-%m-%d',
                          '%Y0%B0%d', 
                          '%y0%B0%d',
                          '%Y0%b0%d',
                          '%y0%b0%d']

    if day_first:
        date_patterns = day_first_patterns + month_first_patterns + year_first_patterns
    else:
        date_patterns = month_first_patterns + day_first_patterns + year_first_patterns

    # QIF files sometimes use ' ' instead of a 0 or a ' instead of a /
    date_string = date_string.replace(' ', '0')
    date_string = date_string.replace('\'', '/')

    for pattern in date_patterns:
        try:
            return datetime.strptime(date_string, pattern)
        except ValueError:
            pass

    raise ValueError(f'Date string \'{date_string}\' is not in a recognised format.')


def create_categories(new_category, categories):
    """Add ``new_category`` to ``categories`` after first creating necessary hierarchy.

    If ``new_category`` fits under a category already in ``categories``, then it will just be added as a child.

    Parameters
    ----------
    new_category : Category
        The new category to be added to the iterable of categories.
    categories : iterable
        Iterable containing categories. If in a dict, Category objects are the values.

    Returns
    -------
    iterable : categories
        The new iterable, now containing ``new_category``
    """
    # Add categories in hierarchy
    categories_is_dict = isinstance(categories, dict)
    if new_category.hierarchy is not None:
        current_category = new_category
        hierarchy = new_category.hierarchy.split(':')

        for i in range(2, len(hierarchy) + 1):
            # Check if category exists
            category_to_find = hierarchy[-i]
            found = False
            if categories_is_dict:
                for root_category in categories.values():
                    try:
                        parent = root_category.find_category(category_to_find)
                        found = True
                        break
                    except KeyError:
                        pass
            else:
                for root_category in categories:
                    try:
                        parent = root_category.find_category(category_to_find)
                        found = True
                        break
                    except KeyError:
                        pass

            if found:
                if current_category not in parent.children:
                    parent.add_child(current_category)
                break

            parent = Category(category_to_find)
            parent.hierarchy = ':'.join(hierarchy[:-i + 1])
            parent.add_child(current_category)
            current_category = parent

            # If at the top of the hierarchy, add to categories list
            if i == len(hierarchy):
                if categories_is_dict:
                    categories[current_category.name] = current_category
                else:
                    categories.append(current_category)
    else:
        if categories_is_dict:
            categories[new_category.name] = new_category
        else:
            categories.append(new_category)

    return categories
