#! /usr/bin/env python
# coding=utf8

import time
from concurrent import futures
import grpc
import os

import distributed_pb2_grpc,distributed_pb2

from datetime import datetime,timedelta
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


# service name:corresponds the keys of pod_uids
# cpu: resource of cpu,1 is 0.1 CPU core
# replica_number: replica number of MS
def set_cpu(uids,cpu):
    cpu=cpu*10000
    cpu=int(cpu)
    
    cpu_every=cpu//len(uids)
    # print(cpu_every)
    for uid in uids:
        uid=uid.replace("\n","")
        path = '/sys/fs/cgroup/cpu/kubepods/besteffort/pod' + uid + '/cpu.cfs_quota_us'
        print(path,cpu_every)
        # f = open(path,"r")
        # original = int(f.read())
        # f.close()
        if cpu_every<1000:
            cpu_every=1000
        curr_value = str(cpu_every)
        with open(path, "w+") as f:
            f.write(curr_value)




class TestService(distributed_pb2_grpc.GrpcServiceServicer):

    def __init__(self):
        
        pass
    
    def adjustRes(self, request, context):
        '''
        adjust resource
        '''
        uids=request.uids
        cpu_value=float(request.value)
        
       
        print(uids,cpu_value)
        set_cpu(uids,cpu_value)
        result='1'
        return distributed_pb2.ResResponse(result=str(result))
    def get_profile(self, request, context):
        '''
        get the cpu use of mircoservices
        '''
        svc_name = request.data
        timestampf=datetime.now().timestamp()
        cmd="docker stats --no-stream | grep "+svc_name
        res1=os.popen(cmd).readlines()
        res_net=''.join(res1)
        # res_net="success"
        return distributed_pb2.ProfileResponse(result=res_net,time_stamp=timestampf)
    def get_net_proc(self, request, context):
        '''
        get the total traffic of interface of net
        '''

        src_ip = request.data
        timestampf=datetime.now().timestamp()
        # print(timestampf)
        
        
        lines = os.popen("cat /proc/net/dev").readlines()
        res_net=','.join(lines)

        # print(res_net)
        
        return distributed_pb2.NetProcResponse(result=res_net,time_stamp=timestampf)
    
    
    
def run():
    '''
    start service
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=70))
    distributed_pb2_grpc.add_GrpcServiceServicer_to_server(TestService(),server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("start service...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
if __name__ == '__main__':
    run()
