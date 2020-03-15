# This script read a chat on telegram and groups expenses (msg in the form {number string} ) by category and month

from __future__ import unicode_literals
from expUtils import get_month, add_expense, utc_to_local, load_codes, plot_data
import csv
from datetime import date
from telethon import TelegramClient, sync
from telethon import utils
from telethon import events
import sys
import os
import csv

import locale
locale.setlocale(locale.LC_TIME, "it_IT")  # swedish


# TODO list
# - should run once a day
# - generate a png instead of html
# - fix titles dimensions
# - deploy system


SEND_CHAT = False
CREATE_GRAPH = True
expenses = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
tot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


if __name__ == '__main__':

    # telegram app ids
    codes = load_codes()
    api_id = codes["api_id"]
    api_hash = codes["api_hash"]

    client = TelegramClient('session_name', api_id, api_hash).start()

    # client.disconnect()

    # GET ALL DIALOGS
    for dialog in client.get_dialogs(limit=10):
        print('>>> getting dialog', dialog.name)
    # client.disconnect()

    # WRITE HEADERS IN CSV
    with open('expenses.csv', mode='w+') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # header
        csv_writer.writerow(['Date', 'Time', 'Value', 'Type', 'Mod'])

    n = 0

    # ITER ON ALL MESSAGES & SUM ON CATEGORY
    for raw_msg in client.iter_messages('Spese'):  # no limits!
        if raw_msg is not None and raw_msg.message is not None:

            msg = raw_msg.message.split(' ')
            n += 1
            # print(n, '-', msg)
            correct_date = utc_to_local(raw_msg.date).strftime('%x')
            correct_time = utc_to_local(raw_msg.date).strftime('%X')

            # if not current year stop return
            if (raw_msg.date.year < date.today().year):
                break
            # sanity check
            if len(msg) < 2 or not msg[0].isdigit():
                continue
            # write row in csv
            with open('expenses.csv', mode='a+') as out_file:
                csv_writer = csv.writer(
                    out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(
                    [correct_date, correct_time, msg[0], msg[1]])

            value = float(msg[0])
            type = msg[1]
            if len(msg) > 2:
                mod = msg[2]

            add_expense(type, value, correct_date, expenses)

    # SUM FROM MONTHS
    for month in range(0, 12):
        month_exp = expenses[month]
        print('>>> ', month)
        for item in month_exp:
            out_msg = item + ' : ' + str(month_exp[item])
            # if SEND_CHAT:
            #     client.send_message("Spese", out_msg)
            tot[month] += month_exp[item]
        print(tot[month])


# PLOT DATA
if CREATE_GRAPH:
    plot_data(expenses)

# SEND PLOT TO CHAT
if SEND_CHAT:
    # client.send_message("Spese", file='images/graph.png')
    client.send_message("Spese", file='graph.html')

print(' ### DONE ### ')
