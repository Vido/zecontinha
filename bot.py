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
    -1001189309671, # "PdM - Homologação"
    -1001389579694, # "Python e Finanças"
]

def select_pair(n):
    from dashboard.models import PairStats, CointParams, Quotes
    qs = PairStats.objects.filter(success=True)
    qs = qs.filter(Q(model_params__120__adf_pvalue__lte=0.05) & (Q(model_params__120__zscore__gte=2.0) | Q(model_params__120__zscore__lte=-2.0)))
    return random.sample(set(qs), n)

def send_msg():

    # Sortear o par
    # rodar o modelo
    #get_residuals_plot()
    ps = select_pair(1)[0]

    msg_template = "<b>Estudo Long&Short do dia:</b>\n" \
              'Par: <a href="%s">%s x %s</a>\n' \
              "N# Periodos: %d\n" \
              "Z-Score: %.2f\n" \
              "ADF p-value: %.2f %%\n" \
              "Ang. Coef.: %.2f\n" \
              "Intercept: %.2f\n" \

    x_str = ps.pair.split( )[0].replace('.SA', '')
    y_str = ps.pair.split( )[1].replace('.SA', '')

    msg_str = msg_template % (
        'http://zecontinha.herokuapp.com/b3/pair_stats/%s/%s' % (x_str, y_str),
        x_str,
        y_str,
        120,
        ps.model_params['120']['zscore'],
        ps.model_params['120']['adf_pvalue'] * 100,
        ps.model_params['120']['ang_coef'],
        ps.model_params['120']['intercept'],
      )

    for chat_id in chat_id_list:
        bot.send_message(
                chat_id=chat_id,
                text=msg_str,
                parse_mode=telegram.ParseMode.HTML)

        #bot.send_photo(chat_id=chat_id, photo=open('tests/test.png', 'rb'))