#!/usr/bin/env python3

import os
import gc
import sys
import asyncio
from multiprocessing import Pool
from itertools import permutations

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

from django.conf import settings
#from coint.ibov import CARTEIRA_IBOV
from coint.ibrx100 import CARTEIRA_IBRX
from coint.b3_calc import download_hquotes as download_b3
from coint.b3_calc import producer as b3_producer

from coint.binance_futures import BINANCE_FUTURES
from coint.binance_calc import download_hquotes as download_binance
from coint.binance_calc import producer as binance_producer

from dashboard.models import PairStats, CointParams, Quotes

if settings.DEBUG:
    CARTEIRA_IBRX = CARTEIRA_IBRX[:5] # DEBUG
    BINANCE_FUTURES = BINANCE_FUTURES[:5] # DEBUG

# TODO: cron_fast and cron_memory could be one functio - with parameters or a strategy pattern
def cron_b3_fast():
    """
    Funcao bastante rapida, porem usa muita memoria do Heroku (640Mb / 512Mb)
    """

    gera_pares = enumerate(permutations(ibrx_tickers, 2))
    with Pool(2) as p:
        bulk_list = p.starmap(b3_producer, gera_pares)

    # Grava dados no Banco
    PairStats.objects.filter(market='BOVESPA').delete()
    PairStats.objects.bulk_create(bulk_list)
    del bulk_list

def cron_memory(market, producer, tickers_list, size=500):
    """
    Funcao que prioriza o uso limitado da memoria.

    History:
    - First version: Heroku (Free)
    - Max batch 2000

    - Second Version: DigitalOcean (1cpu and 2Gb RAM)
    - This server was shared with other aplications
    - There is ~ 1.2Gb RAM used
    - Early max batch 500 -> 800 was too much
    - After some improvements: 700

    - Third Version
    - After Docker refactor ~ 0.9Gb RAM used
    """
    # Limpa a Base
    PairStats.objects.filter(market=market).delete()
    bulk_list = []

    gera_pares = enumerate(permutations(tickers_list, 2))
    for idx, pair in gera_pares:
        obj = producer(idx, pair)
        if not obj:
            continue
        bulk_list.append(obj)

        if len(bulk_list) > size:
            print(idx, pair)
            # Grava dados no Banco
            PairStats.objects.bulk_create(bulk_list)
            del bulk_list
            gc.collect() # Libera a memória
            bulk_list = []

    # Grava dados no Banco o restante
    PairStats.objects.bulk_create(bulk_list)
    del bulk_list

def main():
    tasks = ['b3', 'binance']
    if len(sys.argv) > 1:
        assert sys.argv[1].lower() in tasks, f"sys.argv[1] must be: {'or '.join(tasks)}"
        tasks = sys.argv[1].lower()

    if 'b3' in tasks:
        Quotes.objects.filter(market='BOVESPA').delete()
        ibrx_tickers = [ f'{t}.SA' for t in CARTEIRA_IBRX]
        download_b3(ibrx_tickers)
        #cron_b3_fast()
        cron_memory('BOVESPA', b3_producer, ibrx_tickers, size=700)

    if 'binance' in tasks:
        # TODO: Parametrize delete and download
        Quotes.objects.filter(market='BINANCE').delete()
        download_binance(BINANCE_FUTURES)
        cron_memory('BINANCE', binance_producer, BINANCE_FUTURES, size=700)

    if 'cross-assets' in tasks:
        # TODO: Calculates B3xBinance (eg. PETR4 x BTCUSDT, VALE3 x ETHUSDT)
        raise NotImplemented

if __name__ == '__main__':
    main()
