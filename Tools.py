"""
Helper functions for the genetic algorithm simulation and estimation
"""
import numpy as np
import pandas as pd
import GeneMap as gmap
reload(gmap)
import json

def rand_base_args(signal_map):
	"""
	"""
	chrom = []
	for gene in signal_map:
		t = np.random.normal(5, 3)  #chose the values arbitraly
		t = int(t)
		t = max(1, t)
		chrom.append(t)
	return tuple(chrom)

def rand_weights(signal_map, sig=.3):
	w = []
	for i in range(len(signal_map)):
		w.append(np.random.normal(0, sig))
	return np.array(w)
 

def evaluate_chrom(series, chrom, signal_map):
	res = []
	for pos, gene in enumerate(chrom):

		func = signal_map[pos]
		val = func(series, gene)
		res.append(val)
	return np.array(res)


