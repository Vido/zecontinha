import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

import pandas as pd
from backtesting import Backtest, Strategy

from dashboard.models import Quotes
from coint.binance_calc import download_hquotes_binance
from coint.cointegration import clean_timeseries

class PairTradingCointegration(Strategy):
    def init(self):
        Close = self.data.Close
        self.ma1 = self.I(SMA, Close, 10)
        self.ma2 = self.I(SMA, Close, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()

if __name__ == '__main__':

    Quotes.objects.filter(market='BINANCE').delete()
    download_hquotes_binance()
    
    _x = Quotes.objects.get(ticker='BTCUSDT').get_series()
    _y = Quotes.objects.get(ticker='LTCUSDT').get_series()
    series_x, series_y = clean_timeseries(_x, _y)
    df = pd.DataFrame()

    df['BTCUSDT'] = series_x
    df['LTCUSDT'] = series_y

    from IPython import embed; embed()
    bt = Backtest(df, PairTradingCointegration,
                  cash=10000, commission=.002)
    bt.run()
    bt.plot()