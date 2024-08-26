import os
import sys
from typing import cast

import lib.exitcode
import lib.utilities as utilities
from lib.dcm2bids_imaging_pipeline_lib.base_pipeline import BasePipeline
from lib.db.orm.dicom_archive import DbDicomArchive

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
        self.validate_subject_ids()
        self._validate_dicom_archive_md5sum()

        # ---------------------------------------------------------------------------------------------
        # If we get here, the tarchive is validated & the script stops running so update mri_upload
        # ---------------------------------------------------------------------------------------------
        message = f"DICOM archive {self.options_dict['tarchive_path']['value']} is valid!"
        self.log_info(message, is_error="N", is_verbose="Y")
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

        self.log_info(message="Verifying DICOM archive md5sum (checksum)", is_error="N", is_verbose="Y")

        # TODO: Refactor so that this cast is not needed
        dicom_archive = cast(DbDicomArchive, self.dicom_archive)

        dicom_archive_path = os.path.join(self.dicom_lib_dir, dicom_archive.archive_location)

        # Compute the md5 sum of the DICOM archive file
        file_md5_sum = utilities.compute_md5_hash(dicom_archive_path)

        # Get the MD5 sum stored in the database
        db_md5_sum = dicom_archive.md5_sum_archive.split()[0]

        if file_md5_sum != db_md5_sum:
            self.imaging_upload_obj.update_mri_upload(
                upload_id=self.upload_id,
                fields=('isTarchiveValidated', 'IsCandidateInfoValidated'),
                values=('0', '0')
            )

            message = 'ERROR: DICOM archive seems corrupted or modified. Upload will exit now.'
            self.log_error_and_exit(message, lib.exitcode.CORRUPTED_FILE, is_error='Y', is_verbose='N')

        message = (
            f"Checksum for target: {file_md5_sum}; "
            f"Checksum from database: {db_md5_sum}"
        )

        self.log_info(message, is_error='N', is_verbose='Y')
