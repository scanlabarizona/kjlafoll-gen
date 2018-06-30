#Author: Kyle J. LaFollette
#Department of Psychology, Univerisity of Michigan, Ann Arbor
#Correspondance: kjlafoll@umich.edu

#The function, Zonotope(), for which the code supports, outputs the total number of transitive and intransitive points in a d-Permutahedron, which can be used to model the (in)consistency of voting-oriented decision making. Simply input the number of candidates in your election into the function (i.e. Zonotope(2)), and note whether you'd like to output all vector projections for a manual check (i.e. Zonotope(2, sums=True))

from itertools import combinations
import random as rn
from math import factorial
import time
import numpy as np

vectorlist = []

def choose_combos(n,r,n_chosen): #With n being the dimensionality of the hypercube, r being sequential in the xlist, and n_chosen being the total number of vertices on a facet.
    total_combs = factorial(n)//(factorial(n-r)*factorial(r))
    combos = combinations(range(n),r) #Stores a list of combination tuples in range(n), of length r
    chosen_indexes = rn.sample(range(total_combs),n_chosen)
    random_combos = []
    for i in range(total_combs):
        ele = combos.__next__()
        if i in chosen_indexes:
            random_combos.append(ele)
    return random_combos

def PairwiseComps(p, sums = False):
	print('Calculating pairwise comparisons...')
	global vectorlist
	start_time = time.time() #Records the time at which the computation begins
	vectorlist = []
	for x in range(0,p+1):
		elems_select = choose_combos(p,x,factorial(p)//(factorial(p-x)*factorial(x))) #The third input is the total number of vertices on a facet
		for this in elems_select:
			vector = np.zeros(p,dtype=np.int).tolist()
			for place in range(0,p):
				if place in this:
					vector=[x + y for x, y in zip(vector, np.eye(1,p,place,dtype=np.int).tolist()[0])]
			vectorlist.append(vector)
	for v in vectorlist:
		for index, x in enumerate(v):
			if x == 0:
				v[index] = -1
	if sums == True: #Sums is redudant, and lists all vector projections in output, for a manual check. This way, user can summate the transitive and intransitive points manually, to confirm final output.
		vectorlist = list(combinations(vectorlist, 2))
		for index, x in enumerate(vectorlist):
			vectorlist[index] = [y + z for y, z in zip(x[0], x[1])]
		for x in vectorlist:
			for index, y in enumerate(x):
				if y > 0:
					x[index] = 1
				elif y < 0:
					x[index] = -1
	print('Pairewise Comparison Base Vectors:')
	print(vectorlist)
	print('time taken', time.time() - start_time)

def Zonotope(d, sums = False):
	global vectorlist
	list_of_points = []
	p = (d*(d-1))//2 #p = the dimensionality of the hypercube
	PairwiseComps(p, sums) #run function with dimensionality of hypercube as input
# Construct the Projection Matrix
	for v in vectorlist:
		jmatrix = []
		posit = 0
		jmatrix = np.eye(d,dtype=np.int).tolist() #build an identity matrix of size d
		for index, x in enumerate(jmatrix): #Set 0 along the diagonal, with 1s and -1s making up matrix along either sides of the diagonal
			row = index
			for index, y in enumerate(x):
				if row == index:
					jmatrix[row][index] = 0
				if row < index:
					jmatrix[row][index] = v[posit]
					posit += 1
				if row > index:
					jmatrix[row][index] = (jmatrix[index][row])*(-1)
# Projecting to d-1 Space
		list_of_i = []
		for x in range(1,d+1):
			innersum = 0
			for y in range(1,d+1):
				if x != y:
					innersum += (jmatrix[x-1][y-1] + 1) #The dxd pairwise comparison matrix
			elementi = np.zeros(d,dtype=np.int).tolist() #The base vector where the ith element is equal to 1
			elementi[x-1] = innersum #Changes the ith element to  the innersum
			list_of_i.append(elementi) #A list of weighted base vectors
		while len(list_of_i) > 1: #Concatenates the base vectors to vector representative of transitivities
			list_of_i[0] = [x + y for x, y in zip(list_of_i[0],list_of_i[1])]
			del list_of_i[1]
		point = []
		for x in list_of_i[0]:
			point.append((x/2)+1)
		list_of_points.append(point)
	print('Projected Vertices:')
	print(list_of_points)
# Counts
	countslist = []
	for x in list_of_points:
		z = 0
		for y in range(1,d+1):
			if x.count(y) > z:
				z = x.count(y)
		countslist.append(z)
	print('Transitive Points: %s' % countslist.count(1))		
	for x in range(0,d-1):
		print('Intransitive-%s Points: %r' % (d-x, countslist.count(d-x)))


