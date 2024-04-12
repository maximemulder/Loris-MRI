import argparse
import gzip
import hashlib
import os
import shutil
import tarfile

from lib.dicom import summary
from lib.dicom import log

parser = argparse.ArgumentParser(description=
    'Archive a DICOM directory.')

parser.add_argument('source',
    help='The source DICOM directory')

parser.add_argument('target',
    help='The target directory in which the archive should be placed')

parser.add_argument('-verbose',
    action='store_true',
    help='Display verbose information')

args = parser.parse_args()

def print_verbose(message: str):
    if args.verbose:
        print(message)

base_name = os.path.basename(args.source)

tar_path     = f'{args.target}/{base_name}.tar'
zip_path     = f'{args.target}/{base_name}.tar.gz'
summary_path = f'{args.target}/{base_name}.meta'
log_path     = f'{args.target}/{base_name}.log'

print_verbose('Extracting DICOM information (may take a long time)')

dicom_summary = summary.make(args.source)

print_verbose('Copying into DICOM tar')

with tarfile.open(tar_path, 'w') as tar:
    for file in os.listdir(args.source):
        tar.add(args.source + '/' + file)

with open(tar_path, 'rb') as tar:
    print_verbose('Calculating DICOM tar MD5 sum')

    tarball_md5_sum = hashlib.md5(tar.read()).hexdigest()
    tar.seek(0)

    print_verbose('Zipping DICOM tar (may take a long time)')

    with gzip.open(zip_path, 'wb') as zip:
        shutil.copyfileobj(tar, zip)

print_verbose('Calculating DICOM zip MD5 sum')

with open(zip_path, 'rb') as zip:
    zipball_md5_sum = hashlib.md5(zip.read()).hexdigest()

date = dicom_summary.info.scan_date
archive_path = f'{args.target}/DCM_{date[0:4]}-{date[5:7]}-{date[8:10]}_{base_name}.tar'

dicom_log = log.make(args.source, archive_path, tarball_md5_sum, zipball_md5_sum)

print_verbose('Writing summary file')

summary.write_to_file(summary_path, dicom_summary)

print_verbose('Writing log file')

log.write_to_file(log_path, dicom_log)

print_verbose('Copying into DICOM archive')

with tarfile.open(archive_path, 'w') as tar:
    tar.add(zip_path)
    tar.add(summary_path)
    tar.add(log_path)

print_verbose('Removing temporary files')

os.remove(tar_path)
os.remove(zip_path)
os.remove(summary_path)
os.remove(log_path)

print('Success')
