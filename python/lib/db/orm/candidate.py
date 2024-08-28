from datetime import date, datetime
import random
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, Mapped, mapped_column
from lib.db.base import Base


class DbCandidate(Base):
    id                      : Mapped[int]            = mapped_column('ID', primary_key=True)
    cand_id                 : Mapped[int]            = mapped_column('CandID')
    psc_id                  : Mapped[str]            = mapped_column('PSCID')
    external_id             : Mapped[Optional[str]]  = mapped_column('ExternalID')
    date_of_birth           : Mapped[Optional[date]] = mapped_column('DoB')
    dete_of_death           : Mapped[Optional[date]] = mapped_column('DoD')
    edc                     : Mapped[Optional[date]] = mapped_column('EDC')
    sex                     : Mapped[Optional[str]]  = mapped_column('Sex')
    registration_center_id  : Mapped[int]            = mapped_column('RegistrationCenterID')
    registration_project_id : Mapped[int]            = mapped_column('RegistrationProjectID')
    ethnicity               : Mapped[Optional[str]]  = mapped_column('Ethnicity')
    active                  : Mapped[str]            = mapped_column('Active')
    date_active             : Mapped[Optional[date]] = mapped_column('Date_active')
    registered_by           : Mapped[Optional[str]]  = mapped_column('RegisteredBy')
    user_id                 : Mapped[str]            = mapped_column('UserID')
    date_registered         : Mapped[Optional[date]] = mapped_column('Date_registered')
    flagged_caveatemptor    : Mapped[Optional[str]]  = mapped_column('flagged_caveatemptor')
    flagged_reason          : Mapped[Optional[int]]  = mapped_column('flagged_reason')
    flagged_other           : Mapped[Optional[str]]  = mapped_column('flagged_other')
    flagged_other_status    : Mapped[Optional[str]]  = mapped_column('flagged_other_status')
    test_date               : Mapped[int]            = mapped_column('Testdate')
    entity_type             : Mapped[str]            = mapped_column('Entity_type')
    proband_sex             : Mapped[Optional[str]]  = mapped_column('ProbandSex')
    proband_sate_of_birth   : Mapped[Optional[date]] = mapped_column('ProbandDoB')

    @staticmethod
    def create_scanner(db: Session, center_id: int, project_id: int):
        """
        Create a new scanner candidate and insert it in the database.
        """

        cand_id = DbCandidate.generate_new_cand_id(db)

        now = datetime.now()

        candidate = DbCandidate(
            cand_id                 = cand_id,
            psc_id                  = 'scanner',
            registration_center_id  = center_id,
            date_active             = now,
            user_id                 = 'imaging.py',
            entity_type             = 'Scanner',
            registration_project_id = project_id,
            date_registered         = now,
        )

        db.add(candidate)
        return candidate

    @staticmethod
    def get_with_cand_id(db: Session, cand_id: int):
        """
        Get a candidate from the database using its CandID, or `None` if these is no such candidate.
        """

        query = select(DbCandidate).where(DbCandidate.cand_id == cand_id)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def generate_new_cand_id(db: Session):
        """
        Generate a new CandID that does not currently exist in the database.
        """

        cand_id = random.randint(100000, 999999)
        while DbCandidate.get_with_cand_id(db, cand_id) is not None:
            cand_id = random.randint(100000, 999999)

        return cand_id
