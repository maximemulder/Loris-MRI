import lib.db.DicomArchiveFile as DicomArchiveFile
import lib.db.DicomArchiveSeries as DicomArchiveSeries
import lib.db.MriUpload as MriUpload
from datetime import date
from lib.db.Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


class DicomArchive(Base):
    __tablename__ = 'tarchive'

    id                : Mapped[int]            = mapped_column('TarchiveID', primary_key=True)
    series            : Mapped[List['DicomArchiveSeries.DicomArchiveSeries']] = relationship('DicomArchiveSeries', back_populates='archive')
    files             : Mapped[List['DicomArchiveFile.DicomArchiveFile']] = relationship('DicomArchiveFile', back_populates='archive')
    upload            : Mapped[Optional['MriUpload.MriUpload']] = relationship('MriUpload', back_populates='dicom_archive')
    patient_id        : Mapped[str]            = mapped_column('PatientID')
    patient_name      : Mapped[str]            = mapped_column('PatientName')
    patient_birthdate : Mapped[Optional[date]] = mapped_column('PatientDoB')
    patient_sex       : Mapped[Optional[str]]  = mapped_column('PatientSex')
    source_location   : Mapped[str]            = mapped_column('SourceLocation')
    archive_location  : Mapped[Optional[str]]  = mapped_column('ArchiveLocation')
