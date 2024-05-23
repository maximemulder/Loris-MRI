import argparse
import getpass
import os
import sys
import lib.exitcode
from datetime import datetime
from lib.db.MriUpload import MriUpload
from lib.db.DicomArchive import DicomArchive
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

parser = argparse.ArgumentParser(description=(
        'Create a MRI upload entry from an existing DICOM archive.'
    ))

parser.add_argument(
    '--profile',
    action='store',
    default=None,
    required=True,
    help='The database profile file (usually \'database_config.py\')')

parser.add_argument(
    '--verbose',
    action='store_true',
    help='Set the script to be verbose')

parser.add_argument(
    'source',
    help='The source path of the MRI upload')

parser.add_argument(
    'archive',
    help='The absolute path of the DICOM archive')

args = parser.parse_args()


def print_error_exit(message: str, code: int):
    print(f'ERROR: {message}', file=sys.stderr)
    sys.exit(code)


# Modified version of 'lorisgetopt.load_config_file'.
# We use argparse to parse the command line options in this script,
# but still use this function to configure the database.
def load_config_file(profile_path: str):
    """
    Load the config file based on the value provided by the option '--profile' when
    running the script. If the config file cannot be loaded, the script will exit
    with a proper error message.
    """

    if "LORIS_CONFIG" not in os.environ.keys():
        print_error_exit(
            'Environment variable \'LORIS_CONFIG\' not set',
            lib.exitcode.INVALID_ENVIRONMENT_VAR,
        )

    config_file = os.path.join(os.environ["LORIS_CONFIG"], ".loris_mri", profile_path)

    if not config_file.endswith(".py"):
        print_error_exit(
            (
                f'\'{config_file}\' does not appear to be the python configuration file.'
                f' Try using \'database_config.py\' instead.'
            ),
            lib.exitcode.INVALID_ARG,
        )

    if not os.path.isfile(config_file):
        print_error_exit(
            f'\'{profile_path}\' does not exist in \'{os.environ["LORIS_CONFIG"]}\'.',
            lib.exitcode.INVALID_PATH,
        )

    sys.path.append(os.path.dirname(config_file))
    return __import__(os.path.basename(config_file[:-3]))

credentials = load_config_file(args.profile).mysql

engine = create_engine(f'mariadb+mysqlconnector://{credentials["username"]}:{credentials["passwd"]}@{credentials["host"]}:{3306}/{credentials["database"]}')

date             = datetime.now()
uploader         = getpass.getuser()
source_path      = args.source
query = select(DicomArchive).where(DicomArchive.archive_location == args.archive)

with Session(engine) as session:
    dicom_archive = session.scalars(query).one()

mri_upload = MriUpload(
    upload_date = date,
    decompressed_location = source_path,
    dicom_archive_id = dicom_archive.id,
    uploaded_by = uploader,
    upload_location = '',
    insertion_complete = False,
    patient_name = dicom_archive.patient_name,
    is_dicom_archive_validated = False,
    is_phantom = 'N',
)

with Session(engine) as session:
    session.add(mri_upload)
    session.commit()
