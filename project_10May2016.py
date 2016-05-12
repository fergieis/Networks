from __future__ import division
from math import floor
import pandas as pd
import numpy as np
from gurobipy import *
#from pulp import *
from datetime import date, datetime

perchange = .02

#Currently using start and end dates of elections, will likely
# want to "back off" first election by a bit.
#Maybe also need an indicator for party (R/D)?
start_date = date(2015, 2, 1) #Iowa Caucus
end_date = date(2016, 6, 8) #thru Jun 7 (+1), Jun 14 for DC for Democrats


def date2t(curr_date):
	start_date = date(2015, 2, 1)
	diff = datetime.utcfromtimestamp(curr_date)-start_date	
	diff = 2 * diff.days + diff.seconds//43200,
	return diff

data = pd.read_csv('Cities.csv')
info = pd.read_csv('ElectionInfo.csv')
p = pd.read_csv('InitialPolls.csv', skip_blank_lines=True)
p = p.dropna()

states =[]
cities = {}
c2s = {}

delegates = dict(zip(info.State, info.NumDel))
delegates_wta = dict(zip(info.State, info.WTADel))
delegates_per = dict(zip(info.State, info.PerDel))
initpoll = dict(zip(p.State,p.InitialPoll /100))
enddate = dict(zip(info.State,info.endT))



for key, s in data.groupby("State")['City']:
	cities[key] = list(s)
	states.append(key)

for i, state in enumerate(states):
	cities[i] = cities[state]
	delegates_wta[i] = delegates_wta[state]


city_list = data["City"]

city_pop = data["City Population"]
state_pop = data["State Population"]


visits = pd.date_range(start_date, end_date, freq="12H")
visit_index = range(len(visits))
total_visits = [None] * len(visits)
visits_dict = dict(zip(xrange(1,len(visits)+1), visits))

city_per = city_pop / state_pop
city_per = dict(zip(city_list, city_per))

m = Model("OPER617Project")

v ={}
I ={}
poll={}
mu={}
for i,state in enumerate(states):
	poll[i,0] = initpoll[state]
	for city in cities[state]:
		I[i] = m.addVar(vtype=GRB.BINARY, name="Win-"+ str(state))		
		for t in visits_dict:
			poll[(i,t)] = m.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name=str(state)+"at_time_" +str(t))
			try:			
				mu[(i,t)] = perchange * max((50/(enddate[state]-t)), 0)
			except ZeroDivisionError:			
				mu[(i,t)] = 5
			v[(city,t)] = m.addVar(vtype=GRB.BINARY, name=str(city)+", "+ str(state) + ":"+ str(t))
	
m.update()


m.setObjective(quicksum(I[i]*delegates_wta[s] + poll[(i,enddate[s])]*delegates_per[s] for i,s in enumerate(states)), GRB.MAXIMIZE)

for i,s in enumerate(states):
	#indicator of whether we win a state	
	diff = LinExpr(I[i] - poll[(i,enddate[s])])
	inf = info[info["State"]==s]
	m.addConstr(diff <= 1-float(inf.WTA_Thresh))
	for t in visits_dict:
		#polling can't exceed our 
		diff = LinExpr(poll[(i,t-1)] - poll[(i,t)])		
			#mu * sqrt(1-poll)
		m.addConstr(mu[(i,t)] * quicksum(city_per[city]* v[(city,t)] for city in cities[i]), GRB.EQUAL, diff)
###add poll[s,end[state]]

m.optimize()

