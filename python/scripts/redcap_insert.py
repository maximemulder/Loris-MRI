#!/usr/bin/env python

import glob
import re

instruments: list[str] = []

for path in glob.glob('/var/www/loris/tools/tmp/*.linst'):
    with open(path) as file:
        text = file.read()
        match_name = re.search(r'table\{@\}(.+)\n', text)
        match_title = re.search(r'title\{@\}(.+)\n', text)
        if match_name is None or match_title is None:
            print(f'Format error for file {path}')
            continue

        name = match_name[1].replace('\'', '\'\'')
        title = match_title[1].replace('\'', '\'\'')

        instruments.append(f"  ('{name}', '{title}', 1)")

query \
    = "INSERT INTO `test_names` (`Test_name`, `Full_name`, `Sub_group`) VALUES\n" \
    + ',\n'.join(instruments) \
    + ';'

print(query)
