import csv
import re
from typing import Any
import xml.etree.ElementTree as ET
from lib.dicom.summary_type import *

def read_value(text: str):
    return text.strip() or None

def read_value_int(text: str):
    value = read_value(text)
    if value == None:
        return None

    return int(value)

def read_value_float(text: str):
    value = read_value(text)
    if value == None:
        return None

    return float(value)

def read_value_required(text: str):
    value = read_value(text)
    if value == None:
        raise Exception(f'Excpected value string but found empty string.')

    return value

def get_xml_child(element: ET.Element, tag: str):
    child = element.get(tag)
    if child == None:
        raise Exception(f'Expected XML element with tag \'{tag}\' but found none.')

    return element

def read_from_file(filename: str):
    return read_summary_xml(ET.parse(filename).getroot())

def read_from_string(string: str):
    return read_summary_xml(ET.fromstring(string))

def read_summary_xml(element: ET.Element):
    study  = get_xml_child(element, 'STUDY')
    info   = get_xml_child(study, 'STUDY_INFO')
    files  = get_xml_child(study, 'FILES')
    acquis = get_xml_child(study, 'ACQUISITIONS')

    info   = read_info_text(info.text or '')
    files  = read_files_table(files.text or '')
    acquis = read_acquis_table(acquis.text or '')

    return Summary( info, files, acquis)

info_regex = r"""
\* Unique Study ID          :    (.+)
\* Patient Name             :    (.+)
\* Patient ID               :    (.+)
\* Patient date of birth    :    (.+)
\* Scan Date                :    (.+)
\* Patient Sex              :    (.+)
\* Scanner Model Name       :    (.+)
\* Scanner Software Version :    (.+)
\* Institution Name         :    (.+)
\* Modality                 :    (.+)
"""

def read_info_text(text: str):
    matches = re.match(info_regex, text)
    if matches == None:
        raise Exception(f'Could not parse the summary general information.')

    return Info(
        matches.group(1),
        matches.group(2),
        matches.group(3),
        matches.group(4),
        matches.group(5),
        matches.group(6),
        matches.group(7),
        matches.group(8),
        matches.group(9),
        matches.group(10),
    )

def read_files_table(text: str):
    reader = csv.reader(text.strip().splitlines(), delimiter='|')
    next(reader)
    return list(map(lambda row: File(
        read_value_int(row[0]),
        read_value_int(row[1]),
        read_value_int(row[2]),
        read_value(row[3]),
        read_value_required(row[4]),
        read_value_required(row[5]),
    ), reader))

def read_acquis_table(text: str):
    reader = csv.reader(text.strip().splitlines(), delimiter='|')
    next(reader)
    return list(map(lambda row: Acquisition(
        int(read_value_required(row[0])),
        read_value(row[1]),
        read_value(row[2]),
        read_value_float(row[3]),
        read_value_float(row[4]),
        read_value_float(row[5]),
        read_value_float(row[6]),
        read_value(row[7]),
        int(read_value_required(row[8])),
    ), reader))
