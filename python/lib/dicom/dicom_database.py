from datetime import datetime

from lib.db.orm.dicom_archive import DicomArchive
from lib.db.orm.dicom_archive_file import DicomArchiveFile
from lib.db.orm.dicom_archive_series import DicomArchiveSeries
from lib.db.orm.mri_upload import MriUpload
from lib.db.orm.session import Session
from lib.dicom.summary_type import DicomFile, Summary
from lib.dicom.dicom_log import Log
from sqlalchemy import select, delete
from sqlalchemy.orm import Session as Db
import lib.dicom.text
import lib.dicom.summary_write
import lib.dicom.dicom_log


def get_mri_upload(db: Db, id: int):
    """
    Get the MRI upload ORM object associated with a given ID if there is one in
    the database.

    :param db: The database session.
    :param id: The MRI upload ID.

    :returns: The MRI upload ORM object or `None`.
    """

    return db.execute(select(MriUpload)
        .where(MriUpload.id == id)
    ).scalar_one_or_none()


def get_dicom_archive_with_study_uid(db: Db, study_uid: str):
    """
    Get the DICOM archive ORM object associated with a given study UID if there
    is one in the database.

    :param db: The database session.
    :param study_uid: The DICOM archive study UID.

    :returns: The DICOM archive ORM object or `None`.
    """

    return db.execute(select(DicomArchive)
        .where(DicomArchive.study_uid == study_uid)
    ).scalar_one_or_none()

def get_dicom_archives_series_id_with_file(db: Db, file: DicomFile):
    return db.execute(select(DicomArchiveSeries.id)
        .where(DicomArchiveSeries.series_uid == file.series_uid)
        .where(DicomArchiveSeries.series_number == file.series_number)
        .where(DicomArchiveSeries.echo_time == file.echo_time)
        .where(DicomArchiveSeries.sequence_name == file.sequence_name)
    ).scalar_one()


def get_session_id_with_cand_visit(db: Db, cand_id: int, visit_label: str):
    """
    Get the session associated with a candidate ID and a visit label.

    :param db: The database session.
    :param cand_id: The candidate ID.
    :param visit_label:  The visit label.

    :returns: The session ID or `None`.
    """

    return db.execute(select(Session.id)
        .where(Session.cand_id == cand_id)
        .where(Session.visit_label == visit_label)
    ).scalar_one_or_none()


def populate_dicom_archive(dicom_archive: DicomArchive, log: Log, summary: Summary, session_id: int | None):
    """
    Populate a DICOM archive ORM object with information from its archiving log
    and DICOM summary.

    :param dicom_archive: The DICOM archive ORM object to populate.
    :param log: The DICOM arching log object.
    :param summary: The DICOM summary object.
    :param session_id: The optional session ID associated with the DICOM archive.
    """

    dicom_archive.study_uid                = str(summary.info.study_uid)
    dicom_archive.patient_id               = summary.info.patient.id
    dicom_archive.patient_name             = str(summary.info.patient.name)
    dicom_archive.patient_birthdate        = summary.info.patient.birth_date
    dicom_archive.patient_sex              = summary.info.patient.sex
    dicom_archive.neuro_db_center_name     = None
    dicom_archive.center_name              = summary.info.institution or ''
    dicom_archive.last_update              = None
    dicom_archive.date_acquired            = summary.info.scan_date
    dicom_archive.date_last_archived       = datetime.now()
    dicom_archive.acquisition_count        = len(summary.acquis)
    dicom_archive.dicom_file_count         = len(summary.dicom_files)
    dicom_archive.non_dicom_file_count     = len(summary.other_files)
    dicom_archive.md5_sum_dicom_only       = log.tarball_md5_sum
    dicom_archive.md5_sum_archive          = log.archive_md5_sum
    dicom_archive.creating_user            = log.creator_name
    dicom_archive.sum_type_version         = log.summary_version
    dicom_archive.tar_type_version         = log.archive_version
    dicom_archive.source_location          = log.source_path
    dicom_archive.archive_location         = log.target_path
    dicom_archive.scanner_manufacturer     = summary.info.scanner.manufacturer
    dicom_archive.scanner_model            = summary.info.scanner.model
    dicom_archive.scanner_serial_number    = summary.info.scanner.serial_number
    dicom_archive.scanner_software_version = summary.info.scanner.software_version
    dicom_archive.session_id               = session_id
    dicom_archive.upload_attempt           = 0
    dicom_archive.create_info              = lib.dicom.dicom_log.write_to_string(log)
    dicom_archive.acquisition_metadata     = lib.dicom.summary_write.write_to_string(summary)
    dicom_archive.date_sent                = None
    dicom_archive.pending_transfer         = 0


def insert_files_series(db: Db, dicom_archive: DicomArchive, summary: Summary):
    for acqui in summary.acquis:
        db.add(DicomArchiveSeries(
            archive_id         = dicom_archive.id,
            series_number      = acqui.series_number,
            series_description = acqui.series_description,
            sequence_name      = acqui.sequence_name,
            echo_time          = acqui.echo_time,
            repetition_time    = acqui.repetition_time,
            inversion_time     = acqui.inversion_time,
            slice_thickness    = acqui.slice_thickness,
            phase_encoding     = acqui.phase_encoding,
            number_of_files    = acqui.number_of_files,
            series_uid         = acqui.series_uid,
            modality           = acqui.modality,
        ))

    for file in summary.dicom_files:
        series_id = get_dicom_archives_series_id_with_file(db, file)
        db.add(DicomArchiveFile(
            archive_id         = dicom_archive.id,
            series_number      = file.series_number,
            file_number        = file.file_number,
            echo_number        = file.echo_number,
            series_description = file.series_description,
            md5_sum            = file.md5_sum,
            file_name          = file.file_name,
            series_id          = series_id,
        ))


def insert(db: Db, log: Log, summary: Summary, session_id: int | None):
    """
    Insert a DICOM archive into the database.

    :param db: The database session.
    :param log: The archiving log of the DICOM archive.
    :param summary: The summary of the DICOM archive.
    :param session_id: The optional session ID of the DICOM archive.

    :returns: The newly created and inserted DICOM archive ORM object.
    """
    dicom_archive = DicomArchive()
    populate_dicom_archive(dicom_archive, log, summary, session_id)
    dicom_archive.date_first_archived = datetime.now()
    db.add(dicom_archive)
    db.flush() # Needed to populate the auto-increment ID of the archive.
    insert_files_series(db, dicom_archive, summary)
    return dicom_archive


def update(db: Db, dicom_archive: DicomArchive, log: Log, summary: Summary, session_id: int | None):
    """
    Insert a DICOM archive into the database.

    :param db: The database session.
    :param dicom_archive: The DICOM archive ORM object to update.
    :param log: The archiving log of the DICOM archive.
    :param summary: The summary of the DICOM archive.
    :param session_id: The optional session ID of the DICOM archive.
    """

    # Delete the associated database DICOM files and series.
    db.execute(delete(DicomArchiveFile).where(DicomArchiveFile.archive_id == dicom_archive.id))
    db.execute(delete(DicomArchiveSeries).where(DicomArchiveSeries.archive_id == dicom_archive.id))

    # Update the database record with the new DICOM information.
    populate_dicom_archive(dicom_archive, log, summary, session_id)

    # Insert the new DICOM files and series.
    insert_files_series(db, dicom_archive, summary)


def upload(dicom_archive: DicomArchive, mri_upload: MriUpload):
    """
    Associate a DICOM archvie to a MRI upload.

    :param dicom_archive: The DICOM archive ORM object.
    :param mri_upload: The MRI upload ORM object.
    """
    mri_upload.dicom_archive_id = dicom_archive.id
