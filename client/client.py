#! /usr/bin/env python
# coding=utf8
import grpc
import time,json
import client.distributed_pb2_grpc as distributed_pb2_grpc
import  client.distributed_pb2  as distributed_pb2

def rpc_get_traffic(ip_str):
    '''
    get the traffic 
    '''
    time1=time.time()
    conn=grpc.insecure_channel(ip_str)
    client = distributed_pb2_grpc.GrpcServiceStub(channel=conn)
    request = distributed_pb2.TrafficRequest(data=ip_str)
    response = client.get_traffic(request)
    res_net=response.result

    return res_net

def rpc_adjust_res(ip_str,uids,value):
    '''
    adjust resource from client
    :return:
    '''
    conn=grpc.insecure_channel(ip_str)
    client = distributed_pb2_grpc.GrpcServiceStub(channel=conn)
    # map_res is the resource allocated
    
    request = distributed_pb2.ResRequest(uids=uids,value=value)
    response = client.adjustRes(request)
    return response.result
    # print("func2 received:",response.result)
def rpc_get_profile(ip_str,svc_name):
    '''
    get the cpu use from client
    '''
    time1=time.time()
    conn=grpc.insecure_channel(ip_str)
    client = distributed_pb2_grpc.GrpcServiceStub(channel=conn)
    request = distributed_pb2.ProfileRequest(data=svc_name)
    response = client.get_profile(request)
    res_net=response.result
    return res_net
def rpc_get_net_proc(ip_str):
    '''
    get the in traffic of every interface of network
    :return:
    '''
    time1=time.time()
    conn=grpc.insecure_channel(ip_str)
    client = distributed_pb2_grpc.GrpcServiceStub(channel=conn)
    request = distributed_pb2.NetProcRequest(data=ip_str)
    response = client.get_net_proc(request)
    res_str=response.result
    res_net=res_str.split(',')

    return res_net
def run():
    # test function
    count=0
    test=10
    ip_str='10.3.64.4:50052'
    # time.sleep(2)
    while count<test:
        count+=1
        str1=rpc_get_traffic(ip_str)
        print(str1)
        time.sleep(1)
    # func3(1)
if __name__ == '__main__':
    run()
