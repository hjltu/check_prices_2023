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


import sys


TOKEN = 'token'
MARKET = ''
DB = 'check.db'
DIR_DATA = 'data'
DIR_PLOTS = 'plots'
LOOP_INTERVAL = 9999
QUART = 99
MONTH = 33
WEEK = 7

TICKERS_RU = [
    'AFKS','AKRN','AGRO','APTK','AQUA','BANE','BANEP','BELU','BLNG',
    'CHMK','CIAN','CNTL','ENPG','ETLN',
    'FEES','FESH','FIVE','FIXP','FLOT','GCHE','GEMC','GLTR','GMKN',
    'HYDR','IRAO','KAZT','KROT','KZOS','KZOSP','LENT','LIFE','LKOH','LSNG','LSRG',
    'MAGN','MDMG','MGNT','MRKU','MOEX','MSRS','MSTT','MTLR','MTLRP','MVID',
    'NKHP','NLMK','NVTK',
    'OKEY','OZON','PLZL','PMSB','PMSBP','POLY','PRFN',
    'ROLO','RUAL','SFIN','SGZH','SPBE','SVAV',
    'TATN','TATNP','TCSG','TRMK','QIWI','VEON','VTBR','UNKL','UWGN','UPRO','YAKG','YNDX'
]

TICKERS_CN = [
    '3','175','288','386','670','688','788','836','857','914','916','968','992',
    '1055','1088','1093','1177','1288','1378','1385','1398','1876','1898','1919',
    '2238','2319','2333','2388','2600','2628','2688','2883','2899',
    '3968','3988','6185','6865','6881','9696'
]

TICKERS_EN = [
    'AAL','AAN','AES','AMCR','AOUT','APPH','ARVL','ASTR','ATRO','ATUS','AWH',
    'BZUN',
    'CEA','CCJ','CCL','CGEN','CLDT','CLF','CLSK','CNP','CORR','CPB','CPNG',
    'DM','DNOW','EAR','ET','ETRN',
    'F','FCEL','FLR','FSLR','FTCI',
    'GE','GEVO','GOLD','GPS','GT','GTX',
    'HAL','HBI','HPE','HSC','HYLN','INSG',
    'KEP','KMI','KOPN','LAZR','LPL','LTHM','LUMN',
    'M','MAC','MFGP','MRC','MEI','MLCO','NOK','NU',
    'OI','OII','OIS','PAAS','PAGS','PBI','PPL','PSTG','RIG','RKLB','RUN',
    'SJI','SKLZ','SLDB','STLA','SWBI','SWI','SWN','TAK','TAL','T','TDS','TTMI','QUOT',
    'UA','UBS','VALE','VTRS','VEON','VIPS','VLDR','VMEO','VUZI','VXRT',
    'WBD','WISH','WKHS','WTTR','WU',
    'XRX','ZYNE','ZYXI'
]

TICKERS_PAIRS = [
    'AMDRUB_TOM','KZTRUB_TOM','KGSRUB_TOM',
    'UZSRUB_TOM','TJSRUB_TOM','TRYRUB_TOM',
    'BYNRUB_TOM','HKDRUB_TOM','CNYRUB_TOM',
    'USD000UTSTOM','GLDRUB_TOM','SLVRUB_TOM'
]

class Style():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BLACK = '\033[30m'
    ORANGE = '\033[33m'
    LIGHT_RED = '\033[91m'
    RED = '\033[31m'
    LIGHT_GREEN = '\033[92m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    LIGHT_BLUE = '\033[94m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    SELECT = '\033[7m'
    BG_GREEN = '\033[102m'
    BG_BLUE = '\033[104m'
    BG_RED = '\033[101m'
    RESET = '\033[0m'


################################ TEST DATA #####################################

TEST_SHARES_TICKERS = ['FEES','ROLO','VTBR']
TEST_PAIRS_TICKERS = ['HKDRUB_TOM','SLVRUB_TOM','USD000UTSTOM']
TEST_MARKET = ''
TEST_DB = 'test.db'
TEST_LOOP_INTERVAL = 9
TEST_DATE_FROM = '2023-05-30T07:44:32Z'
TEST_DATE_TO = '2023-06-02T07:44:32Z'
TEST_QUART = 3
TEST_MONTH = 2
TEST_WEEK = 1

TEST_MY_SHARES = []

TEST_MY_CANDLES = []

TEST_MY_AVEARAGE = []


























