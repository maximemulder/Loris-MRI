import lib.db.DicomArchive as DicomArchive
import lib.db.DicomArchiveSeries as DicomArchiveSeries
from lib.db.Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional


class DicomArchiveFile(Base):
    __tablename__ = 'tarchive_files'

    id                 : Mapped[int]           = mapped_column('TarchiveFileID', primary_key=True)
    archive_id         : Mapped[int]           = mapped_column('TarchiveID', ForeignKey('tarchive.TarchiveID'))
    archive            : Mapped['DicomArchive.DicomArchive'] = relationship('DicomArchive', back_populates='files')
    series_id          : Mapped[Optional[int]] = mapped_column('TarchiveSeriesID', ForeignKey('tarchive_series.TarchiveSeriesID'))
    series             : Mapped[Optional['DicomArchiveSeries.DicomArchiveSeries']] = relationship('DicomArchiveSeries', back_populates="files")
    series_number      : Mapped[Optional[int]] = mapped_column('SeriesNumber')
    series_description : Mapped[Optional[str]] = mapped_column('SeriesDescription')
    file_number        : Mapped[Optional[int]] = mapped_column('FileNumber')
    echo_number        : Mapped[Optional[int]] = mapped_column('EchoNumber')
    md5_sum            : Mapped[str]           = mapped_column('Md5Sum')
    file_name          : Mapped[str]           = mapped_column('FileName')
