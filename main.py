from __future__ import unicode_literals
from expUtils import get_month, add_value, utc_to_local, load_codes, plot
import csv
from datetime import date
from telethon import TelegramClient, sync
from telethon import utils
from telethon import events
import sys
import os
import csv
import locale
import argparse
locale.setlocale(locale.LC_TIME, "it_IT")  # swedish

SEND_CHAT = False
CREATE_GRAPH = True
expenses = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
incomes = [{'entrate': 0}, {'entrate': 0}, {'entrate': 0}, {
    'entrate': 0}, {'entrate': 0}, {'entrate': 0}, {'entrate': 0}, {'entrate': 0}, {'entrate': 0}, {'entrate': 0}, {'entrate': 0}, {'entrate': 0}]
tot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def parse_row(row):
    tag = 0
    row[2] = row[2].replace('.', '')
    row[2] = row[2].replace(',', '.')
    val = float(row[2])
    descr = row[4].lower()
    if "enel energia" in descr:
        tag = "bollette"
    elif "a2a spa" in descr:
        tag = "bollette"
    elif "condominio" in descr:
        tag = "condominio"
    elif "bonifica" in descr:
        tag = "bollette"
    elif "7873" in descr:
        tag = "prepagata"
    elif "findomestic" in descr:
        tag = "rata_auto"
    elif "telepass" in descr:
        tag = "telepass"
    elif "comm" in descr:
        tag = "commissioni_banca"
    elif "imposta di bollo" in descr:
        tag = "tasse"
    elif "agenzia entrate" in descr:
        tag = "tasse"
    elif "f24-web" in descr:
        tag = "tasse"
    elif "mutuo" in descr:
        tag = "mutuo"
    elif "nexi" in descr:
        tag = "nexi"
    elif "pagam. diversi" in descr:
        tag = "vodafone?"
    elif ("prel.bancomat" in descr) or ("prel.sport" in descr):
        tag = "prelievi"
    elif ("bancomat" in descr) or ("pag.pos" in descr):
        tag = "pag.bancomat"
    elif val > 0:
        tag = "entrate"
    else:
        tag = "altro"

    return tag, val


def parseAccountFile(csv_file_path):
    print('Parsing')
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                category, value = parse_row(row)

                if category == 0:
                    continue

                date = row[0]
                # TODO compare with today instead of hardcoded year

                if int(date.split('/')[2]) < 2020:
                    continue

                if (category == "entrate"):
                    add_value(category, value, date, incomes)
                else:
                    add_value(category, -value, date, expenses)

                line_count += 1
                if (category == "altro"):
                    print(row[4])
                    input(category)
                print(f'Processed {line_count} lines.')

    # print(expenses)
    # if (CREATE_GRAPH):
    #     plot_data(expenses)

    return


def parseChat():
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

    # PLOT DATA
    # if CREATE_GRAPH:
    #     plot_data(expenses)

    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Parse data')

    parser.add_argument('--csv', action='store', help='')
    parser.add_argument('--parseChat', action='store_true', help='')
    parser.add_argument('--parseFile', action='store_true', help='')
    parser.add_argument('--parseAll', action='store_true', help='')
    parser.add_argument('--render_graph', action='store_true', help='')

    args = parser.parse_args()

    if((args.parseFile or args.parseAll) and not args.csv):
        sys.exit(print('no file to parse'))

    if (args.parseFile):
        parseAccountFile(args.csv)
    elif (args.parseChat):
        parseChat()
    elif (args.parseAll):
        parseAccountFile(args.csv)
        parseChat()

    # SUM FROM MONTHS
    for month in range(0, 12):
        month_exp = expenses[month]
        for item in month_exp:
            out_msg = item + ' : ' + str(month_exp[item])
            # if SEND_CHAT:
            #     client.send_message("Spese", out_msg)
            tot[month] += month_exp[item]
        print('Month: \t', month, '\t', tot[month], incomes[month]['entrate'])

    all_keys = set().union(*(d.keys() for d in expenses))
    cat_sum = dict.fromkeys(all_keys)
    for key in all_keys:
        cat_sum[key] = 0
        for month_exp in expenses:
            if (key in month_exp.keys()):
                cat_sum[key] += month_exp[key]

    print(cat_sum)

    # PLOT DATA
    if args.render_graph:
        plot(incomes, expenses, tot)

    # # SEND PLOT TO CHAT
    # if SEND_CHAT:
    #     # client.send_message("Spese", file='images/graph.png')
    #     client.send_message("Spese", file='graph.html')

    print(' ### DONE ### ')
