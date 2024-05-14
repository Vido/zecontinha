from itertools import permutations

from django.views.generic.edit import FormView, FormMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from coint import cointegration
from dashboard.models import PairStats, Quotes
from dashboard.forms import InputForm, FilterForm, StatsForm
from dashboard.forms import B3FilterForm, BinanceFilterForm
from dashboard.context_processors import RecaptchaMixin


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


class Index(RecaptchaMixin, FormView):
    template_name = 'dashboard/base.html'
    form_class = InputForm
    success_url = '/'

    def get_context_data(self, *args, **kwargs):

        from coint.ibrx100 import  CARTEIRA_IBRX
        from coint.binance_futures import BINANCE_FUTURES

        context = super(FormMixin, self).get_context_data(*args, **kwargs)
        context['pairs_b3'] = PairStats.objects.filter(market='BOVESPA').count()
        context['pairs_binance'] = PairStats.objects.filter(market='BINANCE').count()
        context['b3_total'] = len(list(permutations(CARTEIRA_IBRX, 2)))
        context['binance_total'] = len(list(permutations(BINANCE_FUTURES, 2)))
        #
        context['b3_update'] = PairStats.last_update(market='BOVESPA')
        context['binance_update'] = PairStats.last_update(market='BINANCE')
        context['b3_et'] = PairStats.estimated_time(market='BOVESPA')
        context['binance_et'] = PairStats.estimated_time(market='BINANCE')

        return context

    def form_valid(self, form):
        super(RecaptchaMixin, self).form_valid(form)
        context = {}
        if form.cleaned_data['ativo_x'] != form.cleaned_data['ativo_y']:
            context = form.get_context()

        context['form'] = form
        return self.render_to_response(context)


class GenericListView(RecaptchaMixin, FormListView):
    template_name = 'dashboard/bovespa_list.html'
    success_url = '/'
    queryset = PairStats.objects.none()
    form_class = None
    market = None

    def get_queryset(self, **kwargs):

        form=kwargs['form']
        if not form.is_valid():
            return PairStats.objects.none()

        pvalue = form.cleaned_data['pvalue']
        ticker = form.cleaned_data['ticker']
        zscore = form.cleaned_data['zscore']
        zscore = form.cleaned_data['hurst']
        #n_per_coint = form.cleaned_data['n_per_coint']
        periodo = form.cleaned_data['periodo']

        self.period = periodo
        self.adf_pvalue = pvalue

        qs = PairStats.objects.filter(market=self.market)

        qs = qs.filter(**{'model_params__%s__adf_pvalue__lte' % periodo: pvalue})
        qs = qs.filter(**{'model_params__%s__hurst__lte' % periodo: pvalue})
        qs = qs.filter(Q(**{'model_params__%s__zscore__gte' % periodo: zscore})
                     | Q(**{'model_params__%s__zscore__lte' % periodo: -zscore}))

        if ticker != 'TODOS':
            qs = qs.filter(pair__icontains=ticker)

        # TODO
        #n_per_coint

        return qs

    def get_context_data(self, **kwargs):
        from papertrading.forms import TradeForm
        context = super(GenericListView, self).get_context_data(**kwargs)
        if context['object_list'].exists():
            obj = context['object_list'].latest('timestamp')
            more_context = {
                'period': self.period,
                'timestamp': obj.timestamp,
                'modal_form': TradeForm()
            }
            context.update(more_context)
        return context


class BovespaListView(GenericListView):
    form_class = B3FilterForm
    market = 'BOVESPA'


class BinanceListView(GenericListView):
    template_name = 'dashboard/binance_list.html'
    form_class = BinanceFilterForm
    success_url = '/'
    queryset = PairStats.objects.none()
    market = 'BINANCE'


class PairStatsDetailView(RecaptchaMixin, DetailView, FormMixin):
    template_name = 'dashboard/pair_stats.html'
    model = PairStats
    form_class = StatsForm
    success_url = '/'

    def post(self, request, *args, **kwargs):
        self.form = self.get_form()
        if self.form.is_valid():
            self.form_valid(self.form)
        else:
            self.form_invalid(self.form)

        return self.get(request, *args, **kwargs)

    def get_object(self):
        if hasattr(self, 'form'):
            return get_object_or_404(PairStats, ticker_x=self.kwargs['x'], ticker_y=self.kwargs['y'])
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super(PairStatsDetailView, self).get_context_data(**kwargs)
        if hasattr(self, 'form'):
            pvalue = self.form.cleaned_data['pvalue']
            zscore = self.form.cleaned_data['zscore']
            periodo = self.form.cleaned_data['periodo']

            beta_plot = cointegration.get_beta_plot(context['object'].beta_rotation)

            context['pvalue'] = float(pvalue)
            context['zscore'] = float(zscore)
            context['beta_plot'] = beta_plot.decode("utf-8")
            context['period'] = periodo

            try:
                periodo = int(periodo)
                ativo_x = self.kwargs['x']
                ativo_y = self.kwargs['y']
                _x = Quotes.objects.get(ticker=ativo_x).get_series()[-periodo:]
                _y = Quotes.objects.get(ticker=ativo_y).get_series()[-periodo:]
                series_x, series_y = cointegration.clean_timeseries(_x, _y)
                plot_context = cointegration.get_plot_context(series_x, series_y, ativo_x, ativo_y)
            except Exception as e:
                print(e)
                plot_context = {'resultados': False}

            context.update(plot_context)

        return context
