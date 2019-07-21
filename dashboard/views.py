import json
import requests

from django import forms
from django.views.generic.edit import FormView
from django.shortcuts import redirect, render_to_response

from . import ibov
from . import cointegration


#PERIODO_YFINANCE = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
PERIODO_YFINANCE = ['1mo', '3mo', '6mo', '1y']
# DADOS INTRADAY VEM COM NAN POR CAUSA DO LEILAO
#INTERVALO_YFINANCE = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
INTERVALO_YFINANCE = ['1d']
TICKERS_YFINANCE = [t+'.SA' for t in ibov.CARTEIRA_IBOV]

ATIVOS_CHOICE = list(zip(TICKERS_YFINANCE, ibov.CARTEIRA_IBOV))
PERIODO_CHOICE = zip(PERIODO_YFINANCE, PERIODO_YFINANCE)
INTERVALO_CHOICE = zip(INTERVALO_YFINANCE, INTERVALO_YFINANCE)

class InputForm(forms.Form):
    ativo_a = forms.ChoiceField(choices=ATIVOS_CHOICE)
    ativo_b = forms.ChoiceField(choices=ATIVOS_CHOICE)
    periodo = forms.ChoiceField(choices=PERIODO_CHOICE)
    intervalo = forms.ChoiceField(choices=INTERVALO_CHOICE)

    def get_context(self):
        context = {}
        ativo_a = self.cleaned_data['ativo_a']
        ativo_b = self.cleaned_data['ativo_b']
        data = cointegration.get_market_data(
            ativo_a,
            ativo_b,
            self.cleaned_data['periodo'],
            self.cleaned_data['intervalo']
        )
        series_a = data[('Close', ativo_a)]
        series_b = data[('Close', ativo_b)]
        test_params = cointegration.coint_model(series_a, series_b)

        context.update(test_params)
        context.update({
            'series_a': series_a,
            'series_b': series_b,
            'resultados': True,
        })
        return context

class Index(FormView):
    template_name = 'dashboard/base.html'
    form_class = InputForm
    success_url = '/'

    def form_valid(self, form):

        response = requests.post('https://www.google.com/recaptcha/api/siteverify',
                data = {'secret':'6LdXsq4UAAAAAGEzZfUt9XtpE0URlMSXK2VJ94ix',
                        'remoteip': self.request.META.get('REMOTE_ADDR', ''),
                        'response': self.request.POST.get('g-recaptcha-response', '')})

        response_payload = json.loads(response.text)

        if not response_payload['success']:
            return redirect('https://www.youtube.com/watch?v=QH2-TGUlwu4')

        context = form.get_context()
        context['form'] = form

        return self.render_to_response(context)
