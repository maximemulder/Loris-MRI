class DicomPatientNameConfigException(Exception):
    """
    Exception raised if the configuration setting \'lookupCenterNameUsing\' is not correctly defined.
    """

    message: str

    def __init__(self, config_value: str):
        self.message = (
            f'Unexpected value \'{config_value}\' for \'lookupCenterNameUsing\' configuration parameter.\n'
            'This configuration parameter should be either \'PatientName\' or \'PatientID\'.'
        )

        super().__init__(self.message)
