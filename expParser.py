import csv

from expUtils import add_expense, plot_data

file_content = []

expenses = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
tot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def parse_row(row):
    # TODO if row[2] contains "," remove it before casting to float
    tag = 0
    descr = row[4].lower()
    if "enel" in descr:
        tag = "bollette"
    elif "a2a" in descr:
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

    val = -float(row[2])
    return tag, val


with open('movimentiConto.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            # print(f'\t{row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]}')
            type, value = parse_row(row)

            if type == 0:
                continue

            date = row[0]
            # # TODO compare with today instead of hardcoded year
            if int(date.split('/')[2]) < 2020:
                continue
            add_expense(type, value, date, expenses)
            line_count += 1
            file_content.append(row)

    print(f'Processed {line_count} lines.')

print(expenses)
plot_data(expenses)
