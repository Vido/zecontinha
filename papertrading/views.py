from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.utils import timezone

from dashboard.models import PairStats
from .models import Trade
from .forms import TradeForm, ExitTradeForm


class TradesListView(LoginRequiredMixin, ListView):

    model = Trade

    def get_queryset(self):
        return Trade.objects.filter(
            user=self.request.user).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(TradesListView, self).get_context_data(**kwargs)
        if context['object_list'].exists():
            more_context = {
                'modal_form': ExitTradeForm()
            }
            context.update(more_context)
        return context


class EnterTradesFormView(LoginRequiredMixin, FormView):

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
            periodo=form.cleaned_data['periodo'],
            beta_rotation=pstats.beta_rotation,
            ativo_x=pstats.ticker_x,
            ativo_y=pstats.ticker_y,
            qnt_x=form.cleaned_data['qnt_x'],
            qnt_y=form.cleaned_data['qnt_y'],
            entry_x=form.cleaned_data['entry_x'],
            entry_y=form.cleaned_data['entry_y'],
            t_entry=timezone.now()
        )

        return super().form_valid(form)

    #def form_invalid(self, form):
    #    from IPython import embed; embed()
    #    return super().form_invalid(form)

class ExitTradesFormView(LoginRequiredMixin, FormView):

    model = Trade
    form_class = ExitTradeForm
    success_url = reverse_lazy('blotter')

    def form_valid(self, form):

        trade_id = form.cleaned_data['trade_id']
        obj = Trade.objects.get(
            id=trade_id, user=self.request.user)
        obj.exit_x = form.cleaned_data['exit_x']
        obj.exit_y = form.cleaned_data['exit_y']
        obj.t_exit = timezone.now()
        obj.save()

        return super().form_valid(form)

    #def form_invalid(self, form):
    #    from IPython import embed; embed()
    #    return super().form_invalid(form)