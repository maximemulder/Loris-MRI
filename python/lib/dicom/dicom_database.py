from datetime import date, datetime
from typing import Any

from lib.database import Database
from lib.dicom.summary import Summary, write_to_string as write_summary
from lib.dicom.dicom_log import Log, write_to_string as write_log
from lib.dicom.text import *

def insert_dict(db: Database, table: str, entries: dict[str, Any]):
    return db.insert(table, list(entries.keys()), [tuple(entries.values())], get_last_id=True)

def update_dict(db: Database, table: str, entries: dict[str, Any], conds: dict[str, Any]):
    query_values = map(lambda key: f'{key} = %s', entries.keys())
    query_conds  = map(lambda key: f'{key} = %s', conds.keys())

    query = f'UPDATE {table} SET {", ".join(query_values)} WHERE {" AND ".join(query_conds)}'

    db.update(query, [*entries.values(), *conds.values()])

def get_archive_with_study_uid(db: Database, study_uid: str):
    results = db.pselect(
        'SELECT TarchiveID, CreateInfo \
            FROM tarchive \
            WHERE DicomArchiveID = %s',
        [study_uid])

    if len(results) == 0:
        return None

    return results[0]['TarchiveID'], results[0]['CreateInfo']

def get_dicom_dict(log: Log, summary: Summary):
    return {
        'DicomArchiveID': summary.info.study_uid,
        'PatientID': summary.info.patient.id,
        'PatientName': summary.info.patient.name,
        'PatientDoB': write_date_none(summary.info.patient.birthdate),
        'PatientSex': summary.info.patient.sex,
        'neurodbCenterName': None,
        'CenterName': summary.info.institution or '',
        'LastUpdate': None,
        'DateAcquired': write_date_none(summary.info.scan_date),
        'DateFirstArchived': write_datetime(datetime.now()),
        'DateLastArchived': write_datetime(datetime.now()),
        'AcquisitionCount': len(summary.acquis),
        'NonDicomFileCount': len(summary.other_files),
        'DicomFileCount': len(summary.dicom_files),
        'md5sumDicomOnly': log.tarball_md5_sum,
        'md5sumArchive': log.archive_md5_sum,
        'CreatingUser': log.creator_name,
        'sumTypeVersion': log.summary_version,
        'tarTypeVersion': log.archive_version,
        'SourceLocation': log.source_path,
        'ArchiveLocation': log.target_path,
        'ScannerManufacturer': summary.info.scanner.manufacturer,
        'ScannerModel': summary.info.scanner.model,
        'ScannerSerialNumber': summary.info.scanner.serial_number,
        'ScannerSoftwareVersion': summary.info.scanner.software_version,
        'SessionID': None,
        'uploadAttempt': 0,
        'CreateInfo': write_log(log),
        'AcquisitionMetadata': write_summary(summary),
        'DateSent': None,
        'PendingTransfer': 0,
    }

def insert(db: Database, log: Log, summary: Summary):
    dicom_dict = get_dicom_dict(log, summary)

    archive_id = insert_dict(db, 'tarchive', dicom_dict)

    for acqui in summary.acquis:
        insert_dict(db, 'tarchive_series', {
            'TarchiveID': archive_id,
            'SeriesNumber': acqui.series_number,
            'SeriesDescription': acqui.series_description,
            'SequenceName': acqui.sequence_name,
            'EchoTime': acqui.echo_time,
            'RepetitionTime': acqui.repetition_time,
            'InversionTime': acqui.inversion_time,
            'SliceThickness': acqui.slice_thickness,
            'PhaseEncoding': acqui.phase_encoding,
            'NumberOfFiles': acqui.number_of_files,
            'SeriesUID': acqui.series_uid,
            'Modality': acqui.modality,
        })

    for file in summary.dicom_files:
        results = db.pselect(
            'SELECT TarchiveSeriesID \
                FROM tarchive_series \
                WHERE SeriesUID = %s AND EchoTime = %s',
            [file.series_uid, file.echo_time])

        series_id = results[0]['TarchiveSeriesID']

        insert_dict(db, 'tarchive_files', {
            'TarchiveID': archive_id,
            'SeriesNumber': file.series_number,
            'FileNumber': file.file_number,
            'EchoNumber': file.echo_number,
            'SeriesDescription': file.series_description,
            'Md5Sum': file.md5_sum,
            'FileName': file.file_name,
            'TarchiveSeriesID': series_id,
        })

def update(db: Database, archive_id: int, log: Log, summary: Summary):
    db.update('DELETE FROM tarchive_files WHERE TarchiveID = %s', [archive_id])
    db.update('DELETE FROM tarchive_series WHERE TarchiveID = %s', [archive_id])

    dicom_dict = get_dicom_dict(log, summary)

    update_dict(db, 'tarchive', dicom_dict, {
        'TarchiveID': archive_id,
    })
