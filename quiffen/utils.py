from datetime import datetime

from quiffen.core.categories_classes import Category


def parse_date(date_string, day_first=True):
    """Parse a string date of an unknown format and return a datetime object."""
    day_first_patterns = ['%d/%m/%Y',
                          '%d-%m-%Y',
                          '%d/%m/%y',
                          '%d-%m-%y',
                          '%d %B %Y',
                          '%d %B %y',
                          '%d %b %Y',
                          '%d %b %y']

    month_first_patterns = ['%m/%d/%Y',
                            '%m-%d-%Y',
                            '%m/%d/%y',
                            '%m-%d-%y',
                            '%B %d %Y',
                            '%B %d %y',
                            '%b %d %Y',
                            '%b %d %y']

    if day_first:
        date_patterns = day_first_patterns + month_first_patterns
    else:
        date_patterns = month_first_patterns + day_first_patterns

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
