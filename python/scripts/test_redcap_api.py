#!/usr/bin/env python

import requests

redcap_api_url = 'https://portal.rimuhc.ca/cim/redcap/api/'
redcap_api_token = '195B812F00648FC5BA0248B55037AE23'

psc_id = ''
instrument = ''
visit_label = ''

"""response = requests.post(redcap_api_url, data = {
    'token'                  : redcap_api_token,
    'content'                : 'record',
    'format'                 : 'json',
    'type'                   : 'flat',
    'csvDelimiter'           : '',
    'records'                : [psc_id],
    'fields'                 : [],
    'forms'                  : [instrument],
    'events'                 : [visit_label],
    'rawOrLabel'             : 'raw',
    'rawOrLabelHeaders'      : 'raw',
    'exportCheckboxLabel'    : 'true',
    'exportSurveyFields'     : 'true',
    'exportDataAccessGroups' : 'true',
    'returnFormat'           : 'json',
})"""

response = requests.post(redcap_api_url, data = {
    'token'                  : redcap_api_token,
    'content'                : 'repeatingFormsEvents',
    'format'                 : 'json',
    'returnFormat'           : 'json',
})

print(response.status_code)
print(response.text)
