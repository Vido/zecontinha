import os
import sys
import django

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

def select_pair(n):
    """
    Select n random PairStats objects filtered by specific model_params criteria.

    Uses order_by('?') for random sampling in the database.

    Returns a list of PairStats instances or an empty list if none found.
    """

    qs = PairStats.objects.filter(
        model_params__120__adf_pvalue__lte=0.05,
        model_params__120__hurst__lte=0.3
    ).filter(
        Q(model_params__120__zscore__gte=2.0) | Q(model_params__120__zscore__lte=-2.0)
    )

    count = qs.count()
    if count == 0:
        return []

    # If n is greater than count, limit to the maximum available
    n = min(n, count)

    # Random sampling directly in the database
    random_qs = qs.order_by('?')[:n]

    return list(random_qs)


def get_plot(x_ticker, y_ticker):
  from coint.cointegration import fp_savefig, _get_residuals_plot
  from coint.cointegration import coint_model, clean_timeseries

  _x = Quotes.objects.get(ticker=x_ticker).get_series()
  _y = Quotes.objects.get(ticker=y_ticker).get_series()
  series_x, series_y = clean_timeseries(_x, _y)

  r = coint_model(series_x[-120:], series_y[-120:])
  return fp_savefig(_get_residuals_plot(r['OLS']))

def get_msg_plot(ps):

    msg_template = "<b>Estudo Long&Short (v2):</b>\n" \
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

    plot = get_plot(ps.ticker_x, ps.ticker_y)

    return msg_str, plot 

def send_msg():
        
    try:
        if settings.DEBUG:
            ps_qs = PairStats.objects.all()
            ps = ps_qs[0]
        else:
            pairs = select_pair(1)
            if not pairs:
                raise ValueError("No pairs found matching criteria")
            ps = pairs[0]
        msg_str, plot = get_msg_plot(ps)

    except Exception as e:
        msg_str, plot = str(e), None

    bot.send_message(
            chat_id='@pythonfinancas',
            #chat_id=-1001389579694, # "Python e Finanças"
            message_thread_id=9973,
            text=msg_str,
            parse_mode=telegram.ParseMode.HTML)

    if plot:
        bot.send_photo(
                chat_id='@pythonfinancas',
                message_thread_id=9973,
                photo=plot)
        plot.seek(0) # Bug do retorno do ponteiro

if __name__ == '__main__':
    send_msg()
