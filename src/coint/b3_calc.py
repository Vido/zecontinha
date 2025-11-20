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

from django.db.models import Q

#from coint.ibov import CARTEIRA_IBOV as CARTEIRA
from coint.ibrx100 import  CARTEIRA_IBRX as _CARTEIRA

from coint.cointegration import get_market_data, clean_timeseries
from coint.common import generic_producer

from dashboard.models import PairStats, CointParams, Quotes
from dashboard.forms import PERIODOS_CALCULO

from bot import send_msg

CARTEIRA = _CARTEIRA
#CARTEIRA = _CARTEIRA[:10] # DEBUG

ibrx_tickers = [ "%s.SA" % s for s in CARTEIRA]


def producer(idx, pair, market='BOVESPA'):
    """ Uses data from global market_data variable
        TODO: This should be called: producer_memory
    """
    # print(idx, pair)
    _x = market_data[('Close', pair[0])]
    _y = market_data[('Close', pair[1])]
    series_x, series_y = clean_timeseries(_x, _y)
    return generic_producer(pair, market, series_x, series_y)

market_data = None

def download_hquotes(carteira_tickers):
    global market_data

    data = get_market_data(carteira_tickers, '2y', '1d')
    market_data = data[-260:]

    obj_buffer, failed_tickers = [], []
    for idx, ticker in enumerate(carteira_tickers):
        series_x = data[('Close', ticker)]
        try:
            obj = Quotes(market='BOVESPA', ticker=ticker,
                hquotes=series_x.values.tolist(), htimestamps=series_x.index.tolist())
            obj_buffer.append(obj)
        except Exception as e:
            failed_tickers.append(ticker)
            print(ticker, e)
            #raise
            continue

    print('failed_tickers', failed_tickers)
    Quotes.objects.bulk_create(obj_buffer)
