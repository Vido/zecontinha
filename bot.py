import os
import django
import asyncio
from collections import defaultdict
from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

import random
import telegram
from decouple import config
from django.db.models import Q
from django.conf import settings

from dashboard.models import PairStats, Quotes

#chat_id = config('TELEGRAM_CHAT_ID', cast=int)
telegram_api_key = config('TELEGRAM_API_KEY')
bot = telegram.Bot(telegram_api_key)

chat_id_list = [
    #-1001164319166, # "Papo de Mercado 📈📉📊"
    #-1001189309671, # "PdM - Homologação"
    -1001389579694, # "Python e Finanças"
]

def get_pairs(
    adf_pvalue_threshold=0.05,
    hurst_threshold=0.3,
    zscore_threshold=2.0,
    periods=120,
    order_by_field='hurst' # 'hurst', 'random'
):
    """
    Select, filter and order PairStats objects based on statistical thresholds.
    """
    positive_z_filter = {f'model_params__{periods}__zscore__gte': zscore_threshold}
    negative_z_filter = {f'model_params__{periods}__zscore__lte': -zscore_threshold}
    exclude_adf_hurst_filter = {
        f'model_params__{periods}__adf_pvalue__gte': adf_pvalue_threshold,
        f'model_params__{periods}__hurst__gte': hurst_threshold,
    }

    queryset = PairStats.objects.filter(
        Q(**positive_z_filter) | Q(**negative_z_filter)
    ).exclude(**exclude_adf_hurst_filter)

    order_by_queries = {
        'hurst': f'model_params__{periods}__hurst',
        'random': '?',
    }

    order_field = order_by_queries.get(order_by_field, order_by_queries['hurst'])
    queryset = queryset.order_by(order_field)

    return queryset if queryset.exists() else None


def get_plot(x_ticker, y_ticker):
  from coint.cointegration import fp_savefig, _get_residuals_plot
  from coint.cointegration import coint_model, clean_timeseries

  _x = Quotes.objects.get(ticker=x_ticker).get_series()
  _y = Quotes.objects.get(ticker=y_ticker).get_series()
  series_x, series_y = clean_timeseries(_x, _y)

  r = coint_model(series_x[-120:], series_y[-120:])
  return fp_savefig(_get_residuals_plot(r['OLS']))

def get_html_msg(ps):
    msg_template = "<b>Estudo Long&Short (v3):</b>\n" \
              'Par: <a href="%s">%s x %s</a>\n' \
              "N# Periodos: %d\n" \
              "Z-Score: %.2f\n" \
              "ADF p-value: %.2f %%\n" \
              "Ang. Coef.: %.2f\n" \
              "Half-life: %.2f\n" \
              "Hurst: %.2f\n" \

    _x = ps.ticker_x.replace('.SA', '')
    _y = ps.ticker_y.replace('.SA', '')

    msg_str = msg_template % (
        'http://zecontinha.com.br/b3/pair_stats/%s.SA/%s.SA' % (_x, _y), _x, _y,
        120,
        ps.model_params['120']['zscore'],
        ps.model_params['120']['adf_pvalue'] * 100,
        ps.model_params['120']['ang_coef'],
        ps.model_params['120']['half_life'],
        ps.model_params['120']['hurst'],
      )

    return msg_str

def _get_msg_and_plot():
    """
    Asynchronously fetches cointegrated stock pair data, generates a plot;
    """
    if settings.DEBUG:
        ps_qs = PairStats.objects.all()
        ps = ps_qs[0]
    else:
        pairs = get_pairs(order_by_field='hurst')
        if not pairs:
            raise ValueError("No pairs found matching criteria")
        ps = pairs.first()
        
    msg_str = get_html_msg(ps)
    plot = get_plot(ps.ticker_x, ps.ticker_y)
    
    return msg_str, plot

async def send_msg():
    try:
        msg_str, plot = await sync_to_async(_get_msg_and_plot, thread_sensitive=True)()
    except Exception as e:
        msg_str, plot = str(e), None

    await bot.send_message(
            chat_id='@pythonfinancas',
            #chat_id=-1001389579694, # "Python e Finanças"
            message_thread_id=9973,
            text=msg_str,
            parse_mode=telegram.constants.ParseMode.HTML)

    if plot:
        plot.seek(0) # Bug do retorno do ponteiro
        await bot.send_photo(
                chat_id='@pythonfinancas',
                message_thread_id=9973,
                photo=plot)

if __name__ == '__main__':
    asyncio.run(send_msg())
