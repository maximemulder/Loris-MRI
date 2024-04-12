class Info:
    study_uid:         str
    patient_id:        str
    patient_name:      str
    patient_sex:       str | None
    patient_birthdate: str | None
    scan_date:         str
    scanner_model:     str
    scanner_software:  str
    institution:       str | None
    modality:          str

    def __init__(self,
        study_uid:         str,
        patient_id:        str,
        patient_name:      str,
        patient_sex:       str | None,
        patient_birthdate: str | None,
        scan_date:         str,
        scanner_model:     str,
        scanner_software:  str,
        institution:       str | None,
        modality:          str,
    ):
        self.study_uid         = study_uid
        self.patient_id        = patient_id
        self.patient_name      = patient_name
        self.patient_sex       = patient_sex
        self.patient_birthdate = patient_birthdate
        self.scan_date         = scan_date
        self.scanner_model     = scanner_model
        self.scanner_software  = scanner_software
        self.institution       = institution
        self.modality          = modality

class File:
    series_number:      int | None
    file_number:        int | None
    echo_number:        int | None
    series_description: str | None
    md5_sum:            str
    file_name:          str

    def __init__(self,
        series_number:      int | None,
        file_number:        int | None,
        echo_number:        int | None,
        series_description: str | None,
        md5_sum:            str,
        file_name:          str,
    ):
        self.series_number      = series_number
        self.file_number        = file_number
        self.echo_number        = echo_number
        self.series_description = series_description
        self.md5_sum            = md5_sum
        self.file_name          = file_name

class Acquisition:
    series_number:      int
    series_description: str | None
    sequence_name:      str | None
    echo_time:          float | None # In Milliseconds
    repetition_time:    float | None # In Milliseconds
    inversion_time:     float | None # In Milliseconds
    slice_thickness:    float | None # In Millimeters
    phase_encoding:     str | None
    files_count:        int

    def __init__(self,
        series_number:      int,
        series_description: str | None,
        sequence_name:      str | None,
        echo_time:          float | None,
        repetition_time:    float | None,
        inversion_time:     float | None,
        slice_thickness:    float | None,
        phase_encoding:     str | None,
        files_count:        int,
    ):
        self.series_number      = series_number
        self.series_description = series_description
        self.sequence_name      = sequence_name
        self.echo_time          = echo_time
        self.repetition_time    = repetition_time
        self.inversion_time     = inversion_time
        self.slice_thickness    = slice_thickness
        self.phase_encoding     = phase_encoding
        self.files_count        = files_count

class Summary:
    info: Info
    files: list[File]
    acquisitions: list[Acquisition]

    def __init__(self, info: Info, files: list[File], acquisitions: list[Acquisition]):
        self.info         = info
        self.files        = files
        self.acquisitions = acquisitions
