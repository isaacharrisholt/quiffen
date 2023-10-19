import sys
import traceback
from collections import Counter
from typing import List


class ParserState:
    """
    keep track of exceptions and other parser state and configuration details

    Parameters
    ----------
        lenient: bool, default=False
            collect errors instead of throwing exceptions

        day_first : bool, default=False
            Whether the day comes before the month in the date.

        debug: bool, default=False
            give debugging information e.g when showing errors include traceback

        line_number: int, default=1
            the initial line number to start with

        num_errors_to_show: int, default=10
            the number of errors to show in lenient mode

    """

    def __init__(
        self,
        lenient: bool = False,
        day_first: bool = False,
        debug: bool = False,
        line_number: int = 1,
        ignore_line_codes: List[str] = [],
        num_errors_to_show: int = 10,
    ):
        """constructor"""
        self.lenient = lenient
        self.debug = debug
        self.errors = []
        self.day_first = (day_first,)
        self.ignore_line_codes = (ignore_line_codes,)
        self.line_number = (line_number,)
        self.num_errors_to_show = num_errors_to_show

    def handle_exception(self, ex):
        if self.lenient:
            self.errors.append(ex)
        else:
            raise ex

    def show_most_common_errors(
        self, num_errors=10
    ):  # Default is 1, showing the most common error
        # Count error types
        error_types = [type(error).__name__ for error in self.errors]
        error_type_counts = Counter(error_types)

        # Display the most common error types
        most_common_errors = error_type_counts.most_common(num_errors)
        for error_type, count in most_common_errors:
            print(f"Error '{error_type}':{count} x.")

    def show(self):
        error_count = len(self.errors)
        if error_count > 0:
            if self.debug:
                for index, error in enumerate(self.errors):
                    print(f"error {index+1:4}:{str(error)}")
                    if index < self.num_errors_to_show:
                        # Print the stack trace of the exception using traceback
                        traceback.print_tb(error.__traceback__)
            self.show_most_common_errors(num_errors=self.num_errors_to_show)
            print(
                f"ignored {error_count} parsing errors while in lenient mode",
                file=sys.stderr,
            )
