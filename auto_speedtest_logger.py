#!/usr/bin/env python

import argparse
import subprocess
import time

from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

isp = 'test'
service = 'fibre'
service_number = 'null'

sheet_title = '{} {} - {}'.format(isp, service, service_number)

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('storage.json')
credentials = store.get()
if not credentials or credentials.invalid:
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
    credentials = tools.run_flow(flow, store, flags)

SHEETS = discovery.build('sheets', 'v4', http=credentials.authorize(Http()))
data = {'properties': {'title': sheet_title}}
res = SHEETS.spreadsheets().create(body=data).execute()
SHEET_ID = res['spreadsheetId']

print 'Created {}'.format(res['properties']['title'])

FIELDS = ('Timestamp', 'Ping (ms)', 'Download (Mbps)', 'Upload (Mbps)')

process = subprocess.Popen('/usr/local/bin/speedtest-cli --simple'.split(),
        stdout=subprocess.PIPE)

start_time = time.strftime('%d-%m-%Y %H:%M:%S')

output = process.communicate()[0]

values = [value.split(' ')[1] for value in output.strip().split('\n')]
values.insert(0, start_time)

with open('speedtest.log', 'a') as logfile:
    logfile.write(','.join(values) + '\n')

values = [tuple(values)]
values.insert(0, FIELDS)
data = {'values': [row for row in values]}

SHEETS.spreadsheets().values().update(spreadsheetId=SHEET_ID, range='A1',
        body=data, valueInputOption='RAW').execute()

print 'Wrote data to Sheet:'

rows = SHEETS.spreadsheets().values().get(spreadsheetId=SHEET_ID,
range='Sheet1').execute().get('values', [])
for row in rows:
    print row


