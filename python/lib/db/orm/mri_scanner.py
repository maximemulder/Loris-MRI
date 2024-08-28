from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Mapped, Session, mapped_column
from lib.db.base import Base
from lib.db.orm import candidate as db_candidate


class DbMriScanner(Base):
    __tablename__ = 'mri_scanner'

    id            : Mapped[int]           = mapped_column('ID', primary_key=True)
    manufacturer  : Mapped[Optional[str]] = mapped_column('Manufacturer')
    model         : Mapped[Optional[str]] = mapped_column('Model')
    serial_number : Mapped[Optional[str]] = mapped_column('Serial_number')
    software      : Mapped[Optional[str]] = mapped_column('Software')
    cand_id       : Mapped[Optional[int]] = mapped_column('CandID')

    @staticmethod
    def create(db: Session, manufacturer: str, software: str, serial_number: str, model: str, cand_id: int):
        """
        Create a new scanner and insert it in the database.
        """

        scanner = DbMriScanner(
            manufacturer  = manufacturer,
            software      = software,
            serial_number = serial_number,
            model         = model,
            cand_id       = cand_id,
        )

        db.add(scanner)
        return scanner

    @staticmethod
    def get_or_create(
        db: Session,
        manufacturer: str,
        software: str,
        serial_number: str,
        model: str,
        center_id: int,
        project_id: int,
    ):
        """
        Get a scanner from the database using its attributes, or create a new scanner and its
        associated candidate if no scanner is found.
        """

        query = select(DbMriScanner) \
            .where(DbMriScanner.manufacturer == manufacturer) \
            .where(DbMriScanner.software == software) \
            .where(DbMriScanner.serial_number == serial_number) \
            .where(DbMriScanner.model == model)

        scanner = db.execute(query).scalar_one_or_none()
        if scanner is not None:
            return scanner

        DbCandidate = db_candidate.DbCandidate
        candidate = DbCandidate.create_scanner(db, center_id, project_id)

        return DbMriScanner.create(db, manufacturer, software, serial_number, model, candidate.cand_id)
