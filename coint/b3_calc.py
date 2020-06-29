"""
O Heroku Scheduler roda este script diariamente
"""

import os
import sys
import django
#from datetime import datetime
#from django.utils import timezone

import copy
import pandas as pd
from multiprocessing import Pool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

from django.forms.models import model_to_dict
from statsmodels.tools.sm_exceptions import MissingDataError
from django.db.models import Q

#from coint.ibov import CARTEIRA_IBOV as CARTEIRA
from coint.ibrx100 import  CARTEIRA_IBRX as _CARTEIRA

from coint.cointegration import get_market_data, coint_model, beta_rotation, clean_timeseries
from dashboard.models import PairStats, CointParams, Quotes
from dashboard.forms import PERIODOS_CALCULO

from bot import send_msg

CARTEIRA = _CARTEIRA
#CARTEIRA = _CARTEIRA[:10] # DEBUG

ibrx_tickers = [ "%s.SA" % s for s in CARTEIRA]

def create_cointparams(success, test_params={}):

    obj = CointParams(success=success)

    if not success:
        obj.success = False
        return obj

    try:
        obj.adf_pvalue = test_params['ADF'][1]
        obj.resid_std = test_params['OLS'].resid.std()
        obj.last_resid = test_params['OLS'].resid.iloc[-1]
        obj.ang_coef = test_params['OLS'].params.x1
        obj.intercept = test_params['OLS'].params.const
        obj.n_observ = len(test_params['OLS'].resid)
        obj.zscore = obj.last_resid / obj.resid_std
    except Exception as e:
        print(e)
        obj.success = False
        #raise

    return obj

def create_pairstats(pair, market, series_x=pd.Series([]), series_y=pd.Series([])):

    obj = PairStats(
        pair = " ".join(pair),
        market = market,
        ticker_x = pair[0],
        ticker_y = pair[1],
    )

    if not series_x.empty:
        obj.x_quote = series_x.iloc[-1]

    if not series_y.empty:
        obj.y_quote = series_y.iloc[-1]

    return obj

def producer(idx, pair):

    _x = market_data[('Close', pair[0])]
    _y = market_data[('Close', pair[1])]
    series_x, series_y = clean_timeseries(_x, _y)

    obj_pair = create_pairstats(pair, 'BOVESPA', series_x=series_x, series_y=series_y)
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

def gera_pares(carteira_tickers):

    # Forma todos os pares sem repetição
    set_pairs = set([])
    for i in carteira_tickers:
        for k in carteira_tickers:
            if i == k:
                continue
            set_pairs.add((i, k))

    print('Total:', len(set_pairs), 'pares')

    return set_pairs

market_data = None

def download_hquotes(carteira_tickers):
    global market_data

    # Faz Download 5y
    data = get_market_data(carteira_tickers, '5y', '1d')
    market_data = data[-260:]

    # Faz o calculo
    obj_buffer = []
    for idx, ticker in enumerate(carteira_tickers):
        series_x = data[('Close', ticker)]
        try:
            obj = Quotes(market='BOVESPA', ticker=ticker,
                hquotes=series_x.values.tolist(), htimestamps=series_x.index.tolist())
            obj_buffer.append(obj)
        except Exception as e:
            print(e)
            #raise

    Quotes.objects.bulk_create(obj_buffer)

    #return market_data