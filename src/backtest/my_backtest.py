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
from backtest.models import PairStats
from coint.cointegration import coint_model, beta_rotation, clean_timeseries
from coint.binance_calc import download_hquotes as download_hquotes_binance
from dashboard.models import PERIODOS_CALCULO

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
    obj_pair = PairStats.create(pair, market, series_x=series_x, series_y=series_y)
    # Valor esperado: 690
    #print(refdate, pair, 'len_X', len(series_x), 'len_Y', len(series_y))
    #print(refdate, pair)

    for periodo in PERIODOS_CALCULO:
        obj_data = {}
        slice_x = series_x[-periodo:]
        slice_y = series_y[-periodo:]

        try:
            test_params = coint_model(slice_x, slice_y)
            obj_data = CointParams.create(True, test_params)
        except MissingDataError:
            obj_data = CointParams.create(False, test_params)
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
        10000,
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

    params = {}
    params = parametros.model_params['60']

    # Todo parametro do Modelo
    if parametros.n_p_coint(0.1) < 6 and not posicao:
        return 'SAIR', 'REGRA NCOINT', params

    if parametros.n_p_coint(0.1) < 2 and posicao:
        return 'SAIR', 'REGRA NCOINT', params

    if params['adf_pvalue'] < 0.1 and not posicao:
        return 'SAIR', 'REGRA ADF', params

    #if params['adf_pvalue'] > 0.5 and posicao:
    #    return 'SAIR', 'REGRA ADF', params

    if abs(params['zscore'])-0.5 < 0:
        return 'SAIR', 'REVERSAO', params

    if abs(params['zscore']) > 4.0:
        return 'SAIR', 'EXTREMO', params

    if abs(params['zscore']) > 2.0:
        return 'ENTRAR', 'ENTRADA', params

    return 'NADA','NADA', params

class Posicao():
    def __init__(self, capital, pair_stats, params):
        self.direcao = params['zscore'] > 0
        self.qy = capital / pair_stats.y_quote
        self.qx = params['ang_coef'] * self.qy
        self.saldo_inicial = self.saldo(
            pair_stats.x_quote, pair_stats.y_quote)

    def __bool__(self):
        return True

    def saldo(self, x, y):
        #if self.direcao:
        if not self.direcao: # Invertido
            return self.qx*x - self.qy*y
        return (self.qy*y) - (self.qx*x)

    def pl(self, x, y):
        return self.saldo(x, y) - self.saldo_inicial

def gestao():

    matriz = matriz_pares()
    for pair, date_list in matriz_pares().iteritems():

        posicao = []
        lastref = date(2019, 8, 18)
        print(pair)

        for refdate, _ in date_list.iteritems():
            #print(pair, refdate)
            #matriz[pair][refdate]

            # Fazer uma maquina de estados

            try:
                pair_stats = PairStats.objects.get(
                    refdate=refdate,
                    pair=' '.join(pair)
                )
            except:
                continue

            # TODO: Achar a posição
            trade, regra, params = sinal(pair, refdate, pair_stats, posicao)
            pl, deltapl = 0, 0

            #elif trade == 'NADA' and posicao:
            if posicao:
                # marcar o PL
                pl = posicao.pl(
                    pair_stats.x_quote, pair_stats.y_quote)
                deltapl = pl - lastpl
                #print(refdate, pair, trade, matriz[pair][lastref], deltapl)

            if trade == 'SAIR' and posicao:
                # marcar o PL
                # Fechar o Trade
                pl = posicao.pl(
                    pair_stats.x_quote, pair_stats.y_quote)
                deltapl = pl - lastpl
                posicao = []
                print(trade, regra)

            elif trade == 'ENTRAR' and not posicao:
                # entrar no Trade
                # não marcar o PL
                posicao = Posicao(
                    matriz[pair][refdate],
                    pair_stats,
                    params)
                lastpl = 0
                print(trade, regra)


            if abs(deltapl) > 10000:
                from IPython import embed; embed()

            matriz[pair][refdate] = matriz[pair][lastref] + deltapl
            lastref = refdate
            lastpl = pl

    matriz.to_excel("output2.xlsx")
    from IPython import embed; embed()


if __name__ == '__main__':

    # Limpa a Base
    #Quotes.objects.filter(market='BINANCE').delete()
    #download_hquotes_binance()

    #print(datetime.now())
    #PairStats.objects.all().delete()
    #dados_binance()
    #print(datetime.now())

    print(datetime.now())
    gestao()
    print(datetime.now())
