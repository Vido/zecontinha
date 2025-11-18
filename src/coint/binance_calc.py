import os
import sys
import copy
import django
from datetime import datetime
from multiprocessing import Pool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

from decouple import config
from binance.client import Client
from binance.exceptions import BinanceAPIException

from statsmodels.tools.sm_exceptions import MissingDataError

from dashboard.models import PairStats, CointParams, Quotes
from dashboard.forms import PERIODOS_CALCULO

from coint.cointegration import clean_timeseries
from coint.common import generic_producer

def download_hquotes(tickers_list):

    client = Client(
        config('BINANCE_APIKEY'),
        config('BINANCE_SECRETKEY'),
        #tld='us'
    )

    obj_buffer, failed_tickers = [], []
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
            ts_list.append(
                datetime.fromtimestamp(int(k[0])/1000)
            )
            q_list.append(k[4])

        obj = Quotes(market='BINANCE', ticker=ticker,
            hquotes=q_list, htimestamps=ts_list)
        obj_buffer.append(obj)

    print('failed_tickers', failed_tickers)
    Quotes.objects.bulk_create(obj_buffer)

def producer(idx, pair, market='BINANCE'):
    """ Uses data from global market_data variable
        TODO: Use the same producer as b3 - from global
        -> better performace - no DB queries

        TODO: This should be called: producer_db
    """
    try:
        _x = Quotes.objects.get(ticker=pair[0]).get_series()
        _y = Quotes.objects.get(ticker=pair[1]).get_series()
        series_x, series_y = clean_timeseries(_x, _y)
    except MissingDataError as mde:
        print(pair, mde)
        #raise
        return None

    return generic_producer(pair, market, series_x, series_y)
