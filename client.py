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
    rest client for invest API
links:
    https://tinkoff.github.io/investAPI/swagger-ui/#/
"""


import csv
import time
import json
import requests
from os.path import exists
from tabulate import tabulate
from statistics import median, mean
from config import Style


#sandbox
URL_OPEN_SB_ACC = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.SandboxService/OpenSandboxAccount'
URL_GET_SB_ACC = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.SandboxService/GetSandboxAccounts'
URL_CLOSE_SB_ACC = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.SandboxService/CloseSandboxAccount'
#users
URL_GET_ACC = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.UsersService/GetAccounts'
URL_GET_PORTFOLIO = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.OperationsService/GetPortfolio'
#instruments
URL_GET_SHARES = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.InstrumentsService/Shares'
URL_GET_ETFS = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.InstrumentsService/Etfs'
URL_GET_CURRENCIES = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.InstrumentsService/Currencies'
URL_GET_ASSETS = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.InstrumentsService/GetAssets'
#market
URL_GET_CANDLES = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.MarketDataService/GetCandles'
URL_GET_LAST_PRICES = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices'
CANDLES_INTERVAL = 'CANDLE_INTERVAL_DAY'


class Client(object):

    def __init__(self, TOKEN):

        if TOKEN:
            print('Client init...')
            self.acc = None
            self.headers = { 'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN }


    def post_request(self, url, headers={}, data={}):

        code, response = None, None
        try:
            res = requests.post(url, headers=headers, data=json.dumps(data, indent=4))
            code, response = res.status_code, json.loads(res.text)
            if code == 200:
                return response
            else:
                print('Client WARN:', code, response)
        except Exception as e:
            print('Client ERR:', code, response, e)


    def open_sb_acc(self):

        if not self.acc:
            self.acc = self.post_request(URL_OPEN_SB_ACC, headers=self.headers)
        return self.acc


    def get_acc(self, sandbox=False):
        if sandbox:
            return self.post_request(URL_GET_SB_ACC, headers=self.headers)
        else:
            return self.post_request(URL_GET_ACC, headers=self.headers)


    def close_sb_acc(self):

        """
        request data:
            {"accountId": "string"}
        """

        if self.acc:
            self.post_request(URL_CLOSE_SB_ACC, headers=self.headers, data=self.acc)
            self.acc = None
        return self.get_acc()


    def get_portfolio(self, acc_id, curr='USD'):

        """ request body:
                {"accountId": "string",
                "currency": "RUB"}
        """

        data = {"accountId": acc_id, "currency": curr}

        return self.post_request(URL_GET_PORTFOLIO, headers=self.headers, data=data)


    def print_portfolio(self, portfolio: dict, assets=None,
        shares=None, bonds=None, etfs=None, currencies=None, futures=None):


        """ output:
            title:
                totals
            row:
                ticker, currency, price/average_price, quantity/lots, yield_by_lot, name
        """

        total_shares = self._concat(portfolio.get('totalAmountShares').get('units'), portfolio.get('totalAmountShares').get('nano'))
        total_bonds = self._concat(portfolio.get('totalAmountBonds').get('units'), portfolio.get('totalAmountBonds').get('nano'))
        total_etfs = self._concat(portfolio.get('totalAmountEtf').get('units'), portfolio.get('totalAmountEtf').get('nano'))
        total_currencies = self._concat(portfolio.get('totalAmountCurrencies').get('units'), portfolio.get('totalAmountCurrencies').get('nano'))
        total_futures = self._concat(portfolio.get('totalAmountFutures').get('units'), portfolio.get('totalAmountFutures').get('nano'))
        total_sum = total_shares + total_bonds + total_etfs + total_currencies + total_futures
        total_yield = self._concat(portfolio.get('expectedYield').get('units'), portfolio.get('expectedYield').get('nano'))

        total = \
            f'{Style.LIGHT_BLUE}{Style.BOLD}Total: shares: {total_shares:g},' + \
            f' etfs: {total_etfs:g}, curr: {total_currencies:g}, Sum: {total_sum}, Yield: {total_yield:g}{Style.RESET}'
        print(total)
        self._sort_portfolio(assets, portfolio, 'usd')
        self._sort_portfolio(assets, portfolio, 'rub')
        self._sort_portfolio(assets, portfolio, 'hkd')
        print(total)
        return True


    def _sort_portfolio(self, assets, portfolio, curr):

        line_color = Style.YELLOW
        table = [['ticker', 'quant', 'yield', 'price', 'average', 'name']]
        assets = [ a for a in assets.get('assets') if a.get('instruments') ]

        for a in assets:
            for p in portfolio.get('positions'):
                if a.get('instruments') and p.get('currentPrice').get('currency') == curr:
                    for i in a.get('instruments'):
                        if i.get('figi') == p.get('figi') and p.get('currentPrice').get('currency') == curr:
                            row = [
                                f'{line_color}' + i.get('ticker')[:6],
                                p.get('quantity').get('units'),
                                str(self._concat(p.get('expectedYield').get('units'), p.get('expectedYield').get('nano')))[:6],
                                str(self._concat(p.get('currentPrice').get('units'), p.get('currentPrice').get('nano')))[:6],
                                str(self._concat(p.get('averagePositionPrice').get('units'), p.get('averagePositionPrice').get('nano')))[:6],
                                a.get('name')[:55] + f'{Style.RESET}']
                            table.append(row)
                            line_color = Style.YELLOW if line_color is Style.WHITE else Style.WHITE
        print(tabulate(table))

        return True


    def get_all_instruments(self, url, filename=None, data=None):

        """
        request data:
            {"instrumentStatus": "INSTRUMENT_STATUS_UNSPECIFIED"}

        output:
            [{
                "figi": "BBG000BQVTF5",
                "ticker": "PCAR",
                "uid": "",
            }]
        """

        if not data:
            data = {"instrumentStatus": "INSTRUMENT_STATUS_UNSPECIFIED"}

        all_instruments = self.post_request(url, headers=self.headers, data=data)

        if all_instruments.get('instruments'):
            print('Client: all instruments length is:', len(all_instruments.get('instruments')))

        if all_instruments.get('assets'):
            print('Client: all assets length is:', len(all_instruments.get('assets')))

        if filename:
            self.save_json(all_instruments, filename)

        return all_instruments


    def get_my_instruments(self, instruments, tickers):

        """
        """

        my_instruments = []

        for t in tickers:
            for i in instruments.get('instruments'):
                if t == i.get('ticker'):
                    my_instruments.append({
                        'ticker': t,
                        'figi': i.get('figi'),
                        'uid': i.get('uid'),
                        'lot': i.get('lot'),
                        'nominal': self._concat(i.get('nominal').get('units'), i.get('nominal').get('nano'))
                        })

        print('Client: my instruments length is:', len(my_instruments))


        return my_instruments


    def get_candles(self, my_instruments, date_from, date_to):

        """
        Add candles to shares

        request data:
            {
                "figi": "string",
                "from": "2023-05-31T15:05:27.453Z",
                "to": "2023-05-31T15:05:27.453Z",
                "interval": "CANDLE_INTERVAL_UNSPECIFIED",
                "instrumentId": "string"
            }
        """

        for s in my_instruments[:]:

            data = {
                'figi': s.get('figi'),
                'from': date_from,
                'to': date_to,
                'interval': CANDLES_INTERVAL,
                'instrumentId': s.get('uid')}

            candles = self.post_request(URL_GET_CANDLES, headers=self.headers, data=data)
            s.update(candles)

        return my_instruments


    def get_prices(self, my_prices):

        """
        request body:
            {
            "figi": ["string"],
            "instrumentId": ["string"]
            } """

        figi, uid = [], []

        for s in my_prices[:]:
            figi.append(s.get('figi'))
            uid.append(s.get('uid'))

        data = {
                'figi': figi,
                'instrumentId': uid}

        prices = self.post_request(URL_GET_LAST_PRICES, headers=self.headers, data=data)

        #print(json.dumps(prices, indent=4))

        for instrument in my_prices[:]:
            for price in prices.get('lastPrices'):
                if price.get('figi') == instrument.get('figi'):
                    instrument.update({'last_price': price})

        return my_prices


    def is_file_exists(self, filename):

        return exists(filename)


    def save_json(self, data, filename='data.json', mode='w'):

        with open(filename, mode,  encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        return True


    def save_csv(self, row, filename='data.csv', mode='w'):

        with open(filename, mode,  encoding='utf-8') as csv_file:
            csv_file.write(row)

        return True


    def _concat(self, units, nano):

        """ nano length = 9 """

        rank = 0.000000001

        return int(units) + nano * rank


    def get_avearage(self, my_candles, quart: int, month: int, week: int):

        """ Avearage price for quart, month, week
        output:
            {avearage: {
                'quart_proc': float, 'quart_diff': float,
                'month_proc': float, 'month_diff': float,
                'week_proc': float, 'week_diff': float }} """

        for instrument in my_candles[:]:

            avearage = {}

            for key, val in {'quart':quart, 'month':month, 'week':week}.items():

                candles = instrument.get('candles')[-val:]
                last_price = instrument.get('last_price')
                lot = instrument.get('lot')
                nominal = instrument.get('nominal')
                avearage.update(self._calc_avearage(key, candles, last_price, lot, nominal))

            instrument.update({'avearage': avearage})

        return my_candles


    def _calc_avearage(self, name, candles, last_price, lot, nominal):

        #close = self._concat(last_price.get('price').get('units'), last_price.get('price').get('nano'))

        if last_price.get('price'):
            close = self._concat(last_price.get('price').get('units'), last_price.get('price').get('nano'))
        elif len(candles) > 0:
            close = self._concat(candles[-1:][0].get('close').get('units'), candles[-1:][0].get('close').get('nano'))
        else:
            return {
                'price': 0, name + '_proc': 0, name + '_diff': 0, name + '_avearage': 0}

        prices = [ self._concat(c.get('close').get('units'), c.get('close').get('nano')) for c in candles] + [close]

        avearage = median(prices)

        #close = self._concat(candles[-1:][0].get('close').get('units'), candles[-1:][0].get('close').get('nano'))
        #close = self._concat(last_price.get('price').get('units'), last_price.get('price').get('nano'))
        high = max([self._concat(c.get('high').get('units'), c.get('high').get('nano')) for c in candles] + [close])
        low = min([self._concat(c.get('low').get('units'), c.get('low').get('nano')) for c in candles] + [close])
        proc = round((close - avearage)/(avearage/100), 1)
        diff = round((high - low)/(avearage/100), 1)

        return {
            'price': close * lot, name + '_proc': proc, name + '_diff': diff, name + '_avearage': avearage * lot}


    def print_table(self, my_shares):

        """ my_shares = ['ticker': str, 'avearage': {}] """

        #print(json.dumps(my_shares, indent=4))

        _sum = 0.0
        line_color = Style.YELLOW
        count = 0
        table = []
        line = ['ticker', 'price', 'quart', 'month', 'week']*3
        table.append(line)
        line = []

        for instrument in my_shares:

            line += [
                f"{line_color}  " + instrument.get('ticker'),
                f"{instrument.get('avearage').get('price')}"[:7],
                self._colorize(instrument.get('avearage').get('quart_proc'), instrument.get('avearage').get('quart_diff'), line_color, 33, 44),
                self._colorize(instrument.get('avearage').get('month_proc'), instrument.get('avearage').get('month_diff'), line_color, 22, 33),
                self._colorize(instrument.get('avearage').get('week_proc'), instrument.get('avearage').get('week_diff'), line_color)]

            count += 1
            _sum += instrument.get('avearage').get('price')

            if count % 3 == 0:

                table.append(line)
                line = []
                count = 0
                line_color = Style.YELLOW if line_color is Style.WHITE else Style.WHITE

        print(tabulate(table), f"\n{Style.RESET}Sum =", int(_sum))

        return True


    def _colorize(self, proc, diff, line_color, max_proc=11, max_diff=22):

        if proc > max_proc:
            proc = f'{Style.LIGHT_GREEN}{Style.BOLD}{proc:.0f}{Style.RESET}{line_color}'
        elif proc < -max_proc:
            proc = f'{Style.LIGHT_BLUE}{Style.BOLD}{proc:.0f}{Style.RESET}{line_color}'
        else:
            proc = f'{proc:.0f}'

        if diff > max_diff * 2:
            diff = f'{Style.LIGHT_RED}{Style.BOLD}{diff:.0f}{Style.RESET}{line_color}'
        elif diff > max_diff:
            diff = f'{Style.RESET}{Style.BOLD}{diff:.0f}{Style.RESET}{line_color}'
        else:
            diff = f'{diff:.0f}'

        return proc + '%' + diff


    def save_avearages(self, my_shares, filename):

        """ row format:
        time, divider, ticker, data
        """

        divider = '#'
        columns_name = 'epoch,time,#,ticker,price,quart_proc,quart_diff,month_proc,month_diff,week_proc,week_diff\n'
        time_epoch = time.time()
        time_str = time.strftime("%d%b%y_%H:%M")
        row = [time_epoch, time_str]
        _sum = 0

        for instrument in my_shares:

            data =[
                divider, instrument.get('ticker'),
                instrument.get('avearage').get('price'),
                instrument.get('avearage').get('quart_proc'),
                instrument.get('avearage').get('quart_diff'),
                instrument.get('avearage').get('month_proc'),
                instrument.get('avearage').get('month_diff'),
                instrument.get('avearage').get('week_proc'),
                instrument.get('avearage').get('week_diff')]

            row.append(','.join(str(d) for d in data))
            _sum += instrument.get('avearage').get('price')

        if not self.is_file_exists(filename):
            self.save_csv(columns_name, filename, mode='w')

        self.save_csv(','.join(str(r) for r in row) + f',{_sum}\n', filename, mode='a')

        return True


    def get_all_shares(self, filename=None):

        return self.get_all_instruments(URL_GET_SHARES, filename)


    def get_all_currencies(self, filename=None):

        return self.get_all_instruments(URL_GET_CURRENCIES, filename)


    def get_all_etfs(self, filename=None):

        return self.get_all_instruments(URL_GET_ETFS, filename)


    def get_all_assets(self, filename=None):

        data = {"instrumentType": "INSTRUMENT_TYPE_UNSPECIFIED"}

        return self.get_all_instruments(URL_GET_ASSETS, filename, data)


class Shares(Client):

    def __init__(self, TOKEN):

        super().__init__(TOKEN)

    def get_all(self, filename=None):

        print('or use get_all_shares instead')

        return self.get_all_instruments(URL_GET_SHARES, filename)


class Currencies(Client):

    def __init__(self, TOKEN):

        super().__init__(TOKEN)


    def get_all(self, filename=None):

        print('or use get_all_shares instead')

        return self.get_all_instruments(URL_GET_CURRENCIES, filename)


    def _calc_avearage(self, name, candles, last_price, lot, nominal):

        #print(json.dumps(candles, indent=4))

        if last_price.get('price'):
            close = self._concat(last_price.get('price').get('units'), last_price.get('price').get('nano'))
        elif len(candles) > 0:
            close = self._concat(candles[-1:][0].get('close').get('units'), candles[-1:][0].get('close').get('nano'))
        else:
            return {
                'price': 0, name + '_proc': 0, name + '_diff': 0, name + '_avearage': 0}

        prices = [ self._concat(c.get('close').get('units'), c.get('close').get('nano')) for c in candles] + [close]

        avearage = median(prices)

        high = max([self._concat(c.get('high').get('units'), c.get('high').get('nano')) for c in candles] + [close])
        low = min([self._concat(c.get('low').get('units'), c.get('low').get('nano')) for c in candles] + [close])
        proc = round((close - avearage)/(avearage/100), 1)
        diff = round((high - low)/(avearage/100), 1)

        return {
            'price': close, name + '_proc': proc, name + '_diff': diff, name + '_avearage': avearage}


    def print_table(self, my_shares):

        """ my_shares = ['ticker': str, 'avearage': {}] """

        #print(json.dumps(my_shares, indent=4))

        _sum = 0.0
        line_color = Style.YELLOW
        count = 0
        table = []
        line = ['ticker', 'price', 'quart', 'month', 'week']*3
        table.append(line)
        line = []

        for instrument in my_shares:

            line += [
                f"{line_color}  " + f"{instrument.get('ticker')}"[:6],
                f"{instrument.get('avearage').get('price')}"[:7],
                self._colorize(instrument.get('avearage').get('quart_proc'), instrument.get('avearage').get('quart_diff'), line_color, 33, 44),
                self._colorize(instrument.get('avearage').get('month_proc'), instrument.get('avearage').get('month_diff'), line_color, 22, 33),
                self._colorize(instrument.get('avearage').get('week_proc'), instrument.get('avearage').get('week_diff'), line_color)]

            count += 1
            _sum += instrument.get('avearage').get('price')

            if count % 3 == 0:

                table.append(line)
                line = []
                count = 0
                line_color = Style.YELLOW if line_color is Style.WHITE else Style.WHITE

        print(tabulate(table), f"\n{Style.RESET}Sum =", int(_sum))

        return True














