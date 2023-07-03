#!/usr/bin/env python3


"""
https://www.w3schools.com/python/matplotlib_plotting.asp

install:
    for rpi: sudo apt install python-dev libatlas-base-dev libopenjp2-7 libtiff5
    python3 -m venv venv
    venv/bin/pip install --upgrade pip
    venv/bin/pip install matplotlib numpy
run:
    venv/bin/python stat.py file.csv
"""


import os, sys, time, csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from itertools import cycle


DATA_PATH = 'data/'
GRAPH_PATH = 'plots/'


def main(csv_file):

    rows = get_rows(csv_file)
    table = get_table(rows)
    print_graph(table, csv_file)


def get_rows(csv_file):

    print('open',csv_file)
    try:
        with open(csv_file, 'r') as f:
            rows = [row.rstrip().split(',') for row in f]
    except Exception as e:
        print('ERR:', e)

    #print(rows[:2])

    return rows


def get_table(rows):

    """ output:
        {
            ticker: [
                {epoch, time, price, long, mid, short},
                ...],
            next ticker: [] ...
        }
    """

    print('prepare table')

    table = {}

    for row in rows[1:]:

        for r in range(1, len(row)):
            if '#' in row[r]:

                if not table.get(row[r+1]):
                    table.update({row[r+1]: []})

                table.get(row[r+1]).append({
                    'epoch': row[0],
                    'time': row[1],
                    'price': row[r+2],
                    'long': float(row[r+3]),
                    'mid': float(row[r+5]),
                    'short': float(row[r+7])})

    #print(table)

    return table


def print_graph(table, csv_file):

    print('drawing graph')
    fig = plt.figure(figsize=(33, 22), dpi=80)
    fig.patch.set_facecolor('tan')
    plt.rcParams['axes.facecolor'] = 'silver'
    plt.title('Procents long, mid, short')

    cycol = cycle(colors.cnames.keys())
    cycol = cycle(['blue','orange','green','red','brown','pink','olive','cyan','magenta','gold','beige','lime','violet','skyblue'])

    proc_min = 10
    proc_max = 10
    ymax = 33
    num = len(table)
    for ticker, data in table.items():
        try:
            fig = plt.figure(figsize=(22, 11), dpi=80, num=1, clear=True)
            fig.patch.set_facecolor('tan')
            plt.rcParams['axes.facecolor'] = 'silver'
            plt.title(f'{ticker} {data[-1].get("price")} Procents long, mid, short')
            times = [d.get('time') for d in data]
            _long = [d.get('long') if abs(d.get('long')) < ymax else None for d in data]
            mid = [d.get('mid') if abs(d.get('mid')) < ymax else None for d in data]
            short = [d.get('short') if abs(d.get('short')) < ymax else None for d in data]
            label_long = ticker + ' ' + str(_long[-1])
            label_mid = ticker + ' ' + str(mid[-1])
            label_short = ticker + ' ' + str(short[-1])
            color = next(cycol)
            #p_fix = [i for i in p if isinstance(i, int)]
            #p_fix = [int(i) for i in p if isinstance(i, float) ]
            #proc_min = min(p_fix) if min(p_fix) < proc_min else proc_min
            #proc_max = max(p_fix) if max(p_fix) > proc_max else proc_max
            plt.plot(times, [0]*len(times), color='black', linewidth=3, linestyle='dotted')
            plt.plot(times, _long, color=color, label=label_long, linewidth=1, linestyle=':')
            plt.plot(times, mid, color=color, label=label_mid, linewidth=2, linestyle='--')
            plt.plot(times, short, color=color, label=label_short, linewidth=3, marker='o', markevery=int(len(data)/9)+1)

            if len(times) > 9:
                plt.xticks([times[i] for i in range(0, len(times), int(len(times)/5))])
            #plt.yticks([p for p in range(proc_min, proc_max+1)])
            plt.grid(color = 'grey', linestyle = '--', linewidth = 0.5)
            plt.tick_params(left=True, right=True)
            plt.tick_params(labelleft=True, labelright=True)
            plt.legend(loc='center left')

            name = os.path.basename(csv_file).split('.')[0]
            graph_name = f'{GRAPH_PATH}draw_{name}_{ticker}.png'
            plt.savefig(graph_name)
            print('saved', graph_name)
        except Exception as e:
            print(e, ticker, len(data))


if __name__ == '__main__':
    main(sys.argv[1:][0])
