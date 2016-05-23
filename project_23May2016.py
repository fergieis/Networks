from __future__ import division
from math import floor,sqrt
import pandas as pd
import numpy as np
from gurobipy import *
#from pulp import *
from datetime import date, datetime



#Currently using start and end dates of elections, will likely
# want to "back off" first election by a bit.
#Maybe also need an indicator for party (R/D)? Currently, model assumes R
start_date = date(2015, 2, 1) #1 year before Iowa Caucus
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
citylist=data.City


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
degrade={}
		
for i,state in enumerate(states):
	poll[i,0] = initpoll[state]
	I[i] = m.addVar(vtype=GRB.BINARY, name="Win-"+ str(state))		
	for t in visits_dict:
		poll[(i,t)] = m.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name=str(state)+"at_time_" +str(t))
		if t<enddate[state]:			
			mu[(i,t)] = (1/(enddate[state]-t+2))
		else:			
			mu[(i,t)] = 0
		

for i,state in enumerate(states):
	for city in cities[state]:	
		for t in visits_dict:
			degrade[(city,t)]=  city_per[city] *0.00005			
			v[(city,t)] = m.addVar(vtype=GRB.BINARY, name=str(city)+", "+ str(state) + ":"+ str(t))

m.update()


m.setObjective(quicksum(I[i]*delegates_wta[s] + poll[(i,enddate[s])]*delegates_per[s] for i,s in enumerate(states)), GRB.MAXIMIZE)


for i,s in enumerate(states):
	#indicator of whether we win a state	
	diff = LinExpr(I[i] - poll[(i,enddate[s])])
	inf = info[info["State"]==s]
	m.addConstr(diff <= 1-float(inf.WTA_Thresh))
	for t in visits_dict:
		if t > 1:		
		#change in polling must equal either change by visit, or decay due to no visit, both scaled by temporal proximity to that state's election day
			diff = LinExpr(poll[(i,t)] - poll[(i,t-1)])		
			m.addConstr(mu[(i,t)] * quicksum(city_per[city]* v[(city,t)] - degrade[(city,t)]*(1-v[(city,t)]) for city in cities[s]), GRB.EQUAL, diff)
			
		else:
			diff = LinExpr(poll[(i,t)]-initpoll[s])		
			m.addConstr(mu[(i,t)] * quicksum(city_per[city]* v[(city,t)] - degrade[(city,t)]*(1-v[(city,t)]) for city in cities[s]), GRB.EQUAL, diff)
for t in visits_dict:
	m.addConstr(quicksum(v[(city,t)] for city in citylist),GRB.EQUAL,1)

###add poll[s,end[state]]
m.params.MIPGapAbs = .1
m.update()
m.optimize()

f = open("Solution.txt","w")
sol=""
#for v in m.getVars():
#	if v.x >0:
#		sol += v.varName + "=" + str(v.x)+"\n" 

for i,s in enumerate(states):
	f.write(s+":"+str(poll[i,enddate[s]].x)+"\n")	
#	if I[i].x >0:
#		f.write("Win "+ str(s)+"\n")
for city in citylist:
	for t in visits_dict:
		if v[(city,t)].x > 0:	
			f.write(str(visits_dict[t])+" "+ city+ str(v[(city,t)].x)+"\n")
f.close()
