"""
O Heroku Scheduler roda este script diariamente
"""

import os
import sys
import django
from multiprocessing import Pool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

#from coint.ibov import CARTEIRA_IBOV
from coint.ibrx100 import  CARTEIRA_IBRX
from coint.b3_calc import download_market_data
from coint.b3_calc import download_hquotes
from coint.b3_calc import gera_pares
from coint.b3_calc import producer as b3_producer

from coint.ibrx100 import BINANCE_FUTURES
from coint.binance_calc import download_hquotes_binance
from coint.binance_calc import producer as binance_producer


from dashboard.models import PairStats, CointParams, Quotes

from bot import send_msg

#CARTEIRA_IBRX = CARTEIRA_IBRX[:10] # DEBUG
ibrx_tickers = [ "%s.SA" % s for s in CARTEIRA_IBRX]


def cron_b3():

    # TODO: fazer o calc_ibovespa usar o hquotes
    download_market_data()
    download_hquotes()

    # Limpa a Base
    PairStats.objects.filter(market='BOVESPA').delete()

    with Pool(2) as p:
        bulk_list = p.starmap(b3_producer, enumerate(gera_pares(ibrx_tickers)))
    PairStats.objects.bulk_create(bulk_list)

    # Telegram
    send_msg()

def cron_binance():
    download_hquotes_binance()

    # Limpa a Base
    PairStats.objects.filter(market='BINANCE').delete()

    bulk_list = []
    for idx, pair in enumerate(gera_pares(BINANCE_FUTURES)):
        obj = producer(idx, pair)
        bulk_list.append(obj)

    PairStats.objects.bulk_create(bulk_list)

if __name__ == '__main__':
    cron_b3()
    cron_binance()