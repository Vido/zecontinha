import json
import requests
from decouple import config
from django.shortcuts import redirect

def g_recaptcha_site_key_processor(request):
    return {config('G_RECAPTCHA_SITE_KEY')}

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
