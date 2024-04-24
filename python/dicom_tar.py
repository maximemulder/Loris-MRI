#!/usr/bin/env python

import argparse

import lib.dicom.dicom_tar

parser = argparse.ArgumentParser(description=(
        'Read a DICOM directory and process it into a structured and compressed archive. '
        'Unlike `dicom_archive.py`, this script does not require a database connexion.'
    ))

parser.add_argument('--verbose',
    action='store_true',
    help='Set the script to verbose')

parser.add_argument('--today',
    action='store_true',
    help='Use today\'s date for the archive name instead of using the scan date')

parser.add_argument('--year',
    action='store_true',
    help='Create the archive in a year subdirectory')

parser.add_argument('source',
    help='The source DICOM directory')

parser.add_argument('target',
    help='The target directory for the DICOM archive')

args = parser.parse_args()

lib.dicom.dicom_tar.run(args.source, args.target, args.verbose, args.today, args.year)
