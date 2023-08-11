import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

import random
import telegram
from decouple import config
from django.db.models import Q

#chat_id = config('TELEGRAM_CHAT_ID', cast=int)
telegram_api_key = config('TELEGRAM_API_KEY')
bot = telegram.Bot(telegram_api_key)

chat_id_list = [
    #-1001164319166, # "Papo de Mercado 📈📉📊"
    #-1001189309671, # "PdM - Homologação"
    -1001389579694, # "Python e Finanças"
]

def select_pair(n):
    from dashboard.models import PairStats, CointParams, Quotes
    qs = PairStats.objects.filter(success=True)
    qs = qs.filter(
      Q(model_params__120__adf_pvalue__lte=0.05) & (Q(model_params__120__zscore__gte=2.0) | Q(model_params__120__zscore__lte=-2.0)))
    return random.sample(set(qs), n)

def get_plot(x_ticker, y_ticker):
  from dashboard.models import PairStats, CointParams, Quotes
  from coint.cointegration import fp_savefig, _get_residuals_plot
  from coint.cointegration import coint_model, clean_timeseries

  _x = Quotes.objects.get(ticker=x_ticker).get_series()
  _y = Quotes.objects.get(ticker=y_ticker).get_series()
  series_x, series_y = clean_timeseries(_x, _y)

  r = coint_model(series_x[-120:], series_y[-120:])
  return fp_savefig(_get_residuals_plot(r['OLS']))

def send_msg():

    ps = select_pair(1)[0]

    msg_template = "<b>Estudo Long&Short do dia:</b>\n" \
              'Par: <a href="%s">%s x %s</a>\n' \
              "N# Periodos: %d\n" \
              "Z-Score: %.2f\n" \
              "ADF p-value: %.2f %%\n" \
              "Ang. Coef.: %.2f\n" \
              "Intercept: %.2f\n" \

    _x = ps.ticker_x.replace('.SA', '')
    _y = ps.ticker_y.replace('.SA', '')

    msg_str = msg_template % (
        'http://zecontinha.com.br/b3/pair_stats/%s.SA/%s.SA' % (_x, _y),
        _x, _y,
        120,
        ps.model_params['120']['zscore'],
        ps.model_params['120']['adf_pvalue'] * 100,
        ps.model_params['120']['ang_coef'],
        ps.model_params['120']['intercept'],
      )

    plot = get_plot(ps.ticker_x, ps.ticker_y)

    for chat_id in chat_id_list:
        bot.send_message(
                chat_id=chat_id,
                message_thread_id=9973,
                text=msg_str,
                parse_mode=telegram.ParseMode.HTML)

        bot.send_photo(
                chat_id=chat_id,
                message_thread_id=9973,
                photo=plot)

        # Bug do retorno do ponteiro
        plot.seek(0)

if __name__ == '__main__':
    send_msg()
