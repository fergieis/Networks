
import numpy as np
from gurobipy import *
from math import sqrt
from itertools import permutations

m = Model("Q5")

points = ["", "A", "B", "C", "D", "E", "F"]
#null for point[0] - boo for human readibility
max_dist = 15



#can construct these data structures using zip() and dict()
coords = {"A":(5,5),"B": (8,1), "C": (3,7),"D":(2,3), "E":(7,3),"F": (8,8)}
values = {"A":0,"B":3,"C":5,"D":1,"E":2,"F":4}

coords = {1:(5,5),2: (8,1), 3: (3,7),4:(2,3), 5:(7,3),6: (8,8)}
values = {1:0,2:3,3:5,4:1,5:2,6:4}


#way number 1
npoints = range(1,len(points))
possibilities = list(permutations(npoints,2))
d = {}
for A in possibilities:
	p1 = np.array(coords[A[0]])
	p2 = np.array(coords[A[1]])	
	dist = np.linalg.norm(p2-p1)		
	d[A] = dist

print(d)


#way number 2
v = {}
for i, coord1 in coords.iteritems():
	for j, coord2 in coords.iteritems():
		v[i,j] = m.addVar(ub=1, obj=values[j], name = "v"+points[i]+"-"+ points[j])


m.update()
m.modelSense = GRB.MAXIMIZE

balance = []
total_dist = []
for i in range(1,7):
	balance.append(m.addConstr(1 >= quicksum(v[i,j] for j in range(1,7))))
	balance.append(m.addConstr(1 >= quicksum(v[j,i] for j in range(1,7))))

m.addConstr(max_dist>= quicksum(d[A]*v[A] for A in possibilities))
m.update() 

m.optimize()

for v in m.getVars():
	if v.x >0:	
		print v.varName, v.x 
