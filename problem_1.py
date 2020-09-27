# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 11:36:53 2020

@author: Rahul
"""

import os
import pandas as pd
import datetime 

# Setting up working directory

path=os.chdir('B:/College/IITM/Beta hackathon/Chennai GTFS/MTC')
print(path)
files=os.listdir(path)
for i in files:
	print(i)
del(path,i)

# Reading files as tables 

agency=pd.read_csv("agency.txt")
calendar=pd.read_csv("calendar.txt")
frequencies=pd.read_csv("frequencies.txt")
routes=pd.read_csv("routes.txt")
stops=pd.read_csv("stops.txt")
stoptimes=pd.read_csv("stop_times.txt")
trips=pd.read_csv("trips.txt")

# Checking valid Boarding point

stop_IDs=[]
k=0
a=0
while (a==0):
     Board=input("Enter the Boarding point: ")
     for i in range(len(stops['stop_name'])): 
         if (Board==stops['stop_name'][i]):
             Boarding_point=Board
             stop_IDs.append(stops['stop_id'][i])
             a=1
             k=k+1
         
     if (a==0):
         print("Please enter a Valid Boarding point")
         
del(Board)
del(a)
del(i)
print(Boarding_point)       
   
# Checking valid time


    
validtime = False

while(validtime==False):   
    print("Please enter time in HH:MM format only")
    Time=input("Enter the time in HH:MM 24 hour format: ")
    res = Time.find(':')
    length=len(Time)
    while(res==-1 or len(Time)!=5):
        # print(res)
        print("Please enter time in HH:MM format only")
        Time=input("Enter the time in HH:MM 24 hour format: ")
        res = Time.find(":")
    hours,minutes = Time.split(':')
    validtime = True
    try :
        datetime.time(int(hours),int(minutes))
    except ValueError :
        validtime = False              

Hours=int(hours)
Minutes=int(minutes)
del(hours)
del(minutes)
del(res)
del(length)
del(validtime)

# Getting the list of relevant buses 

k=0
compare1=datetime.time(hour=Hours,minute=Minutes ,second=0)
stoprelateddata=pd.DataFrame(columns=stoptimes.columns)

for j in range(len(stop_IDs)):
    i = 0
    l = 0
    #for i in range(len(stoptimes['stop_id'])):
    while i < len(stoptimes['stop_id']):    
        hours,minutes,seconds = stoptimes['arrival_time'][i].split(':')
        if (int(hours)>=24):
            hours=int(hours)-24            
        compare2=datetime.time(hour=int(hours),minute=int(minutes),second=int(seconds))
        if (stoptimes['stop_id'][i]==stop_IDs[j] and compare2>=compare1):
            stoprelateddata.loc[k]=stoptimes.loc[i]
            k=k+1
            l=l+1
        if (l==6):
            i = len(stoptimes['stop_id'])
        else:
            i += 1
        
    
del(i)
del(j)        

# Getting route ID, ETA and terminal stop

Times=Time+":00"
route_id=[]
ETA=[]
terminal_stops = []
for i in range(len(stoprelateddata['trip_id'])):
    found = False
    j = 0
    terminal_id = stoptimes[stoptimes.trip_id == stoprelateddata['trip_id'][i]].stop_id.to_list()[-1]
    terminal_stops.append(stops[stops.stop_id == terminal_id].stop_name.iloc[0])
    while j < len(trips['route_id']) and not found: 
       if (stoprelateddata['trip_id'][i]==trips['trip_id'][j]):
           route_id.append(trips['route_id'][j])
           FMT = '%H:%M:%S'
           tdelta = datetime.datetime.strptime(stoprelateddata['arrival_time'][i], FMT) - datetime.datetime.strptime(Times, FMT)
           ETA.append(tdelta)
           found = True
       j += 1

stoprelateddata['route_id']=route_id      
stoprelateddata['ETA']=ETA
stoprelateddata['terminal_stop'] = terminal_stops
stoprelateddata.drop(columns=['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'], inplace=True)
         




