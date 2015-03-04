"""
Provides a Gene Map for the genes
Each gene is a function and the map is a tuple.
"""
import numpy as np
import copy



# Map for the genes describing the stops

StopsMap = [
(None, (5, 100) ),  # Stop Loss
(None, (5, 100) ),  # Take Profit
(None, (5, 500) ),  # Maximum hold time (in number of periods)
]
		
SignalsMap = []  # Map of the signal genes

###########################
# Change From Last Period #
###########################

class Change_One_Period(object):

	def __init__(self, t):
		self.t = t

	def func(self, func_args):
		"""
		Returns True if the change from period t to t-1 was
		within the range: value-error : value+error	
		"""

		series, value, error, enabled = func_args
		if not enabled:
			return True
		change = (series[-self.t-1] - series[-self.t-2]) / series[-self.t-2]
		return value-error < change < value + error

range_ch_val = (-0.01, 0.01)
range_ch_err = (0, 0.0001)

# Add t conditions for the past t periods changes
for t in range(6):
	cls = Change_One_Period(t)
	SignalsMap.append(
	(cls.func,		range_ch_val,		range_ch_err))

######################################
# Price Level Relative to Hist Price #
######################################

# Checks if the current price is below above some historical max/min price

class HistValues(object):
	# Use level price series
	def __init__(self, t, n_periods, func_type):
		"""
		n_periods : number of periods over which you take the max price
		"""
		self.t = t
		self.n_periods = n_periods
		self.func_type = func_type

	def func(self, func_args):
		"""
		Returns if the distance from max/min price is
		within given range
		"""

		series, value, error, enabled = func_args
		if not enabled:
			return True
		price = self.func_type(series[-self.n_periods:])
		x = series[-self.t - 1] - value * price
		return value - error < x < value + error

pr_n_periods = 1e3
range_pr_val = (0.5, 1.5)
range_pr_err = (0, 1)
cls = HistValues(0, pr_n_periods, np.max)
SignalsMap.append(
	(cls.func, range_pr_val, range_pr_err)
	) 

cls = HistValues(0, pr_n_periods, np.min)
SignalsMap.append(
	(cls.func, range_pr_val, range_pr_err)
	) 

##############
# Volatility #
##############

class Volatility(object):
	# Use level price series
	def __init__(self, n_periods):
		self.n_periods = n_periods

	def func(self, func_args):
		series, value, error, enabled = func_args
		if not enabled:
			return True
		vol = np.std(series[-self.n_periods:]) / np.mean(series[-self.n_periods:])
		return value - error < vol < value + error

vol_n_periods = 1e3
range_vol_val = (0, 2)
range_vol_err = (0, 0.1)
cls = Volatility(vol_n_periods)
SignalsMap.append(
	(cls.func, range_vol_val, range_vol_err)
)

#######################
# Chartist Indicators #
#######################

class MovAvCross(object):
	def __init__(self, indicator):
		self.indicator = indicator

	def func(self, func_args):

		series, MA1, MA2, enabled = func_args
		if not enabled:
			return True
		mean1 = np.mean(series[-MA1:])
		mean2 = np.mean(series[-MA2:])

		mean1_lag = np.mean(series[-MA1 - 1:-1])
		mean2_lag = np.mean(series[-MA2 - 1:-1])

		if self.indicator == "Cross from below":
		# Returns True if the current moving averages cross (mean1==mean2)
		# and the "short" (mean2_lag) moving average last period was below the long (mean1_lag)
		# Crossed it from below
			return (mean1 == mean2) & (mean2_lag < mean1_lag)
		elif self.indicator == "Cross from above": # sell signal
			return (mean1 == mean2) & (mean2_lag > mean1_lag)
		else:
			print "Indicator ust be either 'Cross from below' or 'from above' -- Error"
			raise

range_movav_ma1 = (2, 1e3)
range_movav_ma2 = (2, 1e3)

cls = MovAvCross(indicator="Cross from below")
SignalsMap.append(
(cls.func, range_movav_ma1, range_movav_ma2)
)

cls = MovAvCross(indicator="Cross from above")
SignalsMap.append(
(cls.func, range_movav_ma1, range_movav_ma2)
)

