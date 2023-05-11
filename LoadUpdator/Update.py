import os
import scipy
import pandas
import numpy as np
import time
import sys
import copy
from queue import Queue

#For tree structure, all in-degree is 1
def Update_Traffic_Tree(ms_dag):
    print("Entering in......")
    BFS_name=list()
    q=Queue()
    q.put(ms_dag.root)
    BFS_name.append(ms_dag.root.name)
    while(not q.empty()):
        target=q.get()
        rate=target.realLoad/(target.handleLoad-target.overLoad)
        if(rate<1):
            rate=1
        print(target.name)
        for child in target.children:
            if(child.name not in BFS_name):
                child.realLoad=(child.monitorLoad-child.overLoad)*rate
                BFS_name.append(child.name)
                q.put(child)
    print("done")
    ms_dag.display()

#For graph structure, some in-degrees are above 1
def Update_Traffic_Graph(ms_dag):
    print("Entering in......")
    # mark visit times
    BFS_name={
        "frontend-search":1,
        "frontend-recommend":1,
        "frontend-reserve":1,
        "search":1,
        "check":2,
        "recommendation":1,
        "profile":2,
        "user":1,
        "reservation":1,
        "geo":1,
        "rate":1,
        "memcached-check":1,
        "rank-category":1,
        "rank-overall":1,
        "memcached-profile":1,
        "memcached-reservation":1,
        "mongodb-reservation":1,
        "memcached-rate":1
    }
    q=Queue()
    q.put(ms_dag.root)
    while(not q.empty()):
        target=q.get()
        idx1=target.index
        if(target.index==0):
            rate=target.realLoad/target.handleLoad
        else:
            target.realLoad=np.sum(ms_dag.Load_matrix[:,idx1])
            rate=target.realLoad/min(target.handleLoad,target.monitorLoad)
        if(rate<1):
            rate=1
        for child in target.pressure_children:
            if(BFS_name[child.name]!=0):
                idx2=child.index
                ms_dag.Load_matrix[idx1][idx2]=ms_dag.Load_matrix[idx1][idx2]*rate
                BFS_name[child.name]-=1
                if(BFS_name[child.name]==0):
                    q.put(child)
    print("==========done==========")
    ms_dag.display()

if __name__ == "__main__":
    Update_Traffic_Graph()