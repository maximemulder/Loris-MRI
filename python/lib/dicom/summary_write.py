from functools import reduce
import re
import xml.etree.ElementTree as ET
from lib.dicom.summary_type import *

def write_value(value: str | int | float):
    return str(value)

def write_value_null(value: str | int | float | None):
    if value == None:
        return ''

    return str(value)

def write_to_file(filename: str, summary: Summary):
    string = write_to_string(summary)
    with open(filename, 'w') as file:
        file.write(string)

def write_to_string(summary: Summary) -> str:
    return ET.tostring(write_xml(summary), encoding='unicode') + '\n'

def write_xml(summary: Summary):
    study = ET.Element('STUDY')
    ET.SubElement(study, 'STUDY_INFO').text   = write_info(summary.info)
    ET.SubElement(study, 'FILES').text        = write_files_table(summary.files)
    ET.SubElement(study, 'ACQUISITIONS').text = write_acquis_table(summary.acquisitions)
    ET.SubElement(study, 'SUMMARY').text      = write_ending(summary)
    ET.indent(study, space='')
    return study

def write_info(info: Info):
    return f"""
* Unique Study ID          :    {write_value(info.study_uid)}
* Patient Name             :    {write_value(info.patient_name)}
* Patient ID               :    {write_value(info.patient_id)}
* Patient date of birth    :    {write_value_null(info.patient_birthdate)}
* Scan Date                :    {write_value(info.scan_date)}
* Patient Sex              :    {write_value_null(info.patient_sex)}
* Scanner Model Name       :    {write_value(info.scanner_model)}
* Scanner Software Version :    {write_value(info.scanner_software)}
* Institution Name         :    {write_value_null(info.institution)}
* Modality                 :    {write_value(info.modality)}
"""

class TableWriter:
    rows: list[list[str]]

    def __init__(self):
        self.rows = []

    def append_row(self, cells: list[str]):
        self.rows.append(cells)

    def get_lengths(self):
        lengths = [0] * len(self.rows[0])
        return reduce(lambda lengths, row: list(map(lambda length, cell: max(length, len(cell)), lengths, row)), self.rows, lengths)

    def to_string(self):
        if len(self.rows) == 0:
            return ''

        lengths = self.get_lengths()

        rows = map(lambda row: list(map(lambda cell, length: cell.ljust(length), row, lengths)), self.rows)
        rows = map(lambda row: ' | '.join(row).rstrip() + '\n', rows)

        return ''.join(rows)

def write_files_table(files: list[File]):
    writer = TableWriter()
    writer.append_row(['SN', 'FN', 'EN', 'Series', 'md5sum', 'File name'])
    for file in files:
        writer.append_row([
            write_value_null(file.series_number),
            write_value_null(file.file_number),
            write_value_null(file.echo_number),
            write_value_null(file.series_description),
            write_value(file.md5_sum),
            write_value(file.file_name),
        ])

    return '\n' + writer.to_string()

def write_acquis_table(acquis: list[Acquisition]):
    writer = TableWriter()
    writer.append_row(['Series (SN)', 'Name of series', 'Seq Name', 'echoT ms', 'repT ms', 'invT ms', 'sth mm', 'PhEnc', 'NoF'])
    for acquisition in acquis:
        writer.append_row([
            write_value(acquisition.series_number),
            write_value_null(acquisition.series_description),
            write_value_null(acquisition.sequence_name),
            write_value_null(acquisition.echo_time),
            write_value_null(acquisition.repetition_time),
            write_value_null(acquisition.inversion_time),
            write_value_null(acquisition.slice_thickness),
            write_value_null(acquisition.phase_encoding),
            write_value(acquisition.files_count),
        ])

    return '\n' + writer.to_string()

def write_ending(summary: Summary):
    if summary.info.patient_birthdate != None:
        birth_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', summary.info.patient_birthdate)
        scan_match  = re.match(r'(\d{4})-(\d{2})-(\d{2})', summary.info.scan_date)

        if birth_match == None or scan_match == None:
            raise Exception()

        years  = int(scan_match.group(1)) - int(birth_match.group(1))
        months = int(scan_match.group(2)) - int(birth_match.group(2))
        days   = int(scan_match.group(3)) - int(birth_match.group(3))
        total  = round(years + months / 12 + days / 365.0, 2)
        age = f'{total} or {years} years, {months} months {days} days'
    else:
        age = ''

    return f"""
Total number of files   :   {len(summary.files)}
Age at scan             :   {age}
"""
