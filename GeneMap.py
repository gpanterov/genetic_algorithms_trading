"""
Provides a Gene Map for the genes
"""
import numpy as np
import copy
import pandas as pd

class BasicGene(object):
	def random_normal_pos_int(self, mu, sig):
		res = np.random.normal(mu, sig)
		res = int(res)
		res = max(0, res)
		return res

SignalsMap = []
class SeriesChange(BasicGene):
	def gen_random_gene(self):
		return [self.random_normal_pos_int(5, 3), ]

	def func(self, args):
		series, t = args[:2]
		return 100 * (series[-1] - series[-t]) / series[-t]

cls = SeriesChange()
SignalsMap.append(cls)

class HistoricalValue(BasicGene):
	def __init__(self, minmax_func):
		self.minmax_func = minmax_func

	def gen_random_gene(self):
		return [self.random_normal_pos_int(500, 200),]

	def func(self, args):
		series, t = args[0:2]
		price =  self.minmax_func(series[-t:])
		return 100 * (series[-1] - price) / price 
cls = HistoricalValue(np.max)
SignalsMap.append(cls)

cls = HistoricalValue(np.min)
SignalsMap.append(cls)

class RelativeVolatility(BasicGene):
	def gen_random_gene(self):
		t = self.random_normal_pos_int(20, 6)
		delta = self.random_normal_pos_int(20, 6)
		return [t, delta]

	def func(self, args):
		series, t, delta = args[:3]
		return 100 * (np.std(series[-t:]) / np.std(series[-t - delta:]) - 1)

cls = RelativeVolatility()
SignalsMap.append(cls)


class RSI(BasicGene):
	def gen_random_gene(self):
		t = self.random_normal_pos_int(15, 3)
		return [t, ]

	def func(self, args):
		series, t = args[:2]
		prices = np.array(series)
		price_changes = np.log(prices[1:]) - np.log(prices[:-1])
		U = (price_changes > 0) * price_changes
		D = (price_changes < 0) * np.abs(price_changes)
		
		Uema = pd.ewma(U, t)
		Dema = pd.ewma(D, t)

		RS = 1. * Uema / Dema
		RSI = 100 - 100. / (1 + RS)
		return RSI[-1]

cls = RSI()
#SignalsMap.append(cls)

class MACD(BasicGene):
	def gen_random_gene(self):
		ma_short = self.random_normal_pos_int(25, 5)
		delta = self.random_normal_pos_int(10,3)
		return [ma_short, delta]

	def func(self, args):
		series, ma_short, delta = args[:3]
		short_ma = pd.ewma(series, ma_short)
		long_ma = pd.ewma(series, ma_short + delta)
		#short_ma = np.mean(series[-ma_short:])
		#long_ma = np.mean(series[-ma_short - d: ])
		return 100*(long_ma[-1] - short_ma[-1]) / short_ma[-1]

cls = MACD()
SignalsMap.append(cls)

