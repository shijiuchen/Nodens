import client.ProfileGet as cc
import os,json
from collections import defaultdict
import pandas
import time
from multiprocessing import Process
import datetime



NodeIpMapper = {
    "cpu-03": "10.2.64.3:50052",
    "cpu-04": "10.2.64.4:50052",
    "cpu-07": "10.2.64.7:50052",
    "cpu-08": "10.2.64.8:50052",
}
def execute_load(cmd):
    print(cmd)
    os.system(cmd)

# analyse the string  format  docker stats 
def getComputeRes(res1):
    Res_mapper={}
    
    res_name,res_CPU,res_MEM=[],[],[]
    for i in range(len(res1)):
        array_temp1=res1[i].split(" ")
        counter1=0
        for j in range(1,len(array_temp1)):
            if(array_temp1[j]!=''):
                counter1+=1
                if(counter1==1):
                    res_name.append(array_temp1[j])
                elif(counter1==2):
                    res_CPU.append([array_temp1[j]])
                elif(counter1==3):
                    res_MEM.append([array_temp1[j]])
                    break
    for i in range(len(res_name)):
        ms=res_name[i]
        temp=ms.replace("\n","").split("_")[1].replace("ebc1-","")
        cpu=float(res_CPU[i][0].replace("%",""))
        if("GiB" in res_MEM[i][0].replace("\n","")):
            memory=float(float(res_MEM[i][0].replace("GiB",""))*1000)
        else:
            memory=float(res_MEM[i][0].replace("MiB",""))
        if(temp not in Res_mapper.keys()):
            Res_mapper[temp]=[cpu,memory]
        else:
            Res_mapper[temp][0]+=cpu
            Res_mapper[temp][1]+=memory
    return Res_mapper



# run loadgenerator
cmd_load = "python3 LoadGenerator.py -q 2000'"
p_load=Process(target=execute_load,args=(cmd_load,))
p_load.start()
dt_time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


# get profile
count=0
max_count=8
list_profile=[]
while(count<max_count):
    lines_str = ''
    for k, v in NodeIpMapper.items():
        str_res = cc.getProfile(v)
        lines_str += str_res
    lines_get_proc = lines_str.split('\n')
    # print(lines_get_proc)
    profile_map = getComputeRes(lines_get_proc)
    list_profile.append(profile_map)
    count+=1
    # time.sleep(3)
dt_time3 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
 
 
# compute the mean value 
new_map=defaultdict(list)
key_new=set()
for profile_map in list_profile:
    for k,v in profile_map.items():
        key_new.add(k)
l_key_new=list(key_new)
for k in l_key_new:
    new_map[k].append(0.0)
    new_map[k].append(0.0)
# cpu_usage_all=defaultdict(float)
# mem_usage_all=defaultdict(float)
c_all=0


list_frame=[]
for profile_map in list_profile:
    for k,v in profile_map.items():
        new_map[k][0]+=v[0]
        new_map[k][1]+=v[1]
        list_frame.append([c_all,k,v[0],v[1]])
    c_all+=1

for k,v in new_map.items():
    new_map[k][0]=new_map[k][0]/c_all
    new_map[k][1]=new_map[k][1]/c_all


res_profile_json=json.dumps(new_map)
with open('profile_test.json',mode='w',encoding='utf-8') as f:
    f.write(res_profile_json)


dt_time4 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

print("2 ",dt_time2)
print("3 ",dt_time3)
print("4 ",dt_time4)

print("end...")
