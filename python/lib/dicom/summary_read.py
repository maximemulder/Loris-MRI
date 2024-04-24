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

def read_from_file(file_path: str):
    """
    Create a DICOM summary object from a text file.
    """
    return read_summary_xml(ET.parse(file_path).getroot())

def read_from_string(string: str):
    """
    Create a DICOM summary object from a string.
    """
    return read_summary_xml(ET.fromstring(string))

def read_summary_xml(study: ET.Element):
    check_tag(study, 'STUDY')

    info        = study[0]
    dicom_files = study[1]
    other_files = study[2]
    acquis      = study[3]

    check_tag(info,        'STUDY_INFO')
    check_tag(dicom_files, 'FILES')
    check_tag(other_files, 'OTHERS')
    check_tag(acquis,      'ACQUISITIONS')

    info        = read_info_text(info.text or '')
    dicom_files = read_dicom_files_table(dicom_files.text or '')
    other_files = read_other_files_table(other_files.text or '')
    acquis      = read_acquis_table(acquis.text or '')

    return Summary(info, acquis, dicom_files, other_files)

def read_patient_entries(entries: dict[str, str]):
    return Patient(
        entries['Patient ID'],
        entries['Patient Name'],
        read_none(entries['Patient Sex']),
        read_date_none(read_none(entries['Patient date of birth'])),
    )

def read_scanner_entries(entries: dict[str, str]):
    return Scanner(
        entries['Scanner Manufacturer'],
        entries['Scanner Model Name'],
        entries['Scanner Serial Number'],
        entries['Scanner Software Version'],
    )

def read_info_text(text: str):
    entries = DictReader(text).read()
    return Info(
        entries['Unique Study ID'],
        read_patient_entries(entries),
        read_scanner_entries(entries),
        read_date_none(entries['Scan Date']),
        read_none(entries['Institution Name']),
        entries['Modality'],
    )

def read_dicom_files_table(text: str):
    return TableReader(text).read(lambda row: DicomFile(
        row[5],
        row[4],
        read_int_none(read_none(row[0])),
        None,
        read_none(row[3]),
        read_int_none(read_none(row[1])),
        read_int_none(read_none(row[2])),
        None,
    ))

def read_other_files_table(text: str):
    return TableReader(text).read(lambda row: OtherFile(
        row[1],
        row[0],
    ))

def read_acquis_table(text: str):
    return TableReader(text).read(lambda row: Acquisition(
        int(row[0]),
        read_none(row[9]),
        read_none(row[1]),
        read_none(row[2]),
        read_float_none(read_none(row[3])),
        read_float_none(read_none(row[4])),
        read_float_none(read_none(row[5])),
        read_float_none(read_none(row[6])),
        read_none(row[7]),
        int(row[8]),
        read_none(row[10]),
    ))
