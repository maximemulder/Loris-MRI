import gzip
import hashlib
import os
import shutil
import tarfile

from lib.dicom import summary
from lib.dicom import dicom_log
from lib.dicom.text import *

def run(source: str, target: str, verbose: bool, today: bool, year: bool):
    """
    Run the pipeline to transform a raw DICOM directory into a structured DICOM
    archive.
    """

    def print_verbose(message: str):
        if verbose:
            print(message)

    # Remove trailing slashes
    while source.endswith('/'):
        source = source[:-1]

    base_name = os.path.basename(source)

    tar_path     = f'{target}/{base_name}.tar'
    zip_path     = f'{target}/{base_name}.tar.gz'
    summary_path = f'{target}/{base_name}.meta'
    log_path     = f'{target}/{base_name}.log'

    print_verbose('Extracting DICOM information (may take a long time)')

    dicom_summary = summary.make(source)

    print_verbose('Copying into DICOM tar')

    with tarfile.open(tar_path, 'w') as tar:
        for file in os.listdir(source):
            tar.add(source + '/' + file)

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

    scan_date = date.today() if today else dicom_summary.info.scan_date

    if year and scan_date:
        if not os.path.exists(f'{target}/{scan_date.year}'):
            os.mkdir(f'{target}/{scan_date.year}')

        scan_date_string = write_date(scan_date)
        archive_path = f'{target}/{scan_date.year}/DCM_{scan_date_string}_{base_name}.tar'
    else:
        scan_date_string = write_date_none(scan_date) or ''
        archive_path = f'{target}/DCM_{scan_date_string}_{base_name}.tar'

    log = dicom_log.make(source, archive_path, tarball_md5_sum, zipball_md5_sum)

    print_verbose('Writing summary file')

    summary.write_to_file(summary_path, dicom_summary)

    print_verbose('Writing log file')

    dicom_log.write_to_file(log_path, log)

    print_verbose('Copying into DICOM archive')

    with tarfile.open(archive_path, 'w') as tar:
        tar.add(zip_path,     os.path.basename(zip_path))
        tar.add(summary_path, os.path.basename(summary_path))
        tar.add(log_path,     os.path.basename(log_path))

    print_verbose('Removing temporary files')

    os.remove(tar_path)
    os.remove(zip_path)
    os.remove(summary_path)
    os.remove(log_path)

    print('Success')

    return dicom_summary, log
