from datetime import datetime
import os
import re
import socket

class Log:
    source_path:     str
    target_path:     str
    creator_host:    str
    creator_os:      str
    creator_name:    str
    archive_date:    str
    summary_version: str
    archive_version: str
    tarball_md5_sum: str
    zipball_md5_sum: str
    archive_md5_sum: str

    def __init__(self,
        source_path:     str,
        target_path:     str,
        creator_host:    str,
        creator_os:      str,
        creator_name:    str,
        archive_date:    str,
        summary_version: str,
        archive_version: str,
        tarball_md5_sum: str,
        zipball_md5_sum: str,
        archive_md5_sum: str,
    ):
        self.source_path     = source_path
        self.target_path     = target_path
        self.creator_host    = creator_host
        self.creator_os      = creator_os
        self.creator_name    = creator_name
        self.archive_date    = archive_date
        self.summary_version = summary_version
        self.archive_version = archive_version
        self.tarball_md5_sum = tarball_md5_sum
        self.zipball_md5_sum = zipball_md5_sum
        self.archive_md5_sum = archive_md5_sum


regex = r"""\
\* Taken from dir                   :    (.+)
\* Archive target location          :    (.+)
\* Name of creating host            :    (.+)
\* Name of host OS                  :    (.+)
\* Created by user                  :    (.+)
\* Archived on                      :    (.+)
\* dicomSummary version             :    (.+)
\* dicomTar version                 :    (.+)
\* md5sum for DICOM tarball         :    (.+)
\* md5sum for DICOM tarball gzipped :    (.+)
\* md5sum for complete archive      :    (.+)
"""

def read_from_string(string: str):
    match = re.match(regex, string)
    if match == None:
        raise Exception('Could not read the log string.')

    return Log(
        match.group(0),
        match.group(1),
        match.group(2),
        match.group(3),
        match.group(4),
        match.group(5),
        match.group(6),
        match.group(7),
        match.group(8),
        match.group(9),
        match.group(10),
    )

def read_from_file(filename: str):
    with open(filename) as file:
        string = file.read()

    return read_from_string(string)

def write_to_string(log: Log):
    return f"""\
* Taken from dir                   :    {log.source_path}
* Archive target location          :    {log.target_path}
* Name of creating host            :    {log.creator_host}
* Name of host OS                  :    {log.creator_os}
* Created by user                  :    {log.creator_name}
* Archived on                      :    {log.archive_date}
* dicomSummary version             :    {log.summary_version}
* dicomTar version                 :    {log.archive_version}
* md5sum for DICOM tarball         :    {log.tarball_md5_sum}
* md5sum for DICOM tarball gzipped :    {log.zipball_md5_sum}
* md5sum for complete archive      :    {log.archive_md5_sum}
"""

def write_to_file(filename: str, log: Log):
    string = write_to_string(log)
    with open(filename, 'w') as file:
        file.write(string)

def make(source: str, target: str, tarball_md5_sum: str, zipball_md5_sum: str):
    return Log(
        source,
        target,
        socket.gethostname(),
        os.uname().sysname,
        os.environ['USER'],
        datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
        '1',
        '1',
        tarball_md5_sum,
        zipball_md5_sum,
        'Provided in database only',
    )
