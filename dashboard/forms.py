from django import forms

from . import ibov
from . import cointegration

# para facilitar a vida
drop_nan = cointegration.drop_nan
match_timeseries = cointegration.match_timeseries

#PERIODO_YFINANCE = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
PERIODO_YFINANCE = ['1mo', '3mo', '6mo', '1y']
# DADOS INTRADAY VEM COM NAN POR CAUSA DO LEILAO
#INTERVALO_YFINANCE = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
INTERVALO_YFINANCE = ['1d', '1h']
TICKERS_YFINANCE = [t+'.SA' for t in ibov.CARTEIRA_IBOV]

PERIODO_CHOICE = zip(PERIODO_YFINANCE, PERIODO_YFINANCE)
INTERVALO_CHOICE = zip(INTERVALO_YFINANCE, INTERVALO_YFINANCE)
PERIODOS_CALCULO = list(range(40,260,20))
PERIODOS_CHOICE = list(zip(PERIODOS_CALCULO, PERIODOS_CALCULO))
ATIVOS_CHOICE = list(zip(TICKERS_YFINANCE, ibov.CARTEIRA_IBOV))


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

        _x = drop_nan(data[('Close', ativo_x)])
        _y = drop_nan(data[('Close', ativo_y)])
        series_x, series_y = match_timeseries(_x, _y)

        plots_dict = cointegration.get_plot_context(series_x, series_y, ativo_x, ativo_y)
        context.update(plots_dict)

        return context


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


class StatsForm(forms.Form):
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

    periodo = forms.ChoiceField(
        label='Periodos',
        required=True,
        choices=PERIODOS_CHOICE
        )