from datetime import date, datetime
from typing import Any

from lib.database import Database
from lib.dicom.summary import Summary, write_to_string as write_summary
from lib.dicom.log import Log, write_to_string as write_log
from lib.dicom.text import *

def insert(db: Database, table: str, entries: dict[str, Any]):
    return db.insert(table, list(entries.keys()), [tuple(entries.values())], get_last_id=True)

def create_tarchive(
    db: Database,
    log: Log,
    summary: Summary,
    neuro_db_center_name: str | None,
):
    archive_id = insert(db, 'tarchive', {
        'DicomArchiveID': summary.info.study_uid,
        'PatientID': summary.info.patient.id,
        'PatientName': summary.info.patient.name,
        'PatientDoB': write_date_none(summary.info.patient.birthdate),
        'PatientSex': summary.info.patient.sex,
        'neurodbCenterName': neuro_db_center_name,
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
    })

    for acqui in summary.acquis:
        insert(db, 'tarchive_series', {
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
        insert(db, 'tarchive_files', {
            'TarchiveID': archive_id,
            'SeriesNumber': file.series_number,
            'FileNumber': file.file_number,
            'EchoNumber': file.echo_number,
            'SeriesDescription': file.series_description,
            'Md5Sum': file.md5_sum,
            'FileName': file.file_name,
            'TarchiveSeriesID': None, # TODO
        })
