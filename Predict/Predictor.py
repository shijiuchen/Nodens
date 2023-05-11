import csv
import scipy.stats as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import time

#Record the slope and interceptes
#(Examples, need to fit on own clusters)
params_net_to_load={
    "entering-ms":[0.06,0.1],
    "frontend-search":[0.06,0.1],
    "frontend-recommend":[0.06,0.1],
    "frontend-reserve":[0.06,0.1],
    "search":[0.06,0.1],
    "check":[0.06,0.1],
    "recommendation":[0.06,0.1],
    "profile":[0.06,0.1],
    "user":[0.06,0.1],
    "reservation":[0.06,0.1],
    "geo":[0.06,0.1],
    "rate":[0.06,0.1],
    "memcached-check":[0.06,0.1],
    "rank-category":[0.06,0.1],
    "rank-overall":[0.06,0.1],
    "memcached-profile":[0.06,0.1],
    "memcached-reservation":[0.06,0.1],
    "mongodb-reservation":[0.06,0.1],
    "memcached-rate":[0.06,0.1]
}

#Record the slope and interceptes
#(Examples, need to fit on own clusters)
params_load_to_CPU={
    "entering-ms":[0.06,0.1],
    "frontend-search":[0.06,0.1],
    "frontend-recommend":[0.06,0.1],
    "frontend-reserve":[0.06,0.1],
    "search":[0.06,0.1],
    "check":[0.06,0.1],
    "recommendation":[0.06,0.1],
    "profile":[0.06,0.1],
    "user":[0.06,0.1],
    "reservation":[0.06,0.1],
    "geo":[0.06,0.1],
    "rate":[0.06,0.1],
    "memcached-check":[0.06,0.1],
    "rank-category":[0.06,0.1],
    "rank-overall":[0.06,0.1],
    "memcached-profile":[0.06,0.1],
    "memcached-reservation":[0.06,0.1],
    "mongodb-reservation":[0.06,0.1],
    "memcached-rate":[0.06,0.1]
}

# Record corresponding edges
edge_mapper={
    "geo": [[4,10]],
    "memcached-rate": [[11,18]],
    "rate": [[4,11]],
    "search": [[1,4]],
    "memcached-check": [[5,12]],
    "check": [[10,5],[18,5]], #2 in-degrees
    "frontend-search": [[0,1]],
    "rank-category": [[6,13]],
    "rank-overall": [[6,14]],
    "recommendation": [[2,6]],
    "memcached-profile": [[7,15]],
    "profile": [[13,7],[14,7]], #2 in-degrees
    "frontend-recommend": [[0,2]],
    "user": [[3,8]],
    "memcached-reservation": [[9,16]],
    "mongodb-reservation": [[9,17]],
    "reservation": [[8,9]],
    "frontend-reserve": [[0,3]]
}

#Get the monitored load
def predict_net_to_load(ms_dag):
    print("Monitor Load......")
    for target in ms_dag.Access_Record:
        slope=params_net_to_load[target.name][0]
        intercept=params_net_to_load[target.name][1]
        target.monitorLoad=target.upper_traffic*slope+intercept
        '''
        # Profile values with traffic error to avoid network fluctuations to evaluate
        target.monitorLoad=Base_MonitoredLoad[target.name]*TrafficMonitorError[target.name]
        '''
        print(target.name,target.monitorLoad)
        # no in-degrees of entering ms
        if(target.name=="entering-ms"):
            continue
        # Update edges in the Load_matrix
        edges=edge_mapper[target.name]
        if(len(edges)==1):#1 in-degree
            ms_dag.Load_matrix[edges[0][0],edges[0][1]]=target.monitorLoad
        else:# multiple in-degrees
            ratios=[0,0]
            if(target.name=="check"):
                load1=min(ms_dag.Access_Record[0].handleLoad,ms_dag.Access_Record[0].monitorLoad)
                load2=min(ms_dag.Access_Record[2].handleLoad,ms_dag.Access_Record[2].monitorLoad)
                ratios[0]=load1/(load1+load2)
                ratios[1]=1-ratios[0]
            elif(target.name=="profile"):
                load1=min(ms_dag.Access_Record[7].handleLoad,ms_dag.Access_Record[7].monitorLoad)
                load2=min(ms_dag.Access_Record[8].handleLoad,ms_dag.Access_Record[8].monitorLoad)
                ratios[0]=load1/(load1+load2)
                ratios[1]=1-ratios[0]
            for i in range(len(edges)):
                edge=edges[i]
                ratio=ratios[i]
                ms_dag.Load_matrix[edge[0],edge[1]]=target.monitorLoad*ratio

#Obtain the CPU allocation
def predict_load_to_CPU(ms_dag):
    for target in ms_dag.Access_Record:
        slope=params_load_to_CPU[target.name][0]
        intercept=params_load_to_CPU[target.name][1]
        target.CPU_Need=target.realLoad*slope+intercept
        target.CPU_Allocated=(target.realLoad+target.overLoad)*slope+intercept
        over_CPU=target.CPU_Allocated-target.CPU_Need
        '''
        # Profile CPUs with real-load error to avoid prediction interference to evaluate
        ratio=target.realLoad/Base_RealLoad[target.name]
        target.CPU_Need=Profile_CPUs[target.name]*ratio
        over_CPU=target.overLoad/target.realLoad*target.CPU_Need
        target.CPU_Allocated=over_CPU+target.CPU_Need
        '''
        print(target.name,target.realLoad,target.overLoad,over_CPU,target.CPU_Allocated)

if __name__ == "__main__":
    predict_load_to_CPU()