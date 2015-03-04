import Tools as tools
import pickle
import numpy as np
import GeneMap as gmap
import GA_Tools as ga
reload(ga)
reload(gmap)
reload(tools)
import time
import json
import TradingSimulation as sim


pop_size = 50  # Size of population
retain_rate = 0.2
direction = 1


gen_random_pop = False

#############
# Load Data #
#############

f=open('usdjpy_data.obj', 'r')
all_data = pickle.load(f)
df = all_data[all_data.Volume>0]
df = sim.collapse_data(df, minutes=5)

c = tools.rand_base_args(gmap.SignalsMap)
w = tools.rand_weights(gmap.SignalsMap)

data = df.Close.values

start = time.time()
sig = []
for i in range(1000, len(data)):
	if i%50000 == 0:
		print i
	series = data[i-1e3 : i]
	val = tools.evaluate_chrom(series, c, gmap.SignalsMap)
	ex = np.exp(-np.sum(val*w))
	sig.append(1/(ex+1))
print time.time() - start
#######################
## Generate Population #
#######################
#SignalsMap = gmap.SignalsMap
#StopsMap = gmap.StopsMap
#prob_enabled = 0.5
#
#if gen_random_pop:
#	tools.gen_random_population(pop_size, SignalsMap, StopsMap, prob_enabled, 
#			json_file_path = 'populations/population.json')
#
#json_file = open('populations/population.json')
#D = json.load(json_file)
#json_file.close()
#
#parent_pop = D['population']
#iteration = D['iteration']
#print "Currently at %s iteration" % iteration
#####################
## Simulate Trading #
#####################
#
#simulation_start_time = time.time()
#pop_fitness = []
#for trader in parent_pop:
#	simulation = tools.simulate_strategy(df, trader, SignalsMap, verbose=False, direction=direction)
#
#	profit= simulation.calculate_profits()
#	pop_fitness.append(abs(profit))
#	print profit, len(simulation.orders_record), pop_fitness[-1]
#
#print "Simulation took %s seconds" % (time.time() - simulation_start_time)
#
###########################
## Produce New Population #
###########################
#
## Retain the best of the population
#new_pop = []
#indx = np.argsort(pop_fitness)
#cutoff = int(len(parent_pop) * retain_rate)
#best_indx = indx[-cutoff:]
#
#for i in best_indx[::-1]:
#	new_pop.append(parent_pop[i])
#
#cdf_vals = ga.cdf(pop_fitness)
#while len(new_pop) < len(parent_pop):
#	new_trader = {}
#	trader1 = ga.choice(parent_pop, cdf_vals)
#	trader2 = ga.choice(parent_pop, cdf_vals)
#
#	off_entry = ga.mate_random(trader1['EntrySignals'], trader2['EntrySignals'])
#	off_entry = ga.mutate_value_genes(off_entry, SignalsMap)
#	off_entry = ga.mutate_enabled_genes(off_entry)
#	new_trader['EntrySignals'] = tools.validate_chrom(off_entry)
#
#
#	off_exit = ga.mate_random(trader1['ExitSignals'], trader2['ExitSignals'])
#	off_exit = ga.mutate_value_genes(off_exit, SignalsMap)
#	off_exit = ga.mutate_enabled_genes(off_exit)
#	new_trader['ExitSignals'] = off_exit
#
#	off_stop = ga.mate_random(trader1['StopSignals'], trader2['StopSignals'])
#	off_stop = ga.mutate_value_genes(off_stop, SignalsMap)
#	new_trader['StopSignals'] = off_stop
#	new_pop.append(new_trader)
#
#print "Open position if: "
#print tools.display_chrom_info(new_pop[0]['EntrySignals'], SignalsMap)
#print "Close position if: "
#print tools.display_chrom_info(new_pop[0]['ExitSignals'], SignalsMap)
#
#
#D={'population': new_pop}
#D['iteration'] = iteration + 1
#with open('populations/population.json', 'w') as outputfile:
#	json.dump(D, outputfile)
#
#
