from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import FormView

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
        #from IPython import embed; embed()
        return super().form_valid(form)
