#Networks Midterm
#Question 5
#MAJ Ferguson

import numpy as np
from gurobipy import *
from math import sqrt
from itertools import permutations

m = Model("Q5")
#first s is because non-CS types don't like indexing at 0
points = ["S", "A", "B", "C", "D", "E", "F", "S"]

max_dist = 15

#can construct these data structures using zip() and dict()
#coords = {"A":(5,5),"B": (8,1), "C": (3,7),"D":(2,3), "E":(7,3),"F": (8,8)}
#values = {"A":0,"B":3,"C":5,"D":1,"E":2,"F":4}

#can automatically convert for larger instances, or rewrite to use alpha keywords
coords = {1:(5,5),2: (8,1), 3: (3,7),4:(2,3), 5:(7,3),6: (8,8), 7:(999,999)}
values = {1:0,2:3,3:5,4:1,5:2,6:4,7:0}
#         A   B   C   D   E   F   S

#Build list of all possible edges in K_n
npoints = range(1,len(points))
possibilities = list(permutations(npoints,2))

#inclusion of each node (x) and arc (v) is a decision variable
v ={}
x={}
for i, value in values.iteritems():
	x[i] = m.addVar(vtype=GRB.BINARY, name= "n"+points[i])	
	for j, value in coords.iteritems():		
		v[i,j] = m.addVar(vtype=GRB.BINARY, name = "a"+points[i]+"-"+ points[j])		
m.update()

#Build a distance matrix for distances between all points
d = {}
for A in possibilities:
	p1 = np.array(coords[A[0]])
	p2 = np.array(coords[A[1]])	
	#numpy defaults to the 2-norm	
	dist = np.linalg.norm(p2-p1)		
	d[A] = dist

#Artifical node/arcs for Source/Terminus
#not strictly necessary, but just to be sure
d[(7,1)] = 0
d[(1,7)] = 9999
#this overrides the distance calc to not penalize a move to S
#this allows for variable path lengths without messing everything up
for i in xrange(2,7):
	d[(i,7)] = 0

#if you want a pretty look at the final distance matrix
#pprint.pprint(d)

m.setObjective(quicksum(values[i]*x[i] for i in range(1,7)), GRB.MAXIMIZE)

#node balance constraints
for i in xrange(1,8):
	if i == 1:
		m.addConstr(1 == quicksum(v[1,j] for j in xrange(1,8)))
	elif i == 7:
		m.addConstr(-1 == quicksum(v[i,j]-v[j,i] for j in xrange(1,8)))
	else:	
		m.addConstr(0 == quicksum(v[i,j]-v[j,i] for j in xrange(1,8)))

#don't go back, since isomorphic to complete graph,
# shortest path will never go through another point, even if co-linear (then will ==)
for i in xrange(2,7):
	m.addConstr(x[i] == quicksum(v[j,i] for j in xrange(1,8)))
	for j in xrange(2,7):
		m.addConstr(0 == v[i,j]*v[j,i])

#no auto-cycling
m.addConstr(0 == quicksum(v[i,i] for i in xrange(1,7)))

#can't go farther than 15k
fuel = m.addConstr(max_dist >= quicksum(d[A]*v[A] for A in possibilities))

#set to 0 to mute gurobi output
m.params.OutputFlag = 1
m.optimize()

#print fuel.slack #0.072553361661 cutting it a little close, aren't we?

sol=""
for v in m.getVars():
	if v.x >0:
		sol += v.varName + " " 
print(sol)

#nA aA-C nB aB-S nC aC-F nF aF-B nS 
#z* = 12
# "Rommel, you magnificent bastard, I read your book!"
