"""
Helper functions for the genetic algorithm simulation and estimation
"""
import numpy as np
import pandas as pd
import GeneMap as gmap
reload(gmap)
import json

def random_signal_params(signal_map):
	"""
	"""
	chrom = []
	for cls in signal_map:
		gene = cls.gen_random_gene()
		chrom.append(tuple(gene))
	return tuple(chrom)



def rand_weights(signal_map, sig=.3):
	w = []
	for i in range(len(signal_map)):
		w.append(np.random.normal(0, sig))
	return np.array(w)
 

def evaluate_chrom(series, chrom, signal_map):
	res = []
	for pos, gene in enumerate(chrom):

		func = signal_map[pos].func
		args = [series]
		args.extend(gene)
		val = func(args)
		res.append(val)
	return res

def gen_signals(data, chrom, SignalsMap, start_pos=1000):
	signals = []
	for i in range(start_pos, len(data)):
		if i%25000==0:
			print i
		series = data[i-1e3 : i]
		val = evaluate_chrom(series, chrom, SignalsMap)
		signals.append(val)

	sample_data = data[start_pos:]
	return sample_data, signals

def calculate_profit(sample_data, positions):
	profit = []
	assert len(sample_data) == len(positions)
	s = np.array(sample_data)
	changes = s[1:] - s[:-1]
	profit.append(changes * positions[1:])
	return profit

def OptimizeWeights(data, signals, pop_size, num_gen):
	pass

