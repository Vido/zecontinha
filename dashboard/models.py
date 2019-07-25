from django.db import models
from django.contrib.auth import get_user_model


class CointParams(models.Model):

    adf_pvalue = models.FloatField(null=True, blank=True)
    resid_std = models.FloatField(null=True, blank=True)
    ang_coef = models.FloatField(null=True, blank=True)
    intercept = models.FloatField(null=True, blank=True)
    last_resid = models.FloatField(null=True, blank=True)
    timestamp_calc = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

MARKET_CHOICES = (
    ('N/A', 'N/A'),
    ('BOVESPA', 'B3 Ações'),
    ('COINBASE', 'Coinbase (Crypo)'),
)


class PairStats(CointParams):
    """
        Essa tabela é recalculado todos os dias com os dados de fechamento
    """

    pair = models.CharField(max_length=32, unique=True)
    success = models.BooleanField(default=False)
    market = models.CharField(
        max_length=32,
        choices=MARKET_CHOICES,
        default='N/A',
    )

    ticker_x = models.CharField(max_length=32, unique=True)
    ticker_y = models.CharField(max_length=32, unique=True)
    x_quote = models.FloatField(null=True, blank=True)
    y_quote = models.FloatField(null=True, blank=True)


class Trade(CointParams):

    user = models.ForeignKey(get_user_model(),
        on_delete=models.CASCADE)

    ativo_x = models.CharField(max_length=32)
    ativo_y = models.CharField(max_length=32)
    market = models.CharField(
        max_length=2,
        choices=MARKET_CHOICES,
        default='N/A',
    )

    # Para Bovespa. Para cryto talvez tenha que ser Decimal
    qnt_x = models.IntegerField()
    qnt_y = models.IntegerField()

    entry_x = models.FloatField()
    entry_y = models.FloatField()

    exit_x = models.FloatField(blank=True, null=True)
    exit_y = models.FloatField(blank=True, null=True)

    t_entry = models.DateField(auto_now_add=True)
    t_exit  = models.DateField(blank=True, null=True)
