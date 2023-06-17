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
    venv/bin/pytest -s check_portfolio.py
    venv/bin/pytest -s -k shares check_portfolio.py
run:
    venv/bin/python check_portfolio.py
"""


import sys
import datetime
from config import *
from time import sleep
from client import Client


def main():

    """
    """

    while True:
        try:
            pass
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


def test_get_portfolio():

    client = Client(TOKEN_REAL)
    portfolio = client.get_portfolio(ACCOUNT_ID)
    #all_shares = client.get_all_shares()
    #all_etfs = client.get_all_etfs()
    #all_currencies = client.get_all_currencies()
    all_assets = client.get_all_assets()
    #all_assets = client.get_all_assets(f'{DIR_DATA}/assets.json')
    client.print_portfolio(portfolio, assets=all_assets)
    #client.save_json(portfolio, f'{DIR_DATA}/portfolio.json')


if __name__ == "__main__":

    main()



















