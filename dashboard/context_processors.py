import json
import requests
from decouple import config
from django.shortcuts import redirect
from itertools import permutations

def g_recaptcha_site_key_processor(request):
    return {'g_recaptcha_site_key': config('G_RECAPTCHA_SITE_KEY')}

class RecaptchaMixin():

    def form_valid(self, form):
        if self.request.user.is_superuser:
            print("Superuser: Pulando o Recaptcha...")
            return

        response = requests.post('https://www.google.com/recaptcha/api/siteverify',
                data = {'secret': config('G_RECAPTCHA_SECRET_KEY'),
                        'remoteip': self.request.META.get('REMOTE_ADDR', ''),
                        'response': self.request.POST.get('g-recaptcha-response', '')})

        response_payload = json.loads(response.text)

        if not response_payload['success']:
            return redirect('https://www.youtube.com/watch?v=QH2-TGUlwu4')

def system_status(request):
    from dashboard.models import PairStats
    from coint.ibrx100 import  CARTEIRA_IBRX
    from coint.binance_futures import BINANCE_FUTURES
    return {
        'pairs_b3': PairStats.objects.filter(market='BOVESPA').count(),
        'b3_total': len(list(permutations(CARTEIRA_IBRX, 2))),
        'b3_update': PairStats.last_update(market='BOVESPA'),
        'b3_et': PairStats.estimated_time(market='BOVESPA'),
        #
        'pairs_binance': PairStats.objects.filter(market='BINANCE').count(),
        'binance_total': len(list(permutations(BINANCE_FUTURES, 2))),
        'binance_update': PairStats.last_update(market='BINANCE'),
        'binance_et': PairStats.estimated_time(market='BINANCE'),
    }
