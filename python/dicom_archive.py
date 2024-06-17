#!/usr/bin/env python

from datetime import date
from typing import cast
import argparse
import gzip
import os
import shutil
import sys
import tarfile

from lib.db.database import connect_to_db
from lib.db.orm.dicom_archive import DicomArchive
from lib.db.orm.mri_upload import MriUpload
import lib.database
import lib.dicom.dicom_database
import lib.dicom.dicom_log
import lib.dicom.summary_make
import lib.dicom.summary_write
import lib.dicom.text
import lib.exitcode
from sqlalchemy.orm import Session as Db


def print_error_exit(message: str, code: int):
    print(f'ERROR: {message}', file=sys.stderr)
    sys.exit(code)


def print_warning(message: str):
    print(f'WARNING: {message}', file=sys.stderr)


def check_create_file(path: str):
    if os.path.exists(path):
        if overwrite:
            print_warning(f'Overwriting \'{path}\'')
        else:
            print_error_exit(
                (
                    f'File or directory \'{path}\' already exists. '
                    'Use option \'--overwrite\' to overwrite it.'
                ),
                lib.exitcode.TARGET_EXISTS_NO_CLOBBER,
            )


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


parser = argparse.ArgumentParser(description=(
        'Read a DICOM directory, process it into a structured and compressed archive, '
        'and insert it or upload it to the LORIS database.'
    ))

parser.add_argument(
    '--profile',
    action='store',
    default=None,
    help='The database profile file (usually \'database_config.py\')')

parser.add_argument(
    '--verbose',
    action='store_true',
    help='Set the script to be verbose')

parser.add_argument(
    '--today',
    action='store_true',
    help='Use today\'s date for the archive name instead of using the scan date')

parser.add_argument(
    '--year',
    action='store_true',
    help='Create the archive in a year subdirectory (example: 2024/DCM_2024-08-27_FooBar.tar)')

parser.add_argument(
    '--overwrite',
    action='store_true',
    help='Overwrite the DICOM archive file if it already exists')

parser.add_argument(
    '--db-insert',
    action='store_true',
    help=(
        'Insert the created DICOM archive in the database (requires the archive '
        'to not be already inserted)'))

parser.add_argument(
    '--db-update',
    action='store_true',
    help=(
        'Update the DICOM archive in the database, which requires the archive to be '
        'already be inserted), generally used with \'--overwrite\''))

parser.add_argument(
    '--db-session',
    action='store_true',
    help=(
        'Update the DICOM archive in the database to add the session ID determined '
        'using the LORIS configuration.')
)

parser.add_argument(
    '--db-upload',
    action='store',
    type=int,
    help=(
        'Update an exisiting MRI upload entry in the database to associate it with '
        'the newly create DICOM archive.'
    )
)

parser.add_argument(
    'source',
    help='The source DICOM directory')

parser.add_argument(
    'target',
    help='The target directory for the DICOM archive')

args = parser.parse_args()

# Typed arguments

profile:    str | None = args.profile
source:     str        = args.source
target:     str        = args.target
verbose:    bool       = args.verbose
today:      bool       = args.today
year:       bool       = args.year
overwrite:  bool       = args.overwrite
db_insert:  bool       = args.db_insert
db_update:  bool       = args.db_update
db_session: bool       = args.db_session
db_upload:  int | None = args.db_upload

source = os.path.abspath(source)
target = os.path.abspath(target)

# Check arguments

if db_insert and db_update:
    print_error_exit(
        'Arguments \'--db-insert\' and \'--db-update\' must not be set both at the same time.',
        lib.exitcode.INVALID_ARG,
    )

if (db_session or db_upload is not None) and not (db_insert or db_update):
    print_error_exit(
        'Arguments \'--db-insert\' or \'--db-update\' must be set when \'--db-session\' or \'--db-upload\' is set.',
        lib.exitcode.INVALID_ARG,
    )

if (db_insert or db_update or db_session or db_upload is not None) and not profile:
    print_error_exit(
        'Argument \'--profile\' must be set when a \'--db-*\' argument is set.',
        lib.exitcode.INVALID_ARG,
    )

if not os.path.isdir(source) or not os.access(source, os.R_OK):
    print_error_exit(
        'Argument \'--source\' must be a readable directory path.',
        lib.exitcode.INVALID_ARG,
    )

if not os.path.isdir(target) or not os.access(target, os.W_OK):
    print_error_exit(
        'Argument \'--target\' must be a writable directory path.',
        lib.exitcode.INVALID_ARG,
    )

# Load configuration

config = load_config_file(args.profile)

# Connect to database (if needed)

db = None
if profile is not None:
    db = connect_to_db(config.mysql)

# Load subject IDs (if needed)

if db_session is not None:
    old_db = lib.database.Database(config.mysql, verbose)
    try:
        get_subject_ids = config.get_subject_ids
    except AttributeError:
        print_error_exit(
            'Config file does not contain a `get_subject_ids` function.',
            lib.exitcode.BAD_CONFIG_SETTING,
        )

# Check paths

base_name = os.path.basename(source)

tar_path     = f'{target}/{base_name}.tar'
zip_path     = f'{target}/{base_name}.tar.gz'
summary_path = f'{target}/{base_name}.meta'
log_path     = f'{target}/{base_name}.log'

check_create_file(tar_path)
check_create_file(zip_path)
check_create_file(summary_path)
check_create_file(log_path)

# Check MRI upload

# Placeholder for type checker
mri_upload = None
if db_upload is not None:
    db = cast(Db, db)

    mri_upload = lib.dicom.dicom_database.get_mri_upload(db, db_upload)
    if mri_upload is None:
        print_error_exit(
            f'No MRI upload found in the database with id {db_upload}.',
            lib.exitcode.UPDATE_FAILURE,
        )

print('Extracting DICOM information (may take a long time)')

summary = lib.dicom.summary_make.make(source, verbose)

# Placeholder for type checker
dicom_archive = None
if db is not None:
    print('Checking database presence')

    dicom_archive = lib.dicom.dicom_database.get_dicom_archive_with_study_uid(db, summary.info.study_uid)

    if db_insert and dicom_archive is not None:
        print_error_exit(
            (
                f'Study \'{summary.info.study_uid}\' is already inserted in the database\n'
                'Previous archiving log:\n'
                f'{dicom_archive.create_info}'
            ),
            lib.exitcode.INSERT_FAILURE,
        )

    if db_update and dicom_archive is None:
        print_error_exit(
            f'No study \'{summary.info.study_uid}\' found in the database',
            lib.exitcode.UPDATE_FAILURE,
        )


if db_session:
    db = cast(Db, db)

    print('Determining session ID')

    ids = config.get_subject_ids(old_db, summary.info.patient.name)
    cand_id     = ids['CandID']
    visit_label = ids['visitLabel']
    session_id = lib.dicom.dicom_database.get_session_id_with_cand_visit(db, cand_id, visit_label)

    if session_id == None:
        print_warning((
            f'No session found in the database for patient name \'{summary.info.patient.name}\' '
            f'and visit label \'{visit_label}\'.'
        ))
else:
    session_id = None

print('Copying into DICOM tar')

with tarfile.open(tar_path, 'w') as tar:
    for file in os.listdir(source):
        tar.add(f'{source}/{file}')

print('Calculating DICOM tar MD5 sum')

tarball_md5_sum = lib.dicom.text.make_hash(tar_path, True)

print('Zipping DICOM tar (may take a long time)')

with open(tar_path, 'rb') as tar:
    with gzip.open(zip_path, 'wb') as zip:
        shutil.copyfileobj(tar, zip)

print('Calculating DICOM zip MD5 sum')

zipball_md5_sum = lib.dicom.text.make_hash(zip_path, True)

print('Getting DICOM scan date')

if not today and summary.info.scan_date is None:
    print_warning((
        'No scan date found for this DICOM archive, '
        'consider using argument \'--today\' to use today\'s date instead.'
    ))

scan_date = date.today() if today else summary.info.scan_date

archive_path = ''

if year:
    if not scan_date:
        print_error_exit(
            'Cannot use year directory with no date found for this DICOM archive.',
            lib.exitcode.CREATE_DIR_FAILURE,
        )

    scan_date = cast(date, scan_date)

    year_path = f'{target}/{scan_date.year}'
    if not os.path.exists(year_path):
        print(f'Creating directory \'{year_path}\'')
        os.mkdir(year_path)
    elif not os.path.isdir(year_path) or not os.access(year_path, os.W_OK):
        print_error_exit(
            f'Path \'{year_path}\' exists but is not a writable directory.',
            lib.exitcode.CREATE_DIR_FAILURE,
        )

    archive_path += f'{scan_date.year}/'

scan_date_string = lib.dicom.text.write_date_none(scan_date) or ''

archive_path += f'DCM_{scan_date_string}_{base_name}.tar'

final_path = f'{target}/{archive_path}'

check_create_file(final_path)

log = lib.dicom.dicom_log.make(source, final_path, tarball_md5_sum, zipball_md5_sum)

if verbose:
    print('The archive will be created with the following arguments:')
    print(lib.dicom.dicom_log.write_to_string(log))

print('Writing summary file')

lib.dicom.summary_write.write_to_file(summary_path, summary)

print('Writing log file')

lib.dicom.dicom_log.write_to_file(log_path, log)

print('Copying into DICOM archive')

with tarfile.open(final_path, 'w') as tar:
    tar.add(zip_path,     os.path.basename(zip_path))
    tar.add(summary_path, os.path.basename(summary_path))
    tar.add(log_path,     os.path.basename(log_path))

print('Removing temporary files')

os.remove(tar_path)
os.remove(zip_path)
os.remove(summary_path)
os.remove(log_path)

print('Calculating DICOM tar MD5 sum')

log.archive_md5_sum = lib.dicom.text.make_hash(log.target_path, True)

if db:
    if db_insert:
        print('Inserting DICOM archive in the database')
        dicom_archive = lib.dicom.dicom_database.insert(db, log, summary, archive_path, session_id)

    if db_update:
        print('Updating DICOM archive in the database')
        dicom_archive = cast(DicomArchive, dicom_archive)
        lib.dicom.dicom_database.update(db, dicom_archive, log, summary, archive_path, session_id)

    if db_upload is not None:
        print('Updating MRI upload in the database')
        mri_upload    = cast(MriUpload, mri_upload)
        dicom_archive = cast(DicomArchive, dicom_archive)
        lib.dicom.dicom_database.upload(dicom_archive, mri_upload)

    db.commit()

print('Success')
