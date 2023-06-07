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


import json
import requests
from tabulate import tabulate
from statistics import median, mean
from config import Style


URL_OPEN_ACC = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.SandboxService/OpenSandboxAccount'
URL_GET_ACC = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.SandboxService/GetSandboxAccounts'
URL_CLOSE_ACC = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.SandboxService/CloseSandboxAccount'
URL_GET_SHARES = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.InstrumentsService/Shares'
URL_GET_CANDLES = 'https://invest-public-api.tinkoff.ru/rest/tinkoff.public.invest.api.contract.v1.MarketDataService/GetCandles'
URL_GET_PRICES = ''
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


    def open_acc(self):

        if not self.acc:
            self.acc = self.post_request(URL_OPEN_ACC, headers=self.headers)
        return self.acc


    def get_acc(self):
        return self.post_request(URL_GET_ACC, headers=self.headers)


    def close_acc(self):

        """
        request data:
            {"accountId": "string"}
        """

        if self.acc:
            self.post_request(URL_CLOSE_ACC, headers=self.headers, data=self.acc)
            self.acc = None
        return self.get_acc()


    def get_shares(self):

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

        data = {"instrumentStatus": "INSTRUMENT_STATUS_UNSPECIFIED"}
        all_shares = self.post_request(URL_GET_SHARES, headers=self.headers, data=data)
        print('Client: all shares length is:', len(all_shares.get('instruments')))
        return all_shares


    def get_my_shares(self, shares, tickers):

        """
        sp = int(len(tickers)/3)
        T1=tickers[:sp]; T2=tickers[sp:sp*2]; T3=tickers[sp*2:]
        tickers=[]
        for i in range(len(T1)):
            tickers+=([T1[i]]+[T2[i]]+[T3[i]])
        """

        my_shares = []

        for t in tickers:
            for i in shares.get('instruments'):
                if t == i.get('ticker'):
                    my_shares.append({'ticker': t, 'figi': i.get('figi'), 'uid': i.get('uid'), 'lot': i.get('lot')})

        print('Client: my shares length is:', len(my_shares))

        return my_shares


    def get_candles(self, my_shares, date_from, date_to):

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

        for s in my_shares[:]:

            data = {
                'figi': s.get('figi'),
                'from': date_from,
                'to': date_to,
                'interval': CANDLES_INTERVAL,
                'instrumentId': s.get('uid')}

            candles = self.post_request(URL_GET_CANDLES, headers=self.headers, data=data)
            s.update(candles)

        return my_shares


    def get_prices(self, my_shares):
        return my_shares


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
                lot = instrument.get('lot')
                avearage.update(self._calc_avearage(key, candles, lot))

            instrument.update({'avearage': avearage})

        return my_candles


    def _calc_avearage(self, name, candles, lot):

        prices = [ self._concat(c.get('close').get('units'), c.get('close').get('nano')) for c in candles]

        if len(prices) == 0:
            return {'price': 0, name + '_proc': 0, name + '_diff': 0, name + '_avearage': 0}

        avearage = mean(prices)
        close = self._concat(candles[-1:][0].get('close').get('units'), candles[-1:][0].get('close').get('nano'))
        high = max(self._concat(c.get('high').get('units'), c.get('high').get('nano')) for c in candles)
        low = min(self._concat(c.get('low').get('units'), c.get('low').get('nano')) for c in candles)
        proc = round((close - avearage)/(avearage/100), 1)
        diff = round((high - low)/(avearage/100), 1)

        return {'price': close * lot, name + '_proc': proc, name + '_diff': diff, name + '_avearage': avearage * lot}


    def _concat(self, units, nano):

        """ nano length = 9 """

        rank = 0.000000001

        return int(units) + nano * rank


    def print_table(self, my_shares):

        """ my_shares = ['ticker': str, 'avearage': {}] """

        _sum = 0.0
        line_color = Style.YELLOW
        count = 0
        table = []
        line = ['ticker', 'price', 'quart', 'month', 'week']*3
        table.append(line)
        line = []

        for instrument in my_shares:
            line += (self._get_instrument(instrument, line_color))
            count += 1
            _sum += instrument.get('avearage').get('price')

            if count % 3 == 0:

                table.append(line)
                line = []
                count = 0
                line_color = Style.YELLOW if line_color is Style.WHITE else Style.WHITE

        print(tabulate(table), f"\n{Style.RESET}Sum =", int(_sum))
        return True


    def _get_instrument(self, instrument, line_color):

        if instrument.get('avearage').get('price'):
            return [
                f"{line_color}  " + instrument.get('ticker'),
                f"{instrument.get('avearage').get('price')}"[:7],
                self._colorize(instrument.get('avearage').get('quart_proc'), instrument.get('avearage').get('quart_diff'), line_color, 33, 44),
                self._colorize(instrument.get('avearage').get('month_proc'), instrument.get('avearage').get('month_diff'), line_color, 22, 33),
                self._colorize(instrument.get('avearage').get('week_proc'), instrument.get('avearage').get('week_diff'), line_color)]
        else:
            return [instrument.get('ticker'),'---','keine','daten','---']


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



















