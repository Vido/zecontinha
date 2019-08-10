import base64
from io import StringIO
from io import BytesIO

import numpy as np
import yfinance as yf
import matplotlib.pyplot as mplt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

def get_market_data(tickers, period, interval):
    data = yf.download(
        tickers = " ".join(tickers),
        period = period,
        interval = interval,
        #group_by = 'ticker',
        #auto_adjust = True,
        #prepost = False,
        #treads = True,
        #proxy = None
    )
    return data

def coint_model(series_x, series_y):
    try:
        X = sm.add_constant(series_x.values)
        mod = sm.OLS(series_y, X)
        results = mod.fit()
        adfTest = adfuller(results.resid, autolag='AIC')
        return {
            'OLS': results,
            'ADF': adfTest,
        }
    except:
        raise

def beta_rotation(series_x, series_y, window=40):
    beta_list = []
    try:
        for i in range(0, len(series_x)-window):
            slice_x = series_x[i:i+window]
            slice_y = series_y[i:i+window]

            X = sm.add_constant(slice_x.values)
            mod = sm.OLS(slice_y, X)
            results = mod.fit()
            beta = results.params.x1
            beta_list.append(beta)
    except:
        raise
    return beta_list

def asBase64(my_plt):
    _buffer = BytesIO()
    my_plt.savefig(_buffer, format='png', bbox_inches='tight')
    _buffer.seek(0)
    return base64.encodestring(_buffer.read())

def get_scatter_plot(series_x, series_y, ols, xlabel='', ylabel=''):
    x = np.arange(series_x.min(), series_x.max())
    # limpa o canvas
    mplt.clf()
    mplt.cla()
    #mplt.close()
    mplt.scatter(series_x, series_y)
    mplt.plot(x, ols.params.const + ols.params.x1 * x, color='red')
    mplt.xlabel(xlabel)
    mplt.ylabel(ylabel)
    return asBase64(mplt)

def get_residuals_plot(ols):
    # TODO: descobrir qual é correto
    stddev = ols.resid.std()
    xmin = ols.resid.index.min()
    xmax = ols.resid.index.max()

    # limpa o canvas
    mplt.clf()
    mplt.cla()
    #mplt.close()
    mplt.plot(ols.resid)
    mplt.xticks(rotation=90)

    mplt.hlines([-1*stddev, 1*stddev], xmin, xmax, color='gray')
    mplt.hlines([-2*stddev, 2*stddev], xmin, xmax, color='black')
    mplt.hlines([-3*stddev, 3*stddev], xmin, xmax, color='red')
    return asBase64(mplt)

def get_raw_plot(series_x, series_y, xlabel='', ylabel=''):
    # limpa o canvas
    mplt.clf()
    mplt.cla()
    mplt.plot(series_x, color='orange', label=xlabel)
    mplt.plot(series_y, color='purple', label=ylabel)
    mplt.xticks(rotation=90)

    mplt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, borderaxespad=0.)
    
    return asBase64(mplt)

def get_beta_plot(beta_list):
    # limpa o canvas
    mplt.clf()
    mplt.cla()
    #mplt.close()
    mplt.plot(beta_list)
    mplt.xticks(rotation=90)
    return asBase64(mplt)