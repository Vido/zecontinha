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

from django.forms.models import model_to_dict

from dashboard.models import PairStats, CointParams, Quotes
from dashboard.forms import PERIODOS_CALCULO
from dashboard.forms import BINANCE_FUTURES

from coint.cointegration import coint_model, beta_rotation, clean_timeseries
# TODO: Criar um arquivos com utils.py
from coint.b3_calc import create_cointparams, create_pairstats, gera_pares

def download_hquotes_binance():

    client = Client(
        config('BINANCE_APIKEY'),
        config('BINANCE_SECRETKEY'),
        #tld='us'
    )

    obj_buffer, failed_tickers = [], []
    for idx, ticker in enumerate(BINANCE_FUTURES):
        print(idx, ticker)

        try:
            # fetch weekly klines since it listed
            klines = client.get_historical_klines(
                ticker, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2017")
        except BinanceAPIException as e:
            failed_tickers.append(ticker)
            print(e)
            #raise
            continue

        ts_list, q_list = [], []
        for k in klines:
            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#general-api-information
            ts_list.append(
                datetime.fromtimestamp(int(k[0])/1000)
            )
            q_list.append(k[4])

        try:
            obj = Quotes(market='BINANCE', ticker=ticker,
                hquotes=q_list, htimestamps=ts_list)
            obj_buffer.append(obj)
        except Exception as e:
            print(e)
            raise

    print('failed_tickers', failed_tickers)
    Quotes.objects.bulk_create(obj_buffer)

def producer(idx, pair, market='BINANCE'):

    _x = Quotes.objects.get(ticker=pair[0]).get_series()
    _y = Quotes.objects.get(ticker=pair[1]).get_series()
    series_x, series_y = clean_timeseries(_x, _y)

    obj_pair = create_pairstats(pair, market, series_x=series_x, series_y=series_y)
    print(idx, pair)

    try:
        beta_list = beta_rotation(series_x=series_x, series_y=series_y)
        obj_pair.beta_rotation = beta_list
    except MissingDataError:
        print('FAIL - MissingDataError - Beta')
        #raise

    for periodo in PERIODOS_CALCULO:
        slice_x = series_x[-periodo:]
        slice_y = series_y[-periodo:]
        try:
            test_params = coint_model(slice_x, slice_y)
            obj_data = create_cointparams(True, test_params)
            obj_pair.success = True
        except MissingDataError:
            obj_data = create_cointparams(False, test_params)
            print('FAIL - MissingDataError - OLS ADF', periodo)
            #raise

        obj_pair.model_params[periodo] = model_to_dict(obj_data)

    return copy.deepcopy(obj_pair)
