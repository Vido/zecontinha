from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.utils import timezone

from dashboard.models import PairStats
from .models import Trade
from .forms import TradeForm


class TradesListView(LoginRequiredMixin, ListView):

    model = Trade

    def get_queryset(self):
        return Trade.objects.filter(
            user=self.request.user).order_by('-id')


class TradesFormView(LoginRequiredMixin, FormView):

    model = Trade
    form_class = TradeForm
    success_url = reverse_lazy('blotter')

    def form_valid(self, form):

        pstats_id = form.cleaned_data['pair_stats_id']
        pstats = PairStats.objects.get(id=pstats_id)

        trade = Trade.objects.create(
            user=self.request.user,
            market='BOVESPA',
            model_params=pstats.model_params,
            beta_rotation=pstats.beta_rotation,
            ativo_x=pstats.ticker_x,
            ativo_y=pstats.ticker_x,
            qnt_x=form.cleaned_data['qnt_x'],
            qnt_y=form.cleaned_data['qnt_y'],
            entry_x=form.cleaned_data['entry_x'],
            entry_y=form.cleaned_data['entry_y'],
            t_entry=timezone.now()
        )

        #from IPython import embed; embed()

        return super().form_valid(form)
