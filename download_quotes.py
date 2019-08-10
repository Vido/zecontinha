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
from dashboard.cointegration import get_market_data
from dashboard.models import Quotes

def download_hquotes():

    # Faz Download
    ibov_tickers = [ "%s.SA" % s for s in CARTEIRA_IBOV]
    data = get_market_data(ibov_tickers, '5y', '1d')

    # Limpa a Base
    Quotes.objects.all().delete()

    # Faz o calculo
    obj_buffer = []
    for idx, ticker in enumerate(ibov_tickers):
        series_x = data[('Close', ticker)]
        obj = Quotes(market='BOVESPA', ticker=ticker, hquotes=series_x)
        obj_buffer.append(obj)
        print(ticker)

    Quotes.objects.bulk_create(obj_buffer)

if __name__ == '__main__':
    download_hquotes()