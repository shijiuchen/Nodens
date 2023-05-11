import os
import scipy
import pandas
import numpy as np
import time
import sys
from MSDAG import *
from NetTrafficMonitor.NetTrafficMonitor import initialize,runOneTime
from LoadUpdator.Update import Update_Traffic_Tree,Update_Traffic_Graph
from Predict.Predictor import predict_net_to_load, predict_load_to_CPU
from QueueCompensator.AdjustRes import run_set_cpu
from QueueCompensator.Compensator import Compensate
from testRes import set_QoS_violations, set_enough
from multiprocessing import Process

if __name__ == "__main__":
    
    # set enough resources
    set_enough()
    #Traffic monitoritor interval & overhead
    time_interval=1.05
    #Initial DAG
    root=Node(0,"test",0,0,0,0,[],[],0,0,0,0,0,0,0)
    ms_dag=MSDAG(root,0, np.zeros((1,1)),np.zeros((1,1)),[],{})
    ms_dag.buildDAG()
    ms_dag.postOrder(ms_dag.root)
    ms_dag.ms_interface()
    ms_dag.display()
    # Run 5 seconds normally
    print("begin_time=",time.time())
    time.sleep(5)
    # Adjust to the resources with initial resouces
    time_monitor_start=time.time()
    print("QoS_violaiton_time=",time_monitor_start)
    set_QoS_violations()
    #Initial monitor
    initialize(ms_dag)
    # Monitor 1 seconds
    time.sleep(1)
    # 1.Get network traffic
    sampling_duration=runOneTime(ms_dag)
    # 2.Get monitor load
    predict_net_to_load(ms_dag)
    ms_dag.root.realLoad=ms_dag.root.monitorLoad
    # 3.Update real load
    Update_Traffic_Graph(ms_dag)
    # 4.Queued query drain
    Compensate(ms_dag,time_interval)
    # 5.Get CPU need
    predict_load_to_CPU(ms_dag)
    # 6.CPU allocation
    run_set_cpu(ms_dag)
    time_set_done=time.time()
    print("Adjustment done=",time_set_done)
    # Run extra time, then set enough
    time.sleep(3-(time.time()-time_monitor_start))
    set_enough()