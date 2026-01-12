"""
Crawler for Binance USDT-M Futures contracts.

Fetches all futures symbols via public API and returns:
    list[str] of tickers (e.g., "BTCUSDT")

If *anything* goes wrong, returns DEFAULT_BINANCE_FUTURES.

Optional parameters:
    limit: int | None  → return only the first N tickers
    exclude: list[str] | None  → remove these symbols before returning
"""

import asyncio
import aiohttp


# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

BINANCE_FUTURES_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"

# Backup list (21/11/25)
DEFAULT_BINANCE_FUTURES = [
    "BTCUSDT", "ETHUSDT", "BCHUSDT", "XRPUSDT", "EOSUSDT", "LTCUSDT",
    "TRXUSDT", "ETCUSDT", "LINKUSDT", "XLMUSDT", "ADAUSDT", "XMRUSDT",
    "DASHUSDT", "ZECUSDT", "XTZUSDT", "BNBUSDT", "ATOMUSDT", "ONTUSDT",
    "IOTAUSDT", "BATUSDT", "VETUSDT", "NEOUSDT", "QTUMUSDT", "IOSTUSDT",
    "THETAUSDT", "ALGOUSDT", "ZILUSDT", "KNCUSDT", "ZRXUSDT", "COMPUSDT",
    "OMGUSDT", "DOGEUSDT", "SXPUSDT", "KAVAUSDT", "BANDUSDT", "RLCUSDT",
    "WAVESUSDT", "MKRUSDT", "SNXUSDT", "DOTUSDT", "YFIUSDT", "BALUSDT",
    "CRVUSDT", "TRBUSDT", "RUNEUSDT", "SUSHIUSDT", "SRMUSDT", "EGLDUSDT",
    "SOLUSDT", "ICXUSDT", "STORJUSDT", "BLZUSDT", "UNIUSDT", "AVAXUSDT",
    "FTMUSDT", "HNTUSDT", "ENJUSDT", "FLMUSDT", "TOMOUSDT", "RENUSDT",
    "KSMUSDT", "NEARUSDT", "AAVEUSDT", "FILUSDT", "RSRUSDT", "LRCUSDT",
    "MATICUSDT", "OCEANUSDT", "CVCUSDT", "BELUSDT", "CTKUSDT", "AXSUSDT",
    "ALPHAUSDT", "ZENUSDT", "SKLUSDT", "GRTUSDT", "1INCHUSDT", "BTCBUSD",
    "CHZUSDT", "SANDUSDT", "ANKRUSDT", "BTSUSDT", "LITUSDT", "UNFIUSDT",
    "REEFUSDT", "RVNUSDT", "SFPUSDT", "XEMUSDT", "BTCSTUSDT", "COTIUSDT",
    "CHRUSDT", "MANAUSDT", "ALICEUSDT", "HBARUSDT", "ONEUSDT", "LINAUSDT",
    "STMXUSDT", "DENTUSDT", "CELRUSDT", "HOTUSDT", #"DEFIUSDT"
][::-1]


# ---------------------------------------------------------
# Fetch JSON from Binance
# ---------------------------------------------------------

async def fetch_binance_futures() -> list[str] | None:
    """
    Fetches futures exchangeInfo from Binance public API.
    Returns list of PERPETUAL symbols or None if failure.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BINANCE_FUTURES_URL, timeout=20) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()

        symbols = [
            s["symbol"]
            for s in data.get("symbols", [])
            if s.get("contractType") == "PERPETUAL"
        ]

        return symbols or None

    except Exception:
        return None


# ---------------------------------------------------------
# Main return function (limit + exclude)
# ---------------------------------------------------------

async def load_binance_futures(
    limit: int | None = None,
    exclude: list[str] | None = None
) -> list[str]:
    """
    Returns list of Binance Futures tickers.
    Always returns DEFAULT_BINANCE_FUTURES on error.

    Parameters:
        limit → return first N tickers
        exclude → remove these tickers from the final list
    """
    tickers = await fetch_binance_futures()

    if not tickers:
        tickers = DEFAULT_BINANCE_FUTURES.copy()

    # Apply exclude functionality
    if exclude:
        tickers = [t for t in tickers if t not in exclude]

    # Apply limit
    if limit is not None:
        tickers = tickers[:limit]

    return tickers


# ---------------------------------------------------------
# CLI for debugging
# ---------------------------------------------------------

if __name__ == "__main__":
    result = asyncio.run(load_binance_futures(limit=100, exclude=["BTCSTUSDT", "GAIBUSDT"]))
    print(f"Binance Futures ({len(result)}):")
    print(result)
