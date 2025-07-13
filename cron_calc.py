import os
import gc
import sys
import django
from multiprocessing import Pool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

from django.conf import settings
#from coint.ibov import CARTEIRA_IBOV
from coint.ibrx100 import  CARTEIRA_IBRX
from coint.b3_calc import download_hquotes
from coint.b3_calc import producer as b3_producer

from coint.binance_futures import BINANCE_FUTURES
from coint.binance_calc import download_hquotes_binance
from coint.binance_calc import producer as binance_producer

from coint.common import gera_pares
from dashboard.models import PairStats, CointParams, Quotes
from bot import send_msg

if settings.DEBUG:
    CARTEIRA_IBRX = CARTEIRA_IBRX[:5] # DEBUG
    BINANCE_FUTURES = BINANCE_FUTURES[:5] # DEBUG

ibrx_tickers = [ "%s.SA" % s for s in CARTEIRA_IBRX]

def download_b3():
    # Limpa a Base
    Quotes.objects.filter(market='BOVESPA').delete()
    download_hquotes(ibrx_tickers)

def download_binance():
    Quotes.objects.filter(market='BINANCE').delete()
    download_hquotes_binance(BINANCE_FUTURES)

def cron_process_pairs(
    market: str,
    producer,
    tickers_list: list,
    mode: str = "sequential",
    batch_size: int = 500,
    processes: int = 2
):
    """
    Processes pairs of tickers and saves results to the database.

    Supports two modes:
        - "sequential" : processes pairs in batches to save memory.
        - "multiprocessing" : processes all pairs in parallel (faster but uses more memory).
    
    Memory Limits:
        - Heroku ~2000 pairs
        - Digital Ocean ~800 pairs
        
        django.db.utils.OperationalError: FATAL:  the database system is in recovery mode
    """

    # Clear old pairs from database
    PairStats.objects.filter(market=market).delete()

    pairs = list(gera_pares(tickers_list))

    if mode == "multiprocessing":
        # Faster method, but it uses a lot of Heroku memory: 640MB / 512MB.

        with Pool(processes) as pool:
            bulk_list = pool.starmap(producer, enumerate(pairs))

        # Save all pairs to the database
        PairStats.objects.bulk_create(bulk_list)
        del bulk_list

    elif mode == "sequential":
        bulk_list = []

        for idx, pair in enumerate(pairs):
            obj = producer(idx, pair)
            bulk_list.append(obj)

            if len(bulk_list) >= batch_size:
                # Save the current batch to free memory
                PairStats.objects.bulk_create(bulk_list)
                del bulk_list
                gc.collect() # Free memory
                bulk_list = []

        if bulk_list:
            # Save any remaining pairs to the database
            PairStats.objects.bulk_create(bulk_list)
            del bulk_list

    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'sequential' or 'multiprocessing'.")


def main():

    download_b3()
    download_binance()

    cron_process_pairs(
        market='BOVESPA',
        producer=b3_producer,
        tickers_list=ibrx_tickers,
        mode="sequential",
        batch_size=500
    )

    cron_process_pairs(
        market='BINANCE',
        producer=binance_producer,
        tickers_list=BINANCE_FUTURES,
        mode="sequential",
        batch_size=250
    )

    # Telegram
    send_msg()

if __name__ == '__main__':
    #asyncio.run(main())
    main()
