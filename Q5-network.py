import sys
import numpy as np
from gurobipy import *
from math import sqrt
from itertools import permutations
#import networkx as nx

#q = int(sys.argv[1])

m = Model("Q5")
#G = nx.Graph()


points = ["S", "A", "B", "C", "D", "E", "F"]
max_dist = 15


#can construct these data structures using zip() and dict()
coords = {"A":(5,5),"B": (8,1), "C": (3,7),"D":(2,3), "E":(7,3),"F": (8,8)}
values = {"A":0,"B":3,"C":5,"D":1,"E":2,"F":4}

coords = {1:(5,5),2: (8,1), 3: (3,7),4:(2,3), 5:(7,3),6: (8,8) }
values = {1:0,2:3,3:5,4:1,5:2,6:4}

#G.add_nodes_from(coords.keys())
npoints = range(1,len(points))
possibilities = list(permutations(npoints,2))
#G.add_edges_from(possibilities)


#way number 1
v = {}
x={}
for i, value in values.iteritems():
	print(value)	
	#x[i] = m.addVar(vtype=GRB.BINARY, obj=value, name= "n"+points[i])	
	x[i] = m.addVar(vtype=GRB.BINARY, name= "n"+points[i])
	for j, value in coords.iteritems():		
		v[i,j] = m.addVar(vtype=GRB.BINARY, name = "a"+points[i]+"-"+ points[j])		
	
		

m.update()

#way number 2
d = {}
c={}
for A in possibilities:
	p1 = np.array(coords[A[0]])
	p2 = np.array(coords[A[1]])	
	dist = np.linalg.norm(p2-p1)		
#	c[A] = values[A[1]]

	d[A] = dist
#	G[A[0]][A[1]]['weight'] = dist


m.setObjective(quicksum(values[i]*x[i] for i in range(1,7)), GRB.MAXIMIZE)


##Must have an arc from A
m.addConstr(1==quicksum(v[1,j] for j in xrange(1,7)))
#nothing goes back to A
m.addConstr(0==quicksum(v[j,1] for j in xrange(1,7)))

for i in range(2,7):
	m.addConstr(x[i] == quicksum(v[i,j] for j in xrange(2,7)))
	#m.addConstr(x[i] == quicksum(v[j,i] for j in xrange(2,7)))

#no auto-cycling
m.addConstr(0 == quicksum(v[i,i] for i in xrange(1,7)))

#can't go farther than 15k
m.addConstr(max_dist >= quicksum(d[A]*v[A] for A in possibilities))

#m.addConstr(0>nx.node_connectivity

#only get points for getting there
#for i in xrange(1,7):
#	m.addConstr(x[i] <= quicksum(v[j,i] for j in xrange(1,7)))
	
m.params.OutputFlag = 1
m.optimize()
#print(q, m.objVal)
sol=""
for v in m.getVars():
	if v.x >0:
		sol += v.varName + " " 
print(sol)
