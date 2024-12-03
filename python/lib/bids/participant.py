from dataclasses import dataclass


@dataclass
class BidsParticipant:
    """
    Information about a BIDS participant represented in an entry in the `participants.tsv` file of
    a BIDS dataset.
    """

    participant_id: str
    date_of_birth:  str | None = None
    sex:            str | None = None
    age:            str | None = None
    site:           str | None = None
    cohort:         str | None = None
    project:        str | None = None
    # FIXME: Both "cohort" and "subproject" are used in scripts, this may be a bug
    subproject:     str | None = None
