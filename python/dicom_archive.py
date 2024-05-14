#!/usr/bin/env python

from datetime import date
from typing import Any, cast
import argparse
import gzip
import os
import shutil
import subprocess
import sys
import tarfile

from lib.database import Database
import lib.dicom.dicom_database
import lib.dicom.dicom_log
import lib.dicom.summary_make
import lib.dicom.summary_write
import lib.dicom.text
import lib.exitcode

def exit_error(message: str, code: int):
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
        exit_error(
            'Environment variable \'LORIS_CONFIG\' not set',
            lib.exitcode.INVALID_ENVIRONMENT_VAR,
        )

    config_file = os.path.join(os.environ["LORIS_CONFIG"], ".loris_mri", profile_path)

    if not config_file.endswith(".py"):
        exit_error(
            (
                f'\'{config_file}\' does not appear to be the python configuration file.'
                f' Try using \'database_config.py\' instead.'
            ),
            lib.exitcode.INVALID_ARG,
        )

    if not os.path.isfile(config_file):
        exit_error(
            f'\'{profile_path}\' does not exist in \'{os.environ["LORIS_CONFIG"]}\'.',
            lib.exitcode.INVALID_PATH,
        )

    sys.path.append(os.path.dirname(config_file))
    return __import__(os.path.basename(config_file[:-3]))

parser = argparse.ArgumentParser(description=(
        'Read a DICOM directory, process it into a structured and compressed archive, '
        'and insert it or upload it to the LORIS database.'
    ))

parser.add_argument('--profile',
    action='store',
    default=None,
    help='The database profile file (usually \'database_config.py\')')

parser.add_argument('--verbose',
    action='store_true',
    help='Set the script to be verbose')

parser.add_argument('--today',
    action='store_true',
    help='Use today\'s date for the archive name instead of using the scan date')

parser.add_argument('--year',
    action='store_true',
    help='Create the archive in a year subdirectory (example: 2024/DCM_2024-08-27_FooBar.tar)')

parser.add_argument('--overwrite',
    action='store_true',
    help='Overwrite the DICOM archive file if it already exists')

parser.add_argument('--db-insert',
    action='store_true',
    help=(
        'Insert the created DICOM archive in the database (requires the archive '
        'to not be already inserted)'))

parser.add_argument('--db-update',
    action='store_true',
    help=(
        'Update the DICOM archive in the database (requires the archive to be '
        'already be inserted)'))

parser.add_argument('source',
    help='The source DICOM directory')

parser.add_argument('target',
    help='The target directory for the DICOM archive')

args = parser.parse_args()

# Check arguments

if args.db_insert and args.db_update:
    exit_error(
        'Arguments \'--db-insert\' and \'--db-update\' must not be both set at the same time',
        lib.exitcode.INVALID_ARG,
    )

if (args.db_insert or args.db_update) and not args.profile:
    exit_error(
        'Argument \'--profile\' must be set when a \'--db-*\' argument is set',
        lib.exitcode.INVALID_ARG,
    )

if not os.path.isdir(args.source) or not os.access(args.source, os.R_OK):
    exit_error(
        'Argument \'--source\' must be a readable directory path',
        lib.exitcode.INVALID_ARG,
    )

if not os.path.isdir(args.target) or not os.access(args.target, os.W_OK):
    exit_error(
        'Argument \'--target\' must be a writable directory path',
        lib.exitcode.INVALID_ARG,
    )

db = None
if args.profile:
    db = Database(load_config_file(args.profile).mysql, False)
    db.connect()

# Type arguments
source:    str  = args.source
target:    str  = args.target
verbose:   bool = args.verbose
today:     bool = args.today
year:      bool = args.year
overwrite: bool = args.overwrite
db_insert: bool = args.db_insert
db_update: bool = args.db_update

# Remove trailing slashes
while source.endswith('/'):
    source = source[:-1]

base_name = os.path.basename(source)

tar_path     = f'{target}/{base_name}.tar'
zip_path     = f'{target}/{base_name}.tar.gz'
summary_path = f'{target}/{base_name}.meta'
log_path     = f'{target}/{base_name}.log'

print('Extracting DICOM information (may take a long time)')

summary = lib.dicom.summary_make.make(source)

print('Copying into DICOM tar')

with tarfile.open(tar_path, 'w') as tar:
    for file in os.listdir(source):
        tar.add(source + '/' + file)

print('Calculating DICOM tar MD5 sum')

tarball_md5_sum = lib.dicom.text.make_hash(tar_path, True)

print('Zipping DICOM tar (may take a long time)')

with open(tar_path, 'rb') as tar:
    with gzip.open(zip_path, 'wb') as zip:
        shutil.copyfileobj(tar, zip)

print('Calculating DICOM zip MD5 sum')

zipball_md5_sum = lib.dicom.text.make_hash(zip_path, True)

scan_date = date.today() if today else summary.info.scan_date

if year and scan_date:
    if not os.path.exists(f'{target}/{scan_date.year}'):
        os.mkdir(f'{target}/{scan_date.year}')

    scan_date_string = lib.dicom.text.write_date(scan_date)
    archive_path = f'{target}/{scan_date.year}/DCM_{scan_date_string}_{base_name}.tar'
else:
    scan_date_string = lib.dicom.text.write_date_none(scan_date) or ''
    archive_path = f'{target}/DCM_{scan_date_string}_{base_name}.tar'

log = lib.dicom.dicom_log.make(source, archive_path, tarball_md5_sum, zipball_md5_sum)

if verbose:
    print('The archive will be created with the following arguments:')
    print(lib.dicom.dicom_log.write_to_string(log))

print('Writing summary file')

lib.dicom.summary_write.write_to_file(summary_path, summary)

print('Writing log file')

lib.dicom.dicom_log.write_to_file(log_path, log)

print('Copying into DICOM archive')

with tarfile.open(archive_path, 'w') as tar:
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

if db_insert:
    # NOTE: `db` cannot be `None` here.
    db = cast(Database, db)

    archive = lib.dicom.dicom_database.get_archive_with_study_uid(db, summary.info.study_uid)
    if archive != None:
        exit_error(
            (
                f'Study \'{summary.info.study_uid}\' is already inserted in the database\n'
                'Previous archiving log:\n'
                f'{archive[1]}'
            ),
            lib.exitcode.INSERT_FAILURE,
        )

    lib.dicom.dicom_database.insert(db, log, summary)

if db_update:
    # NOTE: `db` cannot be `None` here.
    db = cast(Database, db)

    archive = lib.dicom.dicom_database.get_archive_with_study_uid(db, summary.info.study_uid)
    if archive == None:
        exit_error(
            f'No study \'{summary.info.study_uid}\' found in the database',
            lib.exitcode.UPDATE_FAILURE,
        )

    # NOTE: `archive` cannot be `None` here.
    archive = cast(tuple[Any, Any], archive)
    lib.dicom.dicom_database.update(db, archive[0], log, summary)

print('Success')
