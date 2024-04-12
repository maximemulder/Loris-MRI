from functools import cmp_to_key
import hashlib
import os
import pydicom
from lib.dicom.summary_type import *

class MissingAttributeException(Exception):
    def __init__(self, tag: str):
        self.tag = tag

def get_value(dicom: pydicom.Dataset, tag: str):
    if tag not in dicom:
        raise MissingAttributeException(tag)

    return dicom[tag].value

def get_value_null(dicom: pydicom.Dataset, tag: str):
    if tag not in dicom:
        return

    return dicom[tag].value

def format_date(date: str):
    return "-".join([date[:4], date[4:6], date[6:]])

def cmp_int_null(a: int | None, b: int | None):
    match a, b:
        case None, None:
            return 0
        case _, None:
            return -1
        case None, _:
            return 1
        case a, b:
            return a - b

def cmp_files(a: File, b: File):
    """
    Compare the order of two files to sort them in the summary.
    """
    return \
        cmp_int_null(a.series_number, b.series_number) or \
        cmp_int_null(a.file_number, b.file_number) or \
        cmp_int_null(a.echo_number, b.echo_number)

def cmp_acquis(a: Acquisition, b: Acquisition):
    """
    Compare the order of two acquisitions to sort them in the summary.
    """
    return a.series_number - b.series_number

def make_summary(dir_path: str):
    info = None
    files: list[File] = []
    acquis_dict: dict[tuple[int, int | None, str | None], Acquisition] = dict()

    for file_name in os.listdir(dir_path):
        dicom = pydicom.dcmread(dir_path + '/' + file_name)
        '''import pprint
        pprint.pprint(dicom)
        exit(0)'''
        if info == None:
            info = make_info(dicom)

        files.append(make_file(dicom))

        series   = dicom.SeriesNumber
        echo     = get_value_null(dicom, 'EchoNumbers')
        sequence = get_value_null(dicom, 'SequenceName')

        if not (series, sequence, echo) in acquis_dict:
            acquis_dict[(series, sequence, echo)] = make_acqui(dicom)

    if info == None:
        raise Exception('Found no DICOM file in the directory.')

    acquis = list(acquis_dict.values())

    files  = sorted(files,  key=cmp_to_key(cmp_files))
    acquis = sorted(acquis, key=cmp_to_key(cmp_acquis))

    return Summary(info, files, acquis)

def make_info(dicom: pydicom.Dataset):
    return Info(
        get_value(dicom, 'StudyInstanceUID'),
        get_value(dicom, 'PatientID'),
        get_value(dicom, 'PatientName'),
        get_value(dicom, 'PatientSex'),
        format_date(get_value(dicom, 'PatientBirthDate')),
        format_date(get_value(dicom, 'StudyDate')),
        get_value(dicom, 'ManufacturerModelName'),
        get_value(dicom, 'SoftwareVersions'),
        get_value_null(dicom, 'InstitutionName'),
        get_value(dicom, 'Modality'),
    )

def make_file(dicom: pydicom.Dataset):
    with open(dicom.filename, 'rb') as file:
        md5_sum = hashlib.md5(file.read()).hexdigest()

    return File(
        get_value_null(dicom, 'SeriesNumber'),
        get_value_null(dicom, 'InstanceNumber'),
        get_value_null(dicom, 'EchoNumbers'),
        get_value_null(dicom, 'SeriesDescription'),
        md5_sum,
        os.path.basename(dicom.filename),
    )

def make_acqui(dicom: pydicom.Dataset):
    return Acquisition(
        get_value(dicom, 'SeriesNumber'),
        get_value_null(dicom, 'SeriesDescription'),
        get_value_null(dicom, 'SequenceName'),
        get_value_null(dicom, 'EchoTime'),
        get_value_null(dicom, 'InversionTime'),
        get_value_null(dicom, 'RepetitionTime'),
        get_value_null(dicom, 'SliceThickness'),
        get_value_null(dicom, 'InPlanePhaseEncodingDirection'),
        get_value(dicom, 'Modality'),
    )
