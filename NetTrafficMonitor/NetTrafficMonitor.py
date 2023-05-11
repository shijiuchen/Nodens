import os
import time
import copy
import math
import sys
sys.path.append("..") 
from client.client import rpc_get_net_proc

traffic_mapper_old={}
t_old=0

#get traffic data based on network interface
#every 1 second
def getTraffic(ms_dag):
    ms_interface_mapper=ms_dag.ms_interface_mapper
    traffic_mapper={}
    res=[]
    for k,v in ms_dag.NodeIpMapper.items():
        res_rpc=rpc_get_net_proc(v)
        res.extend(res_rpc)
    for i in range(2,len(res)):
        line=res[i].replace("\n","").split(" ")
        while '' in line:
            line.remove('')
        interface=line[0].replace(":","")
        if(interface in ms_interface_mapper.keys()):
            if(ms_interface_mapper[interface] not in traffic_mapper.keys()):
                traffic_mapper[ms_interface_mapper[interface]]=[int(line[9]),int(line[1])]
            else:
                traffic_mapper[ms_interface_mapper[interface]][0]+=int(line[9])
                traffic_mapper[ms_interface_mapper[interface]][1]+=int(line[1])
    return traffic_mapper

#call traffic difference
def calTrafficRate(traffic_mapper_old,traffic_mapper_new,duration):
    this_sample_rate={}
    for key in traffic_mapper_old:
        in_traffic_rate=(traffic_mapper_new[key][0]-traffic_mapper_old[key][0])/duration/1000000*8
        out_traffic_rate=(traffic_mapper_new[key][1]-traffic_mapper_old[key][1])/duration/1000000*8
        this_sample_rate[key]=[in_traffic_rate,out_traffic_rate,duration]
    return this_sample_rate

#Post order update based on structure
def calUpperandBacktrafic(ms_dag,this_sample_rate):
    for target in ms_dag.Access_Record:
        target.in_traffic=this_sample_rate[target.name][0]
        target.out_traffic=this_sample_rate[target.name][1]
        target.upper_traffic=target.in_traffic
        target.back_traffic=target.out_traffic
        for child in target.children:
            target.upper_traffic-=child.back_traffic
            target.back_traffic-=child.upper_traffic
            #deal with fluncations
            if(target.upper_traffic<0):
                target.upper_traffic=0
            if(target.back_traffic<0):
                target.back_traffic=0

#For initialization
def initialize(ms_dag):
    global traffic_mapper_old,t_old
    traffic_mapper_old=getTraffic(ms_dag)
    t_old=time.time()
    print(t_old,traffic_mapper_old)
    # print("==========")

def runOneTime(ms_dag):
    global t_old,traffic_mapper_old
    # print(t_old,traffic_mapper_old)
    traffic_mapper_new=getTraffic(ms_dag)
    t_new=time.time()
    # print(t_new,traffic_mapper_new)
    this_sample_rate=calTrafficRate(traffic_mapper_old,traffic_mapper_new,t_new-t_old)
    # this_Access_Record=calUpperandBacktrafic(copy.deepcopy(ms_dag.Access_Record),this_sample_rate)
    calUpperandBacktrafic(ms_dag,this_sample_rate)
    # print(ms_dag.Access_Record[11].upper_traffic,this_sample_rate['entering-ms'][2])
    # update the last record
    t_old=t_new
    traffic_mapper_old=traffic_mapper_new
    return this_sample_rate['entering-ms'][2]

#For separable test
def runTrafficMonitor(Access_Record):
    traffic_mapper_old=getTraffic()
    t_old=time.time()
    while(True):
        time.sleep(1)
        traffic_mapper_new=getTraffic()
        t_new=time.time()
        this_sample_rate=calTrafficRate(traffic_mapper_old,traffic_mapper_new,t_new-t_old)
        this_Access_Record=calUpperandBacktrafic(copy.deepcopy(Access_Record),this_sample_rate)
        # obtain upper traffic
        print(this_Access_Record[11].name,this_Access_Record[11].upper_traffic,this_sample_rate['entering-ms'][2])
        # temp_Record.append(this_Access_Record[11].upper_traffic)
        traffic_mapper_old=traffic_mapper_new
        t_old=t_new
    # print(len(temp_Record))