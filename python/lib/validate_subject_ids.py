from typing import cast
from sqlalchemy.orm import Session as Database
from lib.database_lib.candidate_db import CandidateDB
from lib.database_lib.visit_windows import VisitWindows
from lib.dataclass.config import SubjectConfig
from lib.db.orm.candidate import DbCandidate
from lib.exception.validate_subject_exception import ValidateSubjectException


def validate_subject_ids(db: Database, verbose: bool, subject: SubjectConfig):
    """
    Validate a subject's information against the database from its parts (PSCID, CandID, VisitLabel).
    Raise an exception if an error is found, or return `None` otherwise.
    """

    candidate = DbCandidate.get_from_cand_id(db, subject.cand_id)
    if candidate is None:
        validate_subject_error(
            subject,
            f'Candidate (CandID = \'{subject.cand_id}\') does not exist in the database.'
        )

    # Safe because the previous check throws an exception if the candidate is `None`.
    candidate = cast(DbCandidate, candidate)

    if candidate.psc_id != subject.psc_id:
        validate_subject_error(
            subject,
            f'Candidate (CandID = \'{subject.cand_id}\') PSCID does not match the subject PSCID.\n'
            f'Candidate PSCID = \'{candidate.psc_id}\', Subject PSCID = \'{subject.psc_id}\''
        )

    visit_window_db = VisitWindows(db, verbose)
    visit_window_exists = visit_window_db.check_visit_label_exists(subject.visit_label)
    if not visit_window_exists and subject.create_visit is not None:
        validate_subject_error(
            subject,
            f'Visit label \'{subject.visit_label}\' does not exist in the database (table `Visit_Windows`).'
        )


def validate_subject_error(subject: SubjectConfig, message: str):
    raise ValidateSubjectException(f'Validation error for subject \'{subject.name}\'.\n{message}')
