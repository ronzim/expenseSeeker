import json
from datetime import date, datetime, timezone
import plotly.graph_objects as pl


def get_month(date):
    return int(date.split('/')[1])


def add_expense(type, val, date, expenses):
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


def plot_data(expenses):
    today = date.today()
    data = []
    # add months data
    for month in range(0, 12):
        bar = pl.Bar(name=month, x=list(expenses[month].keys()), y=list(
            expenses[month].values()))
        data.append(bar)

    fig = pl.Figure(data)
    fig.write_html('graph.html', auto_open=True)
