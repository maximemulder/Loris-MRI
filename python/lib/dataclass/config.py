"""
This module stores the dataclasses used in the Python configuration file of LORIS-MRI.
"""

from dataclasses import dataclass


@dataclass
class CreateVisitConfig:
    """
    Class wrapping the parameters for automated visit creatinon (in the `Visit_Windows` table).
    """

    project_id: int
    cohort_id:  int


@dataclass
class SubjectConfig:
    """
    Dataclass wrapping information about a subject configuration, including information about the
    candidate, the visit label, and the automated visit creation (or not).
    """

    name: str
    # The name of the subject may be either the DICOM's PatientName or PatientID depending on the
    # LORIS configuration.
    is_phantom: bool
    # For a phantom scan, the PSCID and CandID are those of the scanner.
    psc_id: str
    cand_id: int
    visit_label: str
    # `CreateVisitConfig` means that a visit can be created automatically using the parameters
    # provided, `None` means that the visit needs to already exist in the database.
    create_visit: CreateVisitConfig | None
