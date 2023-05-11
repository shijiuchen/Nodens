import os
import pandas
import numpy as np
import time

SLA=3#QoS reovery time, can be changed

#time_interval: monitor interval
def Compensate(ms_dag,time_interval):
    # Compensate for every microservice
    for ms in ms_dag.Access_Record:
        # this queue
        this_overLoad=ms.realLoad-min(ms.monitorLoad-ms.overLoad,ms.handleLoad-ms.overLoad)
        this_queueRequests=this_overLoad*time_interval
        # history queue
        history_overLoad=ms.overLoad
        history_surplusTime=ms.SLAtime-time_interval
        history_queueRequests=history_overLoad*history_surplusTime
        # all queue
        all_queueRequests=this_queueRequests+history_queueRequests
        # needed total load
        ms.SLAtime=SLA-time_interval
        all_Requests=all_queueRequests+ms.realLoad*ms.SLAtime
        tot_load=all_Requests/ms.SLAtime
        # cal overload
        ms.overLoad=tot_load-ms.realLoad
        
    print("==========Compensate Done.==========")
    ms_dag.display()

if __name__ == "__main__":
    print()