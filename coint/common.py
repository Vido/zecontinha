import copy

from statsmodels.tools.sm_exceptions import MissingDataError
from django.forms.models import model_to_dict

from dashboard.forms import PERIODOS_CALCULO
from dashboard.models import PairStats, CointParams, Quotes

from coint.analysis import beta_rotation, analysis_model
from coint.cointegration import coint_model

def generic_producer(pair, market, series_x, series_y):

    obj_pair = PairStats.create(pair, market, series_x=series_x, series_y=series_y)

    try:
        beta_list = beta_rotation(series_x=series_x, series_y=series_y)
        obj_pair.beta_rotation = beta_list
    except MissingDataError:
        print('FAIL - MissingDataError - Beta')
        #raise

    for periodo in PERIODOS_CALCULO:
        slice_x = series_x[-periodo:]
        slice_y = series_y[-periodo:]
        try:
            test_params = coint_model(slice_x, slice_y)
            analysis_params = analysis_model(test_params['OLS'].resid)
            obj_data = CointParams.create(True, test_params, analysis_params)
        except ValueError as ve:
            print(ve)
            obj_data = CointParams.create(False)
            #raise
        except MissingDataError:
            obj_data = CointParams.create(False)
            print('FAIL - MissingDataError - OLS ADF', periodo)
            #raise

        obj_pair.model_params[periodo] = model_to_dict(obj_data)

    return copy.deepcopy(obj_pair)

from itertools import permutations
def gera_pares(carteira_tickers):
    return permutations(carteira_tickers, 2)
