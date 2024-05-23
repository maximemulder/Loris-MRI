import lib.db.DicomArchive as DicomArchive
import lib.db.DicomArchiveFile as DicomArchiveFile
from lib.db.Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List, Optional


class DicomArchiveSeries(Base):
    __tablename__ = 'tarchive_series'

    id                 : Mapped[int]              = mapped_column('TarchiveSeriesID', primary_key=True)
    archive_id         : Mapped[int]              = mapped_column('TarchiveID', ForeignKey("tarchive.TarchiveID"))
    archive            : Mapped['DicomArchive.DicomArchive']     = relationship('DicomArchive', back_populates="series")
    files              : Mapped[List['DicomArchiveFile.DicomArchiveFile']] = relationship('DicomArchiveFile', back_populates="series")
    series_number      : Mapped[int]              = mapped_column('SeriesNumber')
    series_description : Mapped[Optional[str]]    = mapped_column('SeriesDescription')
    sequence_name      : Mapped[Optional[str]]    = mapped_column('SequenceName')
    echo_time          : Mapped[Optional[float]]  = mapped_column('EchoTime')
    repetition_time    : Mapped[Optional[float]]  = mapped_column('RepetitionTime')
    inversion_time     : Mapped[Optional[float]]  = mapped_column('InversionTime')
    slice_thickness    : Mapped[Optional[float]]  = mapped_column('SliceThickness')
    phase_encoding     : Mapped[Optional[str]]    = mapped_column('PhaseEncoding')
    number_of_files    : Mapped[int]              = mapped_column('NumberOfFiles')
    series_uid         : Mapped[Optional[str]]    = mapped_column('SeriesUID')
    modality           : Mapped[Optional[str]]    = mapped_column('Modality')
