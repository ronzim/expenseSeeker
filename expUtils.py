import json
from datetime import date, datetime, timezone
import plotly.graph_objects as pl
from plotly.subplots import make_subplots


def get_month(date):
    return int(date.split('/')[1])


def add_value(type, val, date, container):
    month_n = get_month(date)
    if type in list(container[month_n-1].keys()):
        container[month_n-1][type] += val
        new = False
    else:
        container[month_n-1][type] = val
        new = True
    return new


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def load_codes():
    with open('codes.json', 'r') as f:
        codes = json.load(f)
    return codes


month_names = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu',
               'lug', 'ago', 'set', 'ott', 'nov', 'dic']


def plot_data(fig, expenses):
    today = date.today()
    data = []
    # add months data
    for month in range(0, 12):
        bar = pl.Bar(name=month_names[month], x=list(expenses[month].keys()), y=list(
            expenses[month].values()))
        # data.append(bar)
        fig.add_trace(bar, row=1, col=1)
    return data


def plot_balance(fig, incoming_list, outcoming):
    data = []
    # add months data
    line1 = pl.Scatter(name='entrate', mode='lines+markers', x=month_names,
                       y=incoming_list)
    line2 = pl.Scatter(name='uscite', mode='lines+markers',
                       x=month_names, y=outcoming)
    bar = pl.Bar(name='balance', x=month_names, y=[
                 incoming_list - outcoming for (incoming_list, outcoming) in zip(incoming_list, outcoming)])
    fig.add_trace(line1, row=1, col=2)
    fig.add_trace(line2, row=1, col=2)
    fig.add_trace(bar, row=1, col=2)
    return data


def plot_prevision(fig, incoming_list, outcoming):
    balance = [incoming_list -
               outcoming for (incoming_list, outcoming) in zip(incoming_list, outcoming)]

    # remove jan for 2020
    balance = balance[1:12]

    balance_sum = []
    balance_mean = 0
    limit = None

    for n in range(0, len(balance)):
        if balance[n] == 0 and not limit:
            limit = n
            balance_mean = sum(balance[:limit]) / len(balance[:limit])
        if n == 0:
            balance_sum.append(balance[n])
        elif limit and n >= limit:
            balance_sum.append(balance_mean + balance_sum[n-1])
        else:
            balance_sum.append(balance[n] + balance_sum[n-1])

    line1 = pl.Scatter(name='ok', mode='lines+markers',
                       x=month_names[0:limit+1], y=balance_sum[0:limit+1], line=dict(color='royalblue', width=1))
    line2 = pl.Scatter(name='previsione', mode='lines+markers',
                       x=month_names[limit:len(balance)], y=balance_sum[limit:len(balance)], line=dict(color='royalblue', width=1, dash='dash'))
    fig.add_trace(line1, row=2, col=1)
    fig.add_trace(line2, row=2, col=1)


def plot(incoming, expenses, outcoming):
    incoming_list = list(d['entrate'] for d in incoming)

    fig = make_subplots(rows=2, cols=2, specs=[[{}, {}],
                                               [{"colspan": 2}, None]],
                        subplot_titles=("Andamento spese", "Entrate/Uscite", "Previsione"))
    plot_data(fig, expenses)
    plot_balance(fig, incoming_list, outcoming)
    plot_prevision(fig, incoming_list, outcoming)
    fig.write_html('./html/graph.html', auto_open=True)
