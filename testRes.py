import os
import time
#To import Grpc APIs
from client.client import rpc_adjust_res

#Node-Ip relationship
NodeIpMapper={
    "cpu-03":"10.2.64.3:50052",
    "cpu-04":"10.2.64.4:50052",
    "cpu-07":"10.2.64.7:50052",
    "cpu-08":"10.2.64.8:50052",
}

#pod-node relationship
pod_node_mapper={'check': 'cpu-04', 'consul': 'cpu-06', 'entering-ms': 'cpu-03', 'frontend-recommend': 'cpu-07', 'frontend-reserve': 'cpu-08', 'frontend-search': 'cpu-04', 'geo': 'cpu-04', 'jaeger': 'cpu-06', 'memcached-check': 'cpu-04', 'memcached-profile': 'cpu-07', 'memcached-rate': 'cpu-04', 'memcached-reservation': 'cpu-08', 'mongodb-check': 'cpu-04', 'mongodb-geo': 'cpu-04', 'mongodb-history': 'cpu-07', 'mongodb-profile': 'cpu-07', 'mongodb-rate': 'cpu-04', 'mongodb-recommendation': 'cpu-07', 'mongodb-reservation': 'cpu-08', 'mongodb-user': 'cpu-08', 'profile': 'cpu-07', 'rank-category': 'cpu-07', 'rank-overall': 'cpu-07', 'rate': 'cpu-04', 'recommendation': 'cpu-07', 'reservation': 'cpu-08', 'search': 'cpu-04', 'user': 'cpu-08'}

#pod-uid relationship
pod_uids={
    "entering-ms":['c95afad8-75ea-4cf6-b0a4-07982fad4cf7\n'],
    "frontend-search":['07b00721-06e6-47a6-abae-c6b6cb6512e0\n'],
    "frontend-recommend":['249ce56f-f436-411d-841a-1430135f8cd9\n'],
    "frontend-reserve":['1a545e65-91a4-4f99-96be-993366e7924d\n'],
    "search": ['41be1c59-1531-478f-8e4b-74b826e00c20\n'],
    "check": ['c2c39aef-516c-469d-b31c-c0e9193cea39\n'],
    "recommendation": ['75b476d8-759a-42ec-b02d-9f79ec0c3e99\n'],
    "profile": ['2fdee85b-2f09-4c96-922b-2f22800c1f53\n'],
    "user": ['153e0a9a-8cd5-439d-96e2-a21db4985b44\n'],
    "reservation": ['12ae4870-ceca-46c5-a8de-74992794251f\n'],
    "geo": ['80a37e50-bfbb-4a13-84e7-79a3a3e61879\n'],
    "rate":['1477e6df-edce-435f-8985-5a9d24359693\n'],
    "memcached-check":['bf8c4d95-e879-4116-82e4-75f0aed3469f\n'],
    "rank-category": ['4a0e4a06-74bd-485b-9108-cda1b0bb2cdb\n'],
    "rank-overall": ['604e15ce-e6b7-45d6-8347-9f51954db5cf\n'],
    "memcached-profile": ['5cb477da-db24-4cee-97eb-c0668a6ef455\n'],
    "memcached-reservation": ['b295189c-b513-4ad5-99b6-ff8e6dd4ff09\n'],
    "mongodb-reservation":['67273aa4-7f56-45fc-a721-04ac453833bb\n'],
    "memcached-rate":['a2630e43-dd25-47f6-b14c-8ac73ba386b1\n']
}

#get pod-node relationship
def pod_node():
    pods=os.popen("kubectl get pods -o wide | awk '{print $1}'").readlines()
    nodes=os.popen("kubectl get pods -o wide | awk '{print $7}'").readlines()
    pod_node_mapper={}
    for i in range(len(pods)):
        pod=pods[i].replace("\n","")
        node=nodes[i].replace("\n","")
        if(pod=="NAME"):
            continue
        temp=pod.split("-")
        extra="-"+temp[-2]+"-"+temp[-1]
        pod_name=pod.replace(extra,"")
        pod_node_mapper[pod_name]=node
    print(pod_node_mapper)

#get pod-uid relationship
def get_pod_uids():
    for svc in pod_uids.keys():
        service=str(svc)
        os.system("./get_pod_uid.sh "+service+" >/dev/null 2>&1")
        uids=os.popen("cat uid.txt").readlines()
        print(svc, uids)

#Call Grpc APIs to adjust resources
def set_cpu(service,cpu,replicas_number=1):
    node=pod_node_mapper[service]
    ip_str=NodeIpMapper[node]
    uids=pod_uids[service]
    res=rpc_adjust_res(ip_str,uids,cpu)

#Adjust the initial state using profiling on own cluster
def set_QoS_violations():
    set_cpu("entering-ms",24,1)
    set_cpu("frontend-search",9.1,1)
    set_cpu("frontend-recommend",10.5,1)
    set_cpu("frontend-reserve",5.1,1)
    set_cpu("search",6.5,1)
    set_cpu("check",10,1)
    set_cpu("recommendation",6,1)
    set_cpu("profile",6,1)
    set_cpu("user",1.6,1)
    set_cpu("reservation",3.5,1)
    set_cpu("geo",2.5,1)
    set_cpu("rate",4.2,1)
    set_cpu("memcached-check",4,1)
    set_cpu("rank-category",2,1)
    set_cpu("rank-overall",3,1)
    set_cpu("memcached-profile",1.5,1)
    set_cpu("memcached-rate",1.2,1)
    set_cpu("memcached-reservation",1.5,1)

#Adjust the enough resources for the  on own cluster
def set_enough():
    set_cpu("entering-ms",48,1)
    set_cpu("frontend-search",19,1)
    set_cpu("frontend-recommend",21,1)
    set_cpu("frontend-reserve",11,1)
    set_cpu("search",13.2,1)
    set_cpu("check",20,1)
    set_cpu("recommendation",13.2,1)
    set_cpu("profile",13.5,1)
    set_cpu("user",3.5,1)
    set_cpu("reservation",9,1)
    set_cpu("geo",5,1)
    set_cpu("rate",8.8,1)
    set_cpu("memcached-check",6.6,1)
    set_cpu("rank-category",4,1)
    set_cpu("rank-overall",6,1)
    set_cpu("memcached-profile",3,1)
    set_cpu("memcached-rate",2.4,1)
    set_cpu("memcached-reservation",2,1)


if __name__ == "__main__":
    pod_node()
    get_pod_uids()
    set_enough()
    set_QoS_violations()
    print(time.time())