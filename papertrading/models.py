from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField, ArrayField

from dashboard.models import MARKET_CHOICES

class Trade(models.Model):

    user = models.ForeignKey(get_user_model(),
        on_delete=models.CASCADE)

    market = models.CharField(
        max_length=32,
        choices=MARKET_CHOICES,
        default='N/A',
    )

    model_params = JSONField(default={})
    beta_rotation = ArrayField(models.FloatField(), blank=True, null=True)

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
        self.model_params['adf_pvalue'] = pair_stats.adf_pvalue
        self.model_params['resid_std'] = pair_stats.resid_std
        self.model_params['zscore'] = pair_stats.zscore
        self.model_params['ang_coef'] = pair_stats.ang_coef
        self.model_params['intercept'] = pair_stats.intercept
        self.model_params['last_resid'] = pair_stats.last_resid
        self.model_params['n_observ'] = pair_stats.n_observ
        self.model_params['timestamp_calc'] = pair_stats.timestamp_calc