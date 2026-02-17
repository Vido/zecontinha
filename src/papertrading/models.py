from django.db import models
from django.contrib.auth import get_user_model

from dashboard.models import MARKET_CHOICES, Quotes
from dashboard.forms import PERIODO_CHOICE

class Trade(models.Model):

    user = models.ForeignKey(get_user_model(),
        on_delete=models.CASCADE)

    market = models.CharField(
        max_length=32,
        choices=MARKET_CHOICES,
        default='N/A',
    )

    periodo = models.IntegerField(choices=PERIODO_CHOICE)
    model_params = models.JSONField(default=dict)
    beta_rotation = models.JSONField(default=list, blank=True, null=True)

    ativo_x = models.CharField(max_length=32)
    ativo_y = models.CharField(max_length=32)

    # Para Bovespa. Para cryto talvez tenha que ser Decimal
    qnt_x = models.IntegerField()
    qnt_y = models.IntegerField()

    entry_x = models.FloatField()
    entry_y = models.FloatField()

    exit_x = models.FloatField(blank=True, null=True)
    exit_y = models.FloatField(blank=True, null=True)

    t_entry = models.DateField(auto_now_add=True)
    t_exit  = models.DateField(blank=True, null=True)

    def is_open(self):
        return self.exit_x is None and self.exit_y is None

    def display_quote(self):
        x_quote = self.exit_x if self.exit_x is not None else Quotes.objects.get(
            ticker=self.ativo_x).get_series()[-1]
        y_quote = self.exit_y if self.exit_y is not None else Quotes.objects.get(
            ticker=self.ativo_y).get_series()[-1]
        return "%.2f x %.2f" % (x_quote, y_quote)

    def display_pair(self):
        pair = "%s x %s" % (self.ativo_x, self.ativo_y)
        return pair.replace('.SA', '')

    def display_qnt(self):
        return "%s x %s" % (self.qnt_x, self.qnt_y)

    def display_zscore(self):
        return self.model_params.get(
            str(self.periodo), {}).get('zscore', 'N/A')

    def display_profit(self):
        """
            Revisar: Está apresentando resultados errados
            - Revisar dados de entrada com relação ao Z
            - Determinar qual é a ponta comprada
        """
        x_quote = self.exit_x if self.exit_x is not None else Quotes.objects.get(
            ticker=self.ativo_x).get_series()[-1]
        y_quote = self.exit_y if self.exit_y is not None else Quotes.objects.get(
            ticker=self.ativo_y).get_series()[-1]


        zscore = self.model_params.get(str(self.periodo), {})['zscore']
        if zscore > 0:
            b_quote, entry_b, qnt_b = 0, 0, 0
            s_quote, entry_s, qnt_s = 0, 0, 0
        else:
            b_quote, entry_b, qnt_b = 0, 0, 0
            s_quote, entry_s, qnt_s = 0, 0, 0

        entry_net = (self.qnt_y * self.entry_y) - (self.qnt_x * self.entry_x)
        open_net = (self.qnt_x * x_quote) - (self.qnt_y * y_quote)

        return open_net - entry_net
