#!/usr/bin/env python

import argparse
import os
import sys

from lib.database import Database
import lib.dicom.dicom_tar
import lib.dicom.dicom_database
import lib.dicom.text
import lib.exitcode

def exit_error(message: str, code: int):
    print(f'ERROR: {message}', file=sys.stderr)
    sys.exit(code)

# Modified version of 'lorisgetopt.load_config_file'.
# We use argparse to parse the command line options in this script,
# but still use this function to configure the database.
# NOTE: We may want to use a more modern database library in the future.
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
    required=True,
    help='The database profile file (usually \'database_config.py\')')

parser.add_argument('--verbose',
    action='store_true',
    help='Set the script to be verbose')

parser.add_argument('--today',
    action='store_true',
    help='Use today\'s date for the archive name instead of using the scan date')

parser.add_argument('--year',
    action='store_true',
    help='Create the archive in a year subdirectory')

parser.add_argument('--insert',
    action='store_true',
    help=(
        'Insert the created dicom archive in the database (requires the archive '
        'to not be already inserted)'))

parser.add_argument('--update',
    action='store_true',
    help=(
        'Update the dicom archive in the database (requires the archive to be '
        'already be inserted)'))

parser.add_argument('source',
    help='The source DICOM directory')

parser.add_argument('target',
    help='The target directory for the DICOM archive')

args = parser.parse_args()

db = Database(load_config_file(args.profile).mysql, False)
db.connect()

if args.insert and args.update:
    exit_error(
        'Arguments \'--insert\' and \'--update\' must not both be set at the same time',
        lib.exitcode.INVALID_ARG,
    )

summary, log = lib.dicom.dicom_tar.run(args.source, args.target, args.verbose, args.today, args.year)

def print_verbose(message: str):
    if args.verbose:
        print(message)

print_verbose('Calculating DICOM tar MD5 sum')

log.archive_md5_sum = lib.dicom.text.make_hash(log.target_path, True)

if args.insert:
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

if args.update:
    archive = lib.dicom.dicom_database.get_archive_with_study_uid(db, summary.info.study_uid)
    if archive == None:
        exit_error(
            f'No study \'{summary.info.study_uid}\' found in the database',
            lib.exitcode.UPDATE_FAILURE,
        )

    # NOTE: The type checker is currently not smart enough to work without this `else`
    else:
        lib.dicom.dicom_database.update(db, archive[0], log, summary)
