import pandas as pd
from django.db import models

PERIODOS_CALCULO = list(range(60,260,20))
PERIODOS_CHOICE = list(zip(PERIODOS_CALCULO, PERIODOS_CALCULO))

class CointParams(models.Model):

    pair = models.ForeignKey(
        'PairStats',
        related_name='coint_params',
        on_delete=models.CASCADE
    )

    period = models.IntegerField(choices=PERIODOS_CHOICE)

    adf_pvalue = models.FloatField(null=True, blank=True)
    resid_std = models.FloatField(null=True, blank=True)
    zscore = models.FloatField(null=True, blank=True)
    ang_coef = models.FloatField(null=True, blank=True)
    intercept = models.FloatField(null=True, blank=True)
    last_resid = models.FloatField(null=True, blank=True)
    half_life = models.FloatField(null=True, blank=True)
    hurst = models.FloatField(null=True, blank=True)
    n_observ = models.IntegerField(null=True, blank=True)

    timestamp_calc = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    class Meta:
        unique_together = ('pair', 'period')
        indexes = [
            models.Index(fields=['pair', 'period']),
        ]

    def __str__(self):
        return f'{self.pair} [{self.period}]'

    @classmethod
    def create(cls, pair, period, success, test_params=None, analysis_params=None):
        test_params = test_params or {}
        analysis_params = analysis_params or {}

        obj = cls(pair=pair, period=period, success=success)

        if not success:
            return obj

        try:
            obj.adf_pvalue = test_params['ADF'][1]
            obj.resid_std = test_params['OLS'].resid.std()
            obj.last_resid = test_params['OLS'].resid.iloc[-1]
            obj.ang_coef = test_params['OLS'].params.x1
            obj.intercept = test_params['OLS'].params.const
            obj.n_observ = len(test_params['OLS'].resid)
            obj.zscore = obj.last_resid / obj.resid_std
            obj.success = True
        except Exception as e:
            obj.success = False
            print(e)

        try:
            obj.half_life = analysis_params['OUHL']
        except Exception as e:
            print(e)

        try:
            obj.hurst = analysis_params['RSHD'][0]
        except Exception as e:
            print(e)

        return obj


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
    # TODO: Normalize
    hquotes = models.JSONField(default=list, blank=True)
    htimestamps = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.ticker + " [%d]" % len(self.hquotes)

    def get_series(self):
        index = pd.to_datetime(self.htimestamps, errors="coerce")
        return pd.Series(self.hquotes, index=index)


# There must be this base abstract class - because of how backtests work
class BasePairStats(models.Model):

    class Meta:
        abstract = True

    # Subclass MUST define:
    # pair = models.CharField(...)

    market = models.CharField(
        max_length=32,
        choices=MARKET_CHOICES,
        default='N/A',
    )

    ticker_x = models.CharField(max_length=32)
    ticker_y = models.CharField(max_length=32)

    # Last Quote - Denormalized
    x_quote = models.FloatField(null=True, blank=True)
    y_quote = models.FloatField(null=True, blank=True)

    # TODO: Normalize
    beta_rotation = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f'{self.ticker_x} x {self.ticker_y}'

    @classmethod
    def create(cls, pair, market, series_x=None, series_y=None):
        """
        Subclass must define 'pair' field.
        """
        if not hasattr(cls, 'pair'):
            raise AttributeError(
                f"{cls.__name__} must define a 'pair' field"
            )

        series_x = series_x or pd.Series(dtype=float)
        series_y = series_y or pd.Series(dtype=float)

        obj = cls(
            pair = " ".join(pair),
            market = market,
            ticker_x = pair[0],
            ticker_y = pair[1],
        )

        if not series_x.empty:
            obj.x_quote = series_x.iloc[-1]

        if not series_y.empty:
            obj.y_quote = series_y.iloc[-1]

        return obj

    def display_pair(self):
        if hasattr(self, 'pair'):
            return self.pair.replace('.SA', '').replace(' ', 'x')
        return f'{self.ticker_x}x{self.ticker_y}'

    def n_p_coint(self, pvalue):
        """Number of cointegrated periods """
        return self.coint_params.filter(
            success=True,
            adf_pvalue__lt=pvalue
        ).count()


class PairStats(BasePairStats):
    """
        This table stores daily calculations results
    """
    pair = models.CharField(max_length=32, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def last_update(cls, market):
        qs = cls.objects.filter(market=market)
        try:
            latest = qs.latest('timestamp')
            return latest.timestamp
        except cls.DoesNotExist:
            return None

    @classmethod
    def estimated_time(cls, market):
        stats = {}
        qs = cls.objects.filter(market=market)
        try:
            latest = qs.latest('timestamp').timestamp
            earliest = qs.earliest('timestamp').timestamp
            duration = latest - earliest
            seconds = duration.total_seconds()
            stats = {
                    'duration': duration,
                    'hours': int(seconds // 3600),
                    'minutes': int((seconds % 3600) // 60),
                    'seconds': int(seconds % 60)
            }
        except Exception as e:
            print(e)

        return stats
