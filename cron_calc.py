import os
import django
import asyncio
import psutil
from itertools import batched
from multiprocessing import Pool
from django.db import connection, transaction

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
from coint.common import generate_pairs
from dashboard.models import PairStats, Quotes
from bot import send_msg

if settings.DEBUG:
    CARTEIRA_IBRX = CARTEIRA_IBRX[:5]  # DEBUG
    BINANCE_FUTURES = BINANCE_FUTURES[:5]  # DEBUG

ibrx_tickers = [f"{s}.SA" for s in CARTEIRA_IBRX]


def get_dynamic_config():
    """
    Detects available CPU and RAM to choose how many processes and how big each batch should be.
    The goal is to use all CPU cores without exceeding memory limits.
    """
    total_cpus = os.cpu_count() or 2
    processes = max(1, total_cpus)  # Use all cores

    # Estimate how much data fits comfortably in memory
    AVG_ITEM_SIZE_BYTES = 5 * 1024  # average 5 KB per PairStats record
    MIN_BATCH_SIZE = 100
    MAX_BATCH_SIZE = 1500
    TARGET_RAM_PERCENT = 0.15  # Use up to 15% of total available RAM

    try:
        mem = psutil.virtual_memory()
        available_ram = mem.available

        # Estimate batch size that uses up to 15% of available RAM
        ram_for_batch = available_ram * TARGET_RAM_PERCENT
        estimated_batch_size = int(ram_for_batch / AVG_ITEM_SIZE_BYTES)

        # Clamp to safe bounds
        batch_size = max(MIN_BATCH_SIZE, min(estimated_batch_size, MAX_BATCH_SIZE))

    except Exception:
        batch_size = 500  # fallback if psutil fails

    return {"processes": processes, "batch_size": batch_size}


def close_db_connections():
    """Closes inherited database connections in a pool worker."""
    connection.close()


def download_b3():
    print("Starting B3 data download...")
    with transaction.atomic():
        Quotes.objects.filter(market='BOVESPA').delete()
    download_hquotes(ibrx_tickers)
    print("B3 data download complete.")


def download_binance():
    print("Starting Binance data download...")
    with transaction.atomic():
        Quotes.objects.filter(market='BINANCE').delete()
    download_hquotes_binance(BINANCE_FUTURES)
    print("Binance data download complete.")


def process_pairs(producer, tickers_list: list, batch_size: int, processes: int):
    """
    Processes pairs in batches using multiprocessing.
    """
    paired_tickers = generate_pairs(tickers_list)
    total_pairs_processed = 0

    print(f"Starting pair processing with {processes} processes and batch size {batch_size}...")

    with Pool(processes, initializer=close_db_connections) as pool:
        for batch in batched(paired_tickers, batch_size):
            bulk_list = pool.starmap(producer, enumerate(batch))
            connection.close()

            try:
                PairStats.objects.bulk_create(bulk_list)
                total_pairs_processed += len(bulk_list)
                print(f"Saved batch of {len(bulk_list)}. Total processed: {total_pairs_processed}")
            except Exception as e:
                print(f"ERROR: Could not save batch of size {len(bulk_list)}. Consider reducing batch_size: {e}")

    print(f"Pair processing finished. Total saved: {total_pairs_processed}")


def main():
    config = get_dynamic_config()
    dynamic_processes = config['processes']
    dynamic_batch_size = config['batch_size']
    binance_batch_size = max(50, int(dynamic_batch_size * 0.5))

    print(f"Running with Dynamic Config: Processes={dynamic_processes}, B3 Batch={dynamic_batch_size}, Binance Batch={binance_batch_size}")

    download_b3()
    download_binance()

    print("Clearing old PairStats data...")
    with transaction.atomic():
        PairStats.objects.filter(market='BOVESPA').delete()
        PairStats.objects.filter(market='BINANCE').delete()
    print("Old PairStats cleared.")

    process_pairs(b3_producer, ibrx_tickers, batch_size=dynamic_batch_size, processes=dynamic_processes)
    process_pairs(binance_producer, BINANCE_FUTURES, batch_size=binance_batch_size, processes=dynamic_processes)

    print("Sending Telegram message...")
    asyncio.run(send_msg())


if __name__ == '__main__':
    main()
