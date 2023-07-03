#!/usr/bin/env python3
# 29may23 hjltu@ya.ru
# Copyright (c) 2023 hjltu

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
about:

install:
    sudo apt install python3-venv python3-pip
    python3 -m venv venv
    venv/bin/pip install --upgrade pip
    venv/bin/pip install requests tabulate pytest
test:
    venv/bin/pytest -s check_prices.py
    venv/bin/pytest -s -k shares check_prices.py
run:
    venv/bin/python check_prices.py
"""


import sys
import datetime
from config import *
from time import sleep
from client import Shares, Currencies


def main():

    """
    date: rfc 3339
    TODO print sum, save data to csv file
    date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=QUART)).strftime('%Y-%m-%dT%H:%M:%SZ')
    date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    """

    date_from = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=LONG)).strftime('%Y-%m-%dT%H:%M:%SZ')
    date_to = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    print('Client: date from:', date_from, 'to:', date_to)
    client, TICKERS, curr = sort_tickers_list()
    my_instruments = client.get_my_instruments(client.get_all(), TICKERS)
    my_candles = client.get_candles(my_instruments, date_from, date_to)

    while True:
        try:
            date_check = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            if date_check not in date_to:
                date_from = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=LONG)).strftime('%Y-%m-%dT%H:%M:%SZ')
                date_to = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
                print('Client: new date from:', date_from, 'to:', date_to)
                my_candles = client.get_candles(my_instruments, date_from, date_to)

            my_prices = client.get_prices(my_candles)
            my_avearages = client.get_avearage(my_prices, LONG, MID, SHORT)
            client.print_table(my_avearages)
            client.save_avearages(my_avearages, filename=f'{DIR_DATA}/avearage_{curr}.csv')
            try:
                sleep(LOOP_INTERVAL)
            except KeyboardInterrupt:
                print('Interrupted')
                sys.exit(0)
        except Exception as e:
            print('ERR:', e)
            sleep(9)


def test_main():
    pass

    #client = Client(TOKEN)
    #print(client.open_acc())
    #print(client.get_acc())
    #print(client.close_acc())


    #assert sort_tickers_list() == (TEST_TICKERS, None)
    #shares = client.get_shares(f'{DIR_DATA}/all_shares.json')
    #assert client.get_my_shares(shares, TEST_TICKERS) == TEST_MY_SHARES
    #assert client.get_candles(TEST_MY_SHARES, TEST_DATE_FROM, TEST_DATE_TO) == TEST_MY_CANDLES
    #assert client.get_avearage(TEST_MY_CANDLES, TEST_QUART, TEST_MONTH, TEST_WEEK) == TEST_MY_AVEARAGE
    #assert client.print_table(TEST_MY_AVEARAGE) == True


def test_shares():

    client, TICKERS, curr = sort_tickers_list(TEST_SHARES_TICKERS)
    client = Shares(TOKEN)
    all_shares = client.get_all()
    my_shares = client.get_my_instruments(all_shares, TICKERS)
    my_candles = client.get_candles(my_shares, TEST_DATE_FROM, TEST_DATE_TO)
    my_candles = client.get_prices(my_candles)
    my_avearages = client.get_avearage(my_candles, TEST_QUART, TEST_MONTH, TEST_WEEK)
    client.print_table(my_avearages)
    client.save_avearages(my_avearages, filename=f'{DIR_DATA}/avearage_{curr}.csv')


def test_pairs():

    client, TICKERS, curr = sort_tickers_list(TEST_PAIRS_TICKERS)
    client = Currencies(TOKEN)
    all_pairs = client.get_all()
    #all_pairs = client.get_all(f'{DIR_DATA}/all_currencies.json')
    my_pairs = client.get_my_instruments(all_pairs, TICKERS)
    my_candles = client.get_candles(my_pairs, TEST_DATE_FROM, TEST_DATE_TO)
    my_prices = client.get_prices(my_candles)
    my_avearages = client.get_avearage(my_prices, TEST_QUART, TEST_MONTH, TEST_WEEK)
    client.print_table(my_avearages)
    client.save_avearages(my_avearages, filename=f'{DIR_DATA}/avearage_{curr}.csv')


def sort_tickers_list(tickers=None):

    arg = sys.argv[1:]
    curr = arg[0] if len(arg) > 0 else None

    if curr == 'cn':
        client = Shares(TOKEN)
        TICKERS = TICKERS_CN
    elif curr == 'ru':
        client = Shares(TOKEN)
        TICKERS = TICKERS_RU
    elif curr == 'en':
        client = Shares(TOKEN)
        TICKERS = TICKERS_EN
    elif curr == 'pairs':
        client = Currencies(TOKEN)
        TICKERS = TICKERS_PAIRS
    elif curr == 'quick':
        client = Shares(TOKEN)
        TICKERS = TICKERS_QUICK
    else:
        client = None
        curr = 'test'
        TICKERS = tickers

    if len(TICKERS)%3 > 0:
        print('WARN: tickers length:', len(TICKERS))

    sp = int(len(TICKERS)/3)
    T1=TICKERS[:sp]; T2=TICKERS[sp:sp*2]; T3=TICKERS[sp*2:]
    TICKERS=[]

    for i in range(len(T1)):
        TICKERS+=([T1[i]]+[T2[i]]+[T3[i]])

    return (client, TICKERS, curr)


if __name__ == "__main__":

    main()



















