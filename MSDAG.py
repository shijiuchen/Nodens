import os
import numpy as np
from queue import Queue

#Node refers to each MS
class Node:
    def __init__(self,index,name,in_traffic,out_traffic,upper_traffic,back_traffic,children,pressure_children,realLoad,monitorLoad,handleLoad,CPU_Allocated,CPU_Need,overLoad,SLAtime):
        self.index=index
        self.name=name
        self.in_traffic=in_traffic
        self.out_traffic=out_traffic
        self.upper_traffic=upper_traffic
        self.back_traffic=back_traffic
        self.children=children
        self.pressure_children=pressure_children
        self.realLoad=realLoad
        self.monitorLoad=monitorLoad
        self.handleLoad=handleLoad
        self.CPU_Allocated=CPU_Allocated
        self.CPU_Need=CPU_Need
        self.overLoad=overLoad
        self.SLAtime=SLAtime

    def display(self):
        print(self.index,self.name,self.in_traffic,self.out_traffic,self.upper_traffic,self.back_traffic,self.children,self.pressure_children,self.realLoad,self.monitorLoad,self.handleLoad,self.CPU_Allocated,self.CPU_Need,self.overLoad,self.SLAtime)

#DAG for all MSs
class MSDAG:
    def __init__(self, root, MS_number, Traffic_matrix, Load_matrix, Access_Record, ms_interface_mapper, PodNodeMapper={},NodeIpMapper={}):
        self.root=root
        self.MS_number=MS_number
        self.Traffic_matrix=Traffic_matrix
        self.Load_matrix=Load_matrix
        self.Access_Record=Access_Record
        self.ms_interface_mapper=ms_interface_mapper
        self.PodNodeMapper=PodNodeMapper
        self.NodeIpMapper=NodeIpMapper

    #Initial microservices
    def buildDAG(self):
        checkmmc=Node(12,"memcached-check",0,0,0,0,[],[],0,0,1000,0,0,0,0)
        check=Node(5,"check",0,0,0,0,[checkmmc],[checkmmc],0,0,1000,0,0,0,0)
        ratemmc=Node(18,"memcached-rate",0,0,0,0,[],[check],0,0,500,0,0,0,0)
        geo=Node(10,"geo",0,0,0,0,[],[check],0,0,500,0,0,0,0)
        rate=Node(11,"rate",0,0,0,0,[ratemmc],[ratemmc],0,0,500,0,0,0,0)
        search=Node(4,"search",0,0,0,0,[geo,rate],[rate,geo],0,0,1000,0,0,0,0)
        frontendSearch=Node(1,"frontend-search",0,0,0,0,[search,check],[search],0,0,1000,0,0,0,0)
        profilemmc=Node(15,"memcached-profile",0,0,0,0,[],[],0,0,1000,0,0,0,0)
        profile=Node(7,"profile",0,0,0,0,[profilemmc],[profilemmc],0,0,1000,0,0,0,0)
        rank_overall=Node(14,"rank-overall",0,0,0,0,[],[profile],0,0,500,0,0,0,0)
        rank_category=Node(13,"rank-category",0,0,0,0,[],[profile],0,0,500,0,0,0,0)
        recommend=Node(6,"recommendation",0,0,0,0,[rank_category,rank_overall],[rank_category,rank_overall],0,0,1000,0,0,0,0)
        frontendRecommend=Node(2,"frontend-recommend",0,0,0,0,[recommend,profile],[recommend],0,0,1000,0,0,0,0)
        reservemongodb=Node(17,"mongodb-reservation",0,0,0,0,[],[],0,0,500,0,0,0,0)
        reservemmc=Node(16,"memcached-reservation",0,0,0,0,[],[],0,0,500,0,0,0,0)
        reserve=Node(9,"reservation",0,0,0,0,[reservemmc,reservemongodb],[reservemmc,reservemongodb],0,0,500,0,0,0,0)
        user=Node(8,"user",0,0,0,0,[],[reserve],0,0,500,0,0,0,0)
        frontendReserve=Node(3,"frontend-reserve",0,0,0,0,[user,reserve],[user],0,0,500,0,0,0,0)
        EnteringMS=Node(0,"entering-ms",0,0,0,0,[frontendSearch,frontendRecommend,frontendReserve],[frontendSearch,frontendRecommend,frontendReserve],3675.0,3675.0,2500,0,0,0,0)
        self.root=EnteringMS
        #Traffic matrix
        self.MS_number=19
        self.Traffic_matrix=np.zeros((self.MS_number,self.MS_number))
        #Load matrix
        self.Load_matrix=np.zeros((self.MS_number,self.MS_number))
        #Node-IP relationship
        self.NodeIpMapper={
            "cpu-03":"10.2.64.3:50052",
            "cpu-04":"10.2.64.4:50052",
            "cpu-07":"10.2.64.7:50052",
            "cpu-08":"10.2.64.8:50052",
        }

    #Post order microservices
    def postOrder(self,root):
        if not root:
            return
        for target in root.children:
            self.postOrder(target)
        self.Access_Record.append(root)

    #pod-interface relationship
    def ms_interface(self):
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
            pod_name=pod.replace(extra,"")
            self.ms_interface_mapper[iplink]=pod_name
            self.PodNodeMapper[pod_name]=node
    
    #display all
    def display(self):
        print("==========DAG Root:==========")
        self.root.display()
        print("==========Microservice Number:==========")
        print(self.MS_number)
        print("==========Load_matrix:==========")
        for i in range(len(self.Load_matrix)):
            print(i,list(self.Load_matrix[i]))
        print("==========All Nodes(post order):==========")
        for target in self.Access_Record:
            target.display()
        print("==========Pod<->Interfaces==========")
        for key in self.ms_interface_mapper:
            print(key,self.ms_interface_mapper[key])
        print("==========Pod<->Node:==========")
        for key in self.PodNodeMapper:
            print(key,self.PodNodeMapper[key])

if __name__ == "__main__":
    root=Node(0,"test",0,0,0,0,[],[],0,0,0,0,0,0,0)
    ms_dag=MSDAG(root,0, np.zeros((1,1)),np.zeros((1,1)),[],{})
    ms_dag.buildDAG()
    ms_dag.postOrder(ms_dag.root)
    ms_dag.ms_interface()
    ms_dag.display()