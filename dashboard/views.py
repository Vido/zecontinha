import json
import requests

from django import forms
from django.views.generic.edit import FormView, FormMixin
from django.views.generic.list import ListView
from django.shortcuts import redirect, render_to_response
from django.db.models import Q

from dashboard.models import PairStats

from . import ibov
from . import cointegration


class FormListView(ListView, FormMixin):
    def get(self, request, *args, **kwargs):
        # From ProcessFormMixin
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        # From BaseListView
        self.object_list = self.get_queryset(form=self.form)

        context = self.get_context_data(object_list=self.object_list, form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.form_valid(form)
        else:
            self.form_invalid(form)

        return self.get(request, *args, **kwargs)


#PERIODO_YFINANCE = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
PERIODO_YFINANCE = ['1mo', '3mo', '6mo', '1y']
# DADOS INTRADAY VEM COM NAN POR CAUSA DO LEILAO
#INTERVALO_YFINANCE = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
INTERVALO_YFINANCE = ['1h', '1d']
TICKERS_YFINANCE = [t+'.SA' for t in ibov.CARTEIRA_IBOV]

ATIVOS_CHOICE = list(zip(TICKERS_YFINANCE, ibov.CARTEIRA_IBOV))
PERIODO_CHOICE = zip(PERIODO_YFINANCE, PERIODO_YFINANCE)
INTERVALO_CHOICE = zip(INTERVALO_YFINANCE, INTERVALO_YFINANCE)
PERIODOS_CALCULO = list(range(20,260,20))
PERIODOS_CHOICE = zip(PERIODOS_CALCULO, PERIODOS_CALCULO)


class InputForm(forms.Form):
    # Todo fazer autocomplete
    ativo_x = forms.ChoiceField(choices=ATIVOS_CHOICE)
    # Todo fazer autocomplete
    ativo_y = forms.ChoiceField(choices=ATIVOS_CHOICE)
    periodo = forms.ChoiceField(choices=PERIODO_CHOICE)
    intervalo = forms.ChoiceField(choices=INTERVALO_CHOICE)

    def get_context(self):
        context = {}
        ativo_x = self.cleaned_data['ativo_x']
        ativo_y = self.cleaned_data['ativo_y']
        data = cointegration.get_market_data(
            [ativo_x, ativo_y],
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
        # TODO: Usar HighCharts
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

        context = {}
        if form.cleaned_data['ativo_x'] != form.cleaned_data['ativo_y']:
            context = form.get_context()

        context['form'] = form
        return self.render_to_response(context)


class FilterForm(forms.Form):
    # Todo fazer autocomplete
    ticker = forms.ChoiceField(
        label='Ativo',
        required=True,
        choices=[('TODOS', 'Todos')]+ATIVOS_CHOICE)
    periodo = forms.ChoiceField(
        label='Periodos',
        required=True,
        choices=PERIODOS_CHOICE
        )
    pvalue = forms.FloatField(
        label='ADF P-Valor (max)',
        #default=0.1,
        required=True,
        max_value=1,
        min_value=0,
        initial=0.1,
        widget=forms.NumberInput(attrs={'id': 'form_pavalue', 'step': "0.01"})
        )
    zscore = forms.FloatField(
        label='|Z-Score|',
        #default=0.1,
        required=True,
        max_value=6,
        min_value=0,
        initial=2.0,
        widget=forms.NumberInput(attrs={'id': 'form_pavalue', 'step': "0.01"})
        )
    success = forms.BooleanField(
        label='Calc. c/ Sucesso',
        required=False,
        initial=True)


class BovespaListView(FormListView):
    template_name = 'dashboard/bovespa_list.html'
    form_class = FilterForm
    success_url = '/'
    queryset = PairStats.objects.none()

    def get_queryset(self, **kwargs):

        form=kwargs['form']
        if not form.is_valid():
            return PairStats.objects.none()

        success = form.cleaned_data['success']
        pvalue = form.cleaned_data['pvalue']
        ticker = form.cleaned_data['ticker']
        zscore = form.cleaned_data['zscore']
        periodo = form.cleaned_data['periodo']

        qs = PairStats.objects.filter(success=success, n_observ=periodo)

        if success:
            qs = qs.filter(adf_pvalue__lte=pvalue)
            qs = qs.filter(Q(zscore__gte=zscore) | Q(zscore__lte=-zscore)) 

        if ticker != 'TODOS':
            qs = qs.filter(pair__icontains=ticker)

        return qs

    def get_context_data(self, **kwargs):
        context = super(BovespaListView, self).get_context_data(**kwargs)
        if context['object_list'].exists():
            obj = context['object_list'].latest('timestamp_calc')
            more_context = {
                'n_observ': obj.n_observ,
                'timestamp_calc': obj.timestamp_calc,
            }
            context.update(more_context)
        return context

    def form_valid(self, form):

        response = requests.post('https://www.google.com/recaptcha/api/siteverify',
                data = {'secret':'6LdXsq4UAAAAAGEzZfUt9XtpE0URlMSXK2VJ94ix',
                        'remoteip': self.request.META.get('REMOTE_ADDR', ''),
                        'response': self.request.POST.get('g-recaptcha-response', '')})

        response_payload = json.loads(response.text)

        if not response_payload['success']:
            return redirect('https://www.youtube.com/watch?v=QH2-TGUlwu4')


class PairStatsListView(ListView):
    template_name = 'dashboard/pair_stats.html'
    success_url = '/'
    queryset = PairStats.objects.none()

    # TODO
    def get_queryset(self, **kwargs):
        #from IPython import embed; embed()
        qs = PairStats.objects.filter(success=True)
