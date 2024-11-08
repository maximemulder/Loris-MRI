#!/usr/bin/env python

"""Script to import BIDS structure into LORIS."""

from argparse import ArgumentParser

# from lib.api.get_candidate_dicom import get_candidate_dicom
# from lib.api.post_candidate_dicom import post_candidate_dicom
from lib.api.post_candidate_dicom_processes import post_candidate_dicom_processes
from lib.dataclass.api import Api

parser = ArgumentParser()

parser.add_argument('-u', '--username', required=True)
parser.add_argument('-p', '--password', required=True)

args = parser.parse_args()

api = Api.from_credentials('https://mmulder-dev.loris.ca', args.username, args.password)
# print(get_candidate_dicom(api, 475906, 'V2'))
# print(post_candidate_dicom(api, 475906, 'DCC422', 'V2', False, '/data/test_upload/DCC422_475906_V2.tar', overwrite=True))
print(post_candidate_dicom_processes(api, 475906, 'V2', 'DCC422_475906_V2', 132))
