from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Trade


class TradesListView(LoginRequiredMixin, ListView):

    model = Trade

    def get_queryset(self):
        return Trade.objects.filter(
        	user=self.request.user).order_by('-id')