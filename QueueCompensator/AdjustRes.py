import os
import time
import sys
sys.path.append(".") 
# To import grpc APIs
from client.client import rpc_adjust_res

#Node-Ip relationship
pod_node_mapper={'check': 'cpu-04', 'consul': 'cpu-06', 'entering-ms': 'cpu-03', 'frontend-recommend': 'cpu-07', 'frontend-reserve': 'cpu-08', 'frontend-search': 'cpu-04', 'geo': 'cpu-04', 'jaeger': 'cpu-06', 'memcached-check': 'cpu-04', 'memcached-profile': 'cpu-07', 'memcached-rate': 'cpu-04', 'memcached-reservation': 'cpu-08', 'mongodb-check': 'cpu-04', 'mongodb-geo': 'cpu-04', 'mongodb-history': 'cpu-07', 'mongodb-profile': 'cpu-07', 'mongodb-rate': 'cpu-04', 'mongodb-recommendation': 'cpu-07', 'mongodb-reservation': 'cpu-08', 'mongodb-user': 'cpu-08', 'profile': 'cpu-07', 'rank-category': 'cpu-07', 'rank-overall': 'cpu-07', 'rate': 'cpu-04', 'recommendation': 'cpu-07', 'reservation': 'cpu-08', 'search': 'cpu-04', 'user': 'cpu-08'}

#pod-node relationship
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

#pod-uid relationship
def get_pod_uids():
    for svc in pod_uids.keys():
        service=str(svc)
        os.system("./get_pod_uid.sh "+service+" >/dev/null 2>&1")
        uids=os.popen("cat uid.txt").readlines()
        print(svc, uids)

#Call Grpc APIs to adjust resources
def set_cpu(ms_dag,service,cpu,replicas_number=1):
    node=ms_dag.PodNodeMapper[service]
    ip_str=ms_dag.NodeIpMapper[node]
    uids=pod_uids[service]
    res=rpc_adjust_res(ip_str,uids,cpu)

#Call set_CPU
def run_set_cpu(ms_dag):
    for target in ms_dag.Access_Record:
        # if(target.name=="mongodb-reservation"):
            # continue
        print(target.name,target.CPU_Allocated)
        set_cpu(ms_dag,target.name,target.CPU_Allocated,1)
        target.handleLoad=target.realLoad+target.overLoad
    print("Set all CPU done")

if __name__ == "__main__":
    get_pod_uids()