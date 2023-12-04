# TODO, Atualizar a lista de contratos automaticamente

#from decouple import config
#from binance.client import Client
#client = Client(
#    config('BINANCE_APIKEY'),
#    config('BINANCE_SECRETKEY'),
#    #tld='us'
#)
#futures_exchange_info = client.futures_exchange_info()
#for symbol in futures_exchange_info["symbols"]:
#    print(symbol["symbol"])

BINANCE_FUTURES = [
    "BTCUSDT",
    "ETHUSDT",
    "BCHUSDT",
    "XRPUSDT",
    "EOSUSDT",
    "LTCUSDT",
    "TRXUSDT",
    "ETCUSDT",
    "LINKUSDT",
    "XLMUSDT",
    "ADAUSDT",
    "XMRUSDT",
    "DASHUSDT",
    "ZECUSDT",
    "XTZUSDT",
    "BNBUSDT",
    "ATOMUSDT",
    "ONTUSDT",
    "IOTAUSDT",
    "BATUSDT",
    "VETUSDT",
    "NEOUSDT",
    "QTUMUSDT",
    "IOSTUSDT",
    "THETAUSDT",
    "ALGOUSDT",
    "ZILUSDT",
    "KNCUSDT",
    "ZRXUSDT",
    "COMPUSDT",
    "OMGUSDT",
    "DOGEUSDT",
    "SXPUSDT",
    "KAVAUSDT",
    "BANDUSDT",
    "RLCUSDT",
    "WAVESUSDT",
    "MKRUSDT",
    "SNXUSDT",
    "DOTUSDT",
    # "DEFIUSDT",
    "YFIUSDT",
    "BALUSDT",
    "CRVUSDT",
    "TRBUSDT",
    "RUNEUSDT",
    "SUSHIUSDT",
    "SRMUSDT",
    "EGLDUSDT",
    "SOLUSDT",
    "ICXUSDT",
    "STORJUSDT",
    "BLZUSDT",
    "UNIUSDT",
    "AVAXUSDT",
    "FTMUSDT",
    "HNTUSDT",
    "ENJUSDT",
    "FLMUSDT",
    "TOMOUSDT",
    "RENUSDT",
    "KSMUSDT",
    "NEARUSDT",
    "AAVEUSDT",
    "FILUSDT",
    "RSRUSDT",
    "LRCUSDT",
    "MATICUSDT",
    "OCEANUSDT",
    "CVCUSDT",
    "BELUSDT",
    "CTKUSDT",
    "AXSUSDT",
    "ALPHAUSDT",
    "ZENUSDT",
    "SKLUSDT",
    "GRTUSDT",
    "1INCHUSDT",
    "BTCBUSD",
    "CHZUSDT",
    "SANDUSDT",
    "ANKRUSDT",
    "BTSUSDT",
    "LITUSDT",
    "UNFIUSDT",
    "REEFUSDT",
    "RVNUSDT",
    "SFPUSDT",
    "XEMUSDT",
    "BTCSTUSDT",
    "COTIUSDT",
    "CHRUSDT",
    "MANAUSDT",
    "ALICEUSDT",
    "HBARUSDT",
    "ONEUSDT",
    "LINAUSDT",
    "STMXUSDT",
    "DENTUSDT",
    "CELRUSDT",
]

foo = [
    "HOTUSDT",
    "MTLUSDT",
    "OGNUSDT",
    "NKNUSDT",
    "SCUSDT",
    "DGBUSDT",
    #"1000SHIBUSDT",
    "BAKEUSDT",
    "GTCUSDT",
    "ETHBUSD",
    #"BTCDOMUSDT",
    "TLMUSDT",
    "BNBBUSD",
    "ADABUSD",
    "XRPBUSD",
    "IOTXUSDT",
    "DOGEBUSD",
    "AUDIOUSDT",
    "RAYUSDT",
    "C98USDT",
    "MASKUSDT",
    "ATAUSDT",
    "SOLBUSD",
    "FTTBUSD",
    "DYDXUSDT",
    #"1000XECUSDT",
    "GALAUSDT",
    "CELOUSDT",
    "ARUSDT",
    "KLAYUSDT",
    "ARPAUSDT",
    "CTSIUSDT",
    "LPTUSDT",
    "ENSUSDT",
    "PEOPLEUSDT",
    "ANTUSDT",
    "ROSEUSDT",
    "DUSKUSDT",
    "FLOWUSDT",
    "IMXUSDT",
    "API3USDT",
    "GMTUSDT",
    "APEUSDT",
    "WOOUSDT",
    "FTTUSDT",
    "JASMYUSDT",
    "DARUSDT",
    "GALUSDT",
    "AVAXBUSD",
    "NEARBUSD",
    "GMTBUSD",
    "APEBUSD",
    "GALBUSD",
    "FTMBUSD",
    "DODOBUSD",
    "ANCBUSD",
    "GALABUSD",
    "TRXBUSD",
    #"1000LUNCBUSD",
    #"LUNA2BUSD",
    "OPUSDT",
    "DOTBUSD",
    "TLMBUSD",
    "ICPBUSD",
    "WAVESBUSD",
    "LINKBUSD",
    "SANDBUSD",
    "LTCBUSD",
    "MATICBUSD",
    "CVXBUSD",
    "FILBUSD",
    #"1000SHIBBUSD",
    "LEVERBUSD",
    "ETCBUSD",
    "LDOBUSD",
    "UNIBUSD",
    "AUCTIONBUSD",
    "INJUSDT",
    "STGUSDT",
    #"FOOTBALLUSDT",
    "SPELLUSDT",
    #"1000LUNCUSDT",
    #"LUNA2USDT",
    "AMBBUSD",
    "PHBBUSD",
    "LDOUSDT",
    "CVXUSDT",
    "ICPUSDT",
    "APTUSDT",
    "QNTUSDT",
    "APTBUSD",
    #"BLUEBIRDUSDT",
    #"ETHUSDT_230331",
    #"BTCUSDT_230331",
    "FETUSDT",
    "AGIXBUSD",
    "FXSUSDT",
    "HOOKUSDT",
    "MAGICUSDT",
    "TUSDT",
    "RNDRUSDT",
    "HIGHUSDT",
    "MINAUSDT",
    "ASTRUSDT",
    "AGIXUSDT",
    "PHBUSDT",
    "GMXUSDT",
    "CFXUSDT",
    "STXUSDT",
    "COCOSUSDT",
    "BNXUSDT",
    "ACHUSDT",
    "SSVUSDT",
    "CKBUSDT",
    "PERPUSDT",
]

"""
#https://binance.zendesk.com/hc/en-us/articles/360033161972-Contract-Specifications
BINANCE_FUTURES = [
    'BTCUSDT',
    'ETHUSDT',
    'BCHUSDT',
    'XRPUSDT',
    'EOSUSDT',
    'LTCUSDT',
    'TRXUSDT',
    'ETCUSDT',
    'LINKUSDT',
    'XLMUSDT',
    'ADAUSDT',
    'XMRUSDT',
    'XTZUSDT',
    'DASHUSDT',
    'ZECUSDT',
    'ATOMUSDT',
    'BNBUSDT',
    'ONTUSDT',
    'IOTAUSDT',
    'BATUSDT',
    'VETUSDT',
    'NEOUSDT',
    'QTUMUSDT',
    'IOSTUSDT',
    'THETAUSDT',
]
"""
