"""
O Heroku Scheduler roda este script diariamente
"""

import os
import sys
import django
#from datetime import datetime
#from django.utils import timezone
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

from django.forms.models import model_to_dict
from statsmodels.tools.sm_exceptions import MissingDataError
from django.db.models import Q

from dashboard.ibov import CARTEIRA_IBOV
from dashboard.cointegration import get_market_data, coint_model
from dashboard.models import PairStats, CointParams
from dashboard.forms import PERIODOS_CALCULO

def create_cointparams(success, pair, series_x=pd.Series([]), series_y=pd.Series([]), test_params={}):

    obj = CointParams(success=success)

    try:
        if success:
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

    return obj

def create_pairstats(pair, series_x=pd.Series([]), series_y=pd.Series([])):

    obj = PairStats(
        pair = " ".join(pair),
        market = 'BOVESPA',
        ticker_x = pair[0],
        ticker_y = pair[1],
    )

    if not series_x.empty:
        obj.x_quote = series_x.iloc[-1]

    if not series_y.empty:
        obj.y_quote = series_y.iloc[-1]

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
        # Limite do Heroku: 10K rows

        series_x = data[('Close', pair[0])]
        series_y = data[('Close', pair[1])]
        obj_pair = create_pairstats(pair, series_x=series_x, series_y=series_y)

        for periodo in PERIODOS_CALCULO:
            series_x = data[('Close', pair[0])][-periodo:]
            series_y = data[('Close', pair[1])][-periodo:]
            try:
                test_params = coint_model(series_x, series_y)
                obj_data = create_cointparams(True, pair, series_x, series_y, test_params)
                obj_pair.success = True
            except MissingDataError:
                obj_data = create_cointparams(False, pair)
                print('FAIL - MissingDataError')

            obj_pair.model_params[periodo] = model_to_dict(obj_data)
            print(id(obj_pair))

        #obj_buffer.append(obj_pair)
        # BUG bizarro do DjangoPython
        obj_pair.save()


    #PairStats.objects.bulk_create(obj_buffer)

def enter_trades():
    """
        TODO
    """
    trade_list()
    qs = PairStats.objects.filter(success=True)
    qs = qs.filter(Q(adf_pvalue__lte=0.05) & (Q(zscore__gte=2.0) | Q(zscore__lte=-2.0)))

def exit_trades():
    """
        TODO
    """
    pass

if __name__ == '__main__':
    calc_ibovespa()