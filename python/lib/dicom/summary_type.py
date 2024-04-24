from datetime import date

class Patient:
    id:        str
    name:      str
    sex:       str | None
    birthdate: date | None

    def __init__(self, id: str, name: str, sex: str | None, birthdate: date | None):
        self.id        = id
        self.name      = name
        self.sex       = sex
        self.birthdate = birthdate

class Scanner:
    manufacturer:     str
    model:            str
    serial_number:    str
    software_version: str

    def __init__(self, manufacturer: str, model: str, serial_number: str, software_version: str):
        self.manufacturer     = manufacturer
        self.model            = model
        self.serial_number    = serial_number
        self.software_version = software_version

class Info:
    study_uid:   str
    patient:     Patient
    scanner:     Scanner
    scan_date:   date | None
    institution: str | None
    modality:    str

    def __init__(self,
        study_uid:   str,
        patient:     Patient,
        scanner:     Scanner,
        scan_date:   date | None,
        institution: str | None,
        modality:    str,
    ):
        self.study_uid   = study_uid
        self.patient     = patient
        self.scanner     = scanner
        self.scan_date   = scan_date
        self.institution = institution
        self.modality    = modality

class File:
    series_number:      int | None
    series_uid:         str | None
    series_description: str | None
    file_number:        int | None
    echo_number:        int | None
    echo_time:          float | None
    md5_sum:            str
    file_name:          str

    def __init__(self,
        series_number:      int | None,
        series_uid:         str | None,
        series_description: str | None,
        file_number:        int | None,
        echo_number:        int | None,
        echo_time:          int | None,
        md5_sum:            str,
        file_name:          str,
    ):
        self.series_number      = series_number
        self.series_uid         = series_uid
        self.series_description = series_description
        self.file_number        = file_number
        self.echo_number        = echo_number
        self.echo_time          = echo_time
        self.md5_sum            = md5_sum
        self.file_name          = file_name

class Acquisition:
    series_number:      int
    series_uid:         str | None
    series_description: str | None
    sequence_name:      str | None
    echo_time:          float | None # In Milliseconds
    repetition_time:    float | None # In Milliseconds
    inversion_time:     float | None # In Milliseconds
    slice_thickness:    float | None # In Millimeters
    phase_encoding:     str | None
    number_of_files:    int
    modality:           str | None

    def __init__(self,
        series_number:      int,
        series_uid:         str | None,
        series_description: str | None,
        sequence_name:      str | None,
        echo_time:          float | None,
        repetition_time:    float | None,
        inversion_time:     float | None,
        slice_thickness:    float | None,
        phase_encoding:     str | None,
        number_of_files:    int,
        modality:           str | None,
    ):
        self.series_number      = series_number
        self.series_uid         = series_uid
        self.series_description = series_description
        self.sequence_name      = sequence_name
        self.echo_time          = echo_time
        self.repetition_time    = repetition_time
        self.inversion_time     = inversion_time
        self.slice_thickness    = slice_thickness
        self.phase_encoding     = phase_encoding
        self.number_of_files    = number_of_files
        self.modality           = modality

class Summary:
    info: Info
    acquis: list[Acquisition]
    dicom_files: list[File]
    other_files: list[None]

    def __init__(self,
        info: Info,
        acquis: list[Acquisition],
        dicom_files: list[File],
        other_files: list[None],
    ):
        self.info         = info
        self.acquis       = acquis
        self.dicom_files  = dicom_files
        self.other_files  = other_files
