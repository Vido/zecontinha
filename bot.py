import os
import asyncio
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")

import django
django.setup()

import telegram
from decouple import config
from django.db.models import Q
from django.conf import settings

from dashboard.models import PairStats, Quotes

telegram_api_key = config('TELEGRAM_API_KEY')
bot = telegram.Bot(telegram_api_key)
#chat_id = config('TELEGRAM_CHAT_ID', '@pythonfinancas')

def select_pairs(
    adf_pvalue_threshold=0.05,
    hurst_threshold=0.3,
    zscore_threshold=2.0,
    periods=120,
    order_by='?'
):
    positive_z_filter = {f'model_params__{periods}__zscore__gte': zscore_threshold}
    negative_z_filter = {f'model_params__{periods}__zscore__lte': -zscore_threshold}
    exclude_adf_hurst_filter = {
        f'model_params__{periods}__adf_pvalue__gte': adf_pvalue_threshold,
        f'model_params__{periods}__hurst__gte': hurst_threshold,
    }

    queryset = PairStats.objects.filter(
        Q(**positive_z_filter) | Q(**negative_z_filter)
    ).exclude(**exclude_adf_hurst_filter)

    return queryset.order_by(order_by)

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

    msg_str = msg_template % (
        f'https://zecontinha.com.br/b3/pair_stats/{_x}.SA/{_y}.SA',
        _x, _y, _p,
        obj.model_params[_p]['zscore'],
        obj.model_params[_p]['adf_pvalue'] * 100,
        obj.model_params[_p]['ang_coef'],
        obj.model_params[_p]['half_life'],
        obj.model_params[_p]['hurst'],
      )

    return msg_str

async def send_msg():

    if settings.DEBUG:
        qs = PairStats.objects.all()
    else:
        qs = select_pairs(
            order_by=f'model_params__120__hurst')

    if not qs.exists():
        raise ValueError("No pairs found matching criteria")

    obj = qs.first()
    msg_str = get_html_msg(obj)
    plot = get_plot(obj.ticker_x, obj.ticker_y)

    async with bot:
        await bot.send_message(
            chat_id='@pythonfinancas',
            #chat_id=-1001389579694, # "Python e Finanças"
            message_thread_id=9973,
            text=msg_str,
            parse_mode=telegram.constants.ParseMode.HTML)

        if not plot:
            return

        plot.seek(0) # Bug do retorno do ponteiro
        await bot.send_photo(
            chat_id='@pythonfinancas',
            message_thread_id=9973,
            photo=plot)

if __name__ == '__main__':
    asyncio.run(send_msg())