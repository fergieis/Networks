import networkx as nx
import numpy as np
from itertools import permutations
import matplotlib.pyplot as plt
import sys



g = nx.Graph()
points = ["A", "B", "C", "D", "E", "F"]
max_dist = 15

#dg = nx.DiGraph()
dg = nx.Graph()

possibilities = list(permutations(points,2))
npoints = range(1,len(points))
d = {}
coords = {"A":(5,5),"B": (8,1), "C": (3,7),"D":(2,3), "E":(7,3), "F": (8,8), "S":(9999,9999) }
values = {"A":0,"B":3,"C":5,"D":1,"E":2,"F":4}

edges = []

for A in possibilities:
	p1 = np.array(coords[A[0]])
	p2 = np.array(coords[A[1]])	
	dist = np.linalg.norm(p2-p1)		
	d[A] = dist
	edges.append((A[0],A[1],dist))
	dg.add_node(A[0]+A[1], demand= dist)
	dg.add_edge(A[0],A[0]+A[1],weight=-values[A[1]])
	dg.add_edge(A[0]+A[1], A[1], weight=0)



dg.node["A"]['demand'] = -15
print(list(dg))
T = nx.bfs_tree(dg,"A")
print(list(T))

#cycles = print(nx.cycle_basis(dg,"A"))


#benefit, flow = nx.network_simplex(dg)



##can also pull from a dictionary
#edges = [(k[0], k[1], v) for k,v in d.iteritems()]
#dg.add_weighted_edges_from(edges)


##Isomorphic to K_6 (not anymore though)
#nx.draw(dg)
#nx.draw_random(dg)
#nx.draw_circular(dg)
#nx.draw_spectral(dg)
#plt.show()

