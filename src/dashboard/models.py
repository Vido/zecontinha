import pandas as pd
from django.db import models


class CointParams(models.Model):

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

    #TODO: Marcar o periodo

    # class Meta:
    #     abstract = True

    @classmethod
    def create(cls, success, test_params={}, analysis_params={}):

        obj = CointParams(success=success)
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
        except Exception as e:
            print(e)
            obj.success = False
            #raise
        else:
            obj.success = True

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
    hquotes = models.JSONField(default=list, blank=True)
    htimestamps = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.ticker + " [%d]" % len(self.hquotes)

    def get_series(self):
        index = pd.to_datetime(self.htimestamps, unit="s")
        return pd.Series(self.hquotes, index=index)


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

    model_params = models.JSONField(default=dict)
    beta_rotation = models.JSONField(default=list, blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ticker_x} x {self.ticker_y}'

    @classmethod
    def create(cls, pair, market, series_x=pd.Series([]), series_y=pd.Series([])):

        obj = PairStats(
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

def _get_update(qs, _callable='latest'):
        ts_update = None
        try:
            _latest = getattr(qs, _callable)('timestamp')
            ts_update = _latest.timestamp
        except PairStats.DoesNotExist as e:
            print(e)
            pass

        return ts_update

class PairStats(BasePairStats):
    pair = models.CharField(max_length=32, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def last_update(cls, market):
        qs = PairStats.objects.filter(market=market)
        return _get_update(qs)

    @classmethod
    def estimated_time(cls, market):
        stats = {}
        qs = PairStats.objects.filter(market=market)
        try:
            duration = _get_update(qs, _callable='latest') - _get_update(qs, _callable='earliest')
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
