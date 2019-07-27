"""
O Heroku Scheduler roda este script diariamente
"""

import os
import sys
import django
#from datetime import datetime
#from django.utils import timezone
import pandas as pd

from statsmodels.tools.sm_exceptions import MissingDataError
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

from dashboard.ibov import CARTEIRA_IBOV
from dashboard.cointegration import get_market_data, coint_model
from dashboard.models import PairStats


def create_object(success, pair, series_x=pd.Series([]), series_y=pd.Series([]), test_params={}):

    obj = PairStats(
        success = success,
        pair = " ".join(pair), 
        market = 'BOVESPA',
        ticker_x = pair[0],
        ticker_y = pair[1],
    )

    try:
        if not series_x.empty:
            obj.x_quote = series_x.iloc[-1]

        if not series_y.empty:
            obj.y_quote = series_y.iloc[-1]

        if success:
            obj.adf_pvalue = test_params['ADF'][1]
            obj.resid_std = test_params['OLS'].resid.std()
            obj.last_resid = test_params['OLS'].resid.iloc[-1]
            obj.ang_coef = test_params['OLS'].params.x1
            obj.intercept = test_params['OLS'].params.const
            obj.zscore = obj.last_resid / obj.resid_std

    except Exception:
        obj.success = False

    return obj


def calc_ibovespa():

    # Faz Download
    ibov_tickers = [ "%s.SA" % s for s in CARTEIRA_IBOV]
    data = get_market_data(ibov_tickers, '1y', '1d')

    # Limpa a Base
    PairStats.objects.all().delete()

    # Forma todos os pares sem repetição
    set_pairs = set([])
    for i in ibov_tickers:
        for k in ibov_tickers:
            if i == k:
                continue
            set_pairs.add((i, k))

    print('Total:', len(set_pairs), 'pares')

    # Faz o calculo
    obj_buffer = []
    for idx, pair in enumerate(set_pairs):
        print(idx, pair)
        series_x = data[('Close', pair[0])]
        series_y = data[('Close', pair[1])]
        success = False

        try:
            test_params = coint_model(series_x, series_y)
            success = True
            obj = create_object(success, pair, series_x, series_y, test_params)
        except MissingDataError:
            print('FAIL - MissingDataError')
            obj = create_object(success, pair)
            
        obj_buffer.append(obj)

    PairStats.objects.bulk_create(obj_buffer)

if __name__ == '__main__':
    calc_ibovespa()
