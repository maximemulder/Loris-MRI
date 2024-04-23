import argparse
import hashlib
import re
import sys
import tarfile
import traceback

from lib.database import Database
from lib.dicom import log as log_lib
from lib.dicom import summary as summary_lib
from lib.dicom import archive_database
from lib.lorisgetopt import LorisGetOpt

"""
parser = argparse.ArgumentParser(description=
    'Upload an existing DICOM archive to the LORIS database.')

parser.add_argument('archive',
    help='The DICOM archive')

parser.add_argument('-profile',
    help='The profile')

args = parser.parse_args() """

archive = 'DCM_2016-08-19_ImagingUpload-18-41-C4ZlTl.tar'

try:
    name = re.match(r'DCM_\d{4}-\d{2}-\d{2}_(.+)\.tar', archive).group(1)
    with tarfile.open(archive) as tar:
        tar.extract(f'{name}.meta')
        tar.extract(f'{name}.log')

    summary = summary_lib.read_from_file(f'{name}.meta')
    log = log_lib.read_from_file(f'{name}.log')
except Exception as e:
    print(f'ERROR: Cannot create a summary for the directory \'{archive}\'.', file=sys.stderr)
    print('Exception message:', file=sys.stderr)
    print(e, file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    exit(-1)

print(summary_lib.write_to_string(summary))
print(log_lib.write_to_string(log))

# get the options provided by the user
loris_getopt_obj = LorisGetOpt("USAGE", {
        "profile": {
            "value": None, "required": True, "expect_arg": True, "short_opt": "p", "is_path": False
        },
        "verbose": {
            "value": False, "required": False, "expect_arg": False, "short_opt": "v", "is_path": False
        },
    }, "NAME")

profile = loris_getopt_obj.options_dict['profile']['value']

# ---------------------------------------------------------------------------------------------
# Establish database connection
# ---------------------------------------------------------------------------------------------
config_file = loris_getopt_obj.config_info
db = Database(config_file.mysql, False)
db.connect()

def print_verbose(message: str):
    if True:
        print(message)

with open(archive, 'rb') as tar:
    print_verbose('Calculating DICOM tar MD5 sum')

    log.archive_md5_sum = hashlib.md5(tar.read()).hexdigest()

archive_database.create_tarchive(
    db,
    log,
    summary,
    None,
)
