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
from coint.b3_calc import download_hquotes
from coint.b3_calc import gera_pares
from coint.b3_calc import producer as b3_producer

from coint.binance_futures import BINANCE_FUTURES
from coint.binance_calc import download_hquotes_binance
from coint.binance_calc import producer as binance_producer

from dashboard.models import PairStats, CointParams, Quotes
from bot import send_msg

#CARTEIRA_IBRX = CARTEIRA_IBRX[:5] # DEBUG
#BINANCE_FUTURES = BINANCE_FUTURES[:5] # DEBUG

ibrx_tickers = [ "%s.SA" % s for s in CARTEIRA_IBRX]

def download_b3():
    # Limpa a Base
    Quotes.objects.filter(market='BOVESPA').delete()
    download_hquotes(ibrx_tickers)

def download_binance():
    Quotes.objects.filter(market='BINANCE').delete()
    download_hquotes_binance()

def cron_b3_fast():
    """
    Funcao bastante rapida, porem usa muita memoria do Heroku (640Mb / 512Mb)
    """
    with Pool(2) as p:
        bulk_list = p.starmap(b3_producer, enumerate(gera_pares(ibrx_tickers)))

    # Grava dados no Banco
    PairStats.objects.filter(market='BOVESPA').delete()
    PairStats.objects.bulk_create(bulk_list)

    del bulk_list
    # Telegram
    send_msg()

def cron_b3_memory():
    """
    Funcao que prioriza o uso limitado da memoria.
    """

    # Limpa a Base
    PairStats.objects.filter(market='BOVESPA').delete()
    bulk_list = []
    for idx, pair in enumerate(gera_pares(ibrx_tickers)):
        obj = b3_producer(idx, pair)
        bulk_list.append(obj)

        if len(bulk_list) > 1000:
            # Grava dados no Banco
            PairStats.objects.bulk_create(bulk_list)
            # Libera a memória
            del bulk_list
            bulk_list = []

    # Grava dados no Banco o restante
    PairStats.objects.bulk_create(bulk_list)

    # Telegram
    send_msg()

def cron_binance_memory():

    PairStats.objects.filter(market='BINANCE').delete()
    bulk_list = []
    for idx, pair in enumerate(gera_pares(BINANCE_FUTURES)):
        obj = binance_producer(idx, pair)
        bulk_list.append(obj)

        if len(bulk_list) > 2000:
            # Grava dados no Banco
            PairStats.objects.bulk_create(bulk_list)
            # Libera a memória
            del bulk_list
            bulk_list = []

    # Grava dados no Banco o restante
    PairStats.objects.bulk_create(bulk_list)

if __name__ == '__main__':
    download_b3()
    download_binance()
    cron_b3_fast()
    cron_binance_memory()
