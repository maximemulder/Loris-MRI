import io
import re
from typing import Callable, TypeVar
from lib.dicom.text import *

class DictWriter:
    def __init__(self, entries: list[tuple[str, str | int | float | None]]):
        self.entries = entries

    def get_keys_length(self):
        length = 0
        for entry in self.entries:
            key = entry[0]
            if len(key) > length:
                length = len(key)

        return length

    def write(self):
        if not self.entries:
            return '\n'

        length = self.get_keys_length()

        entries = map(lambda entry: f'* {entry[0].ljust(length)} :   {write_value(entry[1])}\n', self.entries)
        return ''.join(entries)

class DictReader:
    def __init__(self, text: str):
        self.reader = io.StringIO(text.strip())

    T = TypeVar('T')
    def read(self, mapper: Callable[[dict[str, str | None]], T]) -> T:
        entries = {}
        for line in self.reader.readlines():
            groups = re.match(r'\* (\w(?: *\w+)*) *: *(.*)', line)
            if not groups:
                raise Exception(f'Cannot parse text dictionnary.')
            entries[groups.group(1)] = read_string(groups.group(2))

        return mapper(entries)
