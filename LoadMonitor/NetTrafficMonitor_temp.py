import os
import time
import copy
import math
import sys
sys.path.append("..") 
from client.client import rpc_get_net_proc

PodNodeMapper={}
NodeIpMapper={
    "cpu-03":"10.2.64.3:50052",
    "cpu-04":"10.2.64.4:50052",
    "cpu-07":"10.2.64.7:50052",
    "cpu-08":"10.2.64.8:50052",
}

class Node:
    def __init__(self,name,in_traffic,out_traffic,upper_traffic,back_traffic,children):
        self.name=name
        self.in_traffic=in_traffic
        self.out_traffic=out_traffic
        self.upper_traffic=upper_traffic
        self.back_traffic=back_traffic
        self.children=children
    def display(self):
        print(self.name,self.in_traffic,self.out_traffic,self.upper_traffic,self.back_traffic,self.children)


def buildDAG():
    profilemmc=Node("memcached-profile",0,0,0,0,[])
    ratemmc=Node("memcached-rate",0,0,0,0,[])
    reservemmc=Node("memcached-reserve",0,0,0,0,[])
    reservemongodb=Node("mongodb-reservation",0,0,0,0,[])
    checkmmc=Node("memcached-check",0,0,0,0,[])
    rank_category=Node("rank-category",0,0,0,0,[])
    rank_overall=Node("rank-overall",0,0,0,0,[])
    recommend=Node("recommendation",0,0,0,0,[rank_category,rank_overall])
    geo=Node("geo",0,0,0,0,[])
    user=Node("user",0,0,0,0,[])    
    profile=Node("profile",0,0,0,0,[profilemmc])
    rate=Node("rate",0,0,0,0,[ratemmc])
    search=Node("search",0,0,0,0,[geo,rate])
    check=Node("check",0,0,0,0,[checkmmc])
    reserve=Node("reservation",0,0,0,0,[reservemmc,reservemongodb])
    frontendSearch=Node("frontend-search",0,0,0,0,[search,check])
    frontendRecommend=Node("frontend-recommend",0,0,0,0,[recommend,profile])
    frontendReserve=Node("frontend-reserve",0,0,0,0,[user,reserve])
    EnteringMS=Node("entering-ms",0,0,0,0,[frontendSearch,frontendRecommend,frontendReserve])
    return EnteringMS

def postOrder(Access_Record,root):
    if not root:
        return
    for target in root.children:
        postOrder(Access_Record,target)
    Access_Record.append(root)

ms_interace_mapper={}

def ms_interace():
    global ms_interace_mapper, PodNodeMapper
    pods=os.popen("kubectl get pods -o wide | awk '{print $1}'").readlines()
    nodes=os.popen("kubectl get pods -o wide | awk '{print $7}'").readlines()
    for i in range(len(pods)):
        pod=pods[i].replace("\n","")
        node=nodes[i].replace("\n","")
        if(pod=="NAME"):
            continue
        id=os.popen("kubectl exec -i "+pod+" -- cat /sys/class/net/eth0/iflink").readlines()[0].replace("\n", "")
        print(pod,id)
        idtarget="^'"+id+":"+" "+"'"
        if(node=="cpu-06"):
            temp=os.popen("ip link show | grep "+idtarget+" | awk '{print $2}'").readlines()[0].replace("\n", "")
        else:
            temp=os.popen("ssh "+node+" 'ip link show | grep "+idtarget+"'").readlines()[0].replace("\n", "").split(" ")[1]
        index=temp.find('@')
        iplink=temp[:index]
        temp=pod.split("-")
        extra="-"+temp[-2]+"-"+temp[-1]
        value=pod.replace(extra,"")
        if(value=="memcached-reservation"):
            value="memcached-reserve"
        ms_interace_mapper[iplink]=value
        PodNodeMapper[value]=node

def getTraffic():
    global ms_interace_mapper
    traffic_mapper={}
    res=[]
    for k,v in NodeIpMapper.items():
        res_rpc=rpc_get_net_proc(v)
        res.extend(res_rpc)
    for i in range(2,len(res)):
        line=res[i].replace("\n","").split(" ")
        while '' in line:
            line.remove('')
        interface=line[0].replace(":","")
        if(interface in ms_interace_mapper.keys()):
            if(ms_interace_mapper[interface] not in traffic_mapper.keys()):
                traffic_mapper[ms_interace_mapper[interface]]=[int(line[9]),int(line[1])]
            else:
                traffic_mapper[ms_interace_mapper[interface]][0]+=int(line[9])
                traffic_mapper[ms_interace_mapper[interface]][1]+=int(line[1])
    return traffic_mapper

def calTrafficRate(traffic_mapper_old,traffic_mapper_new,duration):
    this_sample_rate={}
    for key in traffic_mapper_old:
        in_traffic_rate=(traffic_mapper_new[key][0]-traffic_mapper_old[key][0])/duration/1000000*8
        out_traffic_rate=(traffic_mapper_new[key][1]-traffic_mapper_old[key][1])/duration/1000000*8
        this_sample_rate[key]=[in_traffic_rate,out_traffic_rate,duration]
    return this_sample_rate

def calUpperandBacktrafic(this_Access_Record,this_sample_rate):
    for target in this_Access_Record:
        target.in_traffic=this_sample_rate[target.name][0]
        target.out_traffic=this_sample_rate[target.name][1]
        target.upper_traffic=target.in_traffic
        target.back_traffic=target.out_traffic
        for child in target.children:
            target.upper_traffic-=child.back_traffic
            target.back_traffic-=child.upper_traffic
    return this_Access_Record

def runTrafficMonitor(Access_Record):
    traffic_mapper_old=getTraffic()
    t_old=time.time()
    while(True):
        time.sleep(1)
        traffic_mapper_new=getTraffic()
        t_new=time.time()
        this_sample_rate=calTrafficRate(traffic_mapper_old,traffic_mapper_new,t_new-t_old)
        this_Access_Record=calUpperandBacktrafic(copy.deepcopy(Access_Record),this_sample_rate)
        for i in range(len(this_Access_Record)):
            print(this_Access_Record[i].name,this_Access_Record[i].upper_traffic,this_sample_rate['entering-ms'][2])
        print()
        traffic_mapper_old=traffic_mapper_new
        t_old=t_new

def runOneTime():
    root=buildDAG()
    Access_Record=[]
    postOrder(Access_Record,root)
    ms_interace()
    traffic_mapper_old=getTraffic()
    t_old=time.time()
    time.sleep(5)
    traffic_mapper_new=getTraffic()
    t_new=time.time()
    this_sample_rate=calTrafficRate(traffic_mapper_old,traffic_mapper_new,t_new-t_old)
    this_Access_Record=calUpperandBacktrafic(copy.deepcopy(Access_Record),this_sample_rate)
    return this_Access_Record

if __name__ == "__main__":
    root=buildDAG()
    Access_Record=[]
    postOrder(Access_Record,root)
    for target in Access_Record:
        print(target.name)
    ms_interace()
    runTrafficMonitor(Access_Record)
