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
    ativo_x = forms.ChoiceField(choices=ATIVOS_CHOICE)
    ativo_y = forms.ChoiceField(choices=ATIVOS_CHOICE)
    periodo = forms.ChoiceField(choices=PERIODO_CHOICE)
    intervalo = forms.ChoiceField(choices=INTERVALO_CHOICE)

    def get_context(self):
        context = {}
        ativo_x = self.cleaned_data['ativo_x']
        ativo_y = self.cleaned_data['ativo_y']
        data = cointegration.get_market_data(
            ativo_x,
            ativo_y,
            self.cleaned_data['periodo'],
            self.cleaned_data['intervalo']
        )
        series_x = data[('Close', ativo_x)]
        series_y = data[('Close', ativo_y)]
        test_params = cointegration.coint_model(series_x, series_y)
        #
        scatter_plot = cointegration.get_scatter_plot(
            series_x, series_y, test_params['OLS'],
            xlabel=ativo_x, ylabel=ativo_y)
        #
        residuals_plot = cointegration.get_residuals_plot(
            test_params['OLS'])
        #
        raw_plot = cointegration.get_raw_plot(series_x, series_y,
        	xlabel=ativo_x, ylabel=ativo_y)
        #
        context.update(test_params)
        context.update({
            'ativo_x': ativo_x,
            'ativo_y': ativo_y,
            'raw_data': zip(series_x.index, series_x, series_y),
            'scatter_plot': scatter_plot.decode("utf-8"),
            'residuals_plot': residuals_plot.decode("utf-8"),
            'raw_plot': raw_plot.decode("utf-8"),
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