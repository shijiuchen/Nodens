import os
import numpy as np
import time
import requests
import json
import pandas
import datetime

def get_time_stamp16(inputTime):
    date_stamp = str(int(time.mktime(inputTime.timetuple())))
    data_microsecond = str("%06d"%inputTime.microsecond)
    date_stamp = date_stamp+data_microsecond
    return int(date_stamp)

def get_latency(startTs,endTs,period):
    data=requests.get(url='http://127.0.0.1:30910/api/traces?service=enteringMS&start='+str(startTs)+'&end='+str(endTs)+'&prettyPrint=true&limit=6000000').json()
    counter=0
    latency = []
    errorCount=0
    for element in data['data']:
        counter+=1
        spanCount=0
        minTs=0.0
        maxTs=0.0
        flag=1
        for a in element['spans']:
            for b in a['tags']:
                if(b['key']=="error" and b['value']==True):
                    flag=0
            if(flag==0):
                errorCount+=1
                break#跳出循环
            spanCount+=1
            if(spanCount==1):
                minTs=float(a['startTime'])
                maxTs=float(a['startTime'])+float(a['duration'])
            else:
                if(minTs>float(a['startTime'])):
                    minTs=float(a['startTime'])
                else:
                    minTs=minTs
                if(maxTs<(float(a['startTime'])+float(a['duration']))):
                    maxTs=float(a['startTime'])+float(a['duration'])
                else:
                    maxTs=maxTs
        if(flag==1):
            time=(maxTs-minTs)/1000
            latency.append(time)
    if(counter==0 or len(latency)==0):
        return [0,0,0,0,0,0]
    return [np.mean(latency),np.percentile(latency,50),np.percentile(latency,99),len(latency)/period,errorCount]

def latency_analyze(startTime,duration):
    t_start=int(startTime*1000000)
    t_end=int((startTime+duration)*1000000)
    interval=100000#every 100ms requests
    index=t_start
    counter=0
    while(index<=t_end):
        res=get_latency(index,index+interval,0.1)
        print(counter,index,index+interval,res[0],res[1],res[2],res[3],res[4])#average,50th,99th,99.9th,throughput,errorCount
        index+=interval
        counter+=1

if __name__ == "__main__":
    latency_analyze(1683713739.2187307,35)