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
run:
    venv/bin/python check_prices.py
"""


import sys
import datetime
from config import *
from time import sleep
from client import Client

arg = sys.argv[1:]
curr = arg[0] if len(arg) > 0 else None
if curr == 'cn':
    from config import TICKERS_CN as TICKERS
elif curr == 'ru':
    from config import TICKERS_RU as TICKERS
elif curr == 'en':
    from config import TICKERS_EN as TICKERS
else:
    from config import TEST_TICKERS as TICKERS


if len(TICKERS)%3 > 0:
    print('ERR: tickers length:', len(TICKERS))
    sys.exit()

sp = int(len(TICKERS)/3)
T1=TICKERS[:sp]; T2=TICKERS[sp:sp*2]; T3=TICKERS[sp*2:]
TICKERS=[]
for i in range(len(T1)):
    TICKERS+=([T1[i]]+[T2[i]]+[T3[i]])


def main():

    """
    date: rfc 3339
    TODO print sum, save data to csv file
    date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=QUART)).strftime('%Y-%m-%dT%H:%M:%SZ')
    date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    """

    if len(TICKERS)%3 > 0:
        print('ERR: tickers length:', len(TICKERS))
        return

    client = Client(TOKEN)

    date_from = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=QUART)).strftime('%Y-%m-%dT%H:%M:%SZ')
    date_to = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    print('Client: date from:', date_from, 'to:', date_to)

    my_shares = client.get_my_shares(client.get_shares(), TICKERS)

    while True:
        try:
            date_to = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            my_shares = client.get_candles(my_shares, date_from, date_to)
            date_check = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT')

            my_shares = client.get_prices(my_shares)
            my_shares = client.get_avearage(my_shares, QUART, MONTH, WEEK)
            client.print_table(my_shares)
            try:
                sleep(LOOP_INTERVAL)
            except KeyboardInterrupt:
                print('Interrupted')
                sys.exit(0)
        except Exception as e:
            print('ERR:', e)
            sleep(9)


def test_main():

    client = Client(TOKEN)
    #print(client.open_acc())
    #print(client.get_acc())
    #print(client.close_acc())

    #shares = client.get_shares()
    #assert client.get_my_shares(shares, TEST_TICKERS) == TEST_MY_SHARES
    #assert client.get_candles(TEST_MY_SHARES, TEST_DATE_FROM, TEST_DATE_TO) == TEST_MY_CANDLES
    assert client.get_avearage(TEST_MY_CANDLES, TEST_QUART, TEST_MONTH, TEST_WEEK) == TEST_MY_AVEARAGE
    #assert client.print_table(TEST_MY_AVEARAGE) == True


if __name__ == "__main__":
    main()



















