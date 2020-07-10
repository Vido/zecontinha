# 1. Fazer todos os calculos com cada par, em cada data
import os
import sys
import copy
import django
from datetime import date, datetime, timedelta
from multiprocessing import Pool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vozdocu.settings")
django.setup()

import pandas as pd
from decouple import config
from binance.client import Client
from statsmodels.tools.sm_exceptions import MissingDataError

from django.forms.models import model_to_dict

from dashboard.models import CointParams, Quotes
from dashboard.forms import PERIODOS_CALCULO

from backtest.models import PairStats

from coint.cointegration import coint_model, beta_rotation, clean_timeseries
# TODO: Criar um arquivos com utils.py
from coint.b3_calc import create_cointparams, gera_pares
from coint.binance_calc import download_hquotes_binance

# Objetos carregado em memória
qsquotes = Quotes.objects.all()

BINANCE_FUTURES = [
    'BTCUSDT',
    'ETHUSDT',
    'XRPUSDT',
    'EOSUSDT',
    'LTCUSDT',
    'TRXUSDT',
    'ETCUSDT',
    'XLMUSDT',
    'ADAUSDT',
    'BNBUSDT',
    'ONTUSDT',
    'IOTAUSDT',
    'NEOUSDT',
    'QTUMUSDT',
]

def calcula_modelo(refdate, pair, market='BINANCE'):

    def create_pairstats(pair, market, series_x=pd.Series([]), series_y=pd.Series([])):

        obj = PairStats(
            pair = " ".join(pair),
            market = market,
            refdate=refdate,
            ticker_x = pair[0],
            ticker_y = pair[1],
        )

        if not series_x.empty:
            obj.x_quote = series_x.iloc[-1]

        if not series_y.empty:
            obj.y_quote = series_y.iloc[-1]

        return obj

    df = qsquotes.get(ticker=pair[0]).get_series()
    df2 = df[df.index < refdate]
    _x = df2[df2.index > refdate-timedelta(days=365)]

    df = qsquotes.get(ticker=pair[1]).get_series()
    df2 = df[df.index < refdate]
    _y = df2[df2.index > refdate-timedelta(days=365)]
    series_x, series_y = clean_timeseries(_x, _y)

    model_params = {}
    obj_pair = create_pairstats(pair, market, series_x=series_x, series_y=series_y)
    # Valor esperado: 690
    #print(refdate, pair, 'len_X', len(series_x), 'len_Y', len(series_y))
    #print(refdate, pair)

    for periodo in PERIODOS_CALCULO:
        obj_data = {}
        slice_x = series_x[-periodo:]
        slice_y = series_y[-periodo:]

        try:
            test_params = coint_model(slice_x, slice_y)
            obj_data = create_cointparams(True, test_params)
            obj_pair.success = True
        except MissingDataError:
            obj_data = create_cointparams(False, test_params)
            print('FAIL - MissingDataError - OLS ADF', periodo)
            #raise

        model_params[periodo] = copy.deepcopy(model_to_dict(obj_data))
    
    obj_pair.model_params = model_params
    return copy.deepcopy(obj_pair)


def matriz_pares():

    def pega_datas():
        """ TODO: Melhorar """
        df = Quotes.objects.get(ticker='BTCUSDT').get_series().index
        df2 = df[df > date(2019, 8, 17)]
        df3 = df2[df2 < date(2020, 8, 17)]
        #df2 = df[df > date(2020, 1, 1)] # DEBUG
        return df3

    return pd.DataFrame(
        0,
        pega_datas(),
        gera_pares(BINANCE_FUTURES))


def dados_binance():
    # Limpa a Base
    PairStats.objects.filter(market='BINANCE').delete()
    pares_list = gera_pares(BINANCE_FUTURES)
    
    for refdate, plist in matriz_pares().iterrows():
        bulk_list = []
        for pair in plist.index:
            #print(refdate, pair)
            obj = calcula_modelo(refdate, pair)
            bulk_list.append(obj)

        # Grava dados no Banco
        print('bulk', refdate)
        PairStats.objects.bulk_create(bulk_list)

# 2. sinal (agente)
def sinal(par, data, parametros, posicao):

    # Par cointegrado min 6 periodos
    # ADF de 0.1
    # |Z| > 2

    # Todo parametro do Modelo
    #if parametros.n_p_coint(0.1) < 3:
    #    return 'SAIR', 'REGRA NPRD'

    params = {}
    params = parametros.model_params['80']
    print(params)

    if params['adf_pvalue'] > 0.1:
        return 'SAIR', 'REGRA ADF', params['adf_pvalue']

    if abs(params['zscore'])-0.5 < 0:
        return 'SAIR', 'REVERSAO', params['zscore']

    if abs(params['zscore']) > 1.8:
        return 'ENTRAR'

    return 'NADA'

def gestao():

    def pega_fechamento_anterior():
        pass

    def marca_pl():
        pass

    matriz = matriz_pares()

    for pair, date_list in matriz_pares().iteritems(): 

        posicao = []

        for refdate, _ in date_list.iteritems(): 
            #print(pair, refdate)
            #matriz[pair][refdate]

            # Fazer uma maquina de estados

            parametros = PairStats.objects.get(
                refdate=refdate,
                pair=' '.join(pair)
            )

            print(parametros.id, pair, refdate)
            print(parametros.model_params['80'])

            # TODO: Achar a posição
            trade = sinal(pair, refdate, parametros, 0)
            
            print(trade)
            """           
            if trade[0] != 'SAIR':
                print(pair, refdate, trade)
            #from IPython import embed; embed()
            """

if __name__ == '__main__':
    
    # Limpa a Base
    #Quotes.objects.filter(market='BINANCE').delete()
    #download_hquotes_binance()
    
    print(datetime.now())
    PairStats.objects.all().delete()
    dados_binance()
    print(datetime.now())
    
    gestao()