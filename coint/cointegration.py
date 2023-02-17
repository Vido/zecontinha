import base64
from io import StringIO
from io import BytesIO

import numpy as np
import yfinance as yf
import matplotlib.pyplot as mplt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

def drop_nan(a):
    return a[~np.isnan(a)]

def clean_timeseries(x, y):
    x, y = drop_nan(x), drop_nan(y),
    intersc = set.intersection(set(x.index), set(y.index))
    newx = x[intersc].sort_index()
    newy = y[intersc].sort_index()
    return newx, newy

def get_market_data(tickers, period, interval):
    """
    https://github.com/ranaroussi/yfinance/issues/363
    """
    data = yf.download(
        tickers = " ".join(tickers),
        period = period,
        interval = interval,
        #group_by = 'ticker',
        #auto_adjust = True,
        #prepost = False,
        threads = False,
        #proxy = None
    )
    return data

def half_life_calc(ts):
    lagged = ts.shift(1).fillna(method="bfill")
    delta = ts-lagged
    X = sm.add_constant(lagged.values)
    ar_res = sm.OLS(delta, X).fit()
    half_life = -1*np.log(2)/ar_res.params['x1']

    return half_life, ar_res

def coint_model(series_x, series_y):
    try:
        X = sm.add_constant(series_x.values)
        mod = sm.OLS(series_y, X)
        results = mod.fit()
        adfTest = adfuller(results.resid, autolag='AIC')
        
        ts = results.resid
        half_life, _ = half_life_calc(ts)
        return {
            'OLS': results,
            'ADF': adfTest,
            'HF': half_life, #TODO: qual a sigla? O return está correto?
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

def fp_savefig(my_plt):
    _buffer = BytesIO()
    my_plt.savefig(_buffer, format='png', bbox_inches='tight')
    _buffer.seek(0)
    return _buffer

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

def _get_residuals_plot(ols):
    # TODO: descobrir qual é correto
    stddev = ols.resid.std()
    xmin = ols.resid.index.min()
    xmax = ols.resid.index.max()

    # limpa o canvas
    mplt.clf()
    mplt.cla()
    #mplt.close()
    mplt.plot(ols.resid, color='k')
    mplt.xticks(rotation=90)

    mplt.hlines([0], xmin, xmax, color='whitesmoke')
    mplt.hlines([-1*stddev, 1*stddev], xmin, xmax, color='gainsboro')
    mplt.hlines([-2*stddev, 2*stddev], xmin, xmax, color='orange')
    mplt.hlines([-3*stddev, 3*stddev], xmin, xmax, color='red')
    
    return mplt

def get_residuals_plot(ols):
    return asBase64(_get_residuals_plot(ols))

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
    try:
        mplt.plot(beta_list, color='limegreen')
    except ValueError:
        mplt.plot([], color='limegreen')
    mplt.xticks(rotation=90)
    return asBase64(mplt)

def get_plot_context(series_x, series_y, ativo_x, ativo_y):
    context = {}
    #
    test_params = coint_model(series_x, series_y)
    #
    scatter_plot = get_scatter_plot(
        series_x, series_y, test_params['OLS'],
        xlabel=ativo_x, ylabel=ativo_y)
    #
    residuals_plot = get_residuals_plot(
        test_params['OLS'])
    #
    # TODO: Usar HighCharts
    raw_plot = get_raw_plot(series_x, series_y,
        xlabel=ativo_x, ylabel=ativo_y)
    #
    context.update(test_params)
    context.update({
        'ativo_x': ativo_x,
        'ativo_y': ativo_y,
        'raw_data': zip(series_x.index, series_x, series_y),
        'scatter_plot': scatter_plot.decode("utf-8"),
        'residuals_plot': residuals_plot.decode("utf-8"),
        'raw_plot': raw_plot.decode("utf-8"),
        'resultados': True,
    })

    return context
