from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField, ArrayField

from dashboard.models import MARKET_CHOICES

class Trade(models.Model):

    user = models.ForeignKey(get_user_model(),
        on_delete=models.CASCADE)

    market = models.CharField(
        max_length=2,
        choices=MARKET_CHOICES,
        default='N/A',
    )

    model_params = JSONField(default={})
    beta_rotation = ArrayField(models.FloatField(), blank=True)

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


    def set_params(self, pair_stats):
        # CointParams
        self.adf_pvalue = pair_stats.adf_pvalue
        self.resid_std = pair_stats.resid_std
        self.zscore = pair_stats.zscore
        self.ang_coef = pair_stats.ang_coef
        self.intercept = pair_stats.intercept
        self.last_resid = pair_stats.last_resid
        self.n_observ = pair_stats.n_observ
        self.timestamp_calc = pair_stats.timestamp_calc

        # PairStats
        self.ativo_x = pair_stats.ticker_x
        self.ativo_y = pair_stats.ticker_y
        self.entry_x = pair_stats.x_quote
        self.entry_y = pair_stats.y_quote

    @property
    def ratio(self):
        return (self.entry_x * self.ang_coef) - self.entry_y

    def calc_margin(money, leverage=5):
        direction = 1 if self.last_resid > 0 else -1
        qnt = money / self.ratio

        self.qnt_x = -direction * math.ceil(qnt * self.ang_coef)
        self.qnt_y = direction * math.ceil(qnt)
