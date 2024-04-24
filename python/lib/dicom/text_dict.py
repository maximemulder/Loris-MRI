import io
import re
from lib.dicom.text import *

class DictWriter:
    """
    Writer for a text dictionary, i.e, a text of the form:

    Key 1 : Value 1
    Key 2 : Value 2
    ...
    """

    def __init__(self, entries: list[tuple[str, str | int | float | None]]):
        self.entries = entries

    def get_keys_length(self):
        """
        Get the maximal length of the keys, used for padding
        """
        length = 0
        for entry in self.entries:
            key = entry[0]
            if len(key) > length:
                length = len(key)

        return length

    def write(self):
        """
        Serialize the text dictionary into a string
        """

        if not self.entries:
            return '\n'

        length = self.get_keys_length()

        entries = map(lambda entry:
            f'* {entry[0].ljust(length)} :   {write_value(entry[1])}\n', self.entries
        )

        return ''.join(entries)

class DictReader:
    """
    Reader for a text dictionary, i.e, a text of the form:

    Key 1 : Value 1
    Key 2 : Value 2
    ...
    """

    def __init__(self, text: str):
        self.reader = io.StringIO(text.strip())

    def read(self):
        """
        Parse the text dictionary, returning a dictionary containing each keys
        and values.
        """

        entries: dict[str, str] = {}
        for line in self.reader.readlines():
            groups = re.match(r'\* (\w(?: *\w+)*) *: *(.*)', line)
            if not groups:
                raise Exception(f'Cannot parse the text following dictionnary line:\n{line}')

            entries[groups.group(1)] = groups.group(2).strip()

        return entries
