import os
import sys
import copy
import django
from datetime import datetime
from multiprocessing import Pool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

import pandas as pd
from decouple import config
from binance.client import Client
from binance.exceptions import BinanceAPIException

from statsmodels.tools.sm_exceptions import MissingDataError

from dashboard.models import PairStats, CointParams, Quotes
from dashboard.forms import PERIODOS_CALCULO

from coint.cointegration import clean_timeseries
from coint.common import generic_producer

# TODO:
# This data does not require Binance Credentials
# https://data.binance.vision/?prefix=data/spot/daily/klines/

binance_data = None

def download_hquotes(tickers_list):
    global binance_data

    client = Client(
        config('BINANCE_APIKEY'),
        config('BINANCE_SECRETKEY'),
        #tld='us'
    )

    obj_buffer, df_buffer, failed_tickers = [], [], []
    for idx, ticker in enumerate(tickers_list):
        print(idx, ticker)
        try:
            # fetch weekly klines since it listed
            klines = client.get_historical_klines(
                ticker, Client.KLINE_INTERVAL_1DAY, "1 year ago UTC")
        except BinanceAPIException as e:
            failed_tickers.append(ticker)
            print(ticker, e)
            #raise
            continue

        ts_list, q_list = [], []
        for k in klines:
            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#general-api-information
            ts_list.append(int(k[0])//1000)
            q_list.append(float(k[4]))

        obj = Quotes(
            market='BINANCE',
            ticker=ticker,
            hquotes=q_list,
            htimestamps=ts_list
        )
        
        df = pd.DataFrame(
            q_list,
            index=pd.to_datetime(ts_list, unit="s"),
            columns=pd.MultiIndex.from_product([["Close"], [ticker]])
        )
        obj_buffer.append(obj)
        df_buffer.append(df)

    print('failed_tickers', failed_tickers)
    Quotes.objects.bulk_create(obj_buffer)

    binance_data = pd.concat(df_buffer, axis=1, sort=True)
    binance_data.columns.names = ['Price', 'Ticker']

def producer_mem(idx, pair, market='BINANCE'):
    _x = binance_data[('Close', pair[0])]
    _y = binance_data[('Close', pair[1])]
    series_x, series_y = clean_timeseries(_x, _y)
    return generic_producer(pair, market, series_x, series_y)

def producer_db(idx, pair, market='BINANCE'):
    try:
        _x = Quotes.objects.get(ticker=pair[0]).get_series()
        _y = Quotes.objects.get(ticker=pair[1]).get_series()
        series_x, series_y = clean_timeseries(_x, _y)
    except MissingDataError as mde:
        print(pair, mde)
        #raise
        return None
    return generic_producer(pair, market, series_x, series_y)
