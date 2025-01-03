import os
import sys

import lib.exitcode
from lib.dcm2bids_imaging_pipeline_lib.base_pipeline import BasePipeline
from lib.logging import log_error_exit, log_verbose

__license__ = "GPLv3"


class DicomValidationPipeline(BasePipeline):
    """
    Pipeline that extends the BasePipeline class to add some specific DICOM validations to be
    run to validate the DICOM archive processed.

    Functions that starts with _ are functions specific to the DicomValidationPipeline class.
    """

    def __init__(self, loris_getopt_obj, script_name):
        """
        Initiate the DicomValidationPipeline class and runs the different validations that need to
        be run on the DICOM archive. The mri_upload table will be updated according to the finding
        of the DICOM archive validation.

        :param loris_getopt_obj: the LorisGetOpt object with getopt values provided to the pipeline
         :type loris_getopt_obj: LorisGetOpt obj
        :param script_name: name of the script calling this class
         :type script_name: str
        """
        super().__init__(loris_getopt_obj, script_name)
        self.validate_subject_info()
        self._validate_dicom_archive_md5sum()

        # ---------------------------------------------------------------------------------------------
        # If we get here, the tarchive is validated & the script stops running so update mri_upload
        # ---------------------------------------------------------------------------------------------
        log_verbose(self.env, f"DICOM archive {self.options_dict['tarchive_path']['value']} is valid!")
        self.imaging_upload_obj.update_mri_upload(
            upload_id=self.upload_id,
            fields=("isTarchiveValidated", "Inserting",),
            values=("1", "0")
        )
        self.remove_tmp_dir()  # remove temporary directory
        sys.exit(lib.exitcode.SUCCESS)

    def _validate_dicom_archive_md5sum(self):
        """
        Validates that the DICOM archive stored on the file system has the same md5sum than the one
        logged in the <tarchive> table.
        """

        log_verbose(self.env, "Verifying DICOM archive md5sum (checksum)")

        tarchive_path = os.path.join(self.dicom_lib_dir, self.dicom_archive_obj.tarchive_info_dict["ArchiveLocation"])
        result = self.dicom_archive_obj.validate_dicom_archive_md5sum(tarchive_path)
        message = result["message"]

        if result['success']:
            log_verbose(self.env, message)
        else:
            self.imaging_upload_obj.update_mri_upload(
                upload_id=self.upload_id,
                fields=("isTarchiveValidated", "IsCandidateInfoValidated"),
                values=("0", "0")
            )
            log_error_exit(self.env,  message, lib.exitcode.CORRUPTED_FILE)
