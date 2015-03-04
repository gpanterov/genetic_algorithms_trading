import Tools as tools
import TradingSimulation as sim
import pickle
import numpy as np
import GeneMap as gmap
import GA_Tools as ga
reload(ga)
reload(gmap)
reload(tools)
reload(sim)
import time
import json



pop_size = 25  # Size of population
retain_rate = 0.2
gen_random_pop = False

#############
# Load Data #
#############

f=open('usdjpy_data.obj', 'r')
all_data = pickle.load(f)
df = all_data[all_data.Volume>0]

#df = df[:200000] # Smaller data set to test and run faster
df = sim.collapse_data(df, 30)
######################
# Generate Population #
######################
SignalsMap = gmap.SignalsMap
StopsMap = gmap.StopsMap
prob_enabled = 0.1

if gen_random_pop:
	tools.gen_random_population(pop_size, SignalsMap, StopsMap, prob_enabled, 
			json_file_path = 'populations/population.json')

json_file = open('populations/population.json')
D = json.load(json_file)
json_file.close()

parent_pop = D['population']
iteration = D['iteration']
print "Currently at %s iteration" % iteration
####################
# Simulate Trading #
####################

simulation_start_time = time.time()
pop_fitness = []
for trader in parent_pop:
	simulation = tools.simulate_strategy(df, trader, SignalsMap, verbose=False, direction=-1)

	profit= simulation.calculate_profits()
	pop_fitness.append(abs(profit))
	print profit, len(simulation.orders_record), pop_fitness[-1]

print "Simulation took %s seconds" % (time.time() - simulation_start_time)

##########################
# Produce New Population #
##########################

# Retain the best of the population
new_pop = []
indx = np.argsort(pop_fitness)
cutoff = int(len(parent_pop) * retain_rate)
best_indx = indx[-cutoff:]

for i in best_indx[::-1]:
	new_pop.append(parent_pop[i])

cdf_vals = ga.cdf(pop_fitness)
while len(new_pop) < len(parent_pop):
	new_trader = {}
	trader1 = ga.choice(parent_pop, cdf_vals)
	trader2 = ga.choice(parent_pop, cdf_vals)

	off_entry = ga.mate_random(trader1['EntrySignals'], trader2['EntrySignals'])
	off_entry = ga.mutate_value_genes(off_entry, SignalsMap)
	off_entry = ga.mutate_enabled_genes(off_entry)
	new_trader['EntrySignals'] = off_entry


	off_exit = ga.mate_random(trader1['ExitSignals'], trader2['ExitSignals'])
	off_exit = ga.mutate_value_genes(off_exit, SignalsMap)
	off_exit = ga.mutate_enabled_genes(off_exit)
	new_trader['ExitSignals'] = off_exit

	off_stop = ga.mate_random(trader1['StopSignals'], trader2['StopSignals'])
	off_stop = ga.mutate_value_genes(off_stop, SignalsMap)
	new_trader['StopSignals'] = off_stop
	new_pop.append(new_trader)


D={'population': new_pop}
D['iteration'] = iteration + 1
with open('populations/population.json', 'w') as outputfile:
	json.dump(D, outputfile)


