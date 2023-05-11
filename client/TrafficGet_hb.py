import os
from collections import defaultdict
from client.client import rpc_adjust_res, rpc_get_traffic
import pandas
import time
from multiprocessing import Process
import datetime


ms_interface_mapper = defaultdict(list)  # {calicoxxx:[10.244.xx.xx,ms-0]}
ms_ip_mapper = defaultdict(list)
order_mapper_hb = {"entering-ms": [], "frontend-search": ["entering-ms"], "frontend-recommend": ["entering-ms"], "frontend-reserve": [
    "entering-ms"], "search": ["frontend-search"], "check": ["frontend-search"], "recommendation": ["frontend-recommend"], "profile": ["frontend-recommend"],  "user": ["frontend-reserve"], "reservation": ["frontend-reserve"], "geo": ["search"], "rate": ["search"], "memcached-check": ["check"], "rank-category": ["recommendation"], "rank-overall": ["recommendation"], "memcached-profile": ["profile"], "memcached-reservation": [
    "reservation"], "mongodb-reservation": ["reservation"], "memcached-rate": ["rate"]}
# {cpu-04:[calicoxxx,calicoxxx,......]} 
Node_interface_mapper = defaultdict(list)
NodeIpMapper = {
    "cpu-03": "10.2.64.3:50052",
    "cpu-04": "10.2.64.4:50052",
    "cpu-07": "10.2.64.7:50052",
    "cpu-08": "10.2.64.8:50052",
}




def analyse_lines(lines_get_proc):
    global ms_interface_mapper, ms_ip_mapper, order_mapper_ebc2, order_mapper_ebc1, order_mapper_hb
    now_ms = ''
    now_ip = ''
    map_res_traffic = defaultdict(int)
    map_res_num = defaultdict(int)
    for l in lines_get_proc:
        line = l.rstrip('\n')
        if line == '':
            continue
        if line.startswith('+'):
            ca_name = line[1:]
            if ca_name not in ms_interface_mapper.keys():
                continue
            now_ip = ms_interface_mapper[ca_name][0]
            now_ms = ms_interface_mapper[ca_name][1]
            continue
        if (now_ms not in order_mapper_hb.keys()) or (now_ms == ''):
            continue

        list_line = line.split(':')
        if len(list_line) < 3:
            print(l, "num is not correct!")
            return defaultdict(int), defaultdict(int)
        src_ip = list_line[0].split(';')[0]
        dst_ip = list_line[0].split(';')[1]
        traffic_loc = int(list_line[1])
        bag_num = int(list_line[2])
        if now_ms == "entering-ms" and (src_ip not in ms_ip_mapper.keys()):
            map_res_traffic[now_ms] += traffic_loc
            map_res_num[now_ms] += bag_num
            continue

        if (src_ip not in ms_ip_mapper) or (dst_ip not in ms_ip_mapper):
            # print(l,"src or dst is not in json")
            continue
        src_ms = ms_ip_mapper[src_ip][1]
        dst_ms = ms_ip_mapper[dst_ip][1]

        if dst_ms != now_ms:
            # print(l,"dst is not now_dst!")
            continue

        if src_ms in order_mapper_hb[now_ms]:
            map_res_traffic[now_ms] += traffic_loc
            map_res_num[now_ms] += bag_num
    return map_res_traffic, map_res_num



def ms_interace():
    global ms_interface_mapper, ms_ip_mapper, Node_interface_mapper
    # MS-name, pod-ip, node-name
    pods_ips_nodes = os.popen(
        "kubectl get pods -o wide | awk '{print $1,$6,$7}'").readlines()
    for p_ip in pods_ips_nodes:
        p_ip = p_ip.rstrip('\n')
        l_pip = p_ip.split(' ')
        if len(l_pip) < 3:
            continue
        pod = l_pip[0]
        ip = l_pip[1]
        node = l_pip[2]
        if (pod == "NAME"):
            continue
        if (pod[:6] == "jaeger"):
            continue
        id = -1
        # Obatin the no of network interface
        try:
            id = os.popen("kubectl exec -i "+pod +
                          " -- cat /sys/class/net/eth0/iflink").readlines()[0].replace("\n", "")
        except IndexError:
            print("kubectl error", pod, id)
            continue
        idtarget = "'^"+id+":"+" "+"'"
        temp = ""
        # Obtain the network interface name
        if (node == "cpu-06"):  
            temp = os.popen("ip link show | grep "+idtarget +
                            " | awk '{print $2}'").readlines()[0].replace("\n", "")
        else: 
            temp = os.popen("ssh "+node+" 'ip link show | grep "+idtarget +
                            "'").readlines()[0].replace("\n", "").split(" ")[1]

        index = temp.find('@')
        iplink = temp[:index]
        temp = pod.split("-")
        extra = "-"+temp[-2]+"-"+temp[-1]
        value = pod.replace(extra, "")

        # print(iplink, ip, value)
        ms_interface_mapper[iplink] = [ip, value]
        ms_ip_mapper[ip] = [iplink, value]
        if node != 'cpu-06':
            Node_interface_mapper[node].append(iplink)
    pods_ips_nodes_svc = os.popen(
        "kubectl get svc | awk '{print $1,$3}'").readlines()
    for p_ip in pods_ips_nodes_svc:
        p_ip = p_ip.rstrip('\n')
        l_pip = p_ip.split(' ')
        if len(l_pip) < 2:
            continue
        pod = l_pip[0]
        ip = l_pip[1]

        if (pod == "NAME"):
            continue
        if (pod[:6] == "jaeger" or pod == "kubernetes"):
            continue
        ms_ip_mapper[ip] = ["", pod]
    for k, v in ms_interface_mapper.items():
        print(k, v)
    for k, v in ms_ip_mapper.items():
        print(k, v)

def execute_cmd(node, list_interface, ip_list):
    str_interface = ' '.join(list_interface)
    str_iplist = ' '.join(ip_list)
    cmd = "ssh "+node+" '/state/partition/zxtong_2/TrafficMonitor/TrafficGet/get_traffic_new " + \
        str_interface+" "+str_iplist+" 25 300 600'"
    print(cmd)
    os.system(cmd)




def start_capture():
    global Node_interface_mapper, ms_interface_mapper
    print("Node_interface_mapper", Node_interface_mapper)
    process_list = []
    for k, v in Node_interface_mapper.items():
        if len(v) == 0:
            continue
        ip_list = []
        for interface_name in v:
            ip_list.append(ms_interface_mapper[interface_name][0])
        p = Process(target=execute_cmd, args=(k, v, ip_list,))
        # print(list_ms_4)
        process_list.append(p)
    for p in process_list:
        p.start()
    return process_list



def getTraffic():
    global ms_interface_mapper, ms_ip_mapper
    traffic_mapper = defaultdict(int)
    lines_str = ''
    for k, v in NodeIpMapper.items():
        if k not in Node_interface_mapper.keys():
            continue
        str_res = rpc_get_traffic(v)
        lines_str += str_res
    lines_get_proc = lines_str.split('\n')
    # print(lines_get_proc)
    traffic_mapper, res_tmp = analyse_lines(lines_get_proc)
    return traffic_mapper, res_tmp


if __name__ == '__main__':
    dt_time0 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    ms_interace()
    dt_time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    process_list = start_capture()

    list_frame = []
    count = 0
    max_count = 20
    lines = []


    old_map_traffic = defaultdict(int)
    old_map_num = defaultdict(int)
    dt_time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    while (count < max_count):
        time.sleep(0.5)
        print(count)
        new_map_traffic, new_map_num = getTraffic()
        for k, v in new_map_traffic.items():
            l_tmp = [count, k, v-old_map_traffic[k],
                     new_map_num[k]-old_map_num[k]]
            list_frame.append(l_tmp)
        old_map_traffic = new_map_traffic
        old_map_num = new_map_num
        count += 1
    dt_time3 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    for p in process_list:
        p.terminate()
        p.join()
    '''
    '''

    dt_time4 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(dt_time0)
    print(dt_time1)
    print(dt_time2)
    print(dt_time3)
    print(dt_time4)

    df = pandas.DataFrame(list_frame, columns=[
                          'time', 'direction', 'traffic', 'num'])
    df.to_csv('speed.csv')
