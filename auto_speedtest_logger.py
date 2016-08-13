#!/usr/bin/env python

import argparse
import subprocess
import time
import os

from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

isp = 'Afrihost'
service = '20 Mbps ADSL2+'
service_number = '021 712 4225'


class SheetHandler(object):
    def __init__(self):
        self.SHEETS = self.connect_to_sheets()

        # check if a spreadsheet was already created
        if os.path.isfile('spreadsheetId.txt'):
            self.SPREADSHEET_ID = open('spreadsheetId.txt',
                                       'r').read().rstrip()
        else:
            spreadsheet_title = '{} {} - {}'.format(isp, service,
                                                    service_number)
            self.SPREADSHEET_ID = self.create_new_spreadsheet(
                spreadsheet_title)

            # store the spreadsheet id for future use
            with open('spreadsheetId.txt', 'w') as sheetid_file:
                sheetid_file.write(self.SPREADSHEET_ID)

            # create spreadsheet headings
            fields = ['Timestamp', 'Ping (ms)', 'Download (Mbps)',
                      'Upload (Mbps)']
            self.write_to_sheet(fields)

    def create_new_spreadsheet(self, spreadsheet_title):
        """
        Creates a new spreadsheet on the google drive
        :param: spreadsheet_title: title for the spreadsheet
        :return: spreadsheet_id
        """

        data = {'properties': {'title': spreadsheet_title}}
        res = self.SHEETS.spreadsheets().create(body=data).execute()
        spreadsheet_id = res['spreadsheetId']

        return spreadsheet_id

    @staticmethod
    def connect_to_sheets():
        """
        Establish a connection to Google Sheets
        and gain authorization
        :return: sheets service endpoint
        """

        scopes = 'https://www.googleapis.com/auth/spreadsheets'
        store = file.Storage('storage.json')
        credentials = store.get()
        if not credentials or credentials.invalid:
            flags = argparse.ArgumentParser(
                parents=[tools.argparser]).parse_args()
            flow = client.flow_from_clientsecrets('client_id.json', scopes)
            credentials = tools.run_flow(flow, store, flags)

        # create Sheets service endpoint
        sheets = discovery.build('sheets', 'v4',
                                 http=credentials.authorize(Http()))

        return sheets

    def write_to_sheet(self, data):
        """
        Write data to a spreadsheet
        :param: data: data to write to sheet
        :return: nothing
        """

        # data must be an array of arrays
        data = [data]

        data = {'values': [row for row in data]}

        self.SHEETS.spreadsheets().values().append(
            spreadsheetId=self.SPREADSHEET_ID, range='A1',
            body=data, valueInputOption='RAW').execute()

    def read_from_sheet(self):
        """
        Read data from a given spreadsheet
        :return: data read, as array of rows
        """

        rows = self.SHEETS.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range='Sheet1').execute().get('values', [])

        return rows

    def run_speedtest(self):
        """
        Run the speedtest and write the results to the Google Sheet
        :return: nothing
        """

        process = subprocess.Popen(
            '/usr/local/bin/speedtest-cli --simple'.split(),
            stdout=subprocess.PIPE)

        # timestamp
        start_time = time.strftime('%d-%m-%Y %H:%M:%S')

        output = process.communicate()[0]

        values = [value.split(' ')[1] for value in output.strip().split('\n')]
        values.insert(0, start_time)

        # write speedtest results to the spreadsheet
        self.write_to_sheet(values)

        # write to local file as debug
        with open('speedtest.log', 'a') as logfile:
            logfile.write(','.join(values) + '\n')


# main
# create object
speed_test_sheet = SheetHandler()

# run speed test
speed_test_sheet.run_speedtest()
