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
    # TODO: Revisar
    qs = PairStats.objects.filter(
      Q(model_params__120__adf_pvalue__lte=0.05) &
      Q(model_params__120__hurst__lte=0.3) &
      (Q(model_params__120__zscore__gte=2.0) | Q(model_params__120__zscore__lte=-2.0)))
    return random.sample(set(qs), n)

def get_plot(x_ticker, y_ticker):
  from coint.cointegration import fp_savefig, _get_residuals_plot
  from coint.cointegration import coint_model, clean_timeseries

  _x = Quotes.objects.get(ticker=x_ticker).get_series()
  _y = Quotes.objects.get(ticker=y_ticker).get_series()
  series_x, series_y = clean_timeseries(_x, _y)

  r = coint_model(series_x[-120:], series_y[-120:])
  return fp_savefig(_get_residuals_plot(r['OLS']))

def get_msg_plot(ps):
    msg_template = (
        "<b>Estudo Long&Short (v2):</b>\n"
        'Par: <a href="%s">%s x %s</a>\n'
        "N# Periodos: %d\n"
        "Z-Score: %.2f\n"
        "ADF p-value: %.2f %%\n"
        "Ang. Coef.: %.2f\n"
        "Half-life: %.2f\n"
        "Hurst: %.2f\n"
    )

    _x = ps.ticker_x.replace('.SA', '')
    _y = ps.ticker_y.replace('.SA', '')

    model_params = ps.model_params.get('120', {})

    zscore = model_params.get('zscore', 0.0)

    adf_pvalue = model_params.get('adf_pvalue')
    adf_pvalue_pct = adf_pvalue * 100 if adf_pvalue is not None else 0.0

    ang_coef = model_params.get('ang_coef', 0.0)
    half_life = model_params.get('half_life', 0.0)
    hurst = model_params.get('hurst', 0.0)

    msg_str = msg_template % (
        f"http://zecontinha.com.br/b3/pair_stats/{_x}.SA/{_y}.SA",
        _x,
        _y,
        120,
        zscore,
        adf_pvalue_pct,
        ang_coef,
        half_life,
        hurst,
    )

    plot = get_plot(ps.ticker_x, ps.ticker_y)

    return msg_str, plot

def send_msg():
        
    try:
        if settings.DEBUG:
            ps_qs = PairStats.objects.all()
            ps = ps_qs[0]
        else:
            ps = select_pair(1)[0]
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
