import csv
from typing import Callable, TypeVar
from lib.dicom.text import *


class TableWriter:
    """
    Writer for a text table, i.e, a table of the form:

    Field 1 | Field 2 | Field 3
    Value 1 | Value 2 | Value 3
    Value 4 | Value 5 | Value 6
    ...
    """

    rows: list[list[str]]

    def __init__(self):
        self.rows = []

    def get_cells_lengths(self):
        """
        Get the longest value length of each column, used for padding
        """

        lengths = [0] * len(self.rows[0])
        for row in self.rows:
            for i in range(len(row)):
                if len(row[i]) > lengths[i]:
                    lengths[i] = len(row[i])

        return lengths

    def append_row(self, cells: list[str | int | float | None]):
        """
        Add a row to the table, which can be either the header or some values.
        """

        self.rows.append(list(map(write_value, cells)))

    def write(self):
        """
        Serialize the text table into a string.
        """

        if not self.rows:
            return '\n'

        lengths = self.get_cells_lengths()

        rows = map(lambda row: list(map(lambda cell, length: cell.ljust(length), row, lengths)), self.rows)
        rows = map(lambda row: ' | '.join(row).rstrip() + '\n', rows)

        return ''.join(rows)

def read_row(row: list[str]) -> list[str]:
    return list(map(lambda cell: cell.strip(), row))

class TableReader:
    """
    Reader for a text table, i.e, a table of the form:

    Field 1 | Field 2 | Field 3
    Value 1 | Value 2 | Value 3
    Value 4 | Value 5 | Value 6
    ...
    """

    def __init__(self, text: str):
        self.reader = csv.reader(text.strip().splitlines(), delimiter='|')

    T = TypeVar('T')
    def read(self, mapper: Callable[[list[str]], T]) -> list[T]:
        """
        Parse a text table, returning a list containing each row transformed
        by the mapper function.
        """

        # Skip table header
        next(self.reader)
        return list(map(lambda row: mapper(read_row(row)), self.reader))
