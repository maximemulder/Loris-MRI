import subprocess


def run_command(command: list[str]):
    process = subprocess.run(command, stderr=subprocess.PIPE)
    assert process.stderr.decode('utf-8') == ''
    assert process.returncode == 0


def test_dicom_archive_validation():
    run_command(['run_dicom_archive_validation.py',
        '--profile', 'database_config.py',
        '--tarchive_path', '/data/raisinbread/tarchive/2018/DCM_2018-04-20_ImagingUpload-14-25-U1OlWq.tar',
        '--upload_id', '82'
    ])


def test_dicom_archive_loader():
    run_command(['run_dicom_archive_loader.py',
        '--profile', 'database_config.py',
        '--tarchive_path', '/data/raisinbread/tarchive/2018/DCM_2018-04-20_ImagingUpload-14-25-U1OlWq.tar',
    ])

#
# UPDATE Config SET Value = 'dcm2niix' WHERE ConfigID = 76
#
# archive_id = SELECT tarchiveID FROM tarchive WHERE ArchiveLocation = '2018/DCM_2018-04-20_ImagingUpload-14-25-U1OlWq.tar'
# file_ids = SELECT FileID FROM files WHERE TarchiveSource = archive_id;
# output_file_ids = SELECT FileID FROM files WHERE SourceFileID IN file_ids;
# DELETE FROM files_intermediary WHERE Output_FileID IN output_file_ids;
# DELETE FROM parameter_file WHERE FileID IN output_file_ids;
# DELETE FROM files WHERE FileID IN output_file_ids;
# DELETE FROM parameter_file WHERE FileID IN file_ids;
# DELETE FROM files WHERE FileID IN file_ids;
#
