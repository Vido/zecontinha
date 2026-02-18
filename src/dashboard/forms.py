from django import forms

from coint.ibrx100 import  CARTEIRA_IBRX
from coint.binance_futures import BINANCE_FUTURES
from coint import cointegration
from dashboard.models import (
    PERIODOS_CALCULO,
    PERIODOS_CHOICE
)


# para facilitar a vida
drop_nan = cointegration.drop_nan
clean_timeseries = cointegration.clean_timeseries

# TODO: Move this variables to coint/config.py

#PERIODO_YFINANCE = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
PERIODO_YFINANCE = ['1mo', '3mo', '6mo', '1y']
# DADOS INTRADAY VEM COM NAN POR CAUSA DO LEILAO
#INTERVALO_YFINANCE = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
INTERVALO_YFINANCE = ['1d', '1h']

PERIODO_YF_CHOICE = zip(PERIODO_YFINANCE, PERIODO_YFINANCE)
INTERVALO_CHOICE = zip(INTERVALO_YFINANCE, INTERVALO_YFINANCE)

TICKERS_YFINANCE = [t+'.SA' for t in CARTEIRA_IBRX]

B3_ATIVOS_CHOICE = list(zip(TICKERS_YFINANCE, CARTEIRA_IBRX))
BINANCE_ATIVOS_CHOICE = list(zip(BINANCE_FUTURES, BINANCE_FUTURES))


class InputForm(forms.Form):
    # TODO: fazer autocomplete
    ativo_x = forms.ChoiceField(choices=B3_ATIVOS_CHOICE)
    # TODO: fazer autocomplete
    ativo_y = forms.ChoiceField(choices=B3_ATIVOS_CHOICE)
    periodo = forms.ChoiceField(choices=PERIODO_YF_CHOICE)
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

        _x = data[('Close', ativo_x)]
        _y = data[('Close', ativo_y)]
        series_x, series_y = clean_timeseries(_x, _y)

        plots_dict = cointegration.get_plot_context(series_x, series_y, ativo_x, ativo_y)
        context.update(plots_dict)

        return context


class FilterForm(forms.Form):

    periodo = forms.ChoiceField(
        label='Periodos',
        required=True,
        choices=PERIODOS_CHOICE
    )

    pvalue = forms.FloatField(
        label='ADF P-Valor (max)',
        #default=0.1,
        required=True,
        max_value=0.5,
        min_value=0.005,
        initial=0.05,
        widget=forms.NumberInput(attrs={'id': 'form_pvalue', 'step': "0.005"})
    )

    hurst = forms.FloatField(
        label='Hurst (max)',
        #default=0.1,
        required=False,
        max_value=1.0,
        min_value=0.01,
        initial=0.3,
        widget=forms.NumberInput(attrs={'id': 'form_hurst', 'step': "0.01"})
    )

    zscore = forms.FloatField(
        label='|Z-Score|',
        #default=0.1,
        required=True,
        max_value=6,
        min_value=0,
        initial=2.0,
        widget=forms.NumberInput(attrs={'id': 'form_zscore', 'step': "0.1"})
    )

    n_per_coint = forms.FloatField(
        label='Número Periodos Cointegrados',
        #default=0.1,
        required=False,
        max_value=len(PERIODOS_CALCULO),
        min_value=0,
        initial=5,
        widget=forms.NumberInput(attrs={'id': 'form_npercoint', 'step': "1"})
    )


class B3FilterForm(FilterForm):
    # Todo fazer autocomplete
    ticker = forms.ChoiceField(
        label='Ativo',
        required=True,
        choices=[('TODOS', 'Todos')] + B3_ATIVOS_CHOICE
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class BinanceFilterForm(FilterForm):
    # Todo fazer autocomplete
    ticker = forms.ChoiceField(
        label='Ativo',
        required=True,
        choices=[('TODOS', 'Todos')] + BINANCE_ATIVOS_CHOICE
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StatsForm(forms.Form):
    pvalue = forms.FloatField(
        label='ADF P-Valor (max)',
        required=True,
        max_value=0.5,
        min_value=0.01,
        initial=0.1,
        widget=forms.NumberInput(attrs={'id': 'form_pavalue', 'step': "0.01"})
        )
    zscore = forms.FloatField(
        label='|Z-Score|',
        required=True,
        max_value=5,
        min_value=0,
        initial=2.0,
        widget=forms.NumberInput(attrs={'id': 'form_pavalue', 'step': "0.1"})
        )
    periodo = forms.ChoiceField(
        label='Periodos',
        required=True,
        choices=PERIODOS_CHOICE
        )
