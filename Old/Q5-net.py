import sys
import numpy as np
from gurobipy import *
from math import sqrt
from itertools import permutations
import networkx as nx

q = int(sys.argv[1])

m = Model("Q5")
G = nx.Graph()


points = ["S", "A", "B", "C", "D", "E", "F"]

max_dist = 15


#can construct these data structures using zip() and dict()
coords = {"A":(5,5),"B": (8,1), "C": (3,7),"D":(2,3), "E":(7,3),"F": (8,8)}
values = {"A":0,"B":3,"C":5,"D":1,"E":2,"F":4}

coords = {1:(5,5),2: (8,1), 3: (3,7),4:(2,3), 5:(7,3),6: (8,8), 0:(999,999)}
values = {1:0,2:3,3:5,4:1,5:2,6:4, 0:0}

G.add_nodes_from(coords.keys())
npoints = range(0,len(points))
possibilities = list(permutations(npoints,2))
G.add_edges_from(possibilities)


#way number 1
v = {}
for i, coord1 in coords.iteritems():
	for j, coord2 in coords.iteritems():		
		v[i,j] = m.addVar(ub=1, vtype=GRB.BINARY, name = "v"+points[i]+"-"+ points[j])		

m.update()




#way number 2
d = {}
c={}
for A in possibilities:
	p1 = np.array(coords[A[0]])
	p2 = np.array(coords[A[1]])	
	dist = np.linalg.norm(p2-p1)		
	c[A] = values[A[1]]

	if A[0] == 0:
	
		if A[1] == 1:
			d[A] = 0
			G[A[0]][A[1]]['weight'] = 0
		else:
			d[A] = 999
	elif A[1] == 0:
		if A[0] == 1:
			d[A] = 999
		else:
			d[A] = 0
	else:
		d[A] = dist
		G[A[0]][A[1]]['weight'] = dist


m.setObjective(quicksum(c[A]*v[A] for A in possibilities), GRB.MAXIMIZE)

balance = []

#balance.append(m.addConstr(1 >= quicksum(v[1,j] for j in range(1,7))))
#balance.append(m.addConstr(0 == quicksum(v[1,j]-v[j,1] for j in range(1,7)) ))


for i in range(0,7):
	if i == 1:
		##Must start at A/1
		m.addConstr(1 <= quicksum(v[i,j] for j in xrange(0,7)) % 2)
	elif i == q:
		m.addConstr(1 ==quicksum(v[j,i] for j in xrange(0,7)) % 2)
	#have to go somewhere
#	balance.append(m.addConstr(1 >= quicksum(v[i,j] for j in range(0,7))))
	#have to have come from somewhere
#	balance.append(m.addConstr(1 >= quicksum(v[j,i] for j in range(0,7))))
	balance.append(m.addConstr(0 == quicksum(v[i,j]-v[j,i] for j in range(1,7)) % 2))
	balance.append(m.addConstr(1 >= quicksum(v[j,i]+v[i,j] for j in range(0,7)) % 2))

#can't go farther than 15k
m.addConstr(max_dist >= quicksum(d[A]*v[A] for A in possibilities))


m.update() 

#for i in G.nodes_iter():
# m.addConstr(0 == grb.quicksum(v for j in g.neighbors_iter(i)))

m.optimize()

for v in m.getVars():
	if v.x >0:
		print v.varName, v.x 
