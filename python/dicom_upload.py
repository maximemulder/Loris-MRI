import argparse
import sys

from lib.dicom import summary

parser = argparse.ArgumentParser(description=
    'Upload an existing DICOM archive to the LORIS database.')

parser.add_argument('directory',
    required=True,
    help='The DICOM directory')

args = parser.parse_args()

try:
    dicom = summary.make(args.directory)
except Exception as e:
    print(f'ERROR: Cannot create a summary for the directory \'{args.directory}\'.', file=sys.stderr)
    print('Exception message:', file=sys.stderr)
    print(e, file=sys.stderr)
    exit(-1)

print(summary.write_to_string(dicom))
