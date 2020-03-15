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
    current_month = int(today.strftime("%m"))-1
    monthly_sum = sum(expenses[current_month].values())
    fig = pl.Figure(data=[
        pl.Bar(name=current_month-2, x=list(expenses[current_month-2].keys()), y=list(
                    expenses[current_month-2].values())),
        pl.Bar(name=current_month-1, x=list(expenses[current_month-1].keys()), y=list(
            expenses[current_month-1].values())),
        pl.Bar(name=current_month, x=list(expenses[current_month].keys()), y=list(
            expenses[current_month].values()))
    ],
        layout_title_text="Month: " + str(current_month) + " : " + str(monthly_sum) + " €")
    fig.write_html('graph.html', auto_open=True)
    # file_name = str(current_month) + "_expenses"
    # fig.write_image("images/" + file_name + ".png")
