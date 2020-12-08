import pandas as pd

from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField


class CointParams(models.Model):

    adf_pvalue = models.FloatField(null=True, blank=True)
    resid_std = models.FloatField(null=True, blank=True)
    zscore = models.FloatField(null=True, blank=True)
    ang_coef = models.FloatField(null=True, blank=True)
    intercept = models.FloatField(null=True, blank=True)
    last_resid = models.FloatField(null=True, blank=True)
    n_observ = models.IntegerField(null=True, blank=True)
    timestamp_calc = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    #TODO: Marcar o periodo

    class Meta:
        abstract = True

MARKET_CHOICES = (
    ('N/A', 'N/A'),
    ('BOVESPA', 'B3 (Ações Brasileiras)'),
    ('BINANCE', 'Binance Futures (Crypto)'),
)

class Quotes(models.Model):

    market = models.CharField(
        max_length=32,
        choices=MARKET_CHOICES,
        default='N/A',
    )

    ticker = models.CharField(max_length=32)
    hquotes = ArrayField(models.FloatField(), blank=True)
    htimestamps = ArrayField(models.DateField(), blank=True)

    def __str__(self):
        return self.ticker + " [%d]" % len(self.hquotes)

    def get_series(self):
        return pd.Series(self.hquotes, index=self.htimestamps)



class BasePairStats(models.Model):
    """
        Essa tabela é recalculado todos os dias com os dados de fechamento
    """

    class Meta:
        abstract = True

    market = models.CharField(
        max_length=32,
        choices=MARKET_CHOICES,
        default='N/A',
    )

    ticker_x = models.CharField(max_length=32)
    ticker_y = models.CharField(max_length=32)

    # Ultima cotação
    x_quote = models.FloatField(null=True, blank=True)
    y_quote = models.FloatField(null=True, blank=True)
    success = models.BooleanField(default=False)

    model_params = JSONField(default=dict)
    beta_rotation = ArrayField(models.FloatField(), blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def display_pair(self):
        return self.pair.replace('.SA', '').replace(' ', 'x')

    def n_p_coint(self, pvalue):
        """ Número de Periodos Cointegrados """
        counter = 0
        for key, obj in self.model_params.items():
            if not obj.get('success', False):
                continue
            if obj.get('adf_pvalue', '') < pvalue:
                counter += 1
        return counter

class PairStats(BasePairStats):
    pair = models.CharField(max_length=32, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
