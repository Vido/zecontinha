#!/usr/bin/env python3

import os
import sys
import asyncio
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")

import django
django.setup()

import telegram
from telegram.constants import ParseMode
from decouple import config
from django.db.models import Q
from django.conf import settings

from dashboard.models import PairStats, Quotes

telegram_api_key = config('TELEGRAM_API_KEY')
bot = telegram.Bot(telegram_api_key)
#chat_id = config('TELEGRAM_CHAT_ID', '@pythonfinancas')

def select_pairs(
    market,
    adf_pvalue_threshold=0.05,
    hurst_threshold=0.3,
    zscore_threshold=2.0,
    periods=120,
    order_by='?'):

    positive_z = Q(**{f'model_params__{periods}__zscore__gte':  zscore_threshold})
    negative_z = Q(**{f'model_params__{periods}__zscore__lte': -zscore_threshold})
    z_filter = positive_z | negative_z

    success = Q(**{f'model_params__{periods}__success': False})
    adf_pvalue = Q(**{f'model_params__{periods}__adf_pvalue__gte': adf_pvalue_threshold})
    hurst = Q(**{f'model_params__{periods}__hurst__gte': hurst_threshold})

    queryset = PairStats.objects.filter(
            Q(market=market) & z_filter
        ).exclude(success | adf_pvalue | hurst)

    return queryset.order_by(order_by)


def select_top_pairs(qs, periods=120, top_n=3):
    """
    Lower is better: |zscore|, adf, half-life
    Higher is better: hurst (mean reversion measure)

    Returns the top N objects (default 3).
    """

    scored = []

    for obj in qs:
        params = obj.model_params.get(str(periods), {})
        if not params:
            continue

        try:
            z = abs(params.get("zscore", 999))
            adf = params.get("adf_pvalue", 1)
            ang = abs(params.get("ang_coef", 999))
            hl = params.get("half_life", 999)
            hurst = params.get("hurst", 0)
        except Exception:
            continue

        # ---- Ranking formula ----
        score = (
            z * 2.0 +
            adf * 5.0 +
            hl * 0.1 +
            ang * 0.5 -
            hurst * 3.0
        )
        # Lower score = better pair

        scored.append((score, obj))

    # Sort by score ascending
    scored.sort(key=lambda x: x[0])

    return [o for _, o in scored[:top_n]]

def get_plot(x_ticker, y_ticker, periods=120):
    from coint.cointegration import fp_savefig, _get_residuals_plot
    from coint.cointegration import coint_model, clean_timeseries

    _x = Quotes.objects.get(ticker=x_ticker).get_series()
    _y = Quotes.objects.get(ticker=y_ticker).get_series()
    series_x, series_y = clean_timeseries(_x, _y)

    r = coint_model(series_x[-periods:], series_y[-periods:])
    return fp_savefig(_get_residuals_plot(r['OLS']))

def get_html_msg(obj, periods=120):
    msg_template = '\n'.join([
        '<b>Estudo Long&Short (v3):</b>',
        'Par: <a href="%s">%s x %s</a>',
        'N# Periodos: %s',
        'Z-Score: %.2f',
        'ADF p-value: %.2f %%',
        'Ang. Coef.: %.2f',
        'Half-life: %.2f',
        'Hurst: %.2f',
    ])

    _x = obj.ticker_x.replace('.SA', '')
    _y = obj.ticker_y.replace('.SA', '')
    _p = str(periods)

    msg_html = msg_template % (
        f'https://zecontinha.com.br/b3/pair_stats/{_x}.SA/{_y}.SA',
        _x, _y, _p,
        obj.model_params[_p]['zscore'],
        obj.model_params[_p]['adf_pvalue'] * 100,
        obj.model_params[_p]['ang_coef'],
        obj.model_params[_p]['half_life'],
        obj.model_params[_p]['hurst'],
      )

    return msg_html

async def send_msg(msg_html, plot):
    async with bot:
        await bot.send_message(
            chat_id='@pythonfinancas',
            #chat_id=-1001389579694, # "Python e Finanças"
            message_thread_id=9973,
            text=msg_html,
            parse_mode=ParseMode.HTML)

        if not plot:
            return

        plot.seek(0) # Bug do retorno do ponteiro
        await bot.send_photo(
            chat_id='@pythonfinancas',
            message_thread_id=9973,
            photo=plot)

def build_top_pairs_message(qs, periods=120, top_n=3):
    top = select_top_pairs(qs, periods=periods, top_n=top_n)

    ranks = ["🥇", "🥈", "🥉"]
    lines = [f"TOP {top_n} Melhores Pares:"]

    for idx, obj in enumerate(top):
        x = obj.ticker_x.replace(".SA", "")
        y = obj.ticker_y.replace(".SA", "")
        link = f"https://zecontinha.com.br/b3/pair_stats/{x}.SA/{y}.SA"

        prefix = ranks[idx] if idx < 3 else f"{idx+1}."
        lines.append(f'{prefix} <a href="{link}">{x} x {y}</a>')

    return "\n".join(lines)

if __name__ == '__main__':

    market = 'BOVESPA'
    market_map = {'b3': 'BOVESPA', 'binance': 'BINANCE'}
    if len(sys.argv) > 1:
        assert sys.argv[1].lower() in market_map.keys(), f"sys.argv[1] must be: {'or '.join(tasks)}"
        market = market_map.get(sys.argv[1], market)

    if settings.DEBUG:
        qs = PairStats.objects.filter(market=market)
    else:
        qs = select_pairs(market=market,
            order_by=f'model_params__120__hurst')

    if not qs.exists():
        raise ValueError("No pairs found matching criteria")

    top3_message = build_top_pairs_message(qs, periods=120, top_n=3)
    asyncio.run(send_msg(top3_message, plot=None))

    obj = qs.first()
    msg_html = get_html_msg(obj)
    plot = get_plot(obj.ticker_x, obj.ticker_y)

    asyncio.run(send_msg(msg_html, plot))
