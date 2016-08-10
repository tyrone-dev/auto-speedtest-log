#!/usr/bin/env python

import subprocess
import time

process = subprocess.Popen('/usr/local/bin/speedtest-cli --simple'.split(),
        stdout=subprocess.PIPE)

start_time = time.strftime('%d-%m-%Y %H:%M:%S')

output = process.communicate()[0]

values = [value.split(' ')[1] for value in output.strip().split('\n')]
values.insert(0, start_time)

with open('speedtest.log', 'a') as logfile:
    logfile.write(','.join(values) + '\n')
