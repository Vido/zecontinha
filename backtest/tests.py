from django.test import TestCase

# Create your tests here.
from coint.binance_calc import download_hquotes_binance


class BacktestTestCase(TestCase):

    #databases = {'backtest'}

    def setUp(self):
        download_hquotes_binance()
        from IPython import embed; embed()

    def test_animals_can_speak(self):
        pass