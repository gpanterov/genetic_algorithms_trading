"""
Helper functions for the genetic algorithm simulation and estimation
"""
import numpy as np
import pandas as pd
import GeneMap as gmap
reload(gmap)
import json
import GA_Tools as ga
reload(ga)

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

def OptimizeWeights(sample_data, signals, pop_size, num_gen, retain_rate=0.2):
	num_signals = np.shape(signals)[1]
	W = np.random.normal(0, 0.3, size=(pop_size, num_signals))
	Best_Fit = []
	for n in range(num_gen):

		pop_fitness = []
		for w in W:
			weighted_sum = np.sum(w * np.array(signals), axis=1)
			weighted_signals = np.exp(weighted_sum) / (np.exp(weighted_sum) + 1)
			positions = np.array([-1]*len(weighted_sum))
			positions[weighted_signals > 0.5] = 1
			profit = calculate_profit(sample_data, positions)
			pop_fitness.append(np.sum(profit))
		# Keep the best, mate and mutate and create new population
		## Retain the best of the population
		parent_pop = list(W)
		new_pop = []
		indx = np.argsort(pop_fitness)
		cutoff = int(pop_size * retain_rate)
		best_indx = indx[-cutoff:]
		
		for i in best_indx[::-1]:
			new_pop.append(parent_pop[i])

		cdf_vals = ga.cdf(pop_fitness)
		while len(new_pop) < pop_size:
			w1 = ga.choice(parent_pop, cdf_vals)
			w2 = ga.choice(parent_pop, cdf_vals)
			off = ga.mate_monoploid_random(w1, w2)
			off = ga.mutate_monoploid(off)
			new_pop.append(off)
		W = np.array(new_pop)
		print pop_fitness[0]
		Best_Fit.append(pop_fitness[0])
		if np.std(Best_Fit[-10:]) < 0.1 and len(Best_Fit[-10:])==10: # If there is no change in the past 10 periods exit
			return pop_fitness[0], W
	return pop_fitness[0], W

