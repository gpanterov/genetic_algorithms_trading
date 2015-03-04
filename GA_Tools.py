import numpy as np
from bisect import bisect
import random

def cdf(weights):
    total=sum(weights) * 1.
    result=[]
    cumsum=0
    for w in weights:
        cumsum += w 
        result.append(cumsum/total)
    return result

def choice(population, cdf_vals):
    """ 
    Returns a random element of population sampled according
    to the weights cdf_vals (produced by the func cdf)
    Inputs
    ------
    population: list, a list with objects to be sampled from
    cdf_vals: list/array with cdfs (produced by the func cdf)
    Returns
    -------
    An element from the list population
    """
    assert len(population) == len(cdf_vals)
    x = random.random()
    idx = bisect(cdf_vals,x)
    return population[idx]

def mate_random(chrom1, chrom2):
	"""
	Mates two chromosomes by exchangin randomly each gene
	"""
	offspring = []

	for pos in range(len(chrom1)):
		gene1 = []
		for gene_pos in range(len(chrom1[pos])):
			if random.getrandbits(1) == 0:
				gene1.append(chrom1[pos][gene_pos])
			else:
				gene1.append(chrom2[pos][gene_pos])
			
		offspring.append(tuple(gene1))
	return tuple(offspring)

def mate_monoploid_random(w1, w2):
	offspring=[]
	for pos in range(len(w1)):
		if random.getrandbits(1) == 0:
			offspring.append(w1[pos])
		else:
			offspring.append(w2[pos])
	return offspring

def mutate_monoploid(w, mutate_prob=1e-2, sig=0.1):
	mutated_w = []
	for gene in w:
		if np.random.uniform() < mutate_prob:
			mutated_w.append(np.random.normal(gene, sig))
		else:
			mutated_w.append(gene)
	return np.array(mutated_w)

def truncated_random_normal(val, val_range, share=0.1):
	"""
	returns a random normal around val within the range
	(used for mutation)
	share: the share of the range which is equal to the st.dev
	"""
	sig = share * (val_range[1] - val_range[0])
	res = np.random.normal(val, sig)
	res = min(res, val_range[1])
	res = max(res, val_range[0])
	return res

def mutate_value_genes(chrom, SignalsMap, mutate_prob=1e-3, verbose=False):
	mutated_chrom = []
	for pos in range(len(chrom)):
		gene = list(chrom[pos])
		for gene_pos in range(len(gene[:-1])):
			if np.random.uniform() < mutate_prob:
				val_range = SignalsMap[pos][gene_pos+1]
				val = gene[gene_pos]
				new_val = truncated_random_normal(val, val_range)
				if verbose:
					print "Mutating at ", pos, gene_pos
					print "Changing from ", val, " to ", new_val

				gene[gene_pos] = new_val


		gene = tuple(gene)
		mutated_chrom.append(gene)
	return tuple(mutated_chrom)

def mutate_enabled_genes(chrom, mutate_prob_on=1e-3, mutate_prob_off=1e-2, verbose=False):
	mutated_chrom = []
	for pos in range(len(chrom)):
		gene = list(chrom[pos])
		switch = False
		if gene[-1]: # gene is enabled
			if np.random.uniform() < mutate_prob_off:
				switch = True
		else:
			if np.random.uniform() < mutate_prob_on:
				switch = True
		if switch:
			if verbose:
				print pos, " switch from ", gene[-1]

			gene[-1] = bool(np.invert(gene[-1]))  # You need to transform from numpy.bool to bool for the json.dump to work !!
		
		mutated_chrom.append(tuple(gene))
	return tuple(mutated_chrom)


