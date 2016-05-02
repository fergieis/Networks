from __future__ import division

import pandas as pd
import numpy as np
from gurobipy import *
from pulp import *
from datetime import date


data = pd.read_csv('Cities.csv')


cities = data["City"]
city_pop = data["City Population"]
state_pop = data["State Population"]
states = data["State"]
states_dict = dict(zip(cities, data["State"]))

#### NEED CANDIDATES DATA IN DATA.CSV########
#-------------------------------------------#
cand = np.random.randint(3,90,len(states))

#Currently using start and end dates of elections, will likely
# want to "back off" first election by a bit.
#Maybe also need an indicator for party (R/D)?
start_date = date(2016, 2, 1) #Iowa Caucus
end_date = date(2016, 6, 8) #thru Jun 7 (+1), Jun 14 for DC for Democrats

visits = pd.date_range(start_date, end_date, freq="12H")
index = range(len(visits))
total_visits = [None] * len(visits)
visits_dict = dict(zip(index, visits))

city_per = city_pop / state_pop
city_per = dict(zip(cities, city_per))

state_visits = dict(zip(states, np.zeros(len(states))))
candidates = dict(zip(states, cand))

prob = pulp.LpProblem("OPER617Project", pulp.LpMaximize)

dv = []

for idx, visit in visits_dict.iteritems():
	total_visits[idx] = ""
	
	for city, state in states_dict.iteritems():	
	#Loop through each available 'visit' period and add to model	
		newDV = str(visit)+'-'+ str(city)+'-'+str(state)
		newDV = pulp.LpVariable(newDV, lowBound = 0, upBound = 1, cat= 'Integer')
		dv.append(newDV)
		total_visits[idx] += dv[len(dv)-1]
		state_visits[state] += dv[len(dv)-1]

total_cand = ""



	#winner take all	
prob += lpSum(candidates[state] * (.5 + .15*state_visits[state]<.5 for state in states))
	

#objective function: max total candidates	
#prob += total_cand

#subject to..
for idx, visit in visits_dict.iteritems():
	prob += (total_visits[idx] <= 1)

#results = prob.solve(GUROBI(msg=0))
results = prob.solve()
print("Status:" + str(LpStatus[prob.status]))
print("Optimal at:" + str(value(prob.objective)))

#print optimal solution
print("Solution:\n")

prob.writeMPS("ProblemFormulation.mps")
prob.writeLP("ProblemFormulation.lp")

#for v in prob.variables():
	#if v.varValue != 0:
		#msg = (v.name + "=" + str(v.varValue))
		#print(msg)



