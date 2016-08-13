# auto-speedtest-log

Runs internet speed test and logs result to a file in csv format.
Logs date/time, ping, download speed and upload speed.

Integrated with Google Sheets API to automatically write the results to a Google Sheet.

Requires [speedtest-cli](https://github.com/sivel/speedtest-cli)

Also requires authentication to be set up. Guide available at [Python Quickstart | Google Sheets API](https://developers.google.com/sheets/quickstart/python)

## Usage
```
python auto_speedtest_logger.py
```
