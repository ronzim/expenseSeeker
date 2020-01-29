from __future__ import unicode_literals
import csv
import json
from datetime import date
from telethon import TelegramClient, sync
from telethon import utils
from telethon import events
import sys
import os
import csv
import plotly.graph_objects as pl
from datetime import datetime, timezone

# TODO list
# - should run once a day
# - generate a png instead of html
# - fix titles dimensions
# - deploy system


SEND_CHAT = True
CREATE_GRAPH = True

expenses = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]


def get_month(date):
    return int(date.split('/')[0])


def add_expense(type, val, date):
    month_n = get_month(date)
    if type in list(expenses[month_n-1].keys()):
        expenses[month_n-1][type] += val
        new = False
    else:
        expenses[month_n-1][type] = val
        new = True
    return new


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def load_codes():
    with open('codes.json', 'r') as f:
        codes = json.load(f)
    return codes


if __name__ == '__main__':

    # telegram app ids
    codes = load_codes()
    api_id = codes["api_id"]
    api_hash = codes["api_hash"]

    client = TelegramClient('session_name', api_id, api_hash).start()

    # client.disconnect()

    for dialog in client.get_dialogs(limit=10):
        print('>>> getting dialog', dialog.name)
    # client.disconnect()
    print(' ### DONE ### ')

    # write into csv
    with open('expenses.csv', mode='w+') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # header
        csv_writer.writerow(['Date', 'Time', 'Value', 'Type', 'Mod'])

    n = 0

    # iter on all messages
    for raw_msg in client.iter_messages('Spese'):  # no limits!
        if raw_msg is not None and raw_msg.message is not None:

            msg = raw_msg.message.split(' ')
            n += 1
            print(n, '-', msg)
            correct_date = utc_to_local(raw_msg.date).strftime('%x')
            correct_time = utc_to_local(raw_msg.date).strftime('%X')

            if len(msg) < 2 or not msg[0].isdigit():
                continue

            with open('expenses.csv', mode='a+') as out_file:
                csv_writer = csv.writer(
                    out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(
                    [correct_date, correct_time, msg[0], msg[1]])

            value = float(msg[0])
            type = msg[1]
            if len(msg) > 2:
                mod = msg[2]

            print(type, value)
            add_expense(type, value, correct_date)

    print('\n ---- PARTIAL ----')
    tot = 0

    for month in range(0, 12):
        month_exp = expenses[month]
        for item in month_exp:
            out_msg = item + ' : ' + str(month_exp[item])
            # if SEND_CHAT:
            #     client.send_message("Spese", out_msg)
            tot += month_exp[item]

    print('\n ---- TOTAL ----')
    print(tot, '€')
    out_msg = 'total: ' + str(tot)

    today = date.today()
    current_month = int(today.strftime("%m"))-1

if CREATE_GRAPH:
    monthly_sum = sum(expenses[current_month].values())
    fig = pl.Figure(data=pl.Bar(
        x=list(expenses[current_month].keys()), y=list(expenses[current_month].values())),
        layout_title_text="Month: " + str(current_month) + " : " + str(monthly_sum) + " €")
    fig.write_html('graph.html', auto_open=True)
    # file_name = str(current_month) + "_expenses"
    # fig.write_image("images/" + file_name + ".png")

if SEND_CHAT:
    # client.send_message("Spese", file='images/graph.png')
    client.send_message("Spese", file='graph.html')
