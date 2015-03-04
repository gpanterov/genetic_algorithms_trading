"""
Helper functions for the genetic algorithm simulation and estimation
"""
import numpy as np
import pandas as pd
import GeneMap as gmap
import TradingSimulation as sim
reload(gmap)
reload(sim)
import json

def gen_random_chrom(signal_map, prob_enabled):
	"""
	Generates a random chromosome based on a signal map
	signal_map: list, each element is a gene.
				Each gene is a tuple(func, range_first_arg, range_second_arg ...)
	prob_enabled: probability that a gene is enabled

	Returns:
	chrom: tuple, each element of chrome is a gene tuple
			gene = (first_arg, second_arg, ...., enabled)
	"""
	chrom = []
	for gene in signal_map:
		random_gene = []
		for element in gene[1:]:  # The first element in the map is the function. We start from the second
			l = element[0]
			u = element[1]
			x = np.random.uniform(l, u)
			random_gene.append(x)
		enabled = False
		if np.random.uniform() < prob_enabled:
			enabled = True
		random_gene.append(enabled)	
		chrom.append(tuple(random_gene))
	return tuple(chrom)

def gen_random_population(pop_size, SignalsMap, StopsMap, prob_enabled, json_file_path):
	Population = []
	for i in range(pop_size):
		trader = {}
		trader['EntrySignals'] = gen_random_chrom(SignalsMap, prob_enabled)
		trader['EntrySignals'] = validate_chrom(trader['EntrySignals'], verbose=True)
		trader['ExitSignals'] = gen_random_chrom(SignalsMap, prob_enabled)
		trader['StopSignals'] = gen_random_chrom(StopsMap, 1.)
		Population.append(trader)
	D = {'population':Population}
	D['iteration'] = 0
	with open(json_file_path, 'w') as outfile:
   		json.dump(D, outfile)
	return Population


	
def evaluate_chrom(series, chrom, signal_map):
	conditions = []
	for pos, gene in enumerate(chrom):
		f_args = [series]
		f_args.extend(gene)

		func = signal_map[pos][0]
		res = func(f_args)
		conditions.append(res)
	return conditions

def validate_chrom(chrom, verbose=False):
	"""
	If none of the genes are enabled randomly enable one
	"""
	Enabled = [i[-1] for i in chrom]
	if np.sum(Enabled) == 0:  # no genes are enabled
		new_chrom = list(chrom)
		pos = np.random.random_integers(0, len(chrom)-1)
		new_chrom[pos] = list(chrom[pos])
		new_chrom[pos][-1] = True
		new_chrom[pos] = tuple(new_chrom[pos])
		if verbose:
			print "Chromosome needed validation and was validated"
		return tuple(new_chrom) 			
	else:
		return chrom

def simulate_strategy(data, trader, SignalsMap, start_period=1e3, verbose=False, direction=1):
	"""
	Simulates trading for a given trader

	trader: dict, dictionary with the three keys: EntrySignals, ExitSignals and StopSignals
	data: data frame with prices

	"""
	sl_pips = trader['StopSignals'][0][0]
	tp_pips = trader['StopSignals'][1][0]
	hold_time = trader['StopSignals'][2][0]
	simulation = sim.Simulation(data, sl_pips, tp_pips, hold_time)

	end_period = len(simulation.data)

	if verbose:
		ENABLED= [i[-1] for i in trader['EntrySignals']]
		print ENABLED
		indx = np.where(np.array(ENABLED) == True)
		s = np.array(SignalsMap)[indx]
		funcs = [i[0] for i in s]
		print funcs
		print np.array(trader['EntrySignals'])[indx]
	for t in np.arange(start_period, end_period):
		simulation.step = int(t)
		if verbose:
			if simulation.step % 100000 == 0:
				print simulation.step
		series = simulation.data.Close[:simulation.step].values
		if simulation.total_position == 0:
			entry_conditions = evaluate_chrom(series, trader['EntrySignals'], SignalsMap)
			entry = np.prod(entry_conditions, dtype=bool)
			if entry:
				if verbose:
					print "Open Position"
				simulation.open_position(direction)
		else:  # Exit the position if there is an exit signal or you hit the stops
			exit_conditions = evaluate_chrom(series, trader['ExitSignals'], SignalsMap)
			exit_ = np.prod(exit_conditions, dtype=bool)
			if exit_:
				simulation.close_position(series[-1])
				if verbose:
					print "Sell Signal"
			simulation.check_stops(verbose)  # Check if the stops are hit

	return simulation


def gene_info(gene, pos, SignalsMap):
	message = None
	if gene[-1]:
		if pos <=5:
			values = (gene[0] - gene[1], gene[0] + gene[1], -pos)
			message = "%s < (P[t-1] - P[t-2]) / P[t-2] < %s where t = %s" % values 
			return message
		if pos == 6:
			values = (gene[0]-gene[1], gmap.pr_n_periods, gene[0] + gene[1])
			message = " %s < Current price / (Max Price in last %s periods) < %s" % values
		if pos == 7:
			values = (gene[0]-gene[1], gmap.pr_n_periods, gene[0] + gene[1])
			message = " %s < Current price / (Min Price in last %s periods) < %s" % values
		if pos == 8:
			values = (gene[0]-gene[1], gmap.vol_n_periods, gene[0] + gene[1])
			message = " %s < Volatility / Average over last %s periods < %s" % values

		if pos == 9:
			values = (gene[0], gene[1])
			message = " MA(%s) crosses from below MA(%s)" % values

		if pos == 10:
			values = (gene[0], gene[1])
			message = " MA(%s) crosses from above  MA(%s)" % values
			

	return message

def display_chrom_info(chrom, SignalsMap):
	info = ""
	for pos, gene in enumerate(chrom):
		message = gene_info(gene, pos, SignalsMap)
		if message is not None:
			info += message + "\n"
	return info
