import yfinance as yf
#import matplotlib.pyplot as mplt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

def get_market_data(ticker_a, ticker_b, period, interval):
    data = yf.download(
        tickers = "%s %s" % (ticker_a, ticker_b),
        period = period,
        interval = interval,
        #group_by = 'ticker',
        #auto_adjust = True,
        #prepost = False,
        #treads = True,
        #proxy = None
    )
    return data

def coint_model(series_a, series_b):
    try:
        X = sm.add_constant(series_a.values)
        mod = sm.OLS(series_b, X)
        results = mod.fit()
        #from IPython import embed; embed()

        #print(results.summary())
        #mplt.plot(results.resid)
        #mplt.show()
        adfTest = adfuller(results.resid, autolag='AIC')
        return {
            'OLS': results,
            'ADF': adfTest,
        }
    except:
        raise
        #from IPython import embed; embed()