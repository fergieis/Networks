from __future__ import division

import pandas as pd
import numpy as np
from gurobipy import *
#from pulp import *
from datetime import date, datetime


def date2t(curr_date):
	start_date = date(2016, 2, 1) #Iowa Caucus
	diff = datetime.utcfromtimestamp(curr_date)-start_date	
	diff = 2 * diff.days + diff.seconds//43200,
	return diff


data = pd.read_csv('Cities.csv')

cities = {}
for key, s in data.groupby("State")['City']:
    cities[key] = list(s)



#city_list = data["City"]
#cities=dict(zip(data["State"]

city_pop = data["City Population"]
state_pop = data["State Population"]
states_list = data["State"]
states = dict(zip(cities, data["State"]))

#### NEED CANDIDATES DATA IN DATA.CSV########
#-------------------------------------------#
cand = np.random.randint(3,90,len(states))

#Currently using start and end dates of elections, will likely
# want to "back off" first election by a bit.
#Maybe also need an indicator for party (R/D)?
start_date = date(2016, 2, 1) #Iowa Caucus
end_date = date(2016, 6, 8) #thru Jun 7 (+1), Jun 14 for DC for Democrats



visits = pd.date_range(start_date, end_date, freq="12H")
visit_index = range(len(visits))
total_visits = [None] * len(visits)
visits_dict = dict(zip(xrange(1,len(visits)+1), visits))
T = len(visits)

city_per = city_pop / state_pop
city_per = dict(zip(cities, city_per))

state_visits = dict(zip(states, np.zeros(len(states))))
candidates = dict(zip(states, cand))

m = Model("OPER617Project")
#prob = pulp.LpProblem("OPER617Project", pulp.LpMaximize)

v ={}
I ={}
mu={}

for state in states:
	for city in cities[state]:
		I[state] = m.addVar(vtype=GRB.BINARY, name="Win-"+ str(state))		
		for t in visits_dict:
#NEEDS END DATES ADDED
			try:			
				mu[state,t] = max((50/(T-t)), 0)
			except ZeroDivisionError:
				mu[state,t] = 0
#What do we want ON election day?
			v[city,t] = m.addVar(vtype=GRB.BINARY, name=str(city)+", "+ str(state) + ":"+ str(t))
	


