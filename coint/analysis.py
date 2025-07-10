import numpy as np
import statsmodels.api as sm
from hurst import compute_Hc

def half_life_calc(ts):
    lagged = ts.shift(1).bfill()
    delta = ts-lagged
    X = sm.add_constant(lagged.values)
    ar_res = sm.OLS(delta, X).fit()
    half_life = -1*np.log(2)/ar_res.params['x1']

    return half_life, ar_res

def hurst_calc(ts):
    H, c, data = compute_Hc(ts, kind='random_walk', simplified=True, min_sample=40)
    return H, 2 - H

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

def analysis_model(ts):

    try:
        half_life, _ = half_life_calc(ts)
    except Exception as e:
        half_life = None
        print(e)

    try:
        rshd = hurst_calc(ts)
    except Exception as e:
        rshd = None
        print(e)

    print(rshd)
    return {
        'OUHL': half_life,
        'RSHD': rshd,
    }
