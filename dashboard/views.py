import json
import requests

from django.views.generic.edit import FormView, FormMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.shortcuts import redirect, render_to_response
from django.shortcuts import get_object_or_404

from django.db.models import Q

from . import cointegration
from dashboard.models import PairStats
from dashboard.forms import InputForm, FilterForm, StatsForm


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
        self.period = periodo

        qs = PairStats.objects.filter(success=success)

        if success:
            qs = qs.filter(**{'model_params__%s__adf_pvalue__lte' % periodo: pvalue})
            qs = qs.filter(Q(**{'model_params__%s__zscore__gte' % periodo:zscore})
                         | Q(**{'model_params__%s__zscore__lte' % periodo:-zscore})) 

        if ticker != 'TODOS':
            qs = qs.filter(pair__icontains=ticker)

        return qs

    def get_context_data(self, **kwargs):
        context = super(BovespaListView, self).get_context_data(**kwargs)
        if context['object_list'].exists():
            obj = context['object_list'].latest('timestamp')
            more_context = {
                'period': self.period,
                'timestamp': obj.timestamp,
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


class PairStatsDetailView(DetailView, FormMixin):
    template_name = 'dashboard/pair_stats.html'
    model = PairStats
    form_class = StatsForm

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
            context['pvalue'] = float(pvalue)
            context['zscore'] = float(zscore)
        return context

    def form_valid(self, form):
        response = requests.post('https://www.google.com/recaptcha/api/siteverify',
                data = {'secret':'6LdXsq4UAAAAAGEzZfUt9XtpE0URlMSXK2VJ94ix',
                        'remoteip': self.request.META.get('REMOTE_ADDR', ''),
                        'response': self.request.POST.get('g-recaptcha-response', '')})

        response_payload = json.loads(response.text)

        if not response_payload['success']:
            return redirect('https://www.youtube.com/watch?v=QH2-TGUlwu4')
