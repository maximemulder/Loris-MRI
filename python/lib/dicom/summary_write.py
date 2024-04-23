from functools import reduce
import re
import xml.etree.ElementTree as ET
from lib.dicom.summary_type import *
from lib.dicom.text_dict import DictWriter
from lib.dicom.text_table import TableWriter

def write_to_file(filename: str, summary: Summary):
    string = write_to_string(summary)
    with open(filename, 'w') as file:
        file.write(string)

def write_to_string(summary: Summary) -> str:
    return ET.tostring(write_xml(summary), encoding='unicode') + '\n'

def write_xml(summary: Summary):
    study = ET.Element('STUDY')
    ET.SubElement(study, 'STUDY_INFO').text   = write_info(summary.info)
    ET.SubElement(study, 'FILES').text        = write_files_table(summary.dicom_files)
    ET.SubElement(study, 'ACQUISITIONS').text = write_acquis_table(summary.acquis)
    ET.SubElement(study, 'SUMMARY').text      = write_ending(summary)
    ET.indent(study, space='')
    return study

def write_info(info: Info):
    return '\n' + DictWriter([
        ('Unique Study ID'          , info.study_uid),
        ('Patient Name'             , info.patient.name),
        ('Patient ID'               , info.patient.id),
        ('Patient date of birth'    , info.patient.birthdate),
        ('Patient Sex'              , info.patient.sex),
        ('Scan Date'                , info.scan_date),
        ('Scanner Manufacturer'     , info.scanner.manufacturer),
        ('Scanner Model Name'       , info.scanner.model),
        ('Scanner Serial Number'    , info.scanner.serial_number),
        ('Scanner Software Version' , info.scanner.software_version),
        ('Institution Name'         , info.institution),
        ('Modality'                 , info.modality),
    ]).write()

def write_files_table(files: list[File]):
    writer = TableWriter()
    writer.append_row(['SN', 'FN', 'EN', 'Series', 'md5sum', 'File name'])
    for file in files:
        writer.append_row([
            file.series_number,
            file.file_number,
            file.echo_number,
            file.series_description,
            file.md5_sum,
            file.file_name,
        ])

    return '\n' + writer.write()

def write_acquis_table(acquis: list[Acquisition]):
    writer = TableWriter()
    writer.append_row(['Series (SN)', 'Name of series', 'Seq Name', 'echoT ms', 'repT ms', 'invT ms', 'sth mm', 'PhEnc', 'NoF', 'Series UID', 'Mod'])
    for acqui in acquis:
        writer.append_row([
            acqui.series_number,
            acqui.series_description,
            acqui.sequence_name,
            acqui.echo_time,
            acqui.repetition_time,
            acqui.inversion_time,
            acqui.slice_thickness,
            acqui.phase_encoding,
            acqui.number_of_files,
            acqui.series_uid,
            acqui.modality,
        ])

    return '\n' + writer.write()

def write_ending(summary: Summary):
    if summary.info.patient.birthdate != None:
        birth_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', summary.info.patient.birthdate)
        scan_match  = re.match(r'(\d{4})-(\d{2})-(\d{2})', summary.info.scan_date)

        if birth_match == None or scan_match == None:
            raise Exception(f'Birth date or scan date does not match date syntax. {summary.info.patient.birthdate} {summary.info.scan_date}')

        years  = int(scan_match.group(1)) - int(birth_match.group(1))
        months = int(scan_match.group(2)) - int(birth_match.group(2))
        days   = int(scan_match.group(3)) - int(birth_match.group(3))
        total  = round(years + months / 12 + days / 365.0, 2)
        age = f'{total} or {years} years, {months} months {days} days'
    else:
        age = ''

    return '\n' + DictWriter([
        ('Total number of files', len(summary.dicom_files) + len(summary.other_files)),
        ('Age at scan', age),
    ]).write()
