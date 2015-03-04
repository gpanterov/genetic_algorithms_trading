"""
Provides a Gene Map for the genes
"""
import numpy as np
import copy
import pandas as pd

def price_change(series, t, scale=1):
	t = t * scale
	return 100 * (series[-1] - series[-t]) / series[-t]

def historical_max(series, t, scale=100):
	t = t * scale
	max_price =  np.max(series[-t:])
	return (series[-1] - max_price) / max_price 

def historical_min(series, t, scale=100):
	t = t * scale
	min_price =  np.min(series[-t:])
	return 100 * (series[-1] - min_price) / min_price 

def volatility(series, t, scale=10):
	t = t * scale
	return 100 * np.std(series[-t:]) / np.mean(series[-t:])


def RSI(series, t, scale=20):
#	return 0
	t = t * scale
	prices = np.array(series)
	price_changes = np.log(prices[1:]) - np.log(prices[:-1])
	U = (price_changes > 0) * price_changes
	D = (price_changes < 0) * np.abs(price_changes)
	
	Uema = pd.ewma(U, t)
	Dema = pd.ewma(D, t)

	RS = 1. * Uema / Dema
	RSI = 100 - 100. / (1 + RS)
	return RSI[-1]

def MACD(series, ma_short, d=10):
	#short_ma = pd.ewma(series, ma_short)
	#long_ma = pd.ewma(series, ma_short + d)
	short_ma = np.mean(series[-ma_short:])
	long_ma = np.mean(series[-ma_short - d: ])
	return 100*(long_ma - short_ma) / short_ma
	#return 100*(long_ma[-1] - short_ma[-1]) / short_ma[-1]

SignalsMap = [
price_change, historical_max, historical_min, volatility, MACD
]
