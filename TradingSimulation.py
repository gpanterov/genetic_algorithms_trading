import pandas as pd
import numpy as np
import datetime

def load_data(path_to_data):
	""" Loads data in df with appropriate index """
	data = pd.read_csv(path_to_data)
	#time_fmt = '%Y-%m-%d %H:%M:%S'  # use this for the test file
	time_fmt = '%d.%m.%Y %H:%M:%S.%f' # Use this for the full file

	data['Time'] = data.Time.apply(lambda x: datetime.datetime.strptime(x,
							time_fmt))
	return data


def collapse_data(data, minutes):
	minutes = int(minutes)
	if minutes == 1:
		return data

	data['Minute_Interval'] = data.Minute.values / minutes
#	data['Weighted_Price'] = data.Close * data.Volume 

	data1 = data[data.Volume > 0]  # no trading at the end of Fridays. Drop these values
	group = data1[['Close', 'Low', 'High',  'Volume', 'Signed_Volume', 'Returns2']].groupby([data1['Year'], 
					data1['Week'], data1['Day'], data1['Hour'], data1['Minute_Interval']])

	df = group.agg({'Close':'last', 'Low':'last', 'High':'last', 'Volume':np.sum, 'Signed_Volume':np.sum,
					'Returns2':np.sum})
	return df

		
class Simulation(object):
	def __init__(self, data, sl_pips, tp_pips, hold_time):
		self.data = data
		self.sl_pips = sl_pips  # stop loss pips
		self.tp_pips = tp_pips  # take profit pips
		self.hold_time = hold_time  # time to hold position (num periods). Close after that
		self.step = 0
		self.pips = 0.01
		self.orders_record = [] # Record of opened positions
		self.positions_record = []
		self.total_position = 0 


	def open_position(self, direction):
		if self.total_position != 0:
			#print "Attempting to open a position when one already exists (no action)"
			return None

		self.direction = direction
		price = self.data['Close'].values[self.step]
		self.stop_loss = price - \
						direction * self.sl_pips * self.pips

		self.take_profit = price + \
						direction * self.tp_pips * self.pips

		self.close_time = self.step + self.hold_time

		self.total_position += direction
		self.orders_record.append([self.step, direction, price])
		self.current_position = [self.step, direction, price]

	def close_position(self,price):
		if self.total_position == 0:
			return None
		self.total_position += - self.direction
		self.orders_record.append([self.step, -self.direction, price])
		self.current_position.extend([self.step, price])
		self.positions_record.append(self.current_position)
		assert self.total_position == 0

	def check_stops(self, verbose=False):
		if self.total_position == 0:
			return None
		min_price_stop = min(self.stop_loss, self.take_profit)
		max_price_stop = max(self.stop_loss, self.take_profit)
		if  min_price_stop > self.data['Low'].values[self.step]:
			self.close_position(min_price_stop)
			if verbose:
				print "stop - min price"

		if  max_price_stop < self.data['High'].values[self.step]:
			self.close_position(max_price_stop)
			if verbose:
				print "stop - max price"

		if self.step >= self.close_time:
			self.close_position(self.data['Close'].values[self.step])
			if verbose:
				print "stop - time"
	def next_period(self):
		self.step += 1

	def calculate_profits(self):
		if len(self.orders_record)<2:
			return 0.1
		df = pd.DataFrame(self.orders_record)
		profit = np.sum(df[1] * df[2])
		return -profit

	def calculate_profits2(self):
		df = pd.DataFrame(self.orders_record)
		df[3] = df[1] * df[2]
		df[4] = df.index/2
		profit = -df[3].groupby(df[4]).apply(sum)
		return profit
