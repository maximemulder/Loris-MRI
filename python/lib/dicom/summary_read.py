import csv
import re
import xml.etree.ElementTree as ET
from lib.dicom.summary_type import *
from lib.dicom.text import *
from lib.dicom.text_dict import DictReader
from lib.dicom.text_table import TableReader

def check_tag(element: ET.Element, tag: str):
    if element.tag != tag:
        raise Exception(f'Expected XML element with tag \'{tag}\' but found none.')

    return element

def get_xml_child(element: ET.Element, tag: str):
    print(tag, element)
    child = element.get(tag)
    if child == None:
        raise Exception(f'Expected XML element with tag \'{tag}\' but found none.')

    return element

def read_from_file(filename: str):
    return read_summary_xml(ET.parse(filename).getroot())

def read_from_string(string: str):
    return read_summary_xml(ET.fromstring(string))

def read_summary_xml(study: ET.Element):
    check_tag(study, 'STUDY')
    info   = study[0]
    files  = study[1]
    acquis = study[2]

    check_tag(info, 'STUDY_INFO')
    check_tag(files, 'FILES')
    check_tag(acquis, 'ACQUISITIONS')

    info   = read_info_text(info.text or '')
    files  = read_files_table(files.text or '')
    acquis = read_acquis_table(acquis.text or '')

    return Summary(info, files, acquis)

def read_info_text(text: str):
    return DictReader(text).read(lambda entries: Info(
        read_required(entries['Unique Study ID']),
        read_required(entries['Patient ID']),
        read_required(entries['Patient Name']),
        entries['Patient Sex'],
        entries['Patient date of birth'],
        read_required(entries['Scan Date']),
        read_required(entries['Scanner Model Name']),
        read_required(entries['Scanner Software Version']),
        entries['Institution Name'],
        read_required(entries['Modality']),
    ))

def read_files_table(text: str):
    return TableReader(text).read(lambda row: File(
        read_int(row[0]),
        read_int(row[1]),
        read_int(row[2]),
        row[3],
        read_required(row[4]),
        read_required(row[5]),
    ))

def read_acquis_table(text: str):
    return TableReader(text).read(lambda row: Acquisition(
        int(read_required(row[0])),
        row[1],
        row[2],
        read_float(row[3]),
        read_float(row[4]),
        read_float(row[5]),
        read_float(row[6]),
        row[7],
        read_required(row[8]),
    ))
