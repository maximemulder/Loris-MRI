import csv
from typing import Callable, TypeVar
from lib.dicom.text import *

def read_row(row: list[str]) -> list[str | None]:
    return list(map(lambda cell: read_string(cell.strip()), row))

class TableWriter:
    rows: list[list[str]]

    def __init__(self):
        self.rows = []

    def get_cells_lengths(self):
        lengths = [0] * len(self.rows[0])
        for row in self.rows:
            for i in range(len(row)):
                if len(row[i]) > lengths[i]:
                    lengths[i] = len(row[i])

        return lengths

    def append_row(self, cells: list[str | int | float | None]):
        self.rows.append(list(map(write_value, cells)))

    def write(self):
        if not self.rows:
            return '\n'

        lengths = self.get_cells_lengths()

        rows = map(lambda row: list(map(lambda cell, length: cell.ljust(length), row, lengths)), self.rows)
        rows = map(lambda row: ' | '.join(row).rstrip() + '\n', rows)

        return ''.join(rows)

class TableReader:
    def __init__(self, text: str):
        self.reader = csv.reader(text.strip().splitlines(), delimiter='|')

    T = TypeVar('T')
    def read(self, mapper: Callable[[list[str | None]], T]) -> list[T]:
        # Skip table header
        next(self.reader)
        return list(map(lambda row: mapper(read_row(row)), self.reader))
